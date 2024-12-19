import json
import logging
from pathlib import Path
from typing import Optional, Sequence
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory

from commander import CommandProtocol, Runner
from wow_tools.commands import CreateMap, ConvertToGltf, ConvertToGlb
from wow_tools.utils import ModelPlacementParser
from wow_tools.data import MapData, ModelPlacement


class MapCreator:
    """
    A class to create and convert maps using Blender.

    Attributes:
        blender_path (Path): The path to the Blender executable.
        input_path (Path): The path to the input directory containing models and maps.
        output_path (Path): The path to the output directory for generated files.
        model_parser (ModelPlacementParser): A parser for model placements.
    """

    def __init__(self, blender_path: Path, input_path: Path, output_path: Path):
        """
        Initializes the MapCreator with the specified paths.

        Args:
            blender_path (Path): The path to the Blender executable.
            input_path (Path): The path to the input directory.
            output_path (Path): The path to the output directory.
        """
        self._blender_path = blender_path
        self._input_path = input_path
        self._output_path = output_path
        self._model_parser = ModelPlacementParser(csv_folder=self._input_path / "csv")
        self._logger = logging.getLogger(__name__)

    def _open_file_dialog(self) -> Optional[Path]:
        """
        Opens a file dialog to select a JSON map file.

        Returns:
            Path | None: The selected file path or None if no valid file was selected.
        """
        Tk().withdraw()

        file_path = Path(
            askopenfilename(
                title="Select a map",
                initialdir=self._output_path / "Maps",
                filetypes=[("JSON files", "*.json")],
            )
        )

        if not file_path.exists() or not file_path.name.endswith(".json"):
            self._logger.error(f"Invalid map file: {file_path.name}")
            return None

        return file_path

    def _open_folder_dialog(self) -> Optional[Path]:
        """
        Opens a folder dialog to select a directory.

        Returns:
            Path | None: The selected folder path or None if the folder does not exist.
        """
        Tk().withdraw()

        folder_path = Path(askdirectory(title="Select a folder", initialdir=self._input_path / "sorted maps"))

        if not folder_path.exists():
            self._logger.error(f"Folder does not exist: {folder_path.name}")
            return None

        if folder_path == Path("."):
            self._logger.error(f"Folder is the current directory: {folder_path.name}")
            return None

        return folder_path

    def _filter_models(self, map: MapData) -> set[ModelPlacement]:
        """
        Filters out models from the map based on specific criteria.

        Args:
            map (Map): The map object containing models to filter.

        Returns:
            set[ModelPlacement]: A set of filtered model placements.
        """
        filtered_models: set[ModelPlacement] = set()

        for model in map.models:
            if "world\\critter" in str(model.model_file):
                continue

            if "world\\wmo" not in str(model.model_file):
                model.model_file = model.model_file.replace(".obj", ".phys.obj")

            filtered_models.add(model)

        return filtered_models

    async def create_map(self):
        """
        Creates a map by executing a series of commands based on the selected map file.
        """
        try:
            map_path = self._open_folder_dialog()
            if map_path is None:
                return

            self._logger.info(f"Map creation started: {map_path.name}")

            commands: dict[str, Sequence[CommandProtocol]] = {
                "Create Map": [CreateMap(map_path, self._blender_path)],
                "Convert To Gltf": [
                    ConvertToGltf(
                        Path(f"{map_path.name}.glb"),
                        self._output_path / "maps",
                    ),
                ],
            }

            results = await Runner.execute_set(commands)
            mapResult = results[0]

            if not mapResult.success:
                self._logger.error(f"Error creating map: {mapResult.message}")
                return

            models = self._model_parser.get_models_for_files(mapResult.output)

            split = map_path.name.split(" - ")

            if len(split) != 2:
                self._logger.error(f"Invalid map name: {map_path.name}")
                return

            map_id = int(split[0])
            map_name = split[1]

            map = MapData(name=map_name, id=map_id, models=models)

            with open(self._output_path / f"maps/{map_path.name}.json", "w") as f:
                f.write(map.model_dump_json(indent=4))

        except FileNotFoundError as e:
            self._logger.error(f"File not found: {e}")
        except Exception as e:
            self._logger.error(f"An unexpected error occurred during map creation: {e}")

    async def convert_map_objects(self):
        """
        Converts map objects to GLB and GLTF formats based on the selected map file.
        """
        file_path = None
        try:
            file_path = self._open_file_dialog()
            if file_path is None:
                return

            map = MapData.model_validate_json(file_path.read_text())
            commands: dict[str, Sequence[CommandProtocol]] = {
                "Convert To Glb": [],
                "Convert To Gltf": [],
            }

            for model in self._filter_models(map):

                model_file_path = self._input_path / model.model_file.replace(".glb", ".obj")

                if not model_file_path.exists():
                    raise FileNotFoundError(f"Model file does not exist: {model_file_path}")

                model_output_path = self._output_path / model.model_file.replace(".glb", "")
                model_output_path.parent.mkdir(parents=True, exist_ok=True)

                if model_output_path.exists():
                    continue

                commands["Convert To Glb"].append(ConvertToGlb(model_file_path, self._blender_path))
                commands["Convert To Gltf"].append(
                    ConvertToGltf(
                        Path(f"{model_file_path.stem}.glb"),
                        Path(model_output_path.parent),
                    )
                )

            return await Runner.execute_set(commands, clean=False, wait_time=1, batch_size=10)

        except FileNotFoundError as e:
            self._logger.error(f"File not found: {e}")
        except json.JSONDecodeError as e:
            self._logger.error(f"Error decoding JSON from file: {file_path}, error: {e}")
        except Exception as e:
            self._logger.error(f"An unexpected error occurred during map object conversion: {e}")
