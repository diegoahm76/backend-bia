from django.urls import path
from recurso_hidrico.views import zonas_hidricas_views as views

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
    ]
