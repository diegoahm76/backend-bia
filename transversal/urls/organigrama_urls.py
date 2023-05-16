from django.urls import path
from transversal.views import organigrama_views as views

urlpatterns = [
    #ORGANIGRAMA
    path('create/', views.CreateOrgChart.as_view(),name="crear-organigrama"),
    path('get/', views.GetOrganigrama.as_view(), name='get-organigrama'),
    path('get-terminados/', views.GetOrganigramasTerminados.as_view(), name='get-terminados-organigrama'),
    path('update/<str:id_organigrama>/', views.UpdateOrganigrama.as_view(), name='update-organigrama'),
    path('finalizar/<str:pk>/', views.FinalizarOrganigrama.as_view(), name='finalizar-organigrama'),
    path('get-nuevo-user-organigrama/<str:tipo_documento>/<str:numero_documento>/', views.GetNuevoUserOrganigrama.as_view(), name='get-nuevo-user-orgranigrama'),
    path('get-nuevo-user-organigrama-filters/',views.GetNuevoUserOrganigramaFilters.as_view(),name='get-nuevo-user-orgranigrama-filters'),
    path('delegate-organigrama-persona/',views.AsignarOrganigramaUser.as_view(),name='delegar-organigrama-persona'),
    path('reanudar-organigrama/<str:id_organigrama>/',views.ReanudarOrganigrama.as_view(),name='reanudar-organigrama'),
    
    # UNIDADES ORGANIZACIONALES
    path('unidades/update/<str:pk>/',views.UpdateUnidades.as_view(),name='unidades-org-update'),
    path('unidades/get-list/', views.GetUnidades.as_view(), name='unidades-get-list'),
    path('unidades/get-by-organigrama/<str:id_organigrama>/', views.GetUnidadesByOrganigrama.as_view(), name='unidades-get-by-organigrama'),
    path('unidades/get-sec-sub/<str:id_organigrama>/', views.GetSeccionSubsecciones.as_view(), name='unidades-get-sec-sub'),
    path('unidades/get-list/organigrama-actual/', views.GetUnidadesOrganigramaActual.as_view(), name='unidades-get-organigrama-actual'),
    path('unidades/get-list/organigrama-retirado-reciente/', views.GetUnidadesOrganigramaRetiradoReciente.as_view(), name='unidades-get-organigrama-retirado-reciente'),
    path('unidades/get-jerarquia/<str:id_organigrama>/', views.GetUnidadesJerarquizadas.as_view(), name='unidades-jerarquizadas'),

    # NIVELES
    path('niveles/get-list/', views.GetNiveles.as_view(), name='get-list-niveles'),
    path('niveles/get-by-organigrama/<str:id_organigrama>/', views.GetNivelesByOrganigrama.as_view(), name='get-by-organigrama-niveles'),
    path('niveles/update/<str:id_organigrama>/', views.UpdateNiveles.as_view(), name='update-niveles'),

    # ACTIVACION ORGANIGRAMA
    path('get-ccd-terminados-by-org/<str:id_organigrama>/', views.GetCCDTerminadoByORG.as_view(), name='ccd-terminados-get-by-org'),
    path('get-organigrama-actual/', views.ObtenerOrganigramaActual.as_view(), name='get-organigrama-actual'),
    path('change-actual-organigrama/<str:id_organigrama>/', views.CambioDeOrganigramaActual.as_view(), name='change-actual-organigrama'),
    path('update-unidad-organizacional-actual/<str:id_unidad_organizacional_actual>/', views.ActualizacionUnidadOrganizativaAntigua.as_view(), name='update-unidad'),
    path('get-unidad-organizacional-desactualizada/', views.GetUnidadOrgDesactualizada.as_view(), name='get-unidad'),
]