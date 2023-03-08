from django.urls import path
from gestion_documental.views import tca_views as views

urlpatterns = [
    path('unidades-by-ccd/get/<str:pk>/', views.GetUnidadesbyCCD.as_view(), name='unidades-get-by-ccd'),
    path('cargos-by-unidades/get/', views.GetCargosByUnidades.as_view(), name='cargos-by-unidades-get'),
    path('tca-list/get/', views.GetListTca.as_view(), name='tca-list-get'),
    
    # Tabla de Control de Acceso
    path('create/', views.PostTablaControlAcceso.as_view(),name='create-tca'),
    path('update/<str:pk>/', views.UpdateTablaControlAcceso.as_view(), name='update-tca'),
    path('resume/<str:pk>/', views.ReanudarTablaControlAcceso.as_view(),name='resume-tca'),
    path('finish/<str:pk>/', views.FinalizarTablaControlAcceso.as_view(),name='finish-tca'),
    path('serie-subserie-unidad-tca/clasificar/<str:id_tca>/',views.ClasifSerieSubserieUnidadTCA.as_view(),name='serie-subserie-unidad-tca-clasificar'),
    path('serie-subserie-unidad-tca/update-clasif/<str:pk>/',views.UpdateClasifSerieSubserieUnidadTCA.as_view(),name='serie-subserie-unidad-tca-clasificar'),
    path('serie-subserie-unidad-tca/get-clasif/<str:id_tca>/',views.GetClasifSerieSubserieUnidad.as_view(),name='serie-subserie-unidad-tca-clasificar'),
    path('cargo-serie-subserie-unidad-tca/create/',views.asignar_cargo_unidad_permiso_expediente,name='cargo-serie-subserie-unidad-tca-crear'),
    path('cargo-serie-subserie-unidad-tca/update/<str:pk>/',views.actualizar_cargo_unidad_permiso_expediente,name='cargo-serie-subserie-unidad-tca-update'),
    path('cargo-serie-subserie-unidad-tca/delete/<str:pk>/',views.EliminarCargoUnidadPermisoExp.as_view(),name='cargo-serie-subserie-unidad-tca-delete'),
    path('cargo-serie-subserie-unidad-tca/get/<str:id_tca>/',views.GetCargoUnidadPermisos.as_view(),name='cargo-serie-subserie-unidad-tca-get'),
]