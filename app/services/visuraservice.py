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
            progressivo = 0
            for item in immobili_results:
                progressivo = progressivo + 1
                item_dict = DatiCatastaliFabbricatoItemResult(**item, by_alias=True).dict()
                item_dict['derivanti_da'] = self.compile_dati_derivanti_da(item_dict['gen_tipo_nota'], item_dict['gen_descr'], item_dict['gen_causa'], item_dict['gen_data_reg'], item_dict['gen_progressivo'], item_dict['gen_data_eff'])
                item_dict['progressivo'] = progressivo
                immobili_item.append(item_dict)
            return immobili_item
        return None

    def select_dettagli_terreno(self, flagstorico: bool, comune: str, foglio:str, particella: str, codiceimmobile: int) -> List[DatiCatastaliFabbricatoItemResult]:
        immobili_results = self.db.execute(
            VisuraView.select_dettagli_terreno(flagstorico=flagstorico, comune=comune, foglio=foglio, particella=particella, codiceimmobile=codiceimmobile)
        ).all()
        if immobili_results:
            immobili_item = []
            progressivo = 0
            for item in immobili_results:
                progressivo = progressivo + 1
                item_dict = DatiCatastaliTerrenoItemResult(**item, by_alias=True).dict()
                item_dict['derivanti_da'] = self.compile_dati_derivanti_da(item_dict['gen_tipo_nota'], item_dict['gen_descr'], item_dict['gen_causa'], item_dict['gen_data_reg'], item_dict['gen_progressivo'], item_dict['gen_data_eff'])
                item_dict['progressivo'] = progressivo
                immobili_item.append(item_dict)
            return immobili_item
        return None

    def select_titolari(self, flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> List[DatiCatastaliFabbricatoItemResult]:
        titolari_results = self.db.execute(
            VisuraView.select_titolari(flagstorico=flagstorico, comune=comune, codiceimmobile=codiceimmobile, tipoimmobile=tipoimmobile)
        ).all()
        if titolari_results:
            titolare_items = {}
            current_date = None
            titolare_items[0] = []
            for item in titolari_results:
                item_dict = TitolareItemResult(**item, by_alias=True).dict()
                if item_dict['data_fine'] != current_date:
                    current_date = item_dict['data_fine']
                    titolare_items[current_date or 0] = []
                item_dict['derivanti_da'] = self.compile_dati_derivanti_da(item_dict['gen_tipo_nota'], item_dict['gen_descr'], item_dict['gen_causa'], item_dict['gen_data_reg'], item_dict['gen_progressivo'], item_dict['gen_data_eff'])
                titolare_items[current_date or 0].append(item_dict)
            return titolare_items
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

    def compile_dati_derivanti_da(self, gen_tipo_nota: str, gen_descr: str, gen_causa: str, gen_data_reg: str, gen_progressivo: str, gen_data_eff: str):
        derivanti_da = ''
        if gen_tipo_nota:
            derivanti_da = f"{gen_tipo_nota}, "

        if gen_causa:
            derivanti_da = f"{derivanti_da}{gen_causa}, " 

        if gen_descr:
            derivanti_da = f"{derivanti_da}{gen_descr}, " 

        if (gen_data_eff and gen_data_eff!='01/01/0001'):
            derivanti_da = f"{derivanti_da}del {gen_data_eff} " 

        if gen_progressivo:
            derivanti_da = f"{derivanti_da}numero {gen_progressivo} "

        if (gen_data_reg and gen_data_reg!='01/01/0001'):
            derivanti_da = f"{derivanti_da}in atti dal {gen_data_reg}"

        return derivanti_da
