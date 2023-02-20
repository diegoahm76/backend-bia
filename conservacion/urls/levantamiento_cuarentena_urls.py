from django.urls import path
from conservacion.views import levantamiento_cuarentena_views as views

urlpatterns = [
    path('filtro-vivero/',views.GetViveroActivo.as_view(),name='filtro-vivero'),
    path('get-registro-cuarentena-by-codigo-bien/<str:id_vivero>/',views.GetMaterialVegetalByCodigo.as_view(),name='get-registro-cuarentena-by-codigo-bien'),
    path('get-registro-cuarentena-by-lupa/<str:id_vivero>/',views.GetCuarentenaMaterialVegetalByLupa.as_view(),name='get-registro-cuarentena-by-lupa') ,
    path('get-cuarentena-by-id/<str:id_cuarentena_mat_vegetal>/',views.GetCuarentenaMaterialVegetalById.as_view(),name='get-cuarentena-by-id'),
    path('get-anulacion-cuarentena-mt-by-lupa/<str:id_vivero>/',views.GetAnulacionCuarentenaMaterialVegetalByLupa.as_view(),name='get-anulacion-cuarentena-mt-by-lupa'),
    path('historial-levantamiento-cuarentena/<str:id_cuarentena_mat_vegetal>/',views.GetHistorialLevantamientoCuarentena.as_view(),name='historial-levantamiento-cuarentena'),
    path('guardar-levantamiento-cuarentena/',views.GuardarLevantamientoCuarentena.as_view(),name='guardar-levantamiento-cuarentena'),
    path('actualizar-levantamiento-cuarentena/<str:id_item_levanta_cuarentena>/',views.UpdateLevantamientoCuarentena.as_view(),name='actualizar-levantamiento-cuarentena'),    
    path('anular-levantamiento-cuarentena/<str:id_item_levanta_cuarentena>/',views.AnularLevantamientoCuarentena.as_view(),name='anular-levantamiento-cuarentena')           
]

