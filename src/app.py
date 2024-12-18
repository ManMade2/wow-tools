import asyncio
from pathlib import Path

from belial_db import create_connection
from belial_db.repos import MapRepo
from belial_db.models import MapModel, AssetModel, AssetFileModel
from belial_db.data import Vector3, Vector4

from wow_tools.data import MapData
from wow_tools.map_creator import MapCreator
from wow_tools.utils.logging_config import setup_logging

input_path = Path("C:/Users/MadsKris/Desktop/Input Data")
output_path = Path("C:/Users/MadsKris/Desktop/Converted Data")
blenderPath = Path("C:/Program Files/Blender Foundation/Blender 4.2/blender.exe")
DATABASE_URL = f"sqlite:///{output_path}/data.db"


def add_to_db(name: str):
    conn = create_connection(DATABASE_URL, echo=True)

    mapRepo = MapRepo(conn)

    assets: set[AssetModel] = set()
    assetFiles: set[AssetFileModel] = set()

    with open(f"{output_path}/Maps/{name}.json", "r") as file:
        map_data = MapData.from_json(file.read())

        for model in map_data.models:

            asset = AssetModel()
            asset.Id = model.ModelId
            asset.AssetFileId = model.FileDataId
            asset.Path = model.ModelFile
            asset.Type = model.Type
            asset.ScaleFactor = model.ScaleFactor
            asset.Position = Vector3(x=model.Position.x, y=model.Position.y, z=model.Position.z)
            asset.Rotation = Vector4(
                x=model.Rotation.x, y=model.Rotation.y, z=model.Rotation.z, w=model.Rotation.w
            )

            assets.add(asset)

            assetFile = AssetFileModel()
            assetFile.Id = model.FileDataId
            assetFile.Path = model.ModelFile
            assetFile.Type = model.Type
            assetFile.DoodadSetIndex = model.DoodadSetIndex
            assetFile.DoodadSetNames = model.DoodadSetNames

            assetFiles.add(assetFile)

            break

    split = map_data.name.split("-")
    name = split[1]
    id = int(split[0])

    map = MapModel()
    map.Name = name
    map.Id = id
    map.Assets = list(assets)
    map.AssetFiles = list(assetFiles)

    mapRepo.create_map(map)


def main():
    setup_logging()
    # map_creator = MapCreator(blenderPath, input_path, output_path)
    # asyncio.run(map_creator.convert_map_objects())
    # asyncio.run(map_creator.create_map())


if __name__ == "__main__":
    main()
