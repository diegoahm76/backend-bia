from django.urls import path
from recaudo.views import garantias_views as views

urlpatterns = [
    
    path('roles-garantias/', views.RolesGarantiasView.as_view(), name='roles-garantias'),


    ]