from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from rest_framework import status
class UtilsGestor:


    def generar_archivo_blanco(data):
        
        
        template = "doc_blanco.html"

        #context = {"nombre_anexo":'HOLAAA QUE TAL?','medio_almacenamiento':'papel','asunto':'mata o quien sabe','categoria_archivo':'modelo','tipologia_documental':'documento'}
        context = data
        template = render_to_string((template), {'mi_json': context})
        buffer = HttpResponse(content_type='application/pdf')
        buffer['Content-Disposition'] = 'attachment; filename="output.pdf"'

        # Crear el objeto PDF utilizando xhtml2pdf.
        pisa_status = pisa.CreatePDF(template, dest=buffer)
        pdf_bytes = buffer.getvalue()

        # Crear un objeto ContentFile con el contenido del PDF.
        nombre_archivo = "black.pdf"
        pdf_content_file = ContentFile(pdf_bytes,name=nombre_archivo)
        vista_archivos = ArchivosDgitalesCreate()
        # Verificar si la generación del PDF fue exitosa.
        ruta = "home,BIA,Otros,PQRSDF,Complementos"
        respuesta_archivo = vista_archivos.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},pdf_content_file)
        data_archivo = respuesta_archivo.data['data']
        if respuesta_archivo.status_code != status.HTTP_201_CREATED:
            return respuesta_archivo
        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=500)

        return respuesta_archivo
        
        
        
        
