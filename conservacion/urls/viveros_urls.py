from django.urls import path
from conservacion.views import viveros_views as views

urlpatterns = [
    path('delete/<str:id_vivero>/', views.DeleteVivero.as_view(), name='delete-vivero'),
    path('abrir-cerrar/<str:id_vivero>/', views.AbrirCerrarVivero.as_view(), name='abrir-cerrar-vivero'),
]