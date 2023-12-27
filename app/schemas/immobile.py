from datetime import date
from pydantic import BaseModel
from typing import Optional, List

class ImmobileItemResult(BaseModel):
    tipoimmobile: str = None
    foglio: str = None
    particella: str = None
    subalterno: str = None
    immobile: str = None
    data_fine: date = None


class ImmobileItem(ImmobileItemResult):

    class Config:
        orm_mode = True

class Titolarita(BaseModel):

    diritto: Optional[str] = None
    quota: Optional[str] = None

class ImmobileFabbricatoDettagli(BaseModel):

    immobile: Optional[int] = None
    data_aggiornamento: Optional[date] = None
    sezione: Optional[str] = None
    foglio: Optional[str] = None
    particella: Optional[str] = None
    subalterno: Optional[str] = None
    zona_censuaria: Optional[str] = None
    micro_zona: Optional[str] = None
    categoria: Optional[str] = None
    classe: Optional[str] = None
    descrizione_categoria: Optional[str] = None
    rendita: Optional[str] = None
    consistenza: Optional[str] = None
    superficie: Optional[str] = None
    annotazioni: Optional[str] = None
    dati_derivanti_da: Optional[str] = None
    indirizzo: Optional[str] = None
    intestazione: Optional[str] = None
    partita: Optional[str] = None

    titolarita: List[Titolarita] = []


class ImmobileTerrenoDettagli(BaseModel):
    immobile: Optional[int] = None
    data_aggiornamento: Optional[date] = None
    sezione: Optional[str] = None
    foglio: Optional[int] = None
    particella: Optional[str] = None
    subalterno: Optional[str] = None
    porzione: Optional[str] = None
    qualita: Optional[str] = None
    classe: Optional[str] = None
    reddito_dominicale_lire: Optional[str] = None
    reddito_dominicale_euro: Optional[str] = None
    reddito_agrario_euro: Optional[str] = None
    superfice_ha: Optional[int] = None
    superfice_are: Optional[int] = None
    superfice_ca: Optional[int] = None
    annotazioni: Optional[str] = None
    dati_derivanti_da: Optional[str] = None
    dati_indirizzo: Optional[str] = None
    intestazione: Optional[str] = None
    partita: Optional[str] = None

    titolarita: List[Titolarita] = []