from app.services.visuraservice import VisuraService
from app.services.personafisicaservice import PersonaFisicaService
from app.services.personagiuridicaservice import PersonaGiuridicaService
from app.services.immobileservice import ImmobileService
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Security
from app.services.pdfformatter import generate_print_pdf
from app.services.csvformatter import generate_print_csv
from app.config.database import get_db
from app.config.auth import OpenAMIDToken, auth
from fastapi.responses import FileResponse, JSONResponse
from datetime import date
from enum import Enum
import re
from app.config.logging import create_logger


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
    db: get_db = Depends()):

        codicefiscale = utente.sub

        if codicefiscale and len(codicefiscale.strip()) == 16:
            result = VisuraService(db).get_visure_by_codicefiscale(comune, codicefiscale)
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
