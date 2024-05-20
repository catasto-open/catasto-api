from typing import List
from app.services.main import AppService, AppQuery
from app.models.visura import VisuraView
from app.services.personafisicaservice import PersonaFisicaService
from app.services.personagiuridicaservice import PersonaGiuridicaService
from app.services.immobileservice import ImmobileService
from app.schemas.visura import (
    TitolareItemResult, VisuraItem, DatiCatastaliFabbricatoItemResult, DatiCatastaliTerrenoItemResult, ErediItemResult, UtilitaItemResult
)
from app.utils.service_result import ServiceResult


class VisuraService(AppService):

    def get_visura_by_codiceimmobile(self, flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> VisuraItem:
        return VisuraQuery(self.db).select_codiceimmobile(flagstorico, comune, codiceimmobile, tipoimmobile)

    def get_visure_by_codicefiscale(self, comune: str, codicefiscale: str, offset: int, limit: int) -> VisuraItem:
        persona_result = PersonaFisicaService.get_persona_by_codice_fiscale(self, comune, codicefiscale)
        if persona_result:
            result = []
            for persona in persona_result:
                cs = persona['soggetto']
                immobili_results = ImmobileService.get_immobili_by_codice_soggetto(self, False, comune, cs, '')
                if immobili_results:
                    for immobile in immobili_results:
                        result.append(immobile['immobile'])
            visure = []
            result = list(set(result))
            result = sorted(result)
            length = len(result)
            if(offset > length):
                return None
            if(offset+limit > length):
                max_value = length
            else:
                max_value = offset+limit
            for x in range(offset,max_value):
                visure.append(VisuraQuery(self.db).select_codiceimmobile(False, comune, result[x], ''))

            pagina = {}
            pagina['total_count'] = length
            pagina['offset'] = offset + 1
            pagina['count'] = max_value - offset
            pagina['visure'] = visure
            return pagina
        return None

    def get_visure_by_partitaiva(self, comune: str, partitaiva: str, offset: int, limit: int) -> VisuraItem:
        persona_result = PersonaGiuridicaService.get_persona_by_partitaiva(self, comune, partitaiva)
        if persona_result and persona_result[0]:
            result = []
            for persona in persona_result:
                cs = persona['soggetto']
                immobili_results = ImmobileService.get_immobili_by_codice_soggetto(self, False, comune, cs, '')
                if immobili_results:
                    for immobile in immobili_results:
                        result.append(immobile['immobile'])
            visure = []
            result = list(set(result))
            result = sorted(result)
            length = len(result)
            if(offset > length):
                return None
            if(offset+limit > length):
                max_value = length
            else:
                max_value = offset+limit
            print(result)
            for x in range(offset,max_value):
                visure.append(VisuraQuery(self.db).select_codiceimmobile(False, comune, result[x], ''))

            pagina = {}
            pagina['total_count'] = length
            pagina['offset'] = offset + 1
            pagina['count'] = max_value - offset
            pagina['visure'] = visure
            return pagina
        return None


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
                if item_dict['partita'] == 'SOPPRESSA' and (not item_dict['gen_tipo_nota'] or item_dict['gen_tipo_nota'].upper() != 'IMPIANTO') :
                    item_dict['eredi'] = self.select_eredi_fabbricati(codiceimmobile, item_dict['mutazioneiniziale'])
                else:
                    item_dict['eredi'] = None
                item_dict['utilita'] = self.select_utilita(codiceimmobile, item_dict['progressivo'])
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
                if(not item_dict['gen_tipo_nota'] or item_dict['gen_tipo_nota'].upper() != 'IMPIANTO'):
                    item_dict['eredi'] = self.select_eredi_terreni(codiceimmobile, item_dict['mutazioneiniziale'])
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

    def select_eredi_fabbricati(self, codiceimmobile: int, mutazioneiniziale: int) -> List[ErediItemResult]:
        eredi_results = self.db.execute(
            VisuraView.select_eredi_fabbricati(codiceimmobile=codiceimmobile, mutazioneiniziale=mutazioneiniziale)
        ).all()
        if eredi_results and len(eredi_results) != 0:
            return eredi_results
        return None

    def select_eredi_terreni(self, codiceimmobile: int, mutazioneiniziale: int) -> List[ErediItemResult]:
        eredi_results = self.db.execute(
            VisuraView.select_eredi_terreni(codiceimmobile=codiceimmobile, mutazioneiniziale=mutazioneiniziale)
        ).all()
        if eredi_results and len(eredi_results) != 0:
            return eredi_results
        return None

    def select_utilita(self, codiceimmobile: int, progressivo: int) -> List[ErediItemResult]:
        utilita_results = self.db.execute(
            VisuraView.select_utilita(codiceimmobile=codiceimmobile, progressivo=progressivo)
        ).all()
        if utilita_results:
            return utilita_results
        return None

    def select_codiceimmobile(self, flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> VisuraItem:
        visura_result = self.db.execute(
            VisuraView.select_codiceimmobile(flagstorico=False, comune=comune, codiceimmobile=codiceimmobile, tipoimmobile=tipoimmobile)
        ).first()
        if visura_result:
            visura_item = VisuraItem(**visura_result, by_alias=True).dict()
            visura_item['codice_immobile'] = codiceimmobile
            visura_item['tipoimmobile'] = tipoimmobile
            visura_item['dati_catastali_fabbricato_attuali'] = self.select_dettagli_fabbricato(False, visura_item['comune'], visura_item['foglio'], visura_item['particella'], codiceimmobile)
            visura_item['dati_catastali_terreno_attuali'] = self.select_dettagli_terreno(False, visura_item['comune'], visura_item['foglio'], visura_item['particella'], codiceimmobile)
            visura_item['titolari_attuali'] = self.select_titolari(False, visura_item['comune'], codiceimmobile, tipoimmobile)
            if visura_item['dati_catastali_fabbricato_attuali']:
                visura_item['tipoimmobile'] = 'F'
            if visura_item['dati_catastali_terreno_attuali']:
                visura_item['tipoimmobile'] = 'T'
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
