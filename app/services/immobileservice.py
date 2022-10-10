from datetime import date

from app.services.main import AppService, AppQuery
from app.models.immobile import ImmobileView
from app.schemas.immobile import (
    ImmobileItem
)


class ImmobileService(AppService):

    def get_immobili_by_codiceimmobile(self, flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> ImmobileItem:
        return ImmobileQuery(self.db).select_codiceimmobile(flagstorico, comune, codiceimmobile, tipoimmobile)

    def get_immobili_by_codice_soggetto(self, flagstorico: bool, comune: str, cs: int, tipoimmobile: str) -> ImmobileItem:
        return ImmobileQuery(self.db).select_codicesoggetto(flagstorico, comune, cs, tipoimmobile)

    def get_immobili_by_dati_catastali(self, flagstorico: bool, comune: str, sezione: str, foglio: str, particella: str, tipoimmobile: str) -> ImmobileItem:
        return ImmobileQuery(self.db).select_daticatastali(flagstorico, comune, sezione, foglio, particella, tipoimmobile)

    def get_immobili_by_indirizzo(self, flagstorico: bool, comune: str, toponimo: int, indirizzo: str, numerocivico: str, tipoimmobile: str) -> ImmobileItem:
        return ImmobileQuery(self.db).select_indirizzo(flagstorico, comune, toponimo, indirizzo, numerocivico, tipoimmobile)


class ImmobileQuery(AppQuery):

    def select_codiceimmobile(self, flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> ImmobileItem:
        immobili_results = self.db.execute(
            ImmobileView.select_codiceimmobile(flagstorico=flagstorico, comune = comune, codiceimmobile=codiceimmobile, tipoimmobile=tipoimmobile)
        ).all()
        if immobili_results:
            immobili_item = []
            for item in immobili_results:
                immobili_item.append(ImmobileItem(**item, by_alias=True).dict())
            return immobili_item
        return None


    def select_codicesoggetto(self, flagstorico: bool, comune: str, cs: int, tipoimmobile: str) -> ImmobileItem:
        immobili_results = self.db.execute(
            ImmobileView.select_codicesoggetto(flagstorico=flagstorico, comune=comune, cs=cs, tipoimmobile=tipoimmobile)
        ).all()
        if immobili_results:
            immobili_item = []
            for item in immobili_results:
                immobili_item.append(ImmobileItem(**item, by_alias=True).dict())
            return immobili_item
        return None

    def select_daticatastali(self, flagstorico: bool, comune: str, sezione: str, foglio: str, particella: str, tipoimmobile: str) -> ImmobileItem:
        immobili_results = self.db.execute(
            ImmobileView.select_daticatastali(flagstorico=flagstorico, comune=comune, sezione=sezione, foglio=foglio, particella=particella, tipoimmobile=tipoimmobile)
        ).all()
        if immobili_results:
            immobili_item = []
            for item in immobili_results:
                immobili_item.append(ImmobileItem(**item, by_alias=True).dict())
            return immobili_item
        return None

    def select_indirizzo(self, flagstorico: bool, comune: str, toponimo: int, indirizzo: str, numerocivico: str, tipoimmobile: str) -> ImmobileItem:
        immobili_results = self.db.execute(
            ImmobileView.select_indirizzo(flagstorico=flagstorico, comune=comune, toponimo=toponimo, indirizzo=indirizzo, numerocivico=numerocivico, tipoimmobile=tipoimmobile)
        ).all()
        if immobili_results:
            immobili_item = []
            for item in immobili_results:
                immobili_item.append(ImmobileItem(**item, by_alias=True).dict())
            return immobili_item
        return None