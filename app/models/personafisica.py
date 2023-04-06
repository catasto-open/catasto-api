from datetime import date

class PersonaFisicaView:

    def select_codicefiscale(comune: str, cf: str) -> str:
        sql_view = \
        f"""
        SELECT
            DISTINCT
                STRING_AGG(F.SOGGETTO::TEXT, ',') AS SOGGETTO,
            F.TIPO_SOG AS TIPOSOG,
            F.NOME AS NOME,
            F.COGNOME AS COGNOME,
            F.CODFISCALE AS CODFISCALE,
            CASE
                WHEN LENGTH(F.DATA) = 8
                        THEN TO_DATE(F.DATA, 'DDMMYYYY')
            END
                        AS DATADINASCITA,
            C.COMUNE ||
            CASE
                WHEN C.PROVINCIA <> ''
                        THEN (' (' || C.PROVINCIA) || ')'
                ELSE ''
            END
                        AS COMUNE,
            CASE
                F.SESSO
                    WHEN '2'
                        THEN 'FEMMINA'
                ELSE 'MASCHIO'
            END
                        AS GENERE,
            C.PROVINCIA AS PROVINCIA
        FROM
            CTCN.CTFISICA F
        LEFT JOIN CTCN.COMUNI C
                ON
            C.CODICE = F.LUOGO
        WHERE
            F.CODICE ILIKE '{comune}'
            AND
            F.TIPO_SOG = 'P'
            AND
            F.CODFISCALE ILIKE '{cf}'
        GROUP BY
            F.TIPO_SOG,
            F.NOME,
            F.COGNOME,
            F.CODFISCALE,
            DATADINASCITA,
            COMUNE,
            GENERE,
            PROVINCIA
        """
        return sql_view

    def select_codicesoggetto(comune: str, cs: int) -> str:
        sql_view = \
        f"""
        SELECT
            DISTINCT
                STRING_AGG(F.SOGGETTO::TEXT, ',') AS SOGGETTO,
            F.TIPO_SOG AS TIPOSOG,
            F.NOME AS NOME,
            F.COGNOME AS COGNOME,
            F.CODFISCALE AS CODFISCALE,
            CASE
                WHEN LENGTH(F.DATA) = 8
                        THEN TO_DATE(F.DATA, 'DDMMYYYY')
            END
                        AS DATADINASCITA,
            C.COMUNE ||
            CASE
                WHEN C.PROVINCIA <> ''
                        THEN (' (' || C.PROVINCIA) || ')'
                ELSE ''
            END
                        AS COMUNE,
            CASE
                F.SESSO
                    WHEN '2'
                        THEN 'FEMMINA'
                ELSE 'MASCHIO'
            END
                        AS GENERE,
            C.PROVINCIA AS PROVINCIA
        FROM
            CTCN.CTFISICA F
        LEFT JOIN CTCN.COMUNI C
                ON
            C.CODICE = F.LUOGO
        WHERE
            F.CODICE ILIKE '{comune}'
            AND
            F.TIPO_SOG = 'P'
            AND
            F.SOGGETTO = {cs}
        GROUP BY
            F.TIPO_SOG,
            F.NOME,
            F.COGNOME,
            F.CODFISCALE,
            DATADINASCITA,
            COMUNE,
            GENERE,
            PROVINCIA
        """
        return sql_view

    def select_datianagrafici(comune: str, nome: str, cognome: str, codicecomunedinascita: str, datadinascita: date) -> str:
        if datadinascita:
            datadinascitastr = datadinascita.isoformat()
            datacheck = \
                f"""(LENGTH(F.DATA) <> 8 OR TO_DATE(F.DATA, 'DDMMYYYY') = TO_DATE('{datadinascitastr}', 'YYYY-MM-DD'))
                    AND
                """
        else:
            datacheck = ""
        if(not codicecomunedinascita):
            codicecomunedinascita = "%"
        sql_view = \
        f"""
        SELECT
            DISTINCT
                STRING_AGG(F.SOGGETTO::TEXT, ',') AS SOGGETTO,
            F.TIPO_SOG AS TIPOSOG,
            F.NOME AS NOME,
            F.COGNOME AS COGNOME,
            F.CODFISCALE AS CODFISCALE,
            CASE
                WHEN LENGTH(F.DATA) = 8
                        THEN TO_DATE(F.DATA, 'DDMMYYYY')
            END
                        AS DATADINASCITA,
            C.COMUNE ||
            CASE
                WHEN C.PROVINCIA <> ''
                        THEN (' (' || C.PROVINCIA) || ')'
                ELSE ''
            END
                        AS COMUNE,
            CASE
                F.SESSO
                    WHEN '2'
                        THEN 'FEMMINA'
                ELSE 'MASCHIO'
            END
                        AS GENERE,
            C.PROVINCIA AS PROVINCIA
        FROM
            CTCN.CTFISICA F
        LEFT JOIN CTCN.COMUNI C
                ON
            C.CODICE = F.LUOGO
        WHERE
            F.CODICE ILIKE '{comune}'
            AND
            F.TIPO_SOG = 'P'
            AND
            F.COGNOME ILIKE '{cognome}'
            AND
            F.NOME ILIKE '{nome}'
            AND
            {datacheck}
            F.LUOGO ILIKE '{codicecomunedinascita}'
        GROUP BY
            F.TIPO_SOG,
            F.NOME,
            F.COGNOME,
            F.CODFISCALE,
            DATADINASCITA,
            COMUNE,
            GENERE,
            PROVINCIA
        """
        return sql_view
