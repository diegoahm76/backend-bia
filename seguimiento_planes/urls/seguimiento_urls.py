from django.urls import path
from seguimiento_planes.views import seguimiento_views as views

urlpatterns=[
    # Fuentes de financiacion indicadores
    path('consultar-fuentes-financiacion-indicadores/',views.FuenteFinanciacionIndicadoresList.as_view(),name='consultarfuentesfinanciacionindicadores'),
    path('crear-fuentes-financiacion-indicadores/',views.FuenteFinanciacionIndicadoresCreate.as_view(),name='crearfuentesfinanciacionindicadores'),
    path('actualizar-fuentes-financiacion-indicadores/<str:pk>/',views.FuenteFinanciacionIndicadoresUpdate.as_view(),name='actualizarfuentesfinanciacionindicadores'),
    path('eliminar-fuentes-financiacion-indicadores/<str:pk>/',views.FuenteFinanciacionIndicadoresDelete.as_view(),name='eliminarfuentesfinanciacionindicadores'),
    # Listar todos los registros de fuentes de financiacion indicadores por id_indicador
    path('consultar-fuentes-financiacion-indicadores-id-indicador/<str:pk>/', views.FuenteFinanciacionIndicadoresPorIndicadorList.as_view(),name='consultaridindicadorfuentesfinanciacionindicadores'),
    # Listar todos los registros de fuentes de financiacion indicadores por id_meta
    path('consultar-fuentes-financiacion-indicadores-id-meta/<str:pk>/', views.FuenteFinanciacionIndicadoresPorMetaList.as_view(),name='consultaridmetafuentesfinanciacionindicadores'),
    # Busqueda avanzada de fuentes de financiacion indicadores por nombre fuente, nombre proyecto, nombre producto, nombre actividad, nombre indicador
    path('consultar-fuentes-financiacion-indicadores-avanzado/',views.BusquedaAvanzadaFuentesFinanciacionIndicadores.as_view(),name='consultarfuentesfinanciacionindicadoresavanzado'),
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
    # Busqueda avanzada de detalle de inversión cuentas por cuenta, nombre programa, nombre subprograma, nombre proyecto, nombre actividad, nombre indicador
    path('consultar-detalle-inversion-cuentas-avanzado/',views.BusquedaAvanzadaDetalleInversionCuentas.as_view(),name='consultardetalleinversioncuentasavanzado'),
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
    # Conceptos POAI
    path('consultar-conceptos-poai/',views.ConceptoPOAIList.as_view(),name='consultarconceptospoai'),
    path('crear-conceptos-poai/',views.ConceptoPOAICreate.as_view(),name='crearconceptospoai'),
    path('actualizar-conceptos-poai/<str:pk>/',views.ConceptoPOAIUpdate.as_view(),name='actualizarconceptospoai'),
    path('eliminar-conceptos-poai/<str:pk>/',views.ConceptoPOAIDelete.as_view(),name='eliminarconceptospoai'),
    # busqueda avanzada de conceptos POAI por concepto, nombre y nombre indicador
    path('consultar-conceptos-poai-avanzado/',views.BusquedaAvanzadaConceptoPOAI.as_view(),name='consultarconceptospoaiavanzado'),
    # Fuente de financiacion
    path('consultar-fuentes-financiacion/',views.FuenteFinanciacionList.as_view(),name='consultarfuentesfinanciacion'),
    path('crear-fuentes-financiacion/',views.FuenteFinanciacionCreate.as_view(),name='crearfuentesfinanciacion'),
    path('actualizar-fuentes-financiacion/<str:pk>/',views.FuenteFinanciacionUpdate.as_view(),name='actualizarfuentesfinanciacion'),
    path('eliminar-fuentes-financiacion/<str:pk>/',views.FuenteFinanciacionDelete.as_view(),name='eliminarfuentesfinanciacion'),
    #Busqueda Avanzada de fuentes de financiación por nombre_fuente, concepto
    path('consultar-fuentes-financiacion-avanzado/',views.BusquedaAvanzadaFuenteFinanciacion.as_view(),name='consultarfuentesfinanciacionavanzado'),
    # Banco de proyectos
    path('consultar-banco-proyectos/',views.BancoProyectoList.as_view(),name='consultarbanco_proyectos'),
    path('crear-banco-proyectos/',views.BancoProyectoCreate.as_view(),name='crearbanco_proyectos'),
    path('actualizar-banco-proyectos/<str:pk>/',views.BancoProyectoUpdate.as_view(),name='actualizarbanco_proyectos'),
    path('eliminar-banco-proyectos/<str:pk>/',views.BancoProyectoDelete.as_view(),name='eliminarbanco_proyectos'),
    # Busqueda avanzada banco proyecto por objeto_contrato, nombre_proyecto, nombre_actividad, nombre_indicador y nombre_meta
    path('consultar-banco-proyectos-avanzado/',views.BusquedaAvanzadaBancoProyecto.as_view(),name='consultarbanco_proyectosavanzado'),
    # Plan anual de adquisiciones
    path('consultar-plan-anual-adquisiciones/',views.PlanAnualAdquisicionesList.as_view(),name='consultarplan_anual_adquisiciones'),
    path('crear-plan-anual-adquisiciones/',views.PlanAnualAdquisicionesCreate.as_view(),name='crearplan_anual_adquisiciones'),
    path('actualizar-plan-anual-adquisiciones/<str:pk>/',views.PlanAnualAdquisicionesUpdate.as_view(),name='actualizarplan_anual_adquisiciones'),
    path('eliminar-plan-anual-adquisiciones/<str:pk>/',views.PlanAnualAdquisicionesDelete.as_view(),name='eliminarplan_anual_adquisiciones'),
    # Busqueda avanzada de planes anuales de adquisiciones por descripcion, nombre_plan, nombre_modalidad, nombre_fuente, nombre_unidad
    path('consultar-plan-anual-adquisiciones-avanzado/',views.BusquedaAvanzadaPlanAnualAdquisiciones.as_view(),name='consultarplan_anual_adquisicionesavanzado'),
    # PAA Codigos UNSP
    path('consultar-paa-codigos-unsp/',views.PAACodUNSPList.as_view(),name='consultarpaacodigosunsp'),
    path('crear-paa-codigos-unsp/',views.PAACodUNSPCreate.as_view(),name='crearpaacodigosunsp'),
    path('actualizar-paa-codigos-unsp/<str:pk>/',views.PAACodUNSPUpdate.as_view(),name='actualizarpaacodigosunsp'),
    path('eliminar-paa-codigos-unsp/<str:pk>/',views.PAACodUNSPDelete.as_view(),name='eliminarpaacodigosunsp'),
    path('consultar-paa-codigos-unsp-id-paa/<str:pk>/', views.PAACodUNSPListIdPAA.as_view(),name='consultaridpaacodigosunsp'),
    # Seguimineto PAI
    path('consultar-seguimiento-pai/',views.SeguimientoPAIList.as_view(),name='consultarseguimientopai'),
    path('crear-seguimiento-pai/',views.SeguimientoPAICreate.as_view(),name='crearseguimientopai'),
    path('actualizar-seguimiento-pai/<str:pk>/',views.SeguimientoPAIUpdate.as_view(),name='actualizarseguimientopai'),
    path('eliminar-seguimiento-pai/<str:pk>/',views.SeguimientoPAIDelete.as_view(),name='eliminarseguimientopai'),
    path('consultar-seguimiento-pai-avanzado/',views.BusquedaAvanzadaSeguimientoPAI.as_view(),name='consultarseguimientopaiavanzado'),
    # Listar por periodo de tiempo SeguimientoPAIListPeriodo
    path('consultar-seguimiento-pai-periodo/',views.SeguimientoPAIListPeriodo.as_view(),name='consultarseguimientopaiperiodo'),
    # Busqueda avanzada de seguimiento PAI
    path('consultar-seguimiento-pai-avanzado/',views.BusquedaAvanzadaSeguimientoPAI.as_view(),name='consultarseguimientopaiavanzado'),
    # Seguimiento PAI Documentos
    path('consultar-seguimiento-pai-documentos/',views.SeguimientoPAIDocumentosList.as_view(),name='consultarseguimientopaidocumentos'),
    path('crear-seguimiento-pai-documentos/',views.SeguimientoPAIDocumentosCreate.as_view(),name='crearseguimientopaidocumentos'),
    path('actualizar-seguimiento-pai-documentos/<str:pk>/',views.SeguimientoPAIDocumentosUpdate.as_view(),name='actualizarseguimientopaidocumentos'),
    path('eliminar-seguimiento-pai-documentos/<str:pk>/',views.SeguimientoPAIDocumentosDelete.as_view(),name='eliminarseguimientopaidocumentos'),
    path('consltar-seguimiento-documentos-id-pai/<str:pk>/', views.SeguimientoPAIDocumentosListIdSeguimiento.as_view(),name='consultaridseguimientopai'),
    # Seguimiento POAI
    # path('consultar-seguimiento-poai/',views.SeguimientoPOAIList.as_view(),name='consultarseguimientopoai'),
    # path('crear-seguimiento-poai/',views.SeguimientoPOAICreate.as_view(),name='crearseguimientopoai'),
    # path('actualizar-seguimiento-poai/<str:pk>/',views.SeguimientoPOAIUpdate.as_view(),name='actualizarseguimientopoai'),
    # path('eliminar-seguimiento-poai/<str:pk>/',views.SeguimientoPOAIDelete.as_view(),name='eliminarseguimientopoai'),
    # # Busqueda avanzada de seguimiento POAI por nombre plan, nombre programa, nombre proyecto, nombre producto, nombre actividad, nombre indicador, nombre meta, nombre, concepto, cuenta, objeto_contrato, codigo_modalidad, 
    # path('consultar-seguimiento-poai-avanzado/',views.BusquedaAvanzadaSeguimientoPOAI.as_view(),name='consultarseguimientopoaiavanzado'),
    ]