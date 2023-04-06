from fastapi.responses import FileResponse
import random
import pandas

class Item:
    def __init__(self, vals):
        self.__dict__ = vals

def generate_print_csv(template: str, data: dict, user_stampa: str) -> FileResponse:

    df = pandas.DataFrame(data)

    if(template=="Persone Fisiche"):
        filename = "listapersonefisiche.csv"
        df.columns = ['Codice soggetto', 'tiposog', 'Nome', 'Cognome', 'Codice fiscale', 'Data di nascita', 'Luogo', 'Sesso', 'provincia']
        del df['tiposog']
        del df['provincia']
    elif(template=="Persone Giuridiche"):
        filename = "listapersonegiuridiche.csv"
        df.columns = ['Codice soggetto' ,'tiposog', 'Denominazione', 'Partita iva', 'Comune', 'Provincia']
        del df['tiposog']
    elif(template=="Immobili"):
        filename = "listaimmobili.csv"
        df.columns = ["Tipo Immobile", "Foglio", "Particella", "Sub.", "Codice Immobile", "Data Fine"]
        del df['Data Fine']
    else:
        raise BaseException()

    # Temporary location of the file
    fileLocation= "/tmp/temp" + str(random.randint(1,100)) + filename

    df.to_csv(fileLocation, sep=';', index=False)

    return FileResponse(
            fileLocation,
            media_type="application/csv",
            filename=filename)