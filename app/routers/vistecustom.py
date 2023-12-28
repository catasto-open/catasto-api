from app.config.auth import get_api_key
from app.config.config import configuration as cfg
from app.config.database import get_db
from app.config.logging import create_logger
from app.services.immobileservice import ImmobileService
from app.utils.app_exceptions import AppException
from app.utils.request import get_real_client
from app.utils.service_result import handle_result, ServiceResult
from fastapi import APIRouter, Depends, Query, Request, Security
from fastapi.responses import JSONResponse
from pydantic import conint


logger = create_logger(name="app.config.client")

router = APIRouter(
    prefix="/custom",
    tags=["dati"],
    responses={404: {"description": "Not found"}},
)

@router.get("/reftree/immobile", response_class=JSONResponse)
async def dati_immobile(
    request: Request,
    api_key: str = Security(get_api_key),
    tipoimmobile: str = Query(
        None,
        title="Tipo Immobile",
        description="Terreno (T) o Fabbricato (F)",
        regex='^(T|F)$',
        max_length=1
    ),
    codiceimmobile: conint(gt=0) = Query(
        None,
        title="Codice Immobile",
        description="Codice identificativo immobile"
    ),
    db: get_db = Depends()):

        logger.debug(f"API-KEY has been successfully evaluated")
        logger.debug(f"Server host: {request.base_url.netloc}")
        result = None
        if request.base_url.netloc not in cfg.ALLOWED_FQDN.split(','):
            result = ServiceResult(
                AppException.AuthAllowedFqdnError(
                    {"fqdn": request.base_url.netloc}
                )
            )
        logger.info(f"Source client host: {request.client.host}")
        if not result:
            source_ip = await get_real_client(request=request)
            # if source_ip not in cfg.SOURCE_IP_WHITELISTED.split(","):
            #     result = ServiceResult(
            #         AppException.AuthAllowedClientIpError(
            #             {"client": source_ip}
            #         )
            #     )
            # else:
            logger.info(f"Source client host: {source_ip} is allowed")

            result = ImmobileService(db).get_immobili_comune_by_codiceimmobile(codiceimmobile, tipoimmobile)

            if not result:
                logger.debug(f"Nothing found")
                result = ServiceResult(
                        AppException.ImmobileNotFound({})
                )
            else:
                result = ServiceResult(result)

        response = handle_result(result)
        return response
