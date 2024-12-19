from pydantic import BaseModel
from typing import Any

from .model_placement import ModelPlacement


class MapData(BaseModel):
    name: str
    id: int
    models: list[ModelPlacement]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MapData":
        return cls.model_validate(data)

    @classmethod
    def from_json(cls, json_str: str) -> "MapData":
        return cls.model_validate_json(json_str)
