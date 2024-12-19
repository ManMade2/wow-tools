import csv
import logging
from typing import List
from pathlib import Path

from wow_tools.data import ModelPlacement, Vector3, Vector4

MODEL_FILE_INDEX = 0
X_INDEX = 1
Y_INDEX = 2
Z_INDEX = 3
ROT_X_INDEX = 4
ROT_Y_INDEX = 5
ROT_Z_INDEX = 6
ROT_W_INDEX = 7
SCALE_FACTOR_INDEX = 8
MODEL_ID_INDEX = 9
TYPE_INDEX = 10
FILE_DATA_ID_INDEX = 11
DOODAD_SET_INDEX = 12
DOODAD_SET_NAMES_INDEX = 13


class ModelPlacementParser:
    """
    A parser for model placement information from CSV files.
    """

    def __init__(self, csv_folder: Path):
        """
        Initializes the ModelPlacementParser with the specified CSV folder.

        :param csv_folder: The folder containing the CSV files for model placements.
        """
        self._csv_folder = csv_folder
        self._logger = logging.getLogger(__name__)

    def _read_csv(self, csv_file: str) -> List[ModelPlacement]:
        """
        Reads model placement data from a CSV file.

        :param csv_file: The name of the CSV file (without extension) to read.
        :return: A list of ModelPlacement objects parsed from the CSV file.
        """
        csv_path = self._csv_folder / f"{csv_file}_ModelPlacementInformation.csv"

        if not csv_path.exists():
            self._logger.debug(f"CSV file not found: {csv_path.name}", extra={"csv_path": csv_path})
            return []

        with open(csv_path, "r") as file:
            reader = csv.reader(file, delimiter=";")
            next(reader)
            return [self._parse_model_placement(row) for row in reader]

    def _parse_model_placement(self, row: List[str]) -> ModelPlacement:
        """
        Parses a single row of model placement data from the CSV.

        :param row: A list of strings representing a row in the CSV file.
        :return: A ModelPlacement object created from the row data.
        """
        rotW = float(row[ROT_W_INDEX] if row[ROT_W_INDEX] != "" else 0)

        position = Vector3(x=float(row[X_INDEX]), y=float(row[Y_INDEX]), z=float(row[Z_INDEX]))
        rotation = Vector4(
            x=float(row[ROT_X_INDEX]), y=float(row[ROT_Y_INDEX]), z=float(row[ROT_Z_INDEX]), w=rotW
        )

        model_file = row[MODEL_FILE_INDEX].replace("..\\..\\", "").replace(".obj", ".glb")

        return ModelPlacement(
            model_file=model_file,
            position=position,
            rotation=rotation,
            scale_factor=float(row[SCALE_FACTOR_INDEX]),
            model_id=int(row[MODEL_ID_INDEX]),
            type=row[TYPE_INDEX],
            file_data_id=int(row[FILE_DATA_ID_INDEX]),
            doodad_set_index=int(row[DOODAD_SET_INDEX]),
            doodad_set_names=row[DOODAD_SET_NAMES_INDEX],
        )

    def get_models_for_files(self, adt_files: List[str]) -> List[ModelPlacement]:
        """
        Retrieves model placements for the specified ADT files.

        :param adt_files: A list of ADT file names to read model placements from.
        :return: A list of ModelPlacement objects.
        """

        self._logger.info("Getting models for files", extra={"adt_files": adt_files})
        models: List[ModelPlacement] = []

        for adt_file in adt_files:
            models.extend(self._read_csv(adt_file))

        return models
