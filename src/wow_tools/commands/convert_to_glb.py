from pathlib import Path
from typing import Sequence

from commander import Result
from commander import CommandBase


def get_blender_script(file_path: Path) -> str:

    return f"""
import bpy
import os
import sys

file_path = r'{str(file_path)}'
file_name = r'{file_path.stem}'

if not os.path.exists(file_path):
    print(f"Input folder does not exist: {{file_name}}", file=sys.stderr)
    exit(3)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=file_path)


bpy.ops.export_scene.gltf(
    filepath=f"{{file_name}}.glb",
    export_format="GLB"
)
"""


class ConvertToGlb(CommandBase):
    def __init__(self, file_path: Path, blender_path: Path):
        super().__init__("Convert To Glb")

        self._file_path: Path = file_path
        self._blender_path: Path = blender_path

    def build(self) -> Sequence[str]:

        return [
            str(self._blender_path),
            "--background",
            "--factory-startup",
            "--python-expr",
            get_blender_script(self._file_path),
        ]

    def post_process(self, stdout: str, temp_dir: Path, result: Result) -> Result:
        return Result(name=self.name, success=True, message="", output=[])

    def dispose(self):
        pass

    def _validate_stderr(self, error: str, stderr: str) -> Result:
        return Result(name=self.name, success=False, message=f"{error}\n{stderr}")

    def _validate_stdout(self, stdout: str) -> Result:
        return Result(name=self.name, success=True, message="", output=[])
