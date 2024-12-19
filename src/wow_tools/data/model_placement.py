from pydantic import BaseModel

from .vector3 import Vector3
from .vector4 import Vector4


class ModelPlacement(BaseModel):
    model_file: str
    position: Vector3
    rotation: Vector4
    scale_factor: float
    model_id: int
    type: str
    file_data_id: int
    doodad_set_index: int
    doodad_set_names: str

    def __str__(self) -> str:
        return f"{self.model_dump_json(indent=4)}"

    def __hash__(self) -> int:
        return self.file_data_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ModelPlacement):
            return NotImplemented

        return self.file_data_id == other.file_data_id
