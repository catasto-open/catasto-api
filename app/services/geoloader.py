import aiofiles
import fiona
import boto3
import geopandas as gpd
from fiona.session import AWSSession
from typing import List, Union
from uuid import uuid4
from fastapi import UploadFile
from pydantic import ValidationError
from app.config.config import configuration as cfg
from app.config.logging import create_logger
from app.schemas.geoloader import (
    DatasetType,
    ShapefileDataset,
    GeopackageDataset,
    UploadSuccessResponse,
)
from app.services.main import AppService, AppValidation
from app.utils.app_exceptions import AppException
from app.utils.service_result import ServiceResult


logger = create_logger(name="app.services.geoloader")


class GeoloaderService(AppService):
    
    async def upload(
        self,
        files: List[UploadFile],
        type_: DatasetType,
    ) -> ServiceResult:
        dataset_id = uuid4().__str__()
        dataset = await GeoValidator(
            self.local_client
        ).get_validated_files(files, type_, dataset_id)
        filenames = [item.filename for item in files]
        if not dataset:
            if type_ == DatasetType.SHAPEFILE:
                return ServiceResult(
                    AppException.ShapefileNotValid(
                        {"Shapefile files": filenames},
                    ),
                )
            elif type_ == DatasetType.GEOPACKAGE:
                return ServiceResult(
                    AppException.GeopackageNotValid(
                        {"Geopackage files": filenames},
                    ),
                )
        for _file in files:
            in_file_path = self.local_client.base_path / dataset_id / _file.filename #output file path
            async with aiofiles.open(in_file_path, 'rb') as infile:
                await self.client.fput_object(
                    "test-upload", f"{dataset.id}/{_file.filename}", in_file_path,
                )
        resource_url = f"http://{cfg.MINIO_BASEURL}/test-upload/{dataset.id}/{dataset.files[0].stem}.shp"

        boto3_session = boto3.Session(
            aws_access_key_id="e5NDexDVLlhTIvCd",
            aws_secret_access_key="xjnSuoApCzXQP4XLVFecULO4KoqOAduv",
            aws_session_token=None,
            region_name="geofeeder",
            botocore_session=None,
            profile_name=None
        )
        with fiona.Env(CPL_DEBUG=True, session=AWSSession(boto3_session)):
            # https://github.com/Toblerity/Fiona/issues/1055
            if type_ == DatasetType.SHAPEFILE:
                fds = fiona.open(resource_url)
                # import s3fs
                # fs = s3fs.S3FileSystem()
                # with fs.open(f"s3://nginx:9000/test-upload/{result.id}/{result.files[0].stem}.shp") as f:
                #     gdf = gpd.read_file(f)
                gdf = gpd.GeoDataFrame(fds)
        # f_run = run_flow(
        #     'file_reader',
        #     by_id=False,
        #     flow_run_input=FlowRunInput(
        #         parameters={"path_to_file": _file.filename}
        #     )
        # )
        # r = f_run.id
        response = UploadSuccessResponse(
            dataset=dataset.id,
            filenames=filenames,
            url=resource_url,
            metadata=fds.meta
        )
        return ServiceResult(response)


class GeoValidator(AppValidation):
    async def get_validated_files(
        self,
        files,
        dataset_type,
        dataset_id,
    ) -> Union[ShapefileDataset, None]:
        filepaths = []
        for _file in files:
            dest_path = self.client.base_path / dataset_id
            if not dest_path.exists():
                dest_path.mkdir()
            out_file_path = dest_path / _file.filename #output file path
            filepaths.append(out_file_path)
            async with aiofiles.open(out_file_path, 'wb') as outfile:
                while content := await _file.read(1024):  # async read chunk
                    await outfile.write(content)  # async write chunk
        try:
            if dataset_type == DatasetType.SHAPEFILE:
                dataset = ShapefileDataset(
                    name=files[0].filename,
                    id=dataset_id,
                    type=dataset_type,
                    files=filepaths
                )
                # for tmpfile in result.files:
                #     if tmpfile.suffix == ".shp":
                #         gdf = GeoDataFrame.from_file(tmpfile)
                #         dataset = ShapefileDataframe(
                #             geodataframe=gdf,
                #             id=result.id
                #         )
            elif dataset_type == DatasetType.GEOPACKAGE:
                dataset = GeopackageDataset(
                    name=files[0].filename,
                    id=dataset_id,
                    type=dataset_type,
                    files=filepaths
                )
            return dataset
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return None