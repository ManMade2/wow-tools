import asyncio  # type: ignore
from pathlib import Path

from belial_db import create_connection
from belial_db.repos import MapRepo
from belial_db.models import MapModel, AssetModel, AssetFileModel
from belial_db.data import Vector3, Vector4

from wow_tools.data import MapData
from wow_tools.map_creator import MapCreator  # type: ignore
from wow_tools.utils.logging_config import setup_logging

input_path = Path("C:/Users/MadsKris/Desktop/Input Data")
output_path = Path("C:/Users/MadsKris/Desktop/Converted Data")
blenderPath = Path("C:/Program Files/Blender Foundation/Blender 4.2/blender.exe")
DATABASE_URL = f"sqlite:///{output_path}/data.db"


def add_to_db(name: str):
    conn = create_connection(DATABASE_URL, echo=False)

    mapRepo = MapRepo(conn)

    assets: set[AssetModel] = set()
    assetFiles: set[AssetFileModel] = set()

    with open(f"{output_path}/maps/{name}.json", "r") as file:
        map_data = MapData.from_json(file.read())

        for model in map_data.models:

            asset = AssetModel()
            asset.id = model.model_id
            asset.asset_file_id = model.file_data_id
            asset.path = model.model_file
            asset.type = model.type
            asset.scale_factor = model.scale_factor
            asset.position = Vector3(x=model.position.x, y=model.position.y, z=model.position.z)
            asset.rotation = Vector4(
                x=model.rotation.x, y=model.rotation.y, z=model.rotation.z, w=model.rotation.w
            )

            assets.add(asset)

            assetFile = AssetFileModel()
            assetFile.id = model.file_data_id
            assetFile.path = model.model_file
            assetFile.type = model.type
            assetFile.doodad_set_index = model.doodad_set_index
            assetFile.doodad_set_names = model.doodad_set_names

            assetFiles.add(assetFile)

    map = MapModel()
    map.name = map_data.name
    map.id = map_data.id
    map.assets = list(assets)
    map.asset_files = list(assetFiles)

    mapRepo.create_map(map)


def main():
    setup_logging()

    # map_creator = MapCreator(blenderPath, input_path, output_path)
    # asyncio.run(map_creator.convert_map_objects())
    # asyncio.run(map_creator.create_map())

    add_to_db("1 - Dun Morogh")


if __name__ == "__main__":
    main()
