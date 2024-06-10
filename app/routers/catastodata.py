from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request, Security
from fastapi.responses import JSONResponse

from app.config.database import get_db
from app.config.auth import OpenAMIDToken, auth, get_api_key
from app.config.logging import create_logger
from app.config.config import configuration as cfg
from app.services.visuraservice import VisuraService
from app.utils.service_result import handle_result, ServiceResult
from app.utils.request import get_real_client
from app.utils.app_exceptions import AppException


logger = create_logger(name="app.config.client")

router = APIRouter(
    prefix="/catasto/dati",
    tags=["dati"],
    responses={404: {"description": "Not found"}},
)

@router.get("/visura", response_class=JSONResponse)
async def visura(
    utente: OpenAMIDToken = Security(auth.authorized),
    comune: Optional[str] = Query(
        "H501",
        title="Comune",
        description="Ricerca per codice immobile",
        regex="^[a-zA-Z0-9_]*$",
        max_length=4
    ),
    tipoimmobile: str = Query(
        None,
        title="Tipo Immobile",
        description="Terreno (T) o Fabbricato (F)",
        regex="^[a-zA-Z]*$",
        max_length=1
    ),
    codiceimmobile: int = Query(
        None,
        title="Codice Immobile",
        description="Ricerca per codice immobile"
    ),
    flagricercastorica: bool = Query(
        False,
        title="Flag ricerca storica",
        description="Ricerca nei dati storici"
    ),
    db: get_db = Depends()):

        if codiceimmobile:
            result = VisuraService(db).get_visura_by_codiceimmobile(flagricercastorica, comune, codiceimmobile, tipoimmobile)
        else:
            raise HTTPException(
                    status_code=422, 
                    detail="Dati input non validi")

        if result:
            return result
        else:
            raise HTTPException(
                status_code=404, 
                detail="Nessun risultato trovato")

@router.get("/visuracittadino", response_class=JSONResponse)
async def visuracittadino(
    utente: OpenAMIDToken = Security(auth.citizen_authorized),
    comune: Optional[str] = Query(
        "H501",
        title="Comune",
        description="Ricerca per codice immobile",
        regex="^[a-zA-Z0-9_]*$",
        max_length=4
    ),
    offset: Optional[int] = Query(
        1,
        title="Offset",
        gt=0,
        description="Primo valore da restituire"
    ),
    limit: Optional[int] = Query(
        cfg.LIMIT_RESULT,
        gt=0,
        title="Limite",
        description="Numero massimo valori da restituire (raccomandato 10)"
    ),
    db: get_db = Depends()):

        codicefiscale = utente.codice_fiscale

        if codicefiscale and len(codicefiscale.strip()) == 16:
            logger.debug(f"Requested codice fiscale {codicefiscale}")
            result = VisuraService(db).get_visure_by_codicefiscale(comune, codicefiscale, offset-1, limit)
        else:
            raise HTTPException(
                    status_code=422, 
                    detail="Dati utenza non validi")

        if result:
            return result
        else:
            raise HTTPException(
                status_code=404, 
                detail="Nessun risultato trovato")

@router.get("/visurapersonagiuridica", response_class=JSONResponse)
async def visuragiuridica(
    request: Request,
    api_key: str = Security(get_api_key),
    comune: Optional[str] = Query(
        "H501",
        title="Comune",
        description="Ricerca per codice immobile",
        regex="^[a-zA-Z0-9_]*$",
        max_length=4
    ),
    partita_iva: Optional[str] = Query(
        None,
        title="Partita IVA",
        description="La partita iva della persona giuridica di interesse",
        regex="^[a-zA-Z0-9_]*$",
        max_length=11
    ),
    offset: Optional[int] = Query(
        1,
        title="Offset",
        gt=0,
        description="Primo valore da restituire"
    ),
    limit: Optional[int] = Query(
        cfg.LIMIT_RESULT,
        gt=0,
        title="Limite",
        description="Numero massimo valori da restituire (raccomandato 10)"
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

            if partita_iva and len(partita_iva.strip()) == 11:
                logger.debug(f"Requested partita iva {partita_iva}")
                result = VisuraService(db).get_visure_by_partitaiva(comune, partita_iva, offset-1, limit)
            else:
                raise HTTPException(
                        status_code=422, 
                        detail="Partita IVA non valida")

            if not result:
                logger.debug(f"Nothing found")
                result = ServiceResult(
                        AppException.ImmobileNotFound({})
                )
            else:
                result = ServiceResult(result)

        response = handle_result(result)
        return response
