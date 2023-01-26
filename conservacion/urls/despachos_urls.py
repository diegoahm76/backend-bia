from django.urls import path
from conservacion.views import despachos_views as views

urlpatterns = [
    # Recepción y Distribución
    path('guardar/<str:id_despacho_entrante>/', views.GuardarDistribucionBienes.as_view(), name='guardar-distribucion'),
    path('get-list/', views.GetDespachosEntrantes.as_view(), name='get-list-despachos'),
    path('items-despacho/get-by-id/<str:pk>/', views.GetItemsDespachosEntrantes.as_view(), name='get-items-despachos'),
    path('confirmar-distribucion/<str:id_despacho_entrante>/',views.ConfirmarDistribucion.as_view(),name='confirmar-distribucion'),
    path('get-obtener-items-predistribuidos/<str:pk>/',views.GetItemsPredistribuidos.as_view(),name='get-obtener-items-predistribuidos'),
]