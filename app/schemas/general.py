from datetime import date
from pydantic import BaseModel


class VersionItemResult(BaseModel):
    codice: str = None
    data_aggiornamento: date = None


class VersionItem(VersionItemResult):

    class Config:
        orm_mode = True

class FoglioParticella(BaseModel):
  foglio: str
  particella: str

class CustomQuery(BaseModel):
  immobili: list[FoglioParticella]

