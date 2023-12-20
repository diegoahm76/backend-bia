from django.urls import path
from recaudo.views import tasa_retributiva__vertimiento_viwes as views

urlpatterns = [
    path('documento_formulario_recuado/', views.CrearDocumentoFormularioRecuado.as_view(), name='crear-sub-zona-hidrica'),
]