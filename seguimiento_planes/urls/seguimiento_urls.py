from django.urls import path
from seguimiento_planes.views import seguimiento_views as views

urlpatterns=[
    # Fuentes de financiacion indicadores
    path('consultar-fuentes-financiacion-indicadores/',views.FuenteFinanciacionIndicadoresList.as_view(),name='consultarfuentesfinanciacionindicadores'),
    path('crear-fuentes-financiacion-indicadores/',views.FuenteFinanciacionIndicadoresCreate.as_view(),name='crearfuentesfinanciacionindicadores'),
    path('actualizar-fuentes-financiacion-indicadores/<str:pk>/',views.FuenteFinanciacionIndicadoresUpdate.as_view(),name='actualizarfuentesfinanciacionindicadores'),
    path('eliminar-fuentes-financiacion-indicadores/<str:pk>/',views.FuenteFinanciacionIndicadoresDelete.as_view(),name='eliminarfuentesfinanciacionindicadores'),
    # Sectores
    path('consultar-sectores/',views.SectorList.as_view(),name='consultarsectores'),
    path('crear-sectores/',views.SectorCreate.as_view(),name='crearsectores'),
    path('actualizar-sectores/<str:pk>/',views.SectorUpdate.as_view(),name='actualizarsectores'),
    path('eliminar-sectores/<str:pk>/',views.SectorDelete.as_view(),name='eliminarsectores'),
    # Detalle de inversion cuentas
    path('consultar-detalle-inversion-cuentas/',views.DetalleInversionCuentasList.as_view(),name='consultardetalleinversioncuentas'),
    path('crear-detalle-inversion-cuentas/',views.DetalleInversionCuentasCreate.as_view(),name='creardetalleinversioncuentas'),
    path('actualizar-detalle-inversion-cuentas/<str:pk>/',views.DetalleInversionCuentasUpdate.as_view(),name='actualizardetalleinversioncuentas'),
    path('eliminar-detalle-inversion-cuentas/<str:pk>/',views.DetalleInversionCuentasDelete.as_view(),name='eliminardetalleinversioncuentas'),
    # Modalidades
    path('consultar-modalidades/',views.ModalidadList.as_view(),name='consultarmodalidades'),
    path('crear-modalidades/',views.ModalidadCreate.as_view(),name='crearmodalidades'),
    path('actualizar-modalidades/<str:pk>/',views.ModalidadUpdate.as_view(),name='actualizarmodalidades'),
    path('eliminar-modalidades/<str:pk>/',views.ModalidadDelete.as_view(),name='eliminarmodalidades'),
    # Ubicaciones
    path('consultar-ubicaciones/',views.UbicacionesList.as_view(),name='consultarubicaciones'),
    path('crear-ubicaciones/',views.UbicacionesCreate.as_view(),name='crearubicaciones'),
    path('actualizar-ubicaciones/<str:pk>/',views.UbicacionesUpdate.as_view(),name='actualizarubicaciones'),
    path('eliminar-ubicaciones/<str:pk>/',views.UbicacionesDelete.as_view(),name='eliminarubicaciones'),
    # Fuente de recursos PAA
    path('consultar-fuentes-recursos-paa/',views.FuenteRecursosPaaList.as_view(),name='consultarfuentesrecursospaa'),
    path('crear-fuentes-recursos-paa/',views.FuenteRecursosPaaCreate.as_view(),name='crearfuentesrecursospaa'),
    path('actualizar-fuentes-recursos-paa/<str:pk>/',views.FuenteRecursosPaaUpdate.as_view(),name='actualizarfuentesrecursospaa'),
    path('eliminar-fuentes-recursos-paa/<str:pk>/',views.FuenteRecursosPaaDelete.as_view(),name='eliminarfuentesrecursospaa'),
    # Intervalos
    path('consultar-intervalos/',views.IntervaloList.as_view(),name='consultarintervalos'),
    path('crear-intervalos/',views.IntervaloCreate.as_view(),name='crearintervalos'),
    path('actualizar-intervalos/<str:pk>/',views.IntervaloUpdate.as_view(),name='actualizarintervalos'),
    path('eliminar-intervalos/<str:pk>/',views.IntervaloDelete.as_view(),name='eliminarintervalos'),
    # Estados de la VF
    path('consultar-estados-vf/',views.EstadoVFList.as_view(),name='consultarestadosvf'),
    path('crear-estados-vf/',views.EstadoVFCreate.as_view(),name='crearestadosvf'),
    path('actualizar-estados-vf/<str:pk>/',views.EstadoVFUpdate.as_view(),name='actualizarestadosvf'),
    path('eliminar-estados-vf/<str:pk>/',views.EstadoVFDelete.as_view(),name='eliminarestadosvf'),
    # Codigos UNSP
    path('consultar-codigos-unsp/',views.CodigosUNSPList.as_view(),name='consultarcodigosunsp'),
    path('crear-codigos-unsp/',views.CodigosUNSPCreate.as_view(),name='crearcodigosunsp'),
    path('actualizar-codigos-unsp/<str:pk>/',views.CodigosUNSPUpdate.as_view(),name='actualizarcodigosunsp'),
    path('eliminar-codigos-unsp/<str:pk>/',views.CodigosUNSPDelete.as_view(),name='eliminarcodigosunsp'),
]