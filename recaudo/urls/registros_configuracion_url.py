from recaudo.views import RegistrosConfiguracion_viwes  as viwes
from django.urls import path

# urls
urlpatterns = [
        path('registrosconfiguracion/get/', viwes.Vista_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
        path('registrosconfiguracion/post/', viwes.Crear_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
        path('registrosconfiguracion/put/<str:pk>/', viwes.Actualizar_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
        path('registrosconfiguracion/delete/<str:pk>/', viwes.Borrar_RegistrosConfiguracion.as_view(), name='registros-configuracion'),
#hola



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

        path('valoresvariables_estado/put/<str:pk>/', viwes.Actualizar_Estado_ValoresVariables.as_view(), name='registros-valoresvariables'),

            #funcion para calcular los dias de el mes
        path('calculadoradiasmeses/', viwes.CalculadoraDiasMeses.as_view(), name='registros-calculadora-dias-meses'),
        
        path('administracionpersonal/', viwes.Vista_AdministraciondePersonal.as_view(), name='administracion-de-personal'),
        path('administracionpersonal/put/<str:pk>/', viwes.Actualizar_AdministraciondePersonal.as_view(), name='administracion-de-personal-update'),
        path('administracionpersonal/post/', viwes.Crear_AdministraciondePersonal.as_view(), name='administracion-de-personal'),
        path('administracionpersonal/delete/<str:pk>/', viwes.Eliminar_AdministraciondePersonal.as_view(), name='administracion-de-personal-delete'),
        path('administracionpersonal/get/', viwes.BusquedaAvanzadaPersonalProfesional.as_view(), name='administracion-de-personal-year-formulario'),
 
        path('configuracioninterres/get/<int:year>/', viwes.Vista_ConfigaraicionInteres.as_view(), name='administracion-de-personal-year-formulario'),
        path('configuracioninterres/post/', viwes.Crear_ConfigaraicionInteres.as_view(), name='administracion-de-personal'),
        path('configuracioninterres/put/<str:pk>/', viwes.Actualizar_ConfigaraicionInteres.as_view(), name='administracion-de-personal-update'),
        path('configuracioninterres/delete/<str:pk>/', viwes.Borrar_ConfigaraicionInteres.as_view(), name='administracion-de-personal-delete'),


        path('indicadores/<int:year>/<int:formulario>/', viwes.Vista_IndicadoresSemestral.as_view(), name='configuracion-interes'),
        path('indicadores/put/<str:pk>/', viwes.Actualizar_IndicadoresSemestral.as_view(), name='configuracion-interes-update'),
        path('indicadores/delete/<str:pk>/', viwes.Borrar_IndicadoresSemestral.as_view(), name='configuracion-interes'),
        path('indicadores/post/', viwes.CrearIndicadoresSemestral.as_view(), name='configuracion-interes'),


        path('frecuencia-choices/', viwes.FrecuenciaMedicionListView.as_view(), name='frecuencia_choices'),
        path('tipo-cobro-choices/', viwes.MONTH_CHOICESListVieas.as_view(), name='tipo_cobro_choices'),


        path('formularios_indicadores/',viwes.Vista_Formulario.as_view(), name='formularios_indicadores'),
        path('formularios_indicadores/post/', viwes.Crear_Formulario_Serializer.as_view(), name='formularios_indicadores'),
        path('formularios_indicadores/delete/<str:pk>/', viwes.Borrar_Formulario.as_view(), name='formularios_indicadores'),



        path('cronjop/', viwes.ProbarCronJop.as_view(), name='ProbarCronJop'),

        path('sueldo_minimo/post/',viwes.Crear_ModeloBase_Sueldo_Minimo.as_view(), name='sueldo_minimo'),
        path('sueldo_minimo/get/',viwes.Vista_ModeloBase_Sueldo_Minimo.as_view(),name='sueldo_minimo'),
        path('sueldo_minimo/put/<str:pk>/', viwes.UpDate_ModeloBase_Sueldo_Minimo.as_view(), name='sueldo_minimo'),
        path('sueldo_minimo/delete/<str:pk>/', viwes.Borrar_ModeloBase_Sueldo_Minimo.as_view(), name='sueldo_minimo'),
     
    ]

