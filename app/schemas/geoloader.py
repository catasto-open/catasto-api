from enum import Enum
from uuid import UUID
# from osgeo import ogr
from geopandas import GeoDataFrame
from typing import List, Union
from pydantic import BaseModel, FilePath, validator, AnyUrl


class DatasetType(Enum):

    # possible list of file types
    SHAPEFILE = "shapefile"
    GEOPACKAGE = "geopackage"


class FilesPath(BaseModel):
    __root__: List[FilePath]


class CustomBaseGeoModel(BaseModel):
    id: Union[int, str, UUID]

    @validator('id')
    def is_uuid4_string(cls, value):
        try:
            UUID(value, version=4)
        except ValueError as ve:
            raise ValueError('The id value is not uuid4') from ve
        return value

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            GeoDataFrame: lambda v: serialize_with_geopandas(v)
        }


class Dataset(CustomBaseGeoModel):
    name: str
    type: DatasetType
    files: FilesPath


class ShapefileDataset(Dataset):
    
    @validator('type')
    def is_shapefile_type(cls, val):
        if not val == DatasetType.SHAPEFILE:
            raise ValueError('The value is not shapefile')
        return val.value

    @validator('files')
    def is_shapefile(cls, values):
        shp_suffixes = []
        for value in values.__root__:
            shp_suffixes.append(value.suffix)
        # using all() to check subset of list
        valid = 0
        if (all(
            x in shp_suffixes for x in [
                '.shp', '.shx', '.dbf', '.prj'
            ]
        )):
            valid = 1
        if not valid:
            raise ValueError('The files are not valid for a shapefile')
        # return files
        return values.__root__


class GeopackageDataset(Dataset):
    
    @validator('type')
    def is_geopackage_type(cls, val):
        if not val == DatasetType.GEOPACKAGE:
            raise ValueError('The value is not geopackage')
        return val.value

    @validator('files')
    def is_geopackage(cls, values):
        gpkg_suffixes = []
        for value in values.__root__:
            gpkg_suffixes.append(value.suffix)
        # using all() to check subset of list
        valid = 0
        if (all(
            x in gpkg_suffixes for x in ['.gpkg']
        )):
            valid = 1
        if not valid:
            raise ValueError('The files are not valid for a geopackage')
        # return files
        return values.__root__


class ShapefileDataframe(CustomBaseGeoModel):
    geodataframe: GeoDataFrame

    @validator('geodataframe')
    def is_geodataframe(cls, val):
        return val


def serialize_with_geopandas(geodataframe: GeoDataFrame):
    return geodataframe.to_json()

# def serialize_with_gdal(files: FilesPath):
#     fc = {
#         'type': 'FeatureCollection',
#         'features': []
#     }
#     for _file in files:
#         if "shp" in _file.absolute():
#             driver_name = "ESRI Shapefile"
#             driver = ogr.GetDriverByName(driver_name)
#             dataset = _file.absolute()
#         datasource = driver.Open(dataset, 0)
#         layer = datasource.GetLayer(0)
#         for feature in layer:    
#             fc['features'].append(
#                 feature.ExportToJson(as_object=True)
#             )
#         return fc


class UploadSuccessResponse(BaseModel):
    dataset: str
    filenames: List[str]
    url: AnyUrl
    metadata: dict