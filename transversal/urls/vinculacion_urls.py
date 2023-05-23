from django.urls import path
from transversal.views import vinculacion_views as views

urlpatterns = [
    #VINCULAR
    path('vinculacion-colaboradores/<str:id_persona>/', views.VinculacionColaboradorView.as_view(), name='vinculacion-colaboradores'),
    #CONSULTAR
    path('get-vinculacion-colaboradores/<str:id_persona>/', views.ConsultaVinculacionColaboradorView.as_view(), name='consulta-vinculacion-colaboradores'),
    #ACTUALIZAR
    path('update-vinculacion-colaboradores/<str:id_persona>/', views.UpdateVinculacionColaboradorView.as_view(), name='actualizacion-vinculacion-colaboradores'),
    #DESVINCULACION
    path('desvinculacion-persona/<str:id_persona>/', views.Desvinculacion_persona.as_view(),name='desvinculacion-persona'),
    # Historico Cargo-Unidad
    path('get-historico-cargo-und/<str:id_persona>/', views.BusquedaHistoricoCargoUnd.as_view(), name='historico_cargos_und'),
]