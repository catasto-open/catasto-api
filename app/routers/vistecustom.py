from app.services.immobileservice import ImmobileService
from fastapi import APIRouter, Depends, Query, HTTPException, Security, status
from app.config.database import get_db
from fastapi.responses import JSONResponse
from app.config.logging import create_logger
from fastapi.security import APIKeyHeader
from pydantic import conint
from app.config.config import configuration as cfg

logger = create_logger(name="app.config.client")

api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in cfg.CUSTOM_APIKEYS:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )

router = APIRouter(
    prefix="/custom",
    tags=["dati"],
    responses={404: {"description": "Not found"}},
)

@router.get("/reftree/immobile", response_class=JSONResponse)
async def dati_immobile(
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

        result = ImmobileService(db).get_immobili_comune_by_codiceimmobile(codiceimmobile, tipoimmobile)

        if result:
            return result
        else:
            raise HTTPException(
                status_code=404, 
                detail="Nessun risultato trovato")