import jinja2
import pdfkit
import random
from fastapi.responses import FileResponse

class Item:
    def __init__(self, vals):
        self.__dict__ = vals

def generate_print(template: str, data: dict) -> FileResponse:

    templateLoader = jinja2.FileSystemLoader(searchpath="./app/templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    if(template=="Persone Fisiche"):
        template_file = "personafisica_list_template.html"
        filename = "listapersonefisiche.pdf"
    elif(template=="Persone Giuridiche"):
        template_file = "personagiuridica_list_template.html"
        filename = "listapersonegiuridiche.pdf"
    elif(template=="Visura"):
        template_file = "visura_template.html"
        filename = "visura.pdf"
    elif(template=="Immobili"):
        template_file = "immobile_list_template.html"
        filename = "listaimmobili.pdf"
    else:
        raise BaseException()

    # Renders template
    tm = templateEnv.get_template(template_file)

    # Temporary location of the file
    fileLocation= "/tmp/temp" + str(random.randint(1,100)) + filename

    if(template=="Visura"):
        # Fills Jinja template with data
        dati_catastali_fabbricato_attuali=None
        dati_catastali_terreno_attuali=None
        titolari_attuali=None
        dati_catastali_fabbricato_storico=None
        dati_catastali_terreno_storico=None
        titolari_storico=None
        storico = False
        tipoImmobile = ''
        if(data['dati_catastali_fabbricato_attuali']):
            dati_catastali_fabbricato_attuali=[Item(i) for i in data['dati_catastali_fabbricato_attuali']]
            tipoImmobile = 'fabbricato'
        if(data['dati_catastali_terreno_attuali']):
            dati_catastali_terreno_attuali=[Item(i) for i in data['dati_catastali_terreno_attuali']]
            tipoImmobile = 'terreno'
        if(data['titolari_attuali']):
            titolari_attuali=[Item(i) for i in data['titolari_attuali']]
        if(data['dati_catastali_fabbricato_storico']):
            dati_catastali_fabbricato_storico=[Item(i) for i in data['dati_catastali_fabbricato_storico']]
            tipoImmobile = 'fabbricato'
            storico = True
        if(data['dati_catastali_terreno_storico']):
            dati_catastali_terreno_storico=[Item(i) for i in data['dati_catastali_terreno_storico']]
            tipoImmobile = 'terreno'
            storico = True
        if(data['titolari_storico']):
            titolari_storico=[Item(i) for i in data['titolari_storico']]
            storico = True

        html_doc_rendered = tm.render(tipoImmobile=tipoImmobile, storico=storico, daticatastali = data, dati_catastali_fabbricato_attuali=dati_catastali_fabbricato_attuali, 
        dati_catastali_terreno_attuali=dati_catastali_terreno_attuali, titolari_attuali=titolari_attuali, 
        dati_catastali_fabbricato_storico=dati_catastali_fabbricato_storico, dati_catastali_terreno_storico=dati_catastali_terreno_storico,
        titolari_storico=titolari_storico)
    else:
        # Fills Jinja template with data
        html_doc_rendered = tm.render(items = [Item(i) for i in data])

#    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltox/bin/')

    options = {
        'orientation': 'Landscape',
        'footer-center': '[page]/[topage]'
    }

    # Generates pdf at fileLocation
    pdfkit.from_string(html_doc_rendered, fileLocation, options=options)

    return FileResponse(
                fileLocation,
                media_type="application/pdf",
                filename=filename)