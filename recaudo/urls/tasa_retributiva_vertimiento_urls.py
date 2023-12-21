from django.urls import path
from recaudo.views import tasa_retributiva_vertimiento_viwes as views

urlpatterns = [
    path('documento_formulario_recuado/', views.CrearDocumentoFormularioRecuado.as_view(), name='crear_documento_formulario_recuado'),
    path('documento_formulario_recuado_get/', views.DocumentoFormularioRecaudoGET.as_view(), name='actualizar_documento_formulario_recuado_get'),
]