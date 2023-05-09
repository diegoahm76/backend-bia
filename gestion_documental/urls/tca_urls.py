from django.urls import path
from gestion_documental.views import tca_views as views

urlpatterns = [
    # Tabla de Control de Acceso
    path('tca-list/get/', views.GetListTca.as_view(), name='tca-list-get'),
    path('get-busqueda-tca/',views.BusquedaTCA.as_view(),name='get-tca'),
    path('create/', views.PostTablaControlAcceso.as_view(),name='create-tca'),
    path('update/<str:pk>/', views.UpdateTablaControlAcceso.as_view(), name='update-tca'),
    path('resume/<str:id_tca>/', views.ReanudarTablaControlAcceso.as_view(),name='resume-tca'),
    path('finish/<str:pk>/', views.FinalizarTablaControlAcceso.as_view(),name='finish-tca'),
    
    # Catalogo TCA
    path('catalogo-tca/clasificar/<str:id_tca>/',views.ClasifSerieSubserieUnidadTCA.as_view(),name='catalogo-tca-clasificar'),
    path('catalogo-tca/update-clasif/<str:pk>/',views.UpdateClasifSerieSubserieUnidadTCA.as_view(),name='catalogo-tca-update-clasif'),
    path('catalogo-tca/get-clasif/<str:id_tca>/',views.GetClasifExpedientesTCA.as_view(),name='catalogo-tca-get-clasif'),
    path('catalogo-tca/delete-clasif/<str:id_tca>/',views.EliminarRelaciones.as_view(),name='catalogo-tca-delete-clasif'),
]