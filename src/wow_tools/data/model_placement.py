from pydantic import BaseModel

from .vector3 import Vector3
from .vector4 import Vector4


class ModelPlacement(BaseModel):
    ModelFile: str
    Position: Vector3
    Rotation: Vector4
    ScaleFactor: float
    ModelId: int
    Type: str
    FileDataId: int
    DoodadSetIndex: int
    DoodadSetNames: str

    def __str__(self) -> str:
        return f"{self.model_dump_json(indent=4)}"

    def __hash__(self) -> int:
        return self.FileDataId

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ModelPlacement):
            return NotImplemented

        return self.FileDataId == other.FileDataId
