from django.urls import path
from conservacion.views import analitica_views as views

urlpatterns = [
    # Tablero de Control
    path('tablero-control/get/', views.TableroControlGetView.as_view(), name='tablero-control-get'),
    path('busqueda-bienes-mezclas/get/', views.BienesMezclasFilterGetView.as_view(), name='busqueda-bienes-mezclas'),
    path('historico-movimientos/get/', views.HistoricoMovimientosGetView.as_view(), name='historico-movimientos'),
    
    # Reportes
    path('busqueda-bienes-inventario/get/', views.BienesInventarioFilterGetView.as_view(), name='busqueda-bienes-mezclas'),
    path('reporte-mortalidad/get/', views.ReporteMortalidadGetView.as_view(), name='reporte-mortalidad-get'),
    path('reporte-solicitudes-despachos/get/', views.ReporteSolicitudesDespachosGetView.as_view(), name='reporte-solicitudes-despachos-get'),
    path('reporte-estado-actividad/get/', views.ReporteEstadoActividadGetView.as_view(), name='reporte-estado-actividad-get'),
    path('reporte-actividad-lote/get/', views.ReporteActividadLoteGetView.as_view(), name='reporte-actividad-lote-get'),
    
    # Historicos de Movimientos por Modulo
    path('historico-bajas/get/', views.HistoricoBajasGetView.as_view(), name='historico-bajas-get'),
    path('historico-distribuciones/get/', views.HistoricoDistribucionesGetView.as_view(), name='historico-distribuciones-get'),
    path('historico-siembras/get/', views.HistoricoSiembrasGetView.as_view(), name='historico-siembras-get'),
    path('historico-cambios-etapa/get/', views.HistoricoCambiosEtapaGetView.as_view(), name='historico-cambios-etapa-get'),
    path('historico-ingreso-cuarentena/get/', views.HistoricoIngresoCuarentenaGetView.as_view(), name='historico-ingreso-cuarentena-get'),
    path('historico-levantamiento-cuarentena/get/', views.HistoricoLevantamientoCuarentenaGetView.as_view(), name='historico-levantamiento-cuarentena-get'),
    path('historico-traslados/get/', views.HistoricoTrasladosGetView.as_view(), name='historico-traslados-get'),
    
    # Analitica
    path('analitica-mortalidad-tiempo/get/', views.AnaliticaMortalidadTiempoGetView.as_view(), name='analitica-mortalidad-tiempo-get'),
    path('analitica-bajas-tiempo/get/', views.AnaliticaBajasTiempoGetView.as_view(), name='analitica-bajas-tiempo-get'),
    path('analitica-cuarentena-tiempo/get/', views.AnaliticaCuarentenaGetView.as_view(), name='analitica-cuarentena-tiempo-get'),
]