from django.urls import path

from gestion_documental.views import depositos_de_archivo_views as views


urlpatterns = [
     path('deposito/crear/',views.DepositoCreate.as_view(), name='crear-deposito'),
     path('deposito/eliminar/<str:pk>/',views.DepositoDelete.as_view(),name='eliminar-deposito'),
     path('deposito/actualizar/<str:pk>/',views.DepositoUpdate.as_view(),name='actualizar-deposito'),
     path('estanteDeposito/crear/',views.EstanteDepositoCreate.as_view(), name='crear-estanteDeposito'),
]