from datetime import date
from typing import List
from app.services.main import AppService, AppQuery
from app.models.visura import VisuraView
from app.schemas.visura import (
    TitolareItemResult, VisuraItem, DatiCatastaliFabbricatoItemResult, DatiCatastaliTerrenoItemResult
)
from app.utils.service_result import ServiceResult


class VisuraService(AppService):

    def get_visura_by_codiceimmobile(self, flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> VisuraItem:
        return VisuraQuery(self.db).select_codiceimmobile(flagstorico, comune, codiceimmobile, tipoimmobile)


class VisuraQuery(AppQuery):

    def select_dettagli_fabbricato(self, flagstorico: bool, comune: str, foglio:str, particella: str, codiceimmobile: int) -> List[DatiCatastaliFabbricatoItemResult]:
        immobili_results = self.db.execute(
            VisuraView.select_dettagli_fabbricato(flagstorico=flagstorico, comune=comune, foglio=foglio, particella=particella, codiceimmobile=codiceimmobile)
        ).all()
        if immobili_results:
            immobili_item = []
            for item in immobili_results:
                immobili_item.append(DatiCatastaliFabbricatoItemResult(**item, by_alias=True).dict())
            return immobili_item
        return None

    def select_dettagli_terreno(self, flagstorico: bool, comune: str, foglio:str, particella: str, codiceimmobile: int) -> List[DatiCatastaliFabbricatoItemResult]:
        immobili_results = self.db.execute(
            VisuraView.select_dettagli_terreno(flagstorico=flagstorico, comune=comune, foglio=foglio, particella=particella, codiceimmobile=codiceimmobile)
        ).all()
        if immobili_results:
            immobili_item = []
            for item in immobili_results:
                immobili_item.append(DatiCatastaliTerrenoItemResult(**item, by_alias=True).dict())
            return immobili_item
        return None

    def select_titolari(self, flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> List[DatiCatastaliFabbricatoItemResult]:
        immobili_results = self.db.execute(
            VisuraView.select_titolari(flagstorico=flagstorico, comune=comune, codiceimmobile=codiceimmobile, tipoimmobile=tipoimmobile)
        ).all()
        if immobili_results:
            immobili_item = []
            for item in immobili_results:
                immobili_item.append(TitolareItemResult(**item, by_alias=True).dict())
            return immobili_item
        return None

    def select_codiceimmobile(self, flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> VisuraItem:
        visura_result = self.db.execute(
            VisuraView.select_codiceimmobile(flagstorico=False, comune=comune, codiceimmobile=codiceimmobile, tipoimmobile=tipoimmobile)
        ).first()
        if visura_result:
            visura_item = VisuraItem(**visura_result, by_alias=True).dict()
            visura_item['dati_catastali_fabbricato_attuali'] = self.select_dettagli_fabbricato(False, visura_item['comune'], visura_item['foglio'], visura_item['particella'], codiceimmobile)
            visura_item['dati_catastali_terreno_attuali'] = self.select_dettagli_terreno(False, visura_item['comune'], visura_item['foglio'], visura_item['particella'], codiceimmobile)
            visura_item['titolari_attuali'] = self.select_titolari(False, visura_item['comune'], codiceimmobile, tipoimmobile)
            if(flagstorico):
                visura_item['dati_catastali_fabbricato_storico'] = self.select_dettagli_fabbricato(True, visura_item['comune'], visura_item['foglio'], visura_item['particella'], codiceimmobile)
                visura_item['dati_catastali_terreno_storico'] = self.select_dettagli_terreno(True, visura_item['comune'], visura_item['foglio'], visura_item['particella'], codiceimmobile)
                visura_item['titolari_storico'] = self.select_titolari(True, visura_item['comune'], codiceimmobile, tipoimmobile)
            else:
                visura_item['dati_catastali_fabbricato_storico'] = None
                visura_item['dati_catastali_terreno_storico'] = None
                visura_item['titolari_storico'] = None

            return visura_item
        else:
            return None


