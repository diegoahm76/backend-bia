from django.urls import path
from recurso_hidrico.views import zonas_hidricas_views as views
# urls
urlpatterns = [
        path('macro-cuencas/get/', views.MacroCuencasListView.as_view(), name='macro-cuencas'),
        path('zona_hidrica/get/<str:pk>/', views.ZonaHidricaListView.as_view(), name='zonas-hidricas'),
        path('tipozonahidrica/get/', views.TipoZonaHidricaListView.as_view(), name='macro-cuencas'),
        path('subZonahidrica/get/<str:pk>/', views.SubZonaHidricaListView.as_view(), name='macro-cuencas'),   
        path('tipoaguazonahidrica/get/', views.TipoAguaZonaHidricaListView.as_view(), name='tipo-agua-cuencas'),   
      
        path('zona_hidrica/list-create/', views.CrearZonaHidricaVista.as_view(), name='zonas-hidricas-crear'),
        path('sub_zona_hidrica/list-create/', views.CrearSubZonaHidricaVista.as_view(), name='sub-zonas-hidricas-crear'),

        path('zona_hidrica/delete/<str:pk>/', views.BorrarZonaHidricaVista.as_view(), name='zonas-hidricas-actualizar'),
        path('sub_zona_hidrica/delete/<str:pk>/', views.BorrarSubZonaHidricaVista.as_view(), name='zonas-hidricas-actualizar'),



        path('zona_hidrica/update/<str:pk>/', views.ActualizarZonaHidricaVista.as_view(), name='zonas-hidricas-actualizar'),
        path('sub_zona_hidrica/update/<str:pk>/', views.ActualizarSubZonaHidricaVista.as_view(), name='sub-zonas-hidricas-actualizar'),
    
    

        path('enviar_sms/', views.EnviarSMSView.as_view(), name='enviar_sms'),
        path('enviar_correo/', views.EnviarCORREOView.as_view(), name='enviar_correo'),


        path('data_rios_completa/', views.SubZonaHidricaListViewwww.as_view(), name='subzonashidricas-list'),
]
    

