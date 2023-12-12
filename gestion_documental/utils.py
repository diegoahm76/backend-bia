#from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from rest_framework import status
#from weasyprint import HTML
from reportlab.pdfgen import canvas
from io import BytesIO
class UtilsGestor:


    def generar_archivo_blanco(data):
        
        
        template = "doc_blanco.html"

       
        context = data
        template_content = render_to_string((template), {'mi_json': context})
        # buffer = HttpResponse(content_type='application/pdf')
        # buffer['Content-Disposition'] = 'attachment; filename="output.pdf"'

        # # Crear el objeto PDF utilizando xhtml2pdf.
        # #pisa_status = pisa.CreatePDF(template, dest=buffer)


        # pdf_bytes = buffer.getvalue()

        buffer = BytesIO()

        # Crear el objeto PDF utilizando ReportLab.
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, 'Hola Mundo')  # Agregar contenido al PDF, puedes omitir esto si todo el contenido está en el HTML
        p.showPage()
        p.save()
        buffer.write(template_content.encode('utf-8'))

    # Obtener el contenido del buffer como bytes
        pdf_bytes = buffer.getvalue()
        
        # response = HttpResponse(pdf_bytes, content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="output.pdf"'

        # return response



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
 
        return respuesta_archivo
        
        
        
        
