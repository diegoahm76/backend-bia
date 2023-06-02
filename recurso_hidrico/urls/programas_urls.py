from django.urls import path
from recurso_hidrico.views import programas_views as views

urlpatterns = [
    path('programa/recurso/hidrico/create/',views.RegistroProgramaPORH.as_view(),name='programa-recurso-hidrico-create'),
    path('get/programas/<str:pk>/',views.GetProgramasporPORH.as_view(),name='get-programas'),
    path('get/proyectos/por/programas/<str:pk>/',views.GetProyectosporProgramas.as_view(),name='get-proyectos-por-programas'),
    path('get/actividades/por/proyectos/<str:pk>/',views.GetActividadesporProyectos.as_view(),name='get-actividades-por-proyectos'),
    path('get/avanzada/programas/',views.BusquedaAvanzada.as_view(),name='get-avanzada-programas'),
    path('actualizar/programa/<str:pk>/',views.ActualizarPrograma.as_view(),name='actualizar-programa'),
    path('eliminar/programa/<str:pk>/',views.EliminarPrograma.as_view(),name='eliminar-programa'),
    path('actualizar/proyecto/<str:pk>/',views.ActualizarProyectos.as_view(),name='actualizar-proyecto'),
    path('eliminar/proyecto/<str:pk>/',views.EliminarProyecto.as_view(),name='eliminar-proyecto'),
    path('actualizar/actividad/<str:pk>/',views.ActualizarActividades.as_view(),name='actualizar-actividades'),
    path('eliminar/actividad/<str:pk>/',views.EliminarActividades.as_view(),name='eliminar-actividad'),
    path('registro/avance/proyecto/',views.RegistroAvance.as_view(),name='registro-avance-proyecto'),
    path('get/avanzada/avances/',views.BusquedaAvanzadaAvances.as_view(),name='get-avanzada-avances'),
    path('registro/avance/proyecto/<str:id_proyecto>/',views.RegistroAvance.as_view(),name='registro-avance-proyecto'),
    path('crear/evidencia/avance/proyecto/<str:id_evidencia>/',views.RegistroEvidencia.as_view(),name='crear-evidencia-avance-proyecto'),
    path('actualizar/evidencia/avance/proyecto/<str:pk>/',views.ActualizarAvanceEvidencia.as_view(),name='crear-evidencia-avance-proyecto'),

]
