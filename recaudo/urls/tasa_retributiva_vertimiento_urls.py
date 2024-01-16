from django.urls import path
from recaudo.views import tasa_retributiva_vertimiento_viwes as views
from recaudo.views.tasa_retributiva_vertimiento_viwes import T0444444FormularioView

urlpatterns = [
    path('documento_formulario_recuado/', views.CrearDocumentoFormularioRecuado.as_view(), name='crear_documento_formulario_recuado'),
    path('documento_formulario_recuado_get/', views.DocumentoFormularioRecaudoGET.as_view(), name='actualizar_documento_formulario_recuado_get'),
    path('crear_formulario/', T0444444FormularioView.as_view(), name='crear_formulario'),
    path('tipo_usuario_options/', views.TipoUsuarioOptionsView.as_view(), name='tipo_usuario_options'),
    path('captacionmensualagua/', views.CaptacionMensualAguaViwes.as_view(), name='meses'),




]