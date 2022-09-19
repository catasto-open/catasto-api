from typing import List
from fastapi import APIRouter, Depends, Query, File, UploadFile

from app.config.client import get_storage_clients
from app.schemas.geoloader import (
    DatasetType,
    UploadSuccessResponse,
)
from app.services.geoloader import GeoloaderService
from app.utils.service_result import handle_result


router = APIRouter(
    prefix="/caricamento",
    tags=["georoma"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/workflows",
    response_model=UploadSuccessResponse,
)
async def upload_files(
    type_: DatasetType = Query(
        ...,
        alias="type",
        title="Dataset type",
        description="Dataset type to be uploaded",
    ),
    files: List[UploadFile] = File(...),
    storages: dict = Depends(get_storage_clients),
):
    client = storages.get("client")
    local_storage = storages.get("local_storage")
    result = await GeoloaderService(
        client, local_storage
    ).upload(files, type_)
    return handle_result(result)

# @router.post(
#     "/toponomastica/indirizzi/",
#     response_model=FeatureIndirizzoCivico,
# )
# async def get_feature(
#     query: RicercaIndirizzoCivico = Body(..., embed=True),
#     client: GeoserverClient = Depends(GeoserverClient),
# ):
#     result = await ToponimyService(client).get_feature(query)
#     return handle_result(result)


@router.get("/toponomastica/status/")
async def healthcheck():
    return {"status": "healthy"}
