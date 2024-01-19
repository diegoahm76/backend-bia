from django.urls import path
from gestion_documental.views import pqr_views as views


urlpatterns = [

    path('tipos_pqr/get/<str:pk>/', views.TiposPQRGet.as_view(), name='get-tipos-radicado'),
    path('tipos_pqr/update/<str:pk>/', views.TiposPQRUpdate.as_view(), name='update-tipos-radicado'),
    path('get_pqrsdf/<str:id_persona_titular>/', views.GetPQRSDFForStatus.as_view(), name='get-pqrsdf'),
    path('get_pqrsdf-panel/<int:id_PQRSDF>/', views.GetPQRSDFForPanel.as_view(), name='get_pqrsdf-panel'),
    path('crear-pqrsdf/', views.PQRSDFCreate.as_view(), name='crear-pqrsdf'),
    path('update-pqrsdf/', views.PQRSDFUpdate.as_view(), name='update-pqrsdf'),
    path('delete-pqrsdf/', views.PQRSDFDelete.as_view(), name='delete-pqrsdf'),
    path('radicar-pqrsdf/', views.RadicarPQRSDF.as_view(), name='radicar-pqrsdf'),

    
    #Medios_Solicitud
    path('tipos_pqr/crear-medio-solicitud/',views.MediosSolicitudCreate.as_view(), name='crear-medio-solicitud'),
    path('tipos_pqr/buscar-medio-solicitud/',views.MediosSolicitudSearch.as_view(), name='buscar-medio-solicitud'),
    path('tipos_pqr/eliminar-medio-solicitud/<int:id_medio_solicitud>/',views.MediosSolicitudDelete.as_view(), name='eliminar-medio-solicitud'),
    path('tipos_pqr/actualizar-medio-solicitud/<int:id_medio_solicitud>/',views.MediosSolicitudUpdate.as_view(), name='actualizar-medio-solicitud'),

    #Respuesta_Solicitud_PQRSDF_104
    path('crear-respuesta-pqrsdf/', views.RespuestaPQRSDFCreate.as_view(), name='crear-respuesta-pqrsdf'),
    path('get_respuesta_pqrsdf-panel/<int:id_pqrsdf>/', views.GetRespuestaPQRSDFForPanel.as_view(), name='get_respuesta_pqrsdf-panel'),

    #Reportes_PQRSDF_109
    path('busqueda-avanzada-reportes/', views.ReportesPQRSDFSearch.as_view(), name='buscar-reportes-pqrsdf'),
    path('get-estado-solicitud/', views.EstadosSolicitudesList.as_view(), name='listar-estados-solicitud'),

    #Consulta_Estado_Solicitud_PQRSDF_111
    path('consulta-estado-pqrsdf/', views.ConsultaEstadoPQRSDF.as_view(), name='listar-estados-solicitud'),

    #Consulta_Estado_Solicitud_PQRSDF_114
    path('consulta-estado-pqrsdf/', views.ConsultaEstadoPQRSDF.as_view(), name='listar-estados-solicitud'),
    path('listar_informacion_arbol/<int:id_PQRSDF>/', views.ListarInformacionArbolWorkflow.as_view(), name='listar-workflow-solicitud'),
    
    #Indicadores_PQRSDF_115
     path('indicadores/indicador-periocidad/', views.IndicadorPeriocidad.as_view(), name='indicador-pqrsdf-periocidad'),
     path('indicadores/indicador-atencion-pqrsdf/', views.IndicadorAtencionPQRSDF.as_view(), name='indicador-atencion-pqrsdf'),
     path('indicadores/indicador-derechos-peticion/', views.IndicadorAtencionDerechosPetecion.as_view(), name='indicador-atencion-derechos-peticion'),
     path('indicadores/indicador-quejas/', views.IndicadorAtencionQuejas.as_view(), name='indicador-atencion-quejas'),
     path('indicadores/indicador-reclamos/', views.IndicadorAtencionReclamos.as_view(), name='indicador-atencion-reclamos'),
     path('indicadores/indicador-sugerencias/', views.IndicadorSugerenciasRadicadas.as_view(), name='indicador-atencion-sugerencias'),
     path('indicadores/indicador-pqrsdf-contestadas-oportunamente/', views.IndicadorPQRSDFContestadosOportunamente.as_view(), name='indicador-pqrsdf-contestadas-oportunamente'),
     path('indicadores/indicador-peticiones-contestadas-oportunamente/', views.IndicadorPeticionesContestadasOportunamente.as_view(), name='indicador-peticiones-contestadas-oportunamente'),
     path('indicadores/indicador-quejas-contestadas-oportunamente/', views.IndicadorQuejasContestadasOportunamente.as_view(), name='indicador-quejas-contestadas-oportunamente'),
     path('indicadores/indicador-reclamos-contestadas-oportunamente/', views.IndicadorReclamosContestadosOportunamente.as_view(), name='indicador-reclamos-contestadas-oportunamente'),
     path('indicadores/indicador-denuncias-contestadas-oportunamente/', views.IndicadorDenunciasContestadasOportunamente.as_view(), name='indicador-denuncias-contestadas-oportunamente'),
     path('indicadores/indicador-pqrsdf-vencidas/', views.IndicadorVencimientoPQRSDF.as_view(), name='indicador-pqrsdf-vencidas'),

]