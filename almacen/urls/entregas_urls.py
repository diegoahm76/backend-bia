from django.urls import path
from almacen.views import entregas_views as views

urlpatterns = [
    path('get-number-despacho/',views.GetNumeroDespachoView.as_view(),name='numero-despacho-get'),
]