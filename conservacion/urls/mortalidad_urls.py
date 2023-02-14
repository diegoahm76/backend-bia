from django.urls import path
from conservacion.views import mortalidad_views as views

urlpatterns = [
    path('registrar/',views.RegistrarMortalidad.as_view(), name='registrar-mortalidad'),
    path('actualizar/<str:id_baja>/',views.ActualizarMortalidad.as_view(), name='actualizar-mortalidad'),
    path('get-by-codigo/<str:id_vivero>/',views.GetMaterialVegetalByCodigo.as_view(), name='get-by-codigo'),
    path('filtro-material-vegetal/<str:id_vivero>/',views.GetMaterialVegetalByLupa.as_view(), name='get-by-codigo')
]