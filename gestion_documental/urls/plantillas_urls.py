from django.urls import path

from gestion_documental.views import plantillas_views as views

urlpatterns = [
    path('plantilla_documento/create/', views.PlantillasDocCreate.as_view(),name='crear-plantilla'),
    path('plantilla_documento/delete/<str:pk>/', views.PlantillasDocDelete.as_view(),name='eliminar-plantilla'),
    path('plantilla_documento/update/<str:pk>/', views.PlantillasDocUpdateUpdate.as_view(),name='actualizar-plantilla'),
    path('plantilla_documento/get/busqueda_avanzada/', views.BusquedaAvanzadaPlantillas.as_view(),name='busqueda-plantilla'),
    path('plantilla_documento/get_id/<str:pk>/', views.PlantillasDocGetById.as_view(),name='listar-detalle-plantilla'),
    path('plantilla_documento/get_detalle_id/<str:pk>/', views.PlantillasDocGetDetalleById.as_view(),name='listar-detalle-plantilla'),
    #
    path('plantilla_documento/get/busqueda_avanzada_admin/', views.BusquedaAvanzadaPlantillasAdmin.as_view(),name='busqueda-plantilla-admin'),
    #OtrasTipologiasDocGetActivo
    path('otras_tipologias/get/', views.OtrasTipologiasDocGetActivo.as_view(),name='otras-tipologias-plantilla-admin'),


    path('tipos_tipologia/get/',views.TipologiasDocGetActivo.as_view(),name='listar-tipologias'),
    path('acceso/create/',views.AccesoUndsOrg_PlantillaDocCreate.as_view(),name='crear-acceso'),
    path('acceso/delete/<str:pk>/', views.AccesoUndsOrg_PlantillaDocDelete.as_view(),name='eliminar-acceso'),
    path('acceso/get/<str:pk>/',views.AccesoUndsOrg_PlantillaDocGetByPlantilla.as_view(),name='listar-acceso'),

    path('plantillas_documentos/get/', views.PlantillasDocGet.as_view(),name='plantillas-documentos'),
    
]
