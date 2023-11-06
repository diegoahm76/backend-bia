from django.urls import path
from seguimiento_planes.views import pnd_views as views

urlpatterns=[
    # Planes Nacionales de Desarrollo
    path('consultar-planes-nacionales-desarrollo/',views.ConsultarPlanNacionalDesarrollo.as_view(),name='consultarplanesnacionalesdesarrollo'),
    path('crear-planes-nacionales-desarrollo/',views.CrearPlanNacionalDesarrollo.as_view(),name='crearplanesnacionalesdesarrollo'),
    path('actualizar-planes-nacionales-desarrollo/<str:pk>/',views.ActualizarPlanNacionalDesarrollo.as_view(),name='actualizarplanesnacionalesdesarrollo'),
    path('eliminar-planes-nacionales-desarrollo/<str:pk>/',views.EliminarPlanNacionalDesarrollo.as_view(),name='eliminarplanesnacionalesdesarrollo'),
    path('consultar-planes-nacionales-desarrollo-id/<str:pk>/',views.ConsultarPlanNacionalDesarrolloId.as_view(),name='consultarplanesnacionalesdesarrolloid'),
    path('busqueda-avanzada-plan-nacional-desarrollo/', views.BusquedaAvanzadaPlanNacionalDesarrollo.as_view(), name='busquedaavanzadaplnacionaldesarrollo'),
    # Sectores
    path('consultar-sectores/',views.ConsultarSector.as_view(),name='consultarsectores'),
    path('crear-sectores/',views.CrearSector.as_view(),name='crearsectores'),
    path('actualizar-sectores/<str:pk>/',views.ActualizarSector.as_view(),name='actualizarsectores'),
    path('eliminar-sectores/<str:pk>/',views.EliminarSector.as_view(),name='eliminarsectores'),
    path('consultar-sectores-id/<str:pk>/',views.ConsultarSectorId.as_view(),name='consultarsectoresid'),
    path('consultar-sectores-pnd-id/<str:pk>/',views.ConsultarSectorPlanId.as_view(),name='consultarsectorespndid'),
    # Programas
    path('consultar-programas/',views.ConsultarPrograma.as_view(),name='consultarprogramas'),
    path('crear-programas/',views.CrearPrograma.as_view(),name='crearprogramas'),
    path('actualizar-programas/<str:pk>/',views.ActualizarPrograma.as_view(),name='actualizarprogramas'),
    path('eliminar-programas/<str:pk>/',views.EliminarPrograma.as_view(),name='eliminarprogramas'),
    path('consultar-programas-id/<str:pk>/',views.ConsultarProgramaId.as_view(),name='consultarprogramasid'),
    path('consultar-programas-sector-id/<str:pk>/',views.ConsultarProgramaSectorId.as_view(),name='consultarprogramassectorid'),
    # Productos
    path('consultar-productos/',views.ConsultarProducto.as_view(),name='consultarproductos'),
    path('crear-productos/',views.CrearProducto.as_view(),name='crearproductos'),
    path('actualizar-productos/<str:pk>/',views.ActualizarProducto.as_view(),name='actualizarproductos'),
    path('eliminar-productos/<str:pk>/',views.EliminarProducto.as_view(),name='eliminarproductos'),
    path('consultar-productos-id/<str:pk>/',views.ConsultarProductoId.as_view(),name='consultarproductosid'),
    path('consultar-productos-programa-id/<str:pk>/',views.ConsultarProductoProgramaId.as_view(),name='consultarproductosprogramaid'),
    # Indicadores
    path('consultar-indicadores/',views.ConsultarIndicador.as_view(),name='consultarindicadores'),
    path('crear-indicadores/',views.CrearIndicador.as_view(),name='crearindicadores'),
    path('actualizar-indicadores/<str:pk>/',views.ActualizarIndicador.as_view(),name='actualizarindicadores'),
    path('eliminar-indicadores/<str:pk>/',views.EliminarIndicador.as_view(),name='eliminarindicadores'),
    path('consultar-indicadores-id/<str:pk>/',views.ConsultarIndicadorId.as_view(),name='consultarindicadoresid'),
    path('consultar-indicadores-producto-id/<str:pk>/',views.ConsultarIndicadorProductoId.as_view(),name='consultarindicadoresproductoid'),
]
