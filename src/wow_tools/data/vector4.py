from pydantic import BaseModel


class Vector4(BaseModel):
    x: float
    y: float
    z: float
    w: float
