from django.urls import path
from recurso_hidrico.views import zonas_hidricas_views as views

urlpatterns = [
    path('macro-cuencas/get/', views.MacroCuencasListView.as_view(), name='macro-cuencas'),
    path('zona_hidrica/get/', views.ZonaHidricaListView.as_view(), name='zonas-hidricas'),
    
]
