from recaudo.views import RegistrosConfiguracion_viwes  as viwes
from django.urls import path

# urls
urlpatterns = [
        path('registrosconfiguracion/get/', viwes.Vista_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
        path('registrosconfiguracion/post/', viwes.Crear_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
        path('registrosconfiguracion/put/<str:pk>/', viwes.Actualizar_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
        path('registrosconfiguracion/delete/<str:pk>/', viwes.Borrar_RegistrosConfiguracion.as_view(), name='registros-configuracion'),




        path('tipoCobro/get/', viwes.Vista_TipoCobro.as_view(), name='registros-tipo-cobro'),
        path('tipoCobro/post/', viwes.Crear_TipoCobro.as_view(), name='registros-tipo-cobro'),
        path('tipoCobro/put/<str:pk>/', viwes.Actualizar_TipoCobro.as_view(), name='registros-TipoCobro'),
        path('tipoCobro/delete/<str:pk>/', viwes.Borrar_TipoCobro.as_view(), name='registros-TipoCobro'),



        path('tiporenta/get/', viwes.Vista_TipoRenta.as_view(), name='registros-tipo-renta'),
        path('tiporenta/post/', viwes.Crear_TipoRenta.as_view(), name='registros-tipo-renta'),
        path('tiporenta/put/<str:pk>/', viwes.Actualizar_TipoRenta.as_view(), name='registros-renta'),
        path('tiporenta/delete/<str:pk>/', viwes.Borrar_TipoRenta.as_view(), name='registros-renta'),




        path('variables/get/', viwes.Vista_Variables.as_view(), name='registros-variables'),
        path('variables/post/', viwes.Crear_Variables.as_view(), name='registros-variables'),
        path('variables/put/<str:pk>/', viwes.Actualizar_Variables.as_view(), name='registros-variables'),
        path('variables/delete/<str:pk>/', viwes.Borrar_Variables.as_view(), name='registros-variables'),


        path('valoresvariables/get/', viwes.Vista_ValoresVariables.as_view(), name='registros-valoresvariables'),
        path('valoresvariables/post/', viwes.Crear_ValoresVariables.as_view(), name='registros-valoresvariables'),
        path('valoresvariables/put/<str:pk>/', viwes.Actualizar_ValoresVariables.as_view(), name='registros-valoresvariables'),
        path('valoresvariables/delete/<str:pk>/', viwes.Borrar_ValoresVariables.as_view(), name='registros-valoresvariables'),



            #funcion para calcular los dias de el mes
        path('calculadoradiasmeses/', viwes.CalculadoraDiasMeses.as_view(), name='registros-calculadora-dias-meses'),


    ]

