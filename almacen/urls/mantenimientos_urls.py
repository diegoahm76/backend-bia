from django.urls import path
from almacen.views import mantenimientos_views as views

urlpatterns = [
    #Mantenimientos Programados
    path('programados/get-by-id/<str:pk>/',views.GetMantenimientosProgramadosById.as_view(),name='mantenimientos-programados-id-get'),
    path('programados/get-list/<str:id_articulo>/',views.GetMantenimientosProgramadosList.as_view(),name='mantenimientos-programados-get'),
    path('programados/get-five-list/<str:id_articulo>/',views.GetMantenimientosProgramadosFiveList.as_view(),name='mantenimientos-programados-five-get'),
    path('programados/anular/<str:id_programacion_mtto>/',views.AnularMantenimientoProgramado.as_view(),name='mantenimientos-programados-anular'),
    path('programados/get-by-fechas/',views.GetMantenimientosProgramadosByFechas.as_view(),name='mantenimientos-programados-fechas-get'),

    #Mantenimientos Ejecutados
    path('ejecutados/get-list/<str:id_articulo>/',views.GetMantenimientosEjecutadosList.as_view(),name='mantenimientos-ejecutados-get'),
    path('ejecutados/get-five-list/<str:id_articulo>/',views.GetMantenimientosEjecutadosFiveList.as_view(),name='mantenimientos-ejecutados-five-get'),
    path('ejecutados/get-by-id/<str:pk>/',views.GetMantenimientosEjecutadosById.as_view(),name='mantenimientos-ejecutados-id-get'),
]