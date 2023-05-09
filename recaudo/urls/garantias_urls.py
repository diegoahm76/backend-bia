from django.urls import path
from recaudo.views import garantias_views as views

urlpatterns = [
    path('roles-garantias/', views.RolesGarantiasView.as_view(), name='roles-garantias'),
    path('tipos-bienes/', views.TiposBienesView.as_view(), name='tipos-bienes'),
    path('crear-bien/', views.CrearBienView.as_view(), name='crear-bien'),
    path('listar-bienes-deudor/<int:id>', views.ListaBienesDeudorView.as_view(), name='listar-bienes-deudor'),

    ]