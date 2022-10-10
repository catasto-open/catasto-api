from datetime import date
from pydantic import BaseModel


class PersonaFisicaItemResult(BaseModel):
    soggetto: str = ...
    tiposog: str = None
    nome: str = None
    cognome: str = None
    codfiscale: str = None
    datadinascita: date = None
    comune: str = None
    genere: str = None
    provincia: str = None


class PersonaFisicaItem(PersonaFisicaItemResult):

    class Config:
        orm_mode = True

