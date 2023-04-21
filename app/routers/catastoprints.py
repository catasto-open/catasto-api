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
    prefix="/catasto",
    tags=["georoma"],
    responses={404: {"description": "Not found"}},
)


@router.get("/status/")
async def healthcheck():
    return {"status": "healthy"}

@router.get("/auth/")
async def protectedURL(user: OpenAMIDToken = Security(auth.authorized)):
    logger.debug(user.tipo_utente)
    return {"status": "Logged in"}

@router.get("/stampa/visura", response_class=FileResponse)
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

        username = utente.sub

        if codiceimmobile:
            result = VisuraService(db).get_visura_by_codiceimmobile(flagricercastorica, comune, codiceimmobile, tipoimmobile)
        else:
            raise HTTPException(
                    status_code=422, 
                    detail="Dati input non validi")

        data_aggiornamento= PersonaFisicaService(db).get_version()['data_aggiornamento']

        if result:
            try:
                return generate_print_pdf("Visura", result, username, data_aggiornamento)
            except BaseException:
                raise HTTPException(
                    status_code=500, 
                    detail="Template non trovato")
        else:
            raise HTTPException(
                status_code=404, 
                detail="Nessun risultato trovato")

@router.get("/stampa/ricerca/immobili", response_class=FileResponse)
async def immobili(
    utente: OpenAMIDToken = Security(auth.authorized),
    codicesoggetto: Optional[str] = Query(
        None,
        title="Codice Soggetto",
        description="Ricerca per codice soggetto"
    ),
    codiceimmobile: Optional[int] = Query(
        None,
        title="Codice Immobile",
        description="Ricerca per codice immobile"
    ),
    comune: Optional[str] = Query(
        "H501",
        title="Comune",
        description="Ricerca per indirizzo e dati catastali",
        regex="^[a-zA-Z0-9_]*$",
        max_length=4
    ),
    toponimo: Optional[int] = Query(
        None,
        title="Toponimo",
        description="Ricerca per indirizzo"
    ),
    indirizzo: Optional[str] = Query(
        None,
        title="Indirizzo",
        description="Ricerca per indirizzo",
        regex="^[a-zA-Z0-9_]*$",
        max_length=64
    ),
    numerocivico: Optional[str] = Query(
        None,
        title="Numero Civico",
        description="Ricerca per indirizzo",
        regex="^[a-zA-Z0-9_]*$",
        max_length=16
    ),
    tipoimmobile: Optional[str] = Query(
        None,
        title="Tipo Immobile",
        description="Terreno (T) o Fabbricato (F) (F)",
        regex="^[a-zA-Z]*$",
        max_length=1
    ),
    sezione: Optional[str] = Query(
        None,
        title="Sezione",
        description="Ricerca per dati catastali",
        regex="^[a-zA-Z0-9_]*$",
        max_length=64
    ),
    foglio: Optional[str] = Query(
        None,
        title="Foglio",
        description="Ricerca per dati catastali",
        regex="^[a-zA-Z0-9_]*$",
        max_length=64
    ),
    particella: Optional[str] = Query(
        None,
        title="Particella",
        description="Ricerca per dati catastali",
        regex="^[a-zA-Z0-9_]*$",
        max_length=64
    ),
    flagricercastorica: bool = Query(
        False,
        title="Flag ricerca storica",
        description="Ricerca nei dati storici"
    ),
    format: Optional[str] = Query(
        "pdf",
        title="Formato export",
        description="Il formato del file output, indicare pdf o csv",
        max_length=3
    ),
    db: get_db = Depends()):

    username = utente.sub

    if codiceimmobile:
        result = ImmobileService(db).get_immobili_by_codiceimmobile(flagricercastorica, comune, codiceimmobile, tipoimmobile)
    elif codicesoggetto:
        try:
            cs = int(re.findall(r'[0-9]+', codicesoggetto)[0])
        except:
            raise HTTPException(
                status_code=422, 
                detail="Codice soggetto must be a number")
        result = ImmobileService(db).get_immobili_by_codice_soggetto(flagricercastorica, comune, cs, tipoimmobile)
    elif foglio and comune and particella:
        result = ImmobileService(db).get_immobili_by_dati_catastali(flagricercastorica, comune, sezione, foglio, particella, tipoimmobile)
    elif comune and toponimo and indirizzo and numerocivico:
        result = ImmobileService(db).get_immobili_by_indirizzo(flagricercastorica, comune, toponimo, indirizzo, numerocivico, tipoimmobile)
    else:
        raise HTTPException(
                status_code=422, 
                detail="Dati input non validi")

    data_aggiornamento= PersonaFisicaService(db).get_version()['data_aggiornamento']

    if result:
        if(format=='pdf'):
            try:
                return generate_print_pdf("Immobili", result, username, data_aggiornamento)
            except BaseException:
                raise HTTPException(
                    status_code=500, 
                    detail="Template non trovato")
        else:
            try:
                return generate_print_csv("Immobili", result, username)
            except BaseException:
                raise HTTPException(
                    status_code=500, 
                    detail="Errore generazione CSV")
    else:
        raise HTTPException(
            status_code=404, 
            detail="Nessun risultato trovato")


