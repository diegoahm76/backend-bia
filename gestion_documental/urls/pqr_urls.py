from django.urls import path
from gestion_documental.views import pqr_views as views
urlpatterns = [
    path('tipos_pqr/get/<str:pk>/', views.TiposPQRGet.as_view(), name='get-tipos-radicado'),
    path('tipos_pqr/update/<str:pk>/', views.TiposPQRUpdate.as_view(), name='update-tipos-radicado')

]