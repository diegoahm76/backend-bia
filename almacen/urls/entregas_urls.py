from django.urls import path
from almacen.views import entregas_views as views

urlpatterns = [
    path('get-number-despacho/',views.GetNumeroDespachoView.as_view(),name='numero-despacho-get'),
    path('get-entregas/',views.GetEntregasView.as_view(),name='entregas-get'),
    path('get-entradas-entregas/',views.GetEntradasEntregasView.as_view(),name='entrada-entregas-get'),
    path('get-items-entradas-entregas/<str:id_entrada>/',views.GetItemsEntradasEntregasView.as_view(),name='items-entrada-entregas-get'),
    path('create-entrega/',views.CrearEntregaView.as_view(),name='entrega-create'),
    path('anular-entrega/<str:id_entrega>/',views.AnularEntregaView.as_view(),name='entrega-anular'),

]