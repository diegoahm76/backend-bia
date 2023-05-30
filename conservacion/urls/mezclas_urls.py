from django.urls import path
from conservacion.views import preparacion_mezclas_views as views
from conservacion.views import mezclas_views as view

urlpatterns = [
    # MEZCLAS
    path('crear-mezcla/',view.CrearMezcla.as_view(),name='crear-mezcla'),
    path('actualizar-mezcla/<str:id_mezcla>/',view.ActualizarMezcla.as_view(),name='actualizar-mezcla'),
    path('eliminar-mezcla/<str:id_mezcla>/',view.EliminarMezcla.as_view(),name='eliminar-mezcla'),
    path('get-list-mezclas/',view.GetListMezclas.as_view(),name='get-list-mezclas'),
    
    # PREPARACION DE MEZCLAS
    path('get-mezclas/<str:nombre_mezcla>/', views.GetMezclasByNombre.as_view(), name='get-mezclas'),
    path('get-insumo-por-codigo/<str:id_vivero>/<str:codigo_bien>/', views.GetBienInsumosByCodigo.as_view(), name='get-insumo-por-codigo'),
    path('get-insumo-por-codigo-y-nombre/', views.GetBienInsumosByCodigoAndName.as_view(), name='get-insumo-por-codigo-y-nombre'),
    path('crear-preparacion-mezclas/', views.CreatePreparacionMezclas.as_view(), name='crear-preparacion-mezclas'), 
    path('actualizar-preparacion-mezclas/', views.UpdatePreparacionMezclas.as_view(), name='actualizar-preparacion-mezclas'), 
    path('anular-preparacion-mezclas/<str:id_preparacion_anular>/', views.AnularPreparacionMezclas.as_view(), name='anular-preparacion-mezclas'), 
    path('filtro-preparacion-mezclas/', views.BusquedaAvanzadaPreparacionesMezclas.as_view(), name='filtro-preparacion-mezclas'), 
    path('get-by-id-preparacion-mezclas/<str:id_preparacion>/', views.GetPreparacionById.as_view(), name='get-by-id-preparacion-mezclas'),
    path('get-items-preparacion-mezclas/', view.ItemsMezclaView.as_view(), name='get-preparacion-mezclas')
]