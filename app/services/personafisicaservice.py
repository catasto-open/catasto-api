from datetime import date

from app.services.main import AppService, AppQuery
from app.models.personafisica import PersonaFisicaView
from app.schemas.personafisica import (
    PersonaFisicaItem
)
from app.models.general import GeneralView
from app.schemas.general import (
    VersionItem
)

class PersonaFisicaService(AppService):

    def get_persona_by_codice_fiscale(self, comune: str, cf: str) -> PersonaFisicaItem:
        return PersonaFisicaQuery(self.db).select_codicefiscale(comune, cf)

    def get_persona_by_codice_soggetto(self, comune: str, cs: int) -> PersonaFisicaItem:
        return PersonaFisicaQuery(self.db).select_codicesoggetto(comune, cs)

    def get_persona_by_dati_anagrafici(self, comune: str, nome: str, cognome: str, codicecomunedinascita: str, datadinascita: date) -> PersonaFisicaItem:
        return PersonaFisicaQuery(self.db).select_datianagrafici(comune, nome, cognome, codicecomunedinascita, datadinascita)

    def get_version(self) -> VersionItem:
        return PersonaFisicaQuery(self.db).select_versione()


class PersonaFisicaQuery(AppQuery):

    def select_codicefiscale(self, comune: str, cf: str) -> PersonaFisicaItem:
        personefisiche_results = self.db.execute(
            PersonaFisicaView.select_codicefiscale(comune=comune, cf=cf)
        ).all()
        if personefisiche_results:
            personefisiche_item = []
            for item in personefisiche_results:
                personefisiche_item.append(PersonaFisicaItem(**item, by_alias=True).dict())
            return personefisiche_item
        return None


    def select_codicesoggetto(self, comune: str, cs: int) -> PersonaFisicaItem:
        personefisiche_results = self.db.execute(
            PersonaFisicaView.select_codicesoggetto(comune=comune, cs=cs)
        ).all()
        if personefisiche_results:
            personefisiche_item = []
            for item in personefisiche_results:
                personefisiche_item.append(PersonaFisicaItem(**item, by_alias=True).dict())
            return personefisiche_item
        return None

    def select_datianagrafici(self, comune: str,  nome: str, cognome: str, codicecomunedinascita: str, datadinascita: date) -> PersonaFisicaItem:
        personefisiche_results = self.db.execute(
            PersonaFisicaView.select_datianagrafici(comune=comune, nome=nome, cognome=cognome, codicecomunedinascita=codicecomunedinascita, datadinascita=datadinascita)
        ).all()
        if personefisiche_results:
            personefisiche_item = []
            for item in personefisiche_results:
                personefisiche_item.append(PersonaFisicaItem(**item, by_alias=True).dict())
            return personefisiche_item
        return None

    def select_versione(self) -> VersionItem:
        version_results = self.db.execute(
            GeneralView.select_versione()
        ).all()
        if version_results:
            for item in version_results:
                return VersionItem(**item, by_alias=True).dict()
        return None