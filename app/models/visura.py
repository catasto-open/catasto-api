from datetime import date

class VisuraView:

    def select_codiceimmobile(flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> str:

        if tipoimmobile == "T":
            checktipo = " AND UN.TIPO_IMM ILIKE 'T'"
        elif tipoimmobile == "F":
            checktipo = " AND UN.TIPO_IMM ILIKE 'F'"
        else:
            checktipo = ""

        if not flagstorico:
            strdatafine = " AND UN.DATA_FINE_F > ('NOW'::TEXT)::DATE"
        else:
            strdatafine = " AND UN.DATA_FINE_F < ('NOW'::TEXT)::DATE"

        sql_view = \
        f"""
        SELECT
            UN.CODICE AS COMUNE,
            UN.TIPO_IMM AS TIPO_IMMOBILE,
            UN.FOGLIO,
            UN.PARTICELLA,
            UN.SUBALTERNO,
            UN.IMMOBILE,
            UN.DATA_FINE
        FROM
            (
            SELECT
                VSF.CODICE,
                VSF.TIPO_IMM,
                VSF.FOGLIO,
                VSF.PARTICELLA,
                VSF.SUBALTERNO,
                VSF.IMMOBILE,
                VSF.DATA_FINE,
                VSF.DATA_FINE_F
            FROM
                CTCN.V_FABBRICATI VSF
        UNION ALL
            SELECT
                VST.CODICE,
                VST.TIPO_IMM,
                VST.FOGLIO::text,
                VST.PARTICELLA,
                VST.SUBALTERNO,
                VST.IMMOBILE,
                VST.DATA_FINE,
                VST.DATA_FINE_F
            FROM
                CTCN.V_TERRENI VST 
        ) UN
        WHERE
            UN.IMMOBILE = {codiceimmobile}
            AND UN.CODICE ILIKE '{comune}'
            {checktipo} {strdatafine}
        GROUP BY
            UN.CODICE,
            UN.TIPO_IMM,
            UN.DATA_FINE,
            UN.FOGLIO,
            UN.PARTICELLA,
            UN.SUBALTERNO,
            UN.IMMOBILE
        ORDER BY
            UN.CODICE,
            UN.TIPO_IMM,
            UN.DATA_FINE DESC NULLS FIRST,
            UN.FOGLIO,
            UN.PARTICELLA,
            UN.SUBALTERNO
        """
        return sql_view


    def select_dettagli_fabbricato(flagstorico: bool, comune: str, foglio:str, particella: str, codiceimmobile: int) -> str:

        if not flagstorico:
            strdatafine = " AND COALESCE(TO_DATE(F.CON_EFF::TEXT, 'DDMMYYYY'::TEXT), 'NOW'::TEXT::DATE + 1) > ('NOW'::TEXT)::DATE"
        else:
            strdatafine = " AND COALESCE(TO_DATE(F.CON_EFF::TEXT, 'DDMMYYYY'::TEXT), 'NOW'::TEXT::DATE + 1) < ('NOW'::TEXT)::DATE"

        sql_view = \
        f"""
        SELECT
            DISTINCT
            C.CODICE,
            F.SEZIONE,
            F.IMMOBILE,
            F.TIPO_IMM AS TIPO_IMMOBILE,
            F.PROGRESSIV AS PROGRESSIVO,
            LTRIM(II.FOGLIO::TEXT, '0'::TEXT) AS FOGLIO,
            LTRIM(II.NUMERO::TEXT, '0'::TEXT) AS PARTICELLA,
            LTRIM(II.SUBALTERNO::TEXT, '0'::TEXT) AS SUBALTERNO,
            LTRIM(F.ZONA::TEXT, '0'::TEXT) AS ZONA_CENSUARIA,
            CASE
                WHEN COALESCE(F.CATEGORIA, ''::CHARACTER VARYING)::TEXT <> ''::TEXT THEN (SUBSTR(F.CATEGORIA::TEXT,
                1,
                1) || '/'::TEXT) || LTRIM(SUBSTR(F.CATEGORIA::TEXT, 2, 2), '0'::TEXT)
                ELSE ''::TEXT
            END AS CATEGORIA,
            LTRIM(F.CLASSE::TEXT, '0'::TEXT) AS CLASSE,
            CASE
                WHEN COALESCE(F.CONSISTENZ, ''::CHARACTER VARYING)::TEXT <> ''::TEXT THEN
                CASE
                    WHEN F.CATEGORIA::TEXT ~~ 'A%'::TEXT THEN (F.CONSISTENZ::TEXT || ' VAN'::TEXT) ||
                    CASE
                        WHEN F.CONSISTENZ::TEXT = '1'::TEXT THEN 'O'::TEXT
                        ELSE 'I'::TEXT
                    END
                    WHEN F.CATEGORIA::TEXT ~~ 'B%'::TEXT THEN F.CONSISTENZ::TEXT || ' MC'::TEXT
                    WHEN F.CATEGORIA::TEXT ~~ 'C%'::TEXT THEN F.CONSISTENZ::TEXT || ' MQ'::TEXT
                    ELSE ''::TEXT
                END
                ELSE ''::TEXT
            END AS CONSISTENZA,
            F.SUPERFICIE AS SUPERFICIE,
            F.RENDITA_E AS RENDITA,
            CASE
                F.PARTITA
                    WHEN 'C'::TEXT THEN 'SOPPRESSA'::TEXT
                ELSE LTRIM(F.PARTITA::TEXT, '0'::TEXT)
            END AS PARTITA,
            TO_DATE(F.GEN_EFF::TEXT, 'DDMMYYYY'::TEXT) AS DATA_DECORRENZA,
            TO_DATE(F.CON_EFF::TEXT, 'DDMMYYYY'::TEXT) AS DATA_FINE,
            F.ANNOTAZION AS ANNOTAZIONI,
            COALESCE(N.DESCRIZION, '') AS GEN_TIPO_NOTA,
            COALESCE(F.GEN_DESCR, '') AS GEN_DESCR,
            COALESCE(X.DESCRIZION, F.GEN_CAUSA, '') AS GEN_CAUSA,
            COALESCE(TO_CHAR(TO_DATE(F.GEN_REGIST, 'DDMMYYYY'::TEXT), 'DD/MM/YYYY'), '') AS GEN_DATA_REG,
            COALESCE(F.GEN_NUMERO || '.' || F.GEN_PROGRE || '/' || F.GEN_ANNO, '') AS GEN_PROGRESSIVO,
            COALESCE(TO_CHAR(TO_DATE(F.GEN_EFF, 'DDMMYYYY'::TEXT), 'DD/MM/YYYY'), '') AS GEN_DATA_EFF,
            COALESCE(TOP.TOPONIMO, '') || ' ' || COALESCE(IND.INDIRIZZO, '') || ' ' || LTRIM(COALESCE(IND.CIVICO1, ''), '0'::TEXT) || COALESCE('/' || IND.CIVICO2, '') ||
            COALESCE(' LOTTO: ' || F.LOTTO, '') ||
            COALESCE(' EDIFICIO: ' || F.EDIFICIO, '') ||
            COALESCE(' SCALA: ' || F.SCALA, '') ||
            COALESCE(' PIANO: ' || F.PIANO_1, '') || COALESCE('-' || F.PIANO_2, '') || COALESCE('-' || F.PIANO_3, '') || COALESCE('-' || F.PIANO_4, '') ||
            COALESCE(' INTERNO: ' || F.INTERNO_1, '') || COALESCE('-' || F.INTERNO_2, '') AS INDIRIZZO
        FROM
            CTCN.CUARCUIU F
        JOIN CTCN.CUIDENTI II ON
            II.CODICE::TEXT = F.CODICE::TEXT
            AND II.SEZIONE::TEXT = F.SEZIONE::TEXT
            AND II.IMMOBILE = F.IMMOBILE
            AND II.TIPO_IMM::TEXT = F.TIPO_IMM::TEXT
            AND II.PROGRESSIV = F.PROGRESSIV
        JOIN CTCN.COMUNI C ON
            C.CODICE::TEXT = F.CODICE::TEXT
        JOIN CTCN.CUINDIRI IND ON
            F.CODICE = IND.CODICE
            AND F.IMMOBILE = IND.IMMOBILE
            AND F.TIPO_IMM = IND.TIPO_IMM
            AND F.PROGRESSIV = IND.PROGRESSIV
        LEFT JOIN CTCN.CUCODTOP TOP ON
            TOP.CODICE = IND.TOPONIMO
        LEFT JOIN CTCN.CUTIPNOT N ON
            N.TIPO_NOTA = F.GEN_TIPO
        LEFT JOIN CTCN.CUCODCAU X ON
            X.COD_CAUSA = F.GEN_CAUSA
        WHERE
            F.CODICE ILIKE '{comune}'
            AND F.IMMOBILE = {codiceimmobile}
            AND LTRIM(II.FOGLIO::TEXT, '0'::TEXT) = '{foglio}'
            AND LTRIM(II.NUMERO::TEXT, '0'::TEXT) = '{particella}'
            AND F.TIPO_IMM ILIKE 'F'
            {strdatafine}
        ORDER BY
            C.CODICE,
            DATA_FINE DESC NULLS FIRST,
            FOGLIO,
            PARTICELLA,
            IMMOBILE,
            PROGRESSIVO ASC,
            SUBALTERNO,
            TIPO_IMMOBILE
        """
        return sql_view

    def select_dettagli_terreno(flagstorico: bool, comune: str, foglio:str, particella: str, codiceimmobile: int) -> str:

        if not flagstorico:
            strdatafine = " AND COALESCE(TO_DATE(T.CON_EFF::TEXT, 'DDMMYYYY'::TEXT), 'NOW'::TEXT::DATE + 1) > ('NOW'::TEXT)::DATE"
        else:
            strdatafine = " AND COALESCE(TO_DATE(T.CON_EFF::TEXT, 'DDMMYYYY'::TEXT), 'NOW'::TEXT::DATE + 1) < ('NOW'::TEXT)::DATE"

        sql_view = \
        f"""
        SELECT
            DISTINCT
            T.CODICE,
            T.SEZIONE,
            T.IMMOBILE,
            T.TIPO_IMM AS TIPO_IMMOBILE,
            T.PROGRESSIV AS PROGRESSIVO,
            C.COMUNE::TEXT ||
            CASE
                WHEN C.PROVINCIA::TEXT <> ''::TEXT THEN (' ('::TEXT || C.PROVINCIA::TEXT) || ')'::TEXT
                ELSE ''::TEXT
            END AS COMUNE,
            T.FOGLIO,
            LTRIM(T.NUMERO::TEXT, '0'::TEXT) AS PARTICELLA,
            T.SUBALTERNO,
            UPPER(Q.QUALITA::TEXT) AS QUALITA,
            LTRIM(T.CLASSE::TEXT, '0'::TEXT) AS CLASSE,
            T.ETTARI AS SUPERFICE_HA,
            T.ARE AS SUPERFICE_ARE,
            T.CENTIARE AS SUPERFICE_CA,
            T.DOMINIC_E AS REDDITO_DOMINICALE,
            T.AGRARIO_E AS REDDITO_AGRARIO,
            CASE
                T.PARTITA
                    WHEN 'C'::TEXT THEN 'SOPPRESSA'::TEXT
                ELSE LTRIM(T.PARTITA::TEXT, '0'::TEXT)
            END AS PARTITA,
            TO_DATE(T.GEN_EFF::TEXT, 'DDMMYYYY'::TEXT) AS DATA_DECORRENZA,
            TO_DATE(T.CON_EFF::TEXT, 'DDMMYYYY'::TEXT) AS DATA_FINE,
            COALESCE(TO_DATE(T.CON_EFF::TEXT, 'DDMMYYYY'::TEXT), 'NOW'::TEXT::DATE + 1) AS DATA_FINE_F,
            T.NUMERO AS NUMERO_F,
            T.ANNOTAZION AS ANNOTAZIONI,
            COALESCE(N.DESCRIZION, '') AS GEN_TIPO_NOTA,
            COALESCE(T.GEN_DESCR, '') AS GEN_DESCR,
            COALESCE(X.DESCRIZION, T.GEN_CAUSA, '') AS GEN_CAUSA,
            COALESCE(TO_CHAR(TO_DATE(T.GEN_REGIST, 'DDMMYYYY'::TEXT), 'DD/MM/YYYY'), '') AS GEN_DATA_REG,
            COALESCE(T.GEN_NUMERO || '.' || T.GEN_PROGRE || '/' || T.GEN_ANNO, '') AS GEN_PROGRESSIVO,
            COALESCE(TO_CHAR(TO_DATE(T.GEN_EFF, 'DDMMYYYY'::TEXT), 'DD/MM/YYYY'), '') AS GEN_DATA_EFF
        FROM
            CTCN.CTPARTIC T
        JOIN CTCN.COMUNI C ON
            C.CODICE::TEXT = T.CODICE::TEXT
        LEFT JOIN CTCN.CTQUALIT Q ON
            Q.CODICE = T.QUALITA
        LEFT JOIN CTCN.CTTIPNOT N ON
            N.TIPO_NOTA = T.GEN_TIPO
        LEFT JOIN CTCN.CUCODCAU X ON
            X.COD_CAUSA = T.GEN_CAUSA
        WHERE
            T.CODICE ILIKE '{comune}'
            AND T.IMMOBILE = {codiceimmobile}
            AND T.FOGLIO = '{foglio}'
            AND LTRIM(T.NUMERO::TEXT, '0'::TEXT) = '{particella}'
            AND T.TIPO_IMM ILIKE 'T'
            {strdatafine}
        ORDER BY
            T.CODICE,
            DATA_FINE DESC NULLS FIRST,
            FOGLIO,
            PARTICELLA,
            IMMOBILE,
            PROGRESSIVO ASC,
            SUBALTERNO
        """
        return sql_view

    def select_titolari(flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> str:

        if tipoimmobile == "T":
            checktipo = " AND TIPO_IMM ILIKE 'T'"
        elif tipoimmobile == "F":
            checktipo = " AND TIPO_IMM ILIKE 'F'"
        else:
            checktipo = ""

        if not flagstorico:
            strdatafine = " AND COALESCE(TO_DATE(T.CON_VALIDA::TEXT, 'DDMMYYYY'::TEXT), 'NOW'::TEXT::DATE + 1) > ('NOW'::TEXT)::DATE"
        else:
            strdatafine = " AND COALESCE(TO_DATE(T.CON_VALIDA::TEXT, 'DDMMYYYY'::TEXT), 'NOW'::TEXT::DATE + 1) < ('NOW'::TEXT)::DATE"

        sql_view = \
        f"""
        SELECT
            T.CODICE,
            T.SEZIONE,
            T.IMMOBILE,
            T.TIPO_IMM AS TIPO_IMMOBILE,
            G.DENOMINAZ || COALESCE(' CON SEDE A ' || C.COMUNE, '') AS NOMINATIVO,
            G.CODFISCALE AS CODICE_FISCALE,
            COALESCE(TT.TITOLO, T.TITOLO) AS TITOLO,
            CASE
                WHEN COALESCE(T.NUMERATORE, 0) > 0 THEN (T.NUMERATORE || '/'::TEXT) || T.DENOMINATO
                ELSE ''::TEXT
            END AS QUOTA,
            TO_DATE(T.GEN_VALIDA::TEXT, 'DDMMYYYY'::TEXT) AS DATA_DECORRENZA,
            TO_DATE(T.CON_VALIDA::TEXT, 'DDMMYYYY'::TEXT) AS DATA_FINE,
            COALESCE(TO_DATE(T.CON_VALIDA::TEXT, 'DDMMYYYY'::TEXT), 'NOW'::TEXT::DATE + 1) AS DATA_FINE_F,
            T.IDENTIFICA,
            COALESCE(N.DESCRIZION, '') AS GEN_TIPO_NOTA,
            COALESCE(T.GEN_DESCR, '') AS GEN_DESCR,
            COALESCE(X.DESCRIZION, T.GEN_CAUSA, '') AS GEN_CAUSA,
            COALESCE(TO_CHAR(TO_DATE(T.GEN_REGIST, 'DDMMYYYY'::TEXT), 'DD/MM/YYYY'), '') AS GEN_DATA_REG,
            COALESCE(T.GEN_NUMERO || '.' || T.GEN_PROGRE || '/' || T.GEN_ANNO, '') AS GEN_PROGRESSIVO
        FROM
            CTCN.CTTITOLA T
        JOIN CTCN.CTNONFIS G ON
            G.CODICE::TEXT = T.CODICE::TEXT
            AND G.SEZIONE::TEXT = T.SEZIONE::TEXT
            AND G.SOGGETTO = T.SOGGETTO
            AND G.TIPO_SOG::TEXT = T.TIPO_SOG::TEXT
        JOIN CTCN.COMUNI C ON
            G.SEDE::TEXT = C.CODICE::TEXT
        LEFT JOIN CTCN.CTTITOLI TT ON
            TT.CODICE::TEXT = T.DIRITTO::TEXT
            AND (T.DIRITTO::TEXT <> ALL (ARRAY['99 '::CHARACTER VARYING::TEXT,
            '990'::CHARACTER VARYING::TEXT]))
        LEFT JOIN CTCN.CUTIPNOT N ON
            N.TIPO_NOTA = T.GEN_NOTA
        LEFT JOIN CTCN.CUCODCAU X ON
            X.COD_CAUSA = T.GEN_CAUSA
        WHERE
            T.IMMOBILE = {codiceimmobile}
            AND T.CODICE = '{comune}'
            {checktipo} {strdatafine}
        UNION ALL
        SELECT
            T.CODICE,
            T.SEZIONE,
            T.IMMOBILE,
            T.TIPO_IMM AS TIPO_IMMOBILE,
            CASE
                WHEN F.SESSO = '1'
                THEN BTRIM((F.COGNOME::TEXT || ' '::TEXT) || F.NOME::TEXT) || COALESCE(' NATO A ' || C.COMUNE, '') || COALESCE(' IL ' || TO_CHAR(TO_DATE(NULLIF(BTRIM(F.DATA::TEXT), ''::TEXT), 'DDMMYYYY'::TEXT),'DD/MM/YYYY'), '')
                ELSE BTRIM((F.COGNOME::TEXT || ' '::TEXT) || F.NOME::TEXT) || COALESCE(' NATA A ' || C.COMUNE, '') || COALESCE(' IL ' || TO_CHAR(TO_DATE(NULLIF(BTRIM(F.DATA::TEXT), ''::TEXT), 'DDMMYYYY'::TEXT),'DD/MM/YYYY'), '')
            END AS NOMINATIVO,
            F.CODFISCALE AS CODICE_FISCALE,
            COALESCE(TT.TITOLO, T.TITOLO) AS TITOLO,
            CASE
                WHEN COALESCE(T.NUMERATORE, 0) > 0 THEN (T.NUMERATORE || '/'::TEXT) || T.DENOMINATO
                ELSE ''::TEXT
            END AS QUOTA,
            TO_DATE(T.GEN_VALIDA::TEXT, 'DDMMYYYY'::TEXT) AS DATA_DECORRENZA,
            TO_DATE(T.CON_VALIDA::TEXT, 'DDMMYYYY'::TEXT) AS DATA_FINE,
            COALESCE(TO_DATE(T.CON_VALIDA::TEXT, 'DDMMYYYY'::TEXT), 'NOW'::TEXT::DATE + 1) AS DATA_FINE_F,
            T.IDENTIFICA,
            COALESCE(N.DESCRIZION, '') AS GEN_TIPO_NOTA,
            COALESCE(T.GEN_DESCR, '') AS GEN_DESCR,
            COALESCE(X.DESCRIZION, T.GEN_CAUSA, '') AS GEN_CAUSA,
            COALESCE(TO_CHAR(TO_DATE(T.GEN_REGIST, 'DDMMYYYY'::TEXT), 'DD/MM/YYYY'), '') AS GEN_DATA_REG,
            COALESCE(T.GEN_NUMERO || '.' || T.GEN_PROGRE || '/' || T.GEN_ANNO, '') AS GEN_PROGRESSIVO
        FROM
            CTCN.CTTITOLA T
        JOIN CTCN.CTFISICA F ON
            F.CODICE::TEXT = T.CODICE::TEXT
            AND F.SEZIONE::TEXT = T.SEZIONE::TEXT
            AND F.SOGGETTO = T.SOGGETTO
            AND F.TIPO_SOG::TEXT = T.TIPO_SOG::TEXT
        JOIN CTCN.COMUNI C ON
            F.LUOGO::TEXT = C.CODICE::TEXT
        LEFT JOIN CTCN.CTTITOLI TT ON
            TT.CODICE::TEXT = T.DIRITTO::TEXT
            AND (T.DIRITTO::TEXT <> ALL (ARRAY['99 '::CHARACTER VARYING::TEXT,
            '990'::CHARACTER VARYING::TEXT]))
        LEFT JOIN CTCN.CUTIPNOT N ON
            N.TIPO_NOTA = T.GEN_NOTA
        LEFT JOIN CTCN.CUCODCAU X ON
            X.COD_CAUSA = T.GEN_CAUSA
        WHERE
            T.IMMOBILE = {codiceimmobile}
            AND T.CODICE = '{comune}'
            {checktipo} {strdatafine}
        ORDER BY
            DATA_FINE DESC,
            NOMINATIVO
        """
        return sql_view




    def select_codicesoggetto(flagstorico: bool, cs: int, tipoimmobile: str) -> str:

        if tipoimmobile == "T":
            checktipo = " AND UN.TIPO_IMMOBILE ILIKE 'Terreni'"
        elif tipoimmobile == "F":
            checktipo = " AND UN.TIPO_IMMOBILE ILIKE 'Fabbricati'"
        else:
            checktipo = ""

        if not flagstorico:
            strdatafine = " AND UN.DATA_FINE_F > ('NOW'::TEXT)::DATE"
        else:
            strdatafine = ""

        sql_view = \
        f"""
        SELECT
            UN.TIPO_IMMOBILE AS TIPOIMMOBILE,
            UN.FOGLIO,
            UN.PARTICELLA,
            UN.SUBALTERNO,
            UN.IMMOBILE,
            UN.DATA_FINE
        FROM
            (
            SELECT
                VSF.TIPO_IMMOBILE,
                VSF.FOGLIO,
                VSF.PARTICELLA,
                VSF.SUBALTERNO,
                VSF.IMMOBILE,
                VSF.SOGGETTO,
                VSF.DATA_FINE,
                VSF.DATA_FINE_F
            FROM
                CTCN.V_SOGGETTI_FABBRICATI VSF
        UNION ALL
            SELECT
                VST.TIPO_IMMOBILE,
                VST.FOGLIO,
                VST.PARTICELLA,
                VST.SUBALTERNO,
                VST.IMMOBILE,
                VST.SOGGETTO,
                VST.DATA_FINE,
                VST.DATA_FINE_F
            FROM
                CTCN.V_SOGGETTI_TERRENI VST 
        ) UN
        WHERE
            UN.SOGGETTO = {cs}
            {checktipo} {strdatafine}
        GROUP BY
            TIPOIMMOBILE,
            UN.DATA_FINE,
            UN.FOGLIO,
            UN.PARTICELLA,
            UN.SUBALTERNO
        ORDER BY
            UN.TIPO_IMMOBILE,
            UN.DATA_FINE DESC NULLS FIRST,
            UN.FOGLIO,
            UN.PARTICELLA,
            UN.SUBALTERNO
        """
        print(sql_view)
        return sql_view