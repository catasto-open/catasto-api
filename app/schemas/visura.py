from datetime import date
from typing import List
from app.schemas.personafisica import PersonaFisicaItemResult
from app.schemas.personagiuridica import PersonaGiuridicaItemResult
from pydantic import BaseModel


class ErediItemResult(BaseModel):
    foglio: str = None
    particella: str = None
    subalterno: str = None

class DatiCatastaliFabbricatoItemResult(BaseModel):
    data_decorrenza: date = None
    progressivo: int = None
    sezione: str = None
    foglio: str = None
    particella: str = None
    subalterno: str = None
    zona_censuaria: str = None
    microzona: str = None
    categoria: str = None
    classe: str = None
    consistenza: str = None
    superficie: str = None 
    rendita: str = None
    partita: str = None
    gen_tipo_nota: str = None
    gen_descr: str = None
    gen_causa: str = None
    gen_data_reg: str = None
    gen_progressivo: str = None
    gen_data_eff: str = None
    derivanti_da: str = None
    indirizzo: str = None
    annotazioni: str = None
    mutazioneiniziale: int = None

    eredi: List[ErediItemResult] = []


class DatiCatastaliTerrenoItemResult(BaseModel):
    data_decorrenza: date = None
    progressivo: int = None
    sezione: str = None
    foglio: str = None
    particella: str = None
    subalterno: str = None
    qualita: str = None
    classe: str = None
    superfice_ha: str = None
    superfice_are: str = None
    superfice_ca: str = None
    reddito_dominicale: str = None
    reddito_agrario: str = None
    partita: str = None
    gen_tipo_nota: str = None
    gen_descr: str = None
    gen_causa: str = None
    gen_data_reg: str = None
    gen_progressivo: str = None
    gen_data_eff: str = None
    derivanti_da: str = None
    annotazioni: str = None
    mutazioneiniziale: int = None

    eredi: List[ErediItemResult] = []


class TitolareItemResult(BaseModel):
    data_decorrenza: str = None
    data_fine: str = None
    sezione: str = None
    immobile: str = None
    tipo_immobile: str = None
    nominativo: str = None
    codice_fiscale: str = None
    titolo: str = None
    quota: str = None
    gen_tipo_nota: str = None
    gen_descr: str = None
    gen_causa: str = None
    gen_data_reg: str = None
    gen_progressivo: str = None
    gen_data_eff: str = None
    derivanti_da: str = None

class VisuraItemResult(BaseModel):
    comune: str = None
    tipoimmobile: str = None
    foglio: str = None
    particella: str = None
    subalterno: str = None
    codice_immobile: str = None
    data_fine: date = None

    titolari_attuali: List[TitolareItemResult] = []
    dati_catastali_fabbricato_attuali: List[DatiCatastaliFabbricatoItemResult] = []
    dati_catastali_terreno_attuali: List[DatiCatastaliTerrenoItemResult] = []


class VisuraItem(VisuraItemResult):

    class Config:
        orm_mode = True



