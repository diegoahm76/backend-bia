from django.urls import path
from seguimiento_planes.views import pgar_views as views

urlpatterns=[
    # Planes de Gestión Ambiental Regional
    path('consultar-planes-gestion-ambiental-regional/',views.PlanGestionAmbientalRegionalList.as_view(),name='consultarplanesgestionambientalregional'),
    path('crear-plan-gestion-ambiental-regional/',views.PlanGestionAmbientalRegionalCreate.as_view(),name='crearplangestionambientalregional'),
    path('editar-plan-gestion-ambiental-regional/<int:pk>/',views.PlanGestionAmbientalRegionalUpdate.as_view(),name='editarplangestionambientalregional'),
    path('eliminar-plan-gestion-ambiental-regional/<int:pk>/',views.PlanGestionAmbientalRegionalDelete.as_view(),name='eliminarplangestionambientalregional'),
    path('detalle-plan-gestion-ambiental-regional/<int:pk>/',views.PlanGestionAmbientalRegionalId.as_view(),name='detalleplangestionambientalregional'),
    # Objetivo
    path('consultar-objetivos/',views.ObjetivoList.as_view(),name='consultarobjetivos'),
    path('crear-objetivo/',views.ObjetivoCreate.as_view(),name='crearobjetivo'),
    path('editar-objetivo/<int:pk>/',views.ObjetivoUpdate.as_view(),name='editarobjetivo'),
    path('eliminar-objetivo/<int:pk>/',views.ObjetivoDelete.as_view(),name='eliminarobjetivo'),
    path('detalle-objetivo/<int:pk>/',views.ObjetivoId.as_view(),name='detalleobjetivo'),
    # Linea Estrategica
    path('consultar-lineas-estrategicas/',views.LineaEstrategicaList.as_view(),name='consultarlineasestrategicas'),
    path('crear-linea-estrategica/',views.LineaEstrategicaCreate.as_view(),name='crearlineaestrategica'),
    path('editar-linea-estrategica/<int:pk>/',views.LineaEstrategicaUpdate.as_view(),name='editarlineaestrategica'),
    path('eliminar-linea-estrategica/<int:pk>/',views.LineaEstrategicaDelete.as_view(),name='eliminarlineaestrategica'),
    path('detalle-linea-estrategica/<int:pk>/',views.LineaEstrategicaId.as_view(),name='detallelineaestrategica'),
    # Meta Estrategica
    path('consultar-metas-estrategicas/',views.MetaEstrategicaList.as_view(),name='consultarmetasestrategicas'),
    path('crear-meta-estrategica/',views.MetaEstrategicaCreate.as_view(),name='crearmetaestrategica'),
    path('editar-meta-estrategica/<int:pk>/',views.MetaEstrategicaUpdate.as_view(),name='editarmetaestrategica'),
    path('eliminar-meta-estrategica/<int:pk>/',views.MetaEstrategicaDelete.as_view(),name='eliminarmetaestrategica'),
    path('detalle-meta-estrategica/<int:pk>/',views.MetaEstrategicaId.as_view(),name='detallemetaestrategica'),
    # Entidades
    path('consultar-entidades/',views.EntidadesList.as_view(),name='consultarentidades'),
    path('crear-entidad/',views.EntidadesCreate.as_view(),name='crearentidad'),
    path('editar-entidad/<int:pk>/',views.EntidadesUpdate.as_view(),name='editarentidad'),
    path('eliminar-entidad/<int:pk>/',views.EntidadesDelete.as_view(),name='eliminarentidad'),
    path('detalle-entidad/<int:pk>/',views.EntidadesId.as_view(),name='detalleentidad'),
    # PgarIndicador
    path('consultar-pgar-indicadores/',views.PgarIndicadorList.as_view(),name='consultarpgarindicadores'),
    path('crear-pgar-indicador/',views.PgarIndicadorCreate.as_view(),name='crearpgarindicador'),
    path('editar-pgar-indicador/<int:pk>/',views.PgarIndicadorUpdate.as_view(),name='editarpgarindicador'),
    path('eliminar-pgar-indicador/<int:pk>/',views.PgarIndicadorDelete.as_view(),name='eliminarpgarindicador'),
    path('detalle-pgar-indicador/<int:pk>/',views.PgarIndicadorId.as_view(),name='detallepgarindicador'),
    # Actividad
    path('consultar-actividades/',views.ActividadList.as_view(),name='consultaractividades'),
    path('crear-actividad/',views.ActividadCreate.as_view(),name='crearactividad'),
    path('editar-actividad/<int:pk>/',views.ActividadUpdate.as_view(),name='editaractividad'),
    path('eliminar-actividad/<int:pk>/',views.ActividadDelete.as_view(),name='eliminaractividad'),
    path('detalle-actividad/<int:pk>/',views.ActividadId.as_view(),name='detalleactividad'),
]
    

