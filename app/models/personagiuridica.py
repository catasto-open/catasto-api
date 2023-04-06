from datetime import date

class PersonaGiuridicaView:

    def select_partitaiva(comune: str, partitaiva: str) -> str:
        sql_view = \
        f"""
        SELECT
            DISTINCT
                F.SOGGETTO AS SOGGETTO,
            F.TIPO_SOG AS TIPOSOG,
            F.DENOMINAZ AS DENOMINAZIONE,
            F.CODFISCALE AS PARTITAIVA,
            C.COMUNE AS COMUNE,
            C.PROVINCIA AS PROVINCIA
        FROM
            CTCN.CTNONFIS F
        LEFT JOIN CTCN.COMUNI C
                ON
            C.CODICE = F.SEDE
        WHERE
            F.CODICE ILIKE '{comune}'
            AND
            F.TIPO_SOG = 'G'
            AND
            F.CODFISCALE = '{partitaiva}'
        """
        return sql_view

    def select_denominazione(comune: str, denominazione: str) -> str:
        sql_view = \
        f"""
         SELECT
            DISTINCT
                F.SOGGETTO AS SOGGETTO,
            F.TIPO_SOG AS TIPOSOG,
            F.DENOMINAZ AS DENOMINAZIONE,
            F.CODFISCALE AS PARTITAIVA,
            C.COMUNE AS COMUNE,
            C.PROVINCIA AS PROVINCIA
        FROM
            CTCN.CTNONFIS F
        LEFT JOIN CTCN.COMUNI C
                ON
            C.CODICE = F.SEDE
        WHERE
            F.CODICE ILIKE '{comune}'
            AND
            F.TIPO_SOG = 'G'
            AND
            F.DENOMINAZ ILIKE '{denominazione}'
        """
        return sql_view

    def select_codicesoggetto(comune: str, cs: int) -> str:
        sql_view = \
        f"""
         SELECT
            DISTINCT
                F.SOGGETTO AS SOGGETTO,
            F.TIPO_SOG AS TIPOSOG,
            F.DENOMINAZ AS DENOMINAZIONE,
            F.CODFISCALE AS PARTITAIVA,
            C.COMUNE AS COMUNE,
            C.PROVINCIA AS PROVINCIA
        FROM
            CTCN.CTNONFIS F
        LEFT JOIN CTCN.COMUNI C
                ON
            C.CODICE = F.SEDE
        WHERE
            F.CODICE ILIKE '{comune}'
            AND
            F.TIPO_SOG = 'G'
            AND
            F.SOGGETTO = {cs}
        """
        return sql_view
