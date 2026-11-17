import json
import threading
import time
from unittest.mock import patch

import pytest
from pydantic import BaseModel

from backend.app.repositories.json_repository import JsonRepository


class Item(BaseModel):
    id: str
    name: str


def test_save_then_load_returns_the_same_items(tmp_path):
    repo = JsonRepository(tmp_path / "items.json", Item)

    repo._save_all([Item(id="1", name="first"), Item(id="2", name="second")])

    assert repo._load_all() == [Item(id="1", name="first"), Item(id="2", name="second")]


def test_missing_file_loads_as_empty_list(tmp_path):
    repo = JsonRepository(tmp_path / "missing.json", Item)

    with pytest.warns(UserWarning):
        assert repo._load_all() == []


def test_file_with_wrong_schema_raises_value_error(tmp_path):
    file_path = tmp_path / "items.json"
    file_path.write_text(json.dumps([{"id": "1"}]))
    repo = JsonRepository(file_path, Item)

    with pytest.raises(ValueError, match=r"list\[Item\]"):
        repo._load_all()


def test_failed_save_keeps_the_old_file_and_leaves_no_temp_file(tmp_path):
    file_path = tmp_path / "items.json"
    repo = JsonRepository(file_path, Item)
    repo._save_all([Item(id="1", name="original")])

    with patch("backend.app.repositories.json_repository.os.replace", side_effect=OSError("disk full")):
        with pytest.raises(OSError, match="Failed to save"):
            repo._save_all([Item(id="2", name="new")])

    assert repo._load_all() == [Item(id="1", name="original")]
    assert list(tmp_path.glob("*.tmp")) == []


def test_lock_stops_parallel_saves_from_overwriting_each_other(tmp_path):
    file_path = tmp_path / "items.json"
    JsonRepository(file_path, Item)._save_all([])

    def add_item(number):
        # A new repository per call, like a new request
        repo = JsonRepository(file_path, Item)
        with repo.lock():
            items = repo._load_all()
            time.sleep(0.01)  # widen the gap between load and save
            items.append(Item(id=str(number), name=f"item {number}"))
            repo._save_all(items)

    threads = [threading.Thread(target=add_item, args=(n,)) for n in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(JsonRepository(file_path, Item)._load_all()) == 8


def test_repositories_for_the_same_file_share_one_lock(tmp_path):
    first = JsonRepository(tmp_path / "items.json", Item)
    second = JsonRepository(tmp_path / "items.json", Item)
    other = JsonRepository(tmp_path / "other.json", Item)

    assert first.lock() is second.lock()
    assert first.lock() is not other.lock()
