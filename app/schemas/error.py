from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"detail": "Not found"},
                {"detail": "Could not validate credentials"},
                {"detail": "Admin access required"},
            ]
        }
    }