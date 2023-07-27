from django.urls import path
from transversal.views import configuracionEntidades_views as views

urlpatterns = [
    path("entidad/get/", views.PersonaEntidadCormacarenaGetView.as_view(), name="get-entidad"),
    path('configuracionEntidad/<str:pk>/', views.GetConfiguracionEntidadByID.as_view(), name='get-configuracionEntidad'),
    path('configuracionEntidad/update/<int:id_persona_entidad>/',views.UpdateConfiguracionEntidad.as_view(),name='update-configuracionEntidad'),
    path('historico_perfiles_entidad/get/<str:para>/',views.HistoricoPerfilesEntidadGet.as_view(),name='get-historico'),
]