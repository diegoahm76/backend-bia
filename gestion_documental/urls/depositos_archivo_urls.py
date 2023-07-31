from django.urls import path

from gestion_documental.views import depositos_de_archivo_views as views


urlpatterns = [
    #Deposito
     path('deposito/crear/',views.DepositoCreate.as_view(), name='crear-deposito'),
     path('deposito/eliminar/<str:pk>/',views.DepositoDelete.as_view(),name='eliminar-deposito'),
     path('deposito/actualizar/<str:pk>/',views.DepositoUpdate.as_view(),name='actualizar-deposito'),
     path('deposito/listar/',views.DepositoGet.as_view(),name='listar-deposito'),
     path('deposito/listar-por-id/<str:pk>/',views.DepositoGetById.as_view(),name='listar-por-id-deposito'),
     path('deposito/siguiente-orden/',views.DepositoGetOrden.as_view(),name='listar-orden-siguiente'),
     #Estante
     path('estanteDeposito/buscar-deposito/',views.EstanteDepositoSearch.as_view(), name='buscar-deposito'),
     path('estanteDeposito/crear/',views.EstanteDepositoCreate.as_view(), name='crear-estanteDeposito'),
     path('estanteDeposito/siguiente-orden/',views.EstanteDepositoGetOrden.as_view(), name='listar-orden-siguiente'),
     path('estanteDeposito/cambiar-orden-estante/<str:pk>/',views.EstanteDepositoChangeOrden.as_view(), name='cambiar-orden-estante'),





     
]