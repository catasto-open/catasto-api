from datetime import date
from pydantic import BaseModel


class PersonaGiuridicaItemResult(BaseModel):
    soggetto: str = ...
    tiposog: str = None
    denominazione: str = None
    partitaiva: str = None
    comune: str = None
    provincia: str = None


class PersonaGiuridicaItem(PersonaGiuridicaItemResult):

    class Config:
        orm_mode = True

