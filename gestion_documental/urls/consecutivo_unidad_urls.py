from django.urls import path


from gestion_documental.views import consecutivo_unidad_views as views


urlpatterns = [
    
    path('config_tipo_consec_agno/get/', views.ConfigTipoConsecAgnoGetView.as_view(), name='listar-consecutivos'),
  
]
