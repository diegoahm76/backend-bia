from django.urls import path
from recaudo.views import tasa_retributiva_vertimiento_viwes as views
from recaudo.views.tasa_retributiva_vertimiento_viwes import T0444444FormularioView

urlpatterns = [
    path('documento_formulario_recuado/', views.CrearDocumentoFormularioRecuado.as_view(), name='crear_documento_formulario_recuado'),
    path('documento_formulario_recuado_get/', views.DocumentoFormularioRecaudoGET.as_view(), name='actualizar_documento_formulario_recuado_get'),
    # path('t0444_formulario_create/', views.T0444FormularioCreateView.as_view(), name='t0444_formulario_create'),
    # path('crear_forsdfsfmudsflariossa/', views.CrearFormularioView.as_view(), name='crear_formularifsdfo'),
    # path('crear_formulario/', CrearFormularioSerializer.as_view(), name='crear_formulario'),
    path('crear_formulario/', T0444444FormularioView.as_view(), name='crear_formulario'),


]