from django.urls import path
from seguimiento_planes.views import planes_views as views

urlpatterns=[
    # Objetivos de Desarrollo Sostenible
    path('consultar-ods/',views.ObjetivoDesarrolloSostenibleList.as_view(),name='consultarods'),
    path('crear-ods/',views.ObjetivoDesarrolloSostenibleCreate.as_view(),name='crearods'),
    path('actualizar-ods/<str:pk>/',views.ObjetivoDesarrolloSostenibleUpdate.as_view(),name='actualizarods'),
    path('eliminar-ods/<str:pk>/',views.ObjetivoDesarrolloSostenibleDelete.as_view(),name='eliminarods'),
    path('consultar-ods-id/<str:pk>/',views.ObjetivoDesarrolloSostenibleDetail.as_view(),name='consultarodsid'),
    # Planes
    path('consultar-planes/',views.ConsultarPlanes.as_view(),name='consultarplanesnacionalesdesarrollo'),
    path('crear-planes/',views.CrearPlanes.as_view(),name='crearplanesnacionalesdesarrollo'),
    path('actualizar-planes/<str:pk>/',views.ActualizarPlanes.as_view(),name='actualizarplanesnacionalesdesarrollo'),
    path('eliminar-planes/<str:pk>/',views.EliminarPlanes.as_view(),name='eliminarplanesnacionalesdesarrollo'),
    path('consultar-planes-id/<str:pk>/',views.ConsultarPlanesId.as_view(),name='consultarplanesnacionalesdesarrolloid'),
    # Busqueda Avanzada Planes Nacionales de Desarrollo
    path('busqueda-avanzada-planes/', views.BusquedaAvanzadaPlanes.as_view(), name='busquedaavanzadaplnacionaldesarrollo'),

    path('consultar-planes-total/',views.PlanesGetAll.as_view(),name='consultarplanesnacionalesdesarrollo'),
    path('consultar-planes-total-id/<str:pk>/',views.PlanesGetId.as_view(),name='consultarplanetotalid'),
    # Ejes Estratégicos
    path('consultar-ejes-estrategicos/',views.EjeEstractegicoList.as_view(),name='consultarejesestrategicos'),
    path('crear-ejes-estrategicos/',views.EjeEstractegicoCreate.as_view(),name='crearejesestrategicos'),
    path('actualizar-ejes-estrategicos/<str:pk>/',views.EjeEstractegicoUpdate.as_view(),name='actualizarejesestrategicos'),
    path('eliminar-ejes-estrategicos/<str:pk>/',views.EjeEstractegicoDelete.as_view(),name='eliminarejesestrategicos'),
    path('consultar-ejes-estrategicos-id/<str:pk>/',views.EjeEstractegicoDetail.as_view(),name='consultarejesestrategicosid'),
    path('consultar-ejes-estrategicos-id-planes/<str:pk>/',views.EjeEstractegicoListIdPlanes.as_view(),name='consultarejesestrategicosidplanes'),
    # Busqueda Avanzada eje por nombre plan, y nombre
    path('busqueda-avanzada-ejes/', views.BusquedaAvanzadaEjes.as_view(), name='busquedaavanzadaejes'),    
    # Objetivos
    path('consultar-objetivos/',views.ObjetivoList.as_view(),name='consultarobjetivos'),
    path('crear-objetivos/',views.ObjetivoCreate.as_view(),name='crearobjetivos'),
    path('actualizar-objetivos/<str:pk>/',views.ObjetivoUpdate.as_view(),name='actualizarobjetivos'),
    path('eliminar-objetivos/<str:pk>/',views.ObjetivoDelete.as_view(),name='eliminarobjetivos'),
    path('consultar-objetivos-id/<str:pk>/',views.ObjetivoDetail.as_view(),name='consultarobjetivosid'),
    path('consultar-objetivos-id-planes/<str:pk>/',views.ObjetivoListIdPlanes.as_view(),name='consultarobjetivosidplanes'),
    # Busqueda Avanzada objetivo por nombre plan y nombre_objetivo
    path('busqueda-avanzada-objetivos/', views.BusquedaAvanzadaObjetivos.as_view(), name='busquedaavanzadaobjetivos'),
    # Programas
    path('consultar-programas/',views.ProgramaList.as_view(),name='consultarprogramas'),
    path('crear-programas/',views.ProgramaCreate.as_view(),name='crearprogramas'),
    path('actualizar-programas/<str:pk>/',views.ProgramaUpdate.as_view(),name='actualizarprogramas'),
    path('eliminar-programas/<str:pk>/',views.ProgramaDelete.as_view(),name='eliminarprogramas'),
    path('consultar-programas-id/<str:pk>/',views.ProgramaDetail.as_view(),name='consultarprogramasid'),
    path('consultar-programas-id-planes/<str:pk>/',views.ProgramaListIdPlanes.as_view(),name='consultarprogramasidplanes'),
    # Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 
    path('consultar-programas-periodo/',views.ProgramaListPeriodoTiempo.as_view(),name='consultarprogramasperiodo'),
    # Busqueda Avanzada Programas por nombre programa y nombre plan
    path('busqueda-avanzada-programas/', views.BusquedaAvanzadaProgramas.as_view(), name='busquedaavanzadaprogramas'),
    # Proyectos
    path('consultar-proyectos/',views.ProyectoList.as_view(),name='consultarproyectos'),
    path('crear-proyectos/',views.ProyectoCreate.as_view(),name='crearproyectos'),
    path('actualizar-proyectos/<str:pk>/',views.ProyectoUpdate.as_view(),name='actualizarproyectos'),
    path('eliminar-proyectos/<str:pk>/',views.ProyectoDelete.as_view(),name='eliminarproyectos'),
    path('consultar-proyectos-id/<str:pk>/',views.ProyectoDetail.as_view(),name='consultarproyectosid'),
    path('consultar-proyectos-id-programas/<str:pk>/',views.ProyectoListIdProgramas.as_view(),name='consultarproyectosidprogramas'),
    # Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 
    path('consultar-proyectos-periodo/',views.ProyectoListPeriodoTiempo.as_view(),name='consultarproyectosperiodo'),
    # Busqueda Avanzada proyectos por nombre plan, nombre programa y nombre proyecto
    path('busqueda-avanzada-proyectos/', views.BusquedaAvanzadaProyectos.as_view(), name='busquedaavanzadaproyectos'),
    # Productos
    path('consultar-productos/',views.ProductosList.as_view(),name='consultarproductos'),
    path('crear-productos/',views.ProductosCreate.as_view(),name='crearproductos'),
    path('actualizar-productos/<str:pk>/',views.ProductosUpdate.as_view(),name='actualizarproductos'),
    path('eliminar-productos/<str:pk>/',views.ProductosDelete.as_view(),name='eliminarproductos'),
    path('consultar-productos-id/<str:pk>/',views.ProductosDetail.as_view(),name='consultarproductosid'),
    path('consultar-productos-id-proyectos/<str:pk>/',views.ProductosListIdProyectos.as_view(),name='consultarproductosidproyectos'),
    # Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 
    path('consultar-productos-periodo/',views.ProductosListPeriodoTiempo.as_view(),name='consultarproductosperiodo'),
    # Busqueda Avanzada Productos por nombre plan, nombre programa, nombre proyecto y nombre producto
    path('busqueda-avanzada-productos/', views.BusquedaAvanzadaProductos.as_view(), name='busquedaavanzadaproductos'),
    # Actividades
    path('consultar-actividades/',views.ActividadList.as_view(),name='consultaractividades'),
    path('crear-actividades/',views.ActividadCreate.as_view(),name='crearactividades'),
    path('actualizar-actividades/<str:pk>/',views.ActividadUpdate.as_view(),name='actualizaractividades'),
    path('eliminar-actividades/<str:pk>/',views.ActividadDelete.as_view(),name='eliminaractividades'),
    path('consultar-actividades-id/<str:pk>/',views.ActividadDetail.as_view(),name='consultaractividadesid'),
    path('consultar-actividades-id-productos/<str:pk>/',views.ActividadListIdProductos.as_view(),name='consultaractividadesidproductos'),
    path('consultar-actividades-id-plan/<str:pk>/',views.ActividadListIdPlanes.as_view(),name='consultaractividadesidplan'),
    # Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan
    path('consultar-actividades-periodo/',views.ActividadListPeriodoTiempo.as_view(),name='consultaractividadesperiodo'),
    # Busqueda Avanzada Actividades por nombre plan, nombre programa, nombre proyecto, nombre producto y nombre actividad
    path('busqueda-avanzada-actividades/', views.BusquedaAvanzadaActividades.as_view(), name='busquedaavanzadaactividades'),
    # Entidades
    path('consultar-entidades/',views.EntidadList.as_view(),name='consultarentidades'),
    path('crear-entidades/',views.EntidadCreate.as_view(),name='crearentidades'),
    path('actualizar-entidades/<str:pk>/',views.EntidadUpdate.as_view(),name='actualizarentidades'),
    path('eliminar-entidades/<str:pk>/',views.EntidadDelete.as_view(),name='eliminarentidades'),
    path('consultar-entidades-id/<str:pk>/',views.EntidadDetail.as_view(),name='consultarentidadesid'),
    # Mediciones
    path('consultar-mediciones/',views.MedicionList.as_view(),name='consultarmediciones'),
    path('crear-mediciones/',views.MedicionCreate.as_view(),name='crearmediciones'),
    path('actualizar-mediciones/<str:pk>/',views.MedicionUpdate.as_view(),name='actualizarmediciones'),
    path('eliminar-mediciones/<str:pk>/',views.MedicionDelete.as_view(),name='eliminarmediciones'),
    path('consultar-mediciones-id/<str:pk>/',views.MedicionDetail.as_view(),name='consultarmedicionesid'),
    # Tipos
    path('consultar-tipos/',views.TipoList.as_view(),name='consultartipos'),
    path('crear-tipos/',views.TipoCreate.as_view(),name='creartipos'),
    path('actualizar-tipos/<str:pk>/',views.TipoUpdate.as_view(),name='actualizartipos'),
    path('eliminar-tipos/<str:pk>/',views.TipoDelete.as_view(),name='eliminartipos'),
    path('consultar-tipos-id/<str:pk>/',views.TipoDetail.as_view(),name='consultartiposid'),
    # Rubros
    path('consultar-rubros/',views.RubroList.as_view(),name='consultarrubros'),
    path('crear-rubros/',views.RubroCreate.as_view(),name='crearrubros'),
    path('actualizar-rubros/<str:pk>/',views.RubroUpdate.as_view(),name='actualizarrubros'),
    path('eliminar-rubros/<str:pk>/',views.RubroDelete.as_view(),name='eliminarrubros'),
    path('consultar-rubros-id/<str:pk>/',views.RubroDetail.as_view(),name='consultarrubrosid'),
    # Indicadores
    path('consultar-indicadores/',views.IndicadorList.as_view(),name='consultarindicadores'),
    path('crear-indicadores/',views.IndicadorCreate.as_view(),name='crearindicadores'),
    path('actualizar-indicadores/<str:pk>/',views.IndicadorUpdate.as_view(),name='actualizarindicadores'),
    path('eliminar-indicadores/<str:pk>/',views.IndicadorDelete.as_view(),name='eliminarindicadores'),
    path('consultar-indicadores-id/<str:pk>/',views.IndicadorDetail.as_view(),name='consultarindicadoresid'),
    path('consultar-indicadores-id-plan/<str:pk>/',views.IndicadorListIdPlanes.as_view(),name='consultarindicadoresidplan'),
    path('consultar-indicadores-id-actividad/<str:pk>/',views.IndicadorListIdActividad.as_view(),name='consultarindicadoresidactividad'),
    path('consultar-indicadores-id-producto/<str:pk>/',views.IndicadorListIdProducto.as_view(),name='consultarindicadoresidproducto'),
    path('consultar-indicadores-id-rubro/<str:pk>/',views.IndicadorListIdRubro.as_view(),name='consultarindicadoresidrubro'),
    # Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 
    path('consultar-indicadores-periodo/',views.IndicadorListPeriodoTiempo.as_view(),name='consultarindicadoresperiodo'),
    # Busqueda Avanzada Actividades por nombre plan, nombre programa, nombre proyecto, nombre producto, nombre actividad y nombre indicador
    path('busqueda-avanzada-indicadores/', views.BusquedaAvanzadaIndicadores.as_view(), name='busquedaavanzadaindicadores'),
    # Metas
    path('consultar-metas/',views.MetaList.as_view(),name='consultarmetas'),
    path('crear-metas/',views.MetaCreate.as_view(),name='crearmetas'),
    path('actualizar-metas/<str:pk>/',views.MetaUpdate.as_view(),name='actualizarmetas'),
    path('eliminar-metas/<str:pk>/',views.MetaDelete.as_view(),name='eliminarmetas'),
    path('consultar-metas-id/<str:pk>/',views.MetaDetail.as_view(),name='consultarmetasid'),
    path('consultar-metas-id-indicador/<str:pk>/',views.MetaListIdIndicador.as_view(),name='consultarmetasidindicador'),
    path('consultar-metas-periodo/',views.MetaListPeriodoTiempo.as_view(),name='consultarmetasperiodo'),
    path('consultar-metas-periodo-indicador/',views.MetaListPeriodoTiempoPorIndicador.as_view(),name='consultarmetasperiodoindicador'),
    # Listar por periodo de tiempo, debe ingresar el usuario fecha_inicial y fecha final e id plan 
    path('consultar-metas-periodo/',views.MetaListPeriodoTiempo.as_view(),name='consultarmetasperiodo'),
    # Busqueda Avanzada Metas por nombre plan, nombre programa, nombre proyecto, nombre producto, nombre actividad, nombre indicador y nombre meta
    path('busqueda-avanzada-metas/', views.BusquedaAvanzadaMetas.as_view(), name='busquedaavanzadametas'),
    
    # Tipos de Ejes 
    path('consultar-tipos-ejes/',views.TipoEjeList.as_view(),name='consultartiposejes'),
    path('crear-tipos-ejes/',views.TipoEjeCreate.as_view(),name='creartiposejes'),
    path('actualizar-tipos-ejes/<str:pk>/',views.TipoEjeUpdate.as_view(),name='actualizartiposejes'),
    path('eliminar-tipos-ejes/<str:pk>/',views.TipoEjeDelete.as_view(),name='eliminartiposejes'),
    path('consultar-tipos-ejes-id/<str:pk>/',views.TipoEjeDetail.as_view(),name='consultartiposejesid'),
    # Subprogramas
    path('consultar-subprogramas/',views.SubprogramaList.as_view(),name='consultarsubprogramas'),
    path('crear-subprogramas/',views.SubprogramaCreate.as_view(),name='crearsubprogramas'),
    path('actualizar-subprogramas/<str:pk>/',views.SubprogramaUpdate.as_view(),name='actualizarsubprogramas'),
    path('eliminar-subprogramas/<str:pk>/',views.SubprogramaDelete.as_view(),name='eliminarsubprogramas'),
    path('consultar-subprogramas-id/<str:pk>/',views.SubprogramaDetail.as_view(),name='consultarsubprogramasid'),
    path('consultar-subprogramas-id-programa/<str:pk>/',views.SubprogramaListIdPrograma.as_view(),name='consultarsubprogramasidprograma'),
]