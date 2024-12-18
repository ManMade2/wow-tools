from pathlib import Path
from typing import Sequence
from commander import Result
from commander import CommandBase


def get_blender_script(input_folder: Path) -> str:
    return f"""
import bpy
import os
import sys

input_folder = r'{str(input_folder)}'
input_folder_name = r'{input_folder.name}'

if not os.path.exists(input_folder):
    print(f"Input folder does not exist: {{input_folder_name}}", file=sys.stderr)
    exit(3)

paths: list[str] = []

for file_name in os.listdir(input_folder):
    file_path = os.path.join(input_folder, file_name)
    if os.path.isfile(file_path) and file_path.lower().endswith(".obj"):
        paths.append(file_path)

if len(paths) == 0:
    print(f"No .obj files found in {{input_folder}}", file=sys.stderr)
    exit(3)

bpy.ops.wm.read_factory_settings(use_empty=True)

for path in paths:
    bpy.ops.wm.obj_import(filepath=path)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.join()
bpy.ops.export_scene.gltf(
    filepath=f"{{input_folder_name}}.glb",
    export_format="GLB"
)

print(f"Converted map: {{input_folder_name}} - {{len(paths)}} objects")
"""


class CreateMap(CommandBase):
    def __init__(self, input_folder: Path, blender_path: Path):
        super().__init__("Create Map")

        self._blender_path: Path = blender_path
        self._input_folder: Path = input_folder
        self._map_name: str = ""

    def _validate_stdout(self, stdout: str) -> Result:

        filtered: list[str] = []

        for line in stdout.splitlines():

            if line.startswith("Blender 4.2.3"):
                continue

            if line.startswith("OBJ import of"):
                continue

            if line.startswith("INFO Draco mesh compression"):
                continue

            if line.startswith("Blender quit"):
                continue

            if line == "":
                continue

            filtered.append(line)

        return Result(name=self.name, success=True, message="\n".join(filtered))

    def _validate_stderr(self, error: str, stderr: str) -> Result:
        return Result(name=self.name, success=False, message=f"{error}\n{stderr}")

    def _parse_map_data(self, stdout: str) -> list[str] | None:

        objects: list[str] = []

        for line in stdout.splitlines():

            if not line.startswith("OBJ import of '"):
                continue

            file_name = line.split("OBJ import of '")[1].split("'")[0].strip()
            base_name = file_name.rsplit(".", 1)[0]
            objects.append(base_name)

        return objects

    def post_process(self, stdout: str, temp_dir: Path, result: Result) -> Result:

        map_objects = self._parse_map_data(stdout)

        if map_objects is None:
            return Result(name=self.name, success=False, message="Failed to parse map data")

        return Result(
            name=self.name,
            success=True,
            message=f"Map: {self._map_name} - {len(map_objects)}",
            output=map_objects,
        )

    def build(self) -> Sequence[str]:
        self._map_name = self._input_folder.name

        return [
            str(self._blender_path),
            "--background",
            "--factory-startup",
            "--python-expr",
            get_blender_script(self._input_folder),
        ]

    def dispose(self):
        pass
