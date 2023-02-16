from django.urls import path
from conservacion.views import mortalidad_views as views

urlpatterns = [
    path('registrar/',views.RegistrarMortalidad.as_view(), name='registrar-mortalidad'),
    path('actualizar/<str:id_baja>/',views.ActualizarMortalidad.as_view(), name='actualizar-mortalidad'),
    path('anular/<str:id_baja>/',views.AnularMortalidad.as_view(), name='anular-mortalidad'),
    path('get-mortalidad-by-nro/',views.GetMortalidadByNro.as_view(), name='get-mortalidad-by-nro'),
    path('get-ultimo-nro/',views.GetUltimoNro.as_view(), name='get-ultimo-nro'),
    path('get-historial-mortalidad/<str:id_cuarentena_mat_vegetal>/',views.GetHistorialMortalidad.as_view(), name='get-historial-mortalidad'),
    path('get-items-mortalidad-by-id/<str:id_baja>/',views.GetItemsMortalidadByIdBaja.as_view(), name='get-items-mortalidad'),
    path('material-vegetal/get-by-codigo/<str:id_vivero>/',views.GetMaterialVegetalByCodigo.as_view(), name='get-by-codigo'),
    path('material-vegetal/filtro/<str:id_vivero>/',views.GetMaterialVegetalByLupa.as_view(), name='filtro-material-vegetal')
]