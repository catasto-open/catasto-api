from datetime import date

class ImmobileView:

    def select_codicesoggetto(flagstorico: bool, comune: str, cs: int, tipoimmobile: str) -> str:

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
                VSF.CODICE,
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
                VST.CODICE,
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
            UN.CODICE ILIKE '{comune}'
            AND UN.SOGGETTO = {cs}
            {checktipo} {strdatafine}
        GROUP BY
            TIPOIMMOBILE,
            UN.DATA_FINE,
            UN.FOGLIO,
            UN.PARTICELLA,
            UN.SUBALTERNO,
            UN.IMMOBILE
        ORDER BY
            UN.TIPO_IMMOBILE,
            UN.DATA_FINE DESC NULLS FIRST,
            UN.FOGLIO,
            UN.PARTICELLA,
            UN.SUBALTERNO,
            UN.IMMOBILE
        """
        return sql_view

    def select_codiceimmobile(flagstorico: bool, comune: str, codiceimmobile: int, tipoimmobile: str) -> str:

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
                VSF.CODICE,
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
                VST.CODICE,
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
            UN.IMMOBILE = {codiceimmobile}
            AND UN.CODICE ILIKE '{comune}'
            {checktipo} {strdatafine}
        GROUP BY
            TIPOIMMOBILE,
            UN.DATA_FINE,
            UN.FOGLIO,
            UN.PARTICELLA,
            UN.SUBALTERNO,
            UN.IMMOBILE
        ORDER BY
            UN.TIPO_IMMOBILE,
            UN.DATA_FINE DESC NULLS FIRST,
            UN.FOGLIO,
            UN.PARTICELLA,
            UN.SUBALTERNO
        """
        return sql_view

    def select_daticatastali(flagstorico: bool, comune: str, sezione: str, foglio: str, particella: str, tipoimmobile: str) -> str:

        if tipoimmobile == "T":
            checktipo = " AND TIPO_IMMOBILE ILIKE 'Terreni'"
        elif tipoimmobile == "F":
            checktipo = " AND TIPO_IMMOBILE ILIKE 'Fabbricati'"
        else:
            checktipo = ""

        if sezione == "F":
            checksezione = f" AND SEZIONE ILIKE '{sezione}'"
        else:
            checksezione = ""

        if not flagstorico:
            strdatafine = " AND DATA_FINE_F > ('NOW'::TEXT)::DATE"
        else:
            strdatafine = ""

        sql_view = \
        f"""
        SELECT
            TIPO_IMMOBILE AS TIPOIMMOBILE,
            FOGLIO,
            PARTICELLA,
            SUBALTERNO,
            IMMOBILE,
            DATA_FINE
        FROM
            ((
            SELECT
                'Terreni' AS TIPO_IMMOBILE,
                VT.CODICE AS COMUNE,
                F.SEZIONE,
                VT.FOGLIO::TEXT,
                VT.PARTICELLA,
                VT.SUBALTERNO,
                VT.IMMOBILE,
                C.TOPONIMO,
                C.INDIRIZZO,
                LTRIM(COALESCE(C.CIVICO1, ''), '0') AS CIVICO,
                VT.DATA_FINE_F AS DATA_FINE_F,
                VT.DATA_FINE AS DATA_FINE
            FROM
                CTCN.V_TERRENI VT
            RIGHT JOIN CTMP.PARTICELLE F
                ON
                F.COMUNE = VT.CODICE
                AND F.FOGLIO LIKE VT.FOGLIO::TEXT
                AND F.NUMERO = VT.PARTICELLA
            LEFT JOIN CTCN.CUINDIRI C
                ON
                C.CODICE = VT.CODICE
                AND C.IMMOBILE = VT.IMMOBILE)
        UNION ALL 
            (
        SELECT
            'Fabbricati' AS TIPO_IMMOBILE,
            VF.CODICE AS COMUNE,
            F.SEZIONE,
            VF.FOGLIO,
            VF.PARTICELLA,
            VF.SUBALTERNO,
            VF.IMMOBILE,
                C.TOPONIMO,
            C.INDIRIZZO,
            LTRIM(COALESCE(C.CIVICO1, ''), '0') AS CIVICO,
            VF.DATA_FINE_F AS DATA_FINE_F,
            VF.DATA_FINE AS DATA_FINE
        FROM
            CTCN.V_FABBRICATI VF
        RIGHT JOIN CTMP.FABBRICATI F
                ON
            F.COMUNE = VF.CODICE
            AND F.FOGLIO = VF.FOGLIO
            AND F.NUMERO = VF.PARTICELLA
        LEFT JOIN CTCN.CUINDIRI C
                ON
            C.CODICE = VF.CODICE
            AND C.IMMOBILE = VF.IMMOBILE)) F
        WHERE
            FOGLIO = '{foglio}'
            AND PARTICELLA = '{particella}'
            AND COMUNE ILIKE '{comune}'
            {checksezione} {checktipo} {strdatafine}
        GROUP BY
            TIPOIMMOBILE,
            DATA_FINE,
            FOGLIO,
            PARTICELLA,
            SUBALTERNO,
            IMMOBILE
        ORDER BY
            TIPO_IMMOBILE,
            F.DATA_FINE NULLS FIRST,
            FOGLIO,
            PARTICELLA,
            SUBALTERNO,
            IMMOBILE
        """
        return sql_view


    def select_indirizzo(flagstorico: bool, comune: str, toponimo: int, indirizzo: str, numerocivico: str, tipoimmobile: str) -> str:

        if tipoimmobile == "T":
            checktipo = " AND TIPO_IMMOBILE ILIKE 'Terreni'"
        elif tipoimmobile == "F":
            checktipo = " AND TIPO_IMMOBILE ILIKE 'Fabbricati'"
        else:
            checktipo = ""

        if not flagstorico:
            strdatafine = " AND DATA_FINE_F > ('NOW'::TEXT)::DATE"
        else:
            strdatafine = ""

        sql_view = \
        f"""
        SELECT
            TIPO_IMMOBILE AS TIPOIMMOBILE,
            FOGLIO,
            PARTICELLA,
            SUBALTERNO,
            IMMOBILE,
            DATA_FINE
        FROM
            ((
            SELECT
                'Terreni' AS TIPO_IMMOBILE,
                VT.CODICE AS COMUNE,
                F.SEZIONE,
                VT.FOGLIO::TEXT,
                VT.PARTICELLA,
                VT.SUBALTERNO,
                VT.IMMOBILE,
                C.TOPONIMO,
                C.INDIRIZZO,
                LTRIM(COALESCE(C.CIVICO1, ''), '0') AS CIVICO,
                VT.DATA_FINE_F AS DATA_FINE_F,
                VT.DATA_FINE AS DATA_FINE
            FROM
                CTCN.V_TERRENI VT
            RIGHT JOIN CTMP.PARTICELLE F
                ON
                F.COMUNE = VT.CODICE
                AND F.FOGLIO LIKE VT.FOGLIO::TEXT
                AND F.NUMERO = VT.PARTICELLA
            LEFT JOIN CTCN.CUINDIRI C
                ON
                C.CODICE = VT.CODICE
                AND C.IMMOBILE = VT.IMMOBILE)
        UNION ALL 
            (
        SELECT
            'Fabbricati' AS TIPO_IMMOBILE,
            VF.CODICE AS COMUNE,
            F.SEZIONE,
            VF.FOGLIO,
            VF.PARTICELLA,
            VF.SUBALTERNO,
            VF.IMMOBILE,
                C.TOPONIMO,
            C.INDIRIZZO,
            LTRIM(COALESCE(C.CIVICO1, ''), '0') AS CIVICO,
            VF.DATA_FINE_F AS DATA_FINE_F,
            VF.DATA_FINE AS DATA_FINE
        FROM
            CTCN.V_FABBRICATI VF
        RIGHT JOIN CTMP.FABBRICATI F
                ON
            F.COMUNE = VF.CODICE
            AND F.FOGLIO = VF.FOGLIO
            AND F.NUMERO = VF.PARTICELLA
        LEFT JOIN CTCN.CUINDIRI C
                ON
            C.CODICE = VF.CODICE
            AND C.IMMOBILE = VF.IMMOBILE)) F
        WHERE
            TOPONIMO = {toponimo}
            AND INDIRIZZO ILIKE '{indirizzo}%'
            AND CIVICO LIKE '{numerocivico}'
            AND COMUNE ILIKE '{comune}'
            {checktipo} {strdatafine}
        GROUP BY
            TIPOIMMOBILE,
            DATA_FINE,
            FOGLIO,
            PARTICELLA,
            SUBALTERNO,
            IMMOBILE
        ORDER BY
            TIPO_IMMOBILE,
            F.DATA_FINE NULLS FIRST,
            FOGLIO,
            PARTICELLA,
            SUBALTERNO,
            IMMOBILE
        """
        return sql_view