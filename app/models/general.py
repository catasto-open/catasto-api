from datetime import date

class GeneralView:

    def select_versione() -> str:

        sql_view = \
        f"""
        SELECT
            CODICE,
            DATA_AGGIORNAMENTO
        FROM CTCN.VERSION
        ORDER BY DATA_AGGIORNAMENTO DESC
        """
        return sql_view