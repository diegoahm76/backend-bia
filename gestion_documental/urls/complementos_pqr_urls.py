from django.urls import path
from gestion_documental.views import complementos_pqr_views as views

urlpatterns = [
    path('get-complementos-pqrsdf/', views.ComplementosPQRSDFGet.as_view(), name='get-complementos-pqrsdf'),
    path('create-complemento-pqrsdf/', views.ComplementoPQRSDFCreate.as_view(), name='create-complemento-pqrsdf'),
    path('update-complemento-pqrsdf/', views.ComplementoPQRSDFUpdate.as_view(), name='update-complemento-pqrsdf'),
    path('delete-complemento-pqrsdf/', views.ComplementoPQRSDFDelete.as_view(), name='delete-complemento-pqrsdf'),
    path('radicar-complemento-pqrsdf/', views.RadicarComplementoPQRSDF.as_view(), name='radicar-complemento-pqrsdf')

]