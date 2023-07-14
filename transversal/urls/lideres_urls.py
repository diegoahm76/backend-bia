from django.urls import path
from transversal.views import lideres_views as views

urlpatterns = [
    path('busqueda-avanzada-organigramas/', views.BusquedaAvanzadaOrganigramasView.as_view(), name='busqueda-avanzada-organigramas'),
    path('get-list/<str:id_organigrama>/',views.GetListLideresAsignadosView.as_view(),name='get-list-lideres-asignados'),
    path('get-list-filter/',views.BuscarLideresAsignadosFilterView.as_view(),name='get-list-lideres-asignados'),
    path('get-lider-by-documento/',views.GetPersonaLiderByNumeroDocumento.as_view(),name='get-lider-by-documento'),
    path('get-lideres-filter/',views.GetPersonaLiderFiltro.as_view(),name='get-lideres-filter'),
    path('crear-asignacion/',views.CreateAsignacionView.as_view(),name='crear-asignacion'),
    path('actualizar-asignacion/<str:id_lider_unidad_org>/',views.UpdateAsignacionView.as_view(),name='actualizar-asignacion')
]