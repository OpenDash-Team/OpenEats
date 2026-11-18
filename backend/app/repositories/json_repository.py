from pathlib import Path
import json
from json import JSONDecodeError
import os
import tempfile
import threading
import warnings

from pydantic import BaseModel, TypeAdapter, ValidationError

# One lock per JSON file, shared by every repository object that points at that file.
# (A new repository is created for each request, so the lock can't live on the object itself.)
_file_locks: dict[Path, threading.RLock] = {}
_file_locks_guard = threading.Lock()


class JsonRepository[T: BaseModel]:
    """Shared load/save code for repositories that keep a list of models in one JSON file.

    Each repository (restaurants, customers, carts, orders...) only has to pass in its file
    path and model class. The reading, validating and atomic saving live here once.
    """

    def __init__(self, file_path: Path, model: type[T]) -> None:
        self.file_path: Path = file_path
        self.model: type[T] = model
        self._list_adapter = TypeAdapter(list[model])

    def lock(self) -> threading.RLock:
        """Hold this around a load -> change -> save, e.g. `with repository.lock(): ...`.

        Requests run in parallel threads, so without it two requests can both load the file,
        each add their change, and the second save silently wipes out the first.
        """
        with _file_locks_guard:
            return _file_locks.setdefault(self.file_path.resolve(), threading.RLock())

    def _load_all(self) -> list[T]:
        if not self.file_path.exists():
            warnings.warn(f"'{self.file_path.absolute()}' does not exist. Defaulting to an empty list.")
            return []

        with open(self.file_path, "r", encoding="utf-8") as file:
            try:
                return self._list_adapter.validate_python(json.load(file))
            except JSONDecodeError as e:
                raise JSONDecodeError(f"{self.file_path.absolute()} is not JSON serializable.", e.doc, e.pos) from e
            except ValidationError as e:
                raise ValueError(f"{self.file_path.absolute()} does not follow the correct list[{self.model.__name__}] schema.") from e

    def _save_all(self, items: list[T]) -> None:
        # Write to a temp file in the same folder first, then swap it in with os.replace.
        # If anything fails halfway, the original file is left untouched.
        temp_file_path = None

        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.file_path.parent, delete=False, suffix=".tmp") as temp_file:
                temp_file_path = temp_file.name
                json.dump([item.model_dump(mode="json") for item in items], temp_file, indent=4)

            os.replace(temp_file_path, self.file_path)

        except OSError as e:
            if temp_file_path is not None:
                try:
                    os.remove(temp_file_path)  # don't leave failed temp files behind
                except FileNotFoundError:
                    pass

            raise OSError(f"Failed to save to '{self.file_path.absolute()}'") from e
