from django.urls import path
from estaciones.views import choices_views as views

urlpatterns = [
    # Choices
    path('tipo-variable/', views.VariableClimatica.as_view(), name='tipo-variable'),
    path('codigo-estacion/', views.VariableClimatica.as_view(), name='codigo-estacion'),
]