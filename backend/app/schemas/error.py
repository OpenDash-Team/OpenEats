from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Body of every error the API sends on purpose (401, 404, 409...)."""

    detail: str