@router.get("/stampa/ricerca/persone_fisiche", response_class=FileResponse)
async def persone_fisiche(
    utente: OpenAMIDToken = Security(auth.authorized),
    comune: Optional[str] = Query(
        "H501",
        title="Comune",
        description="Ricerca per indirizzo e dati catastali",
        regex="^[a-zA-Z0-9_]*$",
        max_length=4
    ),
    codicesoggetto: Optional[int] = Query(
        None,
        title="Codice Soggetto",
        description="Ricerca per codice soggetto"
    ),
    codicefiscale: Optional[str] = Query(
        None,
        title="Codice Fiscale",
        description="Ricerca per codice fiscale",
        regex="^[a-zA-Z0-9_]*$",
        min_length=16, 
        max_length=16
    ),
    nome: Optional[str] = Query(
        None,
        title="Nome",
        description="Ricerca per dati anagrafici",
        regex="^[a-zA-Z0-9_\x20]*$",
        max_length=64
    ),
    cognome: Optional[str] = Query(
        None,
        title="Cognome",
        description="Ricerca per dati anagrafici",
        regex="^[a-zA-Z0-9_\x20]*$",
        max_length=64
    ),
    datadinascita: Optional[date] = Query(
        None,
        title="Data di Nascita",
        description="Ricerca per dati anagrafici in formato ISO YYYY-MM-DD"
    ),
    comunenascita: Optional[str] = Query(
        None,
        title="Comune di Nascita",
        description="Ricerca per dati anagrafici",
        regex="^[a-zA-Z0-9_]*$",
        max_length=4
    ),
    format: Optional[str] = Query(
        "pdf",
        title="Formato export",
        description="Il formato del file output, indicare pdf o csv",
        max_length=3
    ),
    db: get_db = Depends()):

    username = utente.sub

    if codicesoggetto:
        result = PersonaFisicaService(db).get_persona_by_codice_soggetto(comune, codicesoggetto)
    elif codicefiscale:
        result = PersonaFisicaService(db).get_persona_by_codice_fiscale(comune, codicefiscale)
    elif cognome and nome:
        result = PersonaFisicaService(db).get_persona_by_dati_anagrafici(comune, nome, cognome, comunenascita, datadinascita)
    else:
        raise HTTPException(
                status_code=422, 
                detail="Dati input non validi")

    data_aggiornamento= PersonaFisicaService(db).get_version()['data_aggiornamento']

    if result:
        if(format=='pdf'):
            try:
                return generate_print_pdf("Persone Fisiche", result, username, data_aggiornamento)
            except BaseException:
                raise HTTPException(
                    status_code=500, 
                    detail="Template non trovato")
        else:
            try:
                return generate_print_csv("Persone Fisiche", result, username)
            except BaseException:
                raise HTTPException(
                    status_code=500, 
                    detail="Errore generazione CSV")
    else:
        raise HTTPException(
            status_code=404, 
            detail="Nessun risultato trovato")


@router.get("/stampa/ricerca/persone_giuridiche", response_class=FileResponse)
async def persone_giuridiche(
    utente: OpenAMIDToken = Security(auth.authorized),
    comune: Optional[str] = Query(
        "H501",
        title="Comune",
        description="Ricerca per indirizzo e dati catastali",
        regex="^[a-zA-Z0-9_]*$",
        max_length=4
    ),
    codicesoggetto: Optional[int] = Query(
        None,
        title="Codice Soggetto",
        description="Ricerca per codice soggetto"
    ),
    partitaiva: Optional[str] = Query(
        None,
        title="Partita IVA",
        description="Ricerca per partita IVA",
        regex="^[a-zA-Z0-9_]*$",
        max_length=11
    ),
    denominazione: Optional[str] = Query(
        None,
        title="Nome",
        description="Ricerca per ragione sociale",
        regex="^[a-zA-Z0-9_\x20]*$",
        max_length=128
    ),
    format: Optional[str] = Query(
        "pdf",
        title="Formato export",
        description="Il formato del file output, indicare pdf o csv",
        max_length=3
    ),
    db: get_db = Depends()):

    username = utente.sub

    if codicesoggetto:
        result = PersonaGiuridicaService(db).get_persona_by_codice_soggetto(comune, codicesoggetto)
    elif partitaiva:
        result = PersonaGiuridicaService(db).get_persona_by_partitaiva(comune, partitaiva)
    elif denominazione:
        result = PersonaGiuridicaService(db).get_persona_by_ragione_sociale(comune, denominazione)
    else:
        raise HTTPException(
                status_code=422, 
                detail="Dati input non validi")

    data_aggiornamento= PersonaFisicaService(db).get_version()['data_aggiornamento']

    if result:
        if(format=='pdf'):
            try:
                return generate_print_pdf("Persone Giuridiche", result, username, data_aggiornamento)
            except BaseException:
                raise HTTPException(
                    status_code=500, 
                    detail="Template non trovato")
        else:
            try:
                return generate_print_csv("Persone Giuridiche", result, username)
            except BaseException:
                raise HTTPException(
                    status_code=500, 
                    detail="Errore generazione CSV")
    else:
        raise HTTPException(
            status_code=404, 
            detail="Nessun risultato trovato")

@router.get("/dati/visura", response_class=JSONResponse)
async def visuraJSON(
#    utente: OpenAMIDToken = Security(auth.authorized),
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
