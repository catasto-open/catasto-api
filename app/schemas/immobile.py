from datetime import date
from pydantic import BaseModel


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

