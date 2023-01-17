from django.urls import path
from conservacion.views import despachos_views as views

urlpatterns = [
    # Recepción y Distribución
    # path('distribuir/', views.DitribucionDespachosViveros.as_view(), name='distribucion-despachos'),
    path('get-list/', views.GetDespachosEntrantes.as_view(), name='get-list-despachos'),
    path('items-despacho/get-by-id/<str:pk>/', views.GetItemsDespachosEntrantes.as_view(), name='get-items-despachos'),
]