from datetime import date

from app.services.main import AppService, AppQuery
from app.models.personagiuridica import PersonaGiuridicaView
from app.schemas.personagiuridica import (
    PersonaGiuridicaItem
)

class PersonaGiuridicaService(AppService):

    def get_persona_by_partitaiva(self, comune: str, partitaiva: str) -> PersonaGiuridicaItem:
        return PersonaGiuridicaQuery(self.db).select_partitaiva(comune, partitaiva)

    def get_persona_by_codice_soggetto(self, comune: str, cs: int) -> PersonaGiuridicaItem:
        return PersonaGiuridicaQuery(self.db).select_codicesoggetto(comune, cs)

    def get_persona_by_ragione_sociale(self, comune: str, denominazione: str) -> PersonaGiuridicaItem:
        return PersonaGiuridicaQuery(self.db).select_denominazione(comune, denominazione)


class PersonaGiuridicaQuery(AppQuery):

    def select_partitaiva(self, comune: str, partitaiva: str) -> PersonaGiuridicaItem:
        personegiuridiche_results = self.db.execute(
            PersonaGiuridicaView.select_partitaiva(comune=comune, partitaiva=partitaiva)
        ).all()
        if personegiuridiche_results:
            personegiuridiche_item = []
            for item in personegiuridiche_results:
                personegiuridiche_item.append(PersonaGiuridicaItem(**item, by_alias=True).dict())
            return personegiuridiche_item
        return None


    def select_codicesoggetto(self, comune: str, cs: int) -> PersonaGiuridicaItem:
        personegiuridiche_results = self.db.execute(
            PersonaGiuridicaView.select_codicesoggetto(comune=comune, cs=cs)
        ).all()
        if personegiuridiche_results:
            personegiuridiche_item = []
            for item in personegiuridiche_results:
                personegiuridiche_item.append(PersonaGiuridicaItem(**item, by_alias=True).dict())
            return personegiuridiche_item
        return None

    def select_denominazione(self, comune: str, denominazione: str) -> PersonaGiuridicaItem:
        personegiuridiche_results = self.db.execute(
            PersonaGiuridicaView.select_denominazione(comune=comune, denominazione=denominazione)
        ).all()
        if personegiuridiche_results:
            personegiuridiche_item = []
            for item in personegiuridiche_results:
                personegiuridiche_item.append(PersonaGiuridicaItem(**item, by_alias=True).dict())
            return personegiuridiche_item
        return None