from pathlib import Path
import shutil

from commander import Result
from commander import BatCommand


def get_convert_to_gltf_script(file_path: Path) -> str:
    return f'npx @threlte/gltf@latest "{file_path}" --transform'


class ConvertToGltf(BatCommand):
    def __init__(self, file_path: Path, output_folder: Path):
        super().__init__("Convert To Gltf", get_convert_to_gltf_script(file_path))

        self._file_path: Path = file_path
        self._output_folder: Path = output_folder

    def _validate_stderr(self, error: str, stderr: str) -> Result:
        return Result(name=self.name, success=False, message=f"{error}\n{stderr}")

    def _validate_stdout(self, stdout: str) -> Result:
        return Result(name=self.name, success=True, message=stdout)

    def post_process(self, stdout: str, temp_dir: Path, result: Result) -> Result:

        path = temp_dir / self._file_path.name.replace(".glb", "-transformed.glb")

        if not path.exists():
            return Result(name=self.name, success=False, message=f"File {path} does not exist")

        try:
            shutil.move(path, self._output_folder / self._file_path.name)
        except Exception as e:
            return Result(
                name=self.name,
                success=False,
                message=f"Failed to move {path} to {self._output_folder / self._file_path.name}: {e}",
            )

        return result
