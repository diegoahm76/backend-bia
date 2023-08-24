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
     path('deposito/buscar-deposito/',views.DepositoSearch.as_view(), name='buscar-deposito'),


     #Estante
     path('estanteDeposito/crear/',views.EstanteDepositoCreate.as_view(), name='crear-estanteDeposito'),
     path('estanteDeposito/buscar-deposito/',views.EstanteDepositoSearch.as_view(), name='buscar-deposito'),
     path('estanteDeposito/siguiente-orden/',views.EstanteDepositoGetOrden.as_view(), name='listar-orden-siguiente'),
     path('estanteDeposito/actualizar-estante/<str:pk>/',views.EstanteDepositoUpDate.as_view(), name='actualizar-estante'),
     path('estanteDeposito/eliminar/<str:pk>/',views.EstanteDepositoDelete.as_view(),name='eliminar-estante'),
     path('estanteDeposito/listar-estante-por-deposito/<str:pk>/',views.EstanteGetByDeposito.as_view(),name='listar-estante-por-deposito'),
     path('estanteDeposito/mover-estante/<str:identificacion_por_deposito>/', views.MoveEstante.as_view(), name='mover-estante'),
     path('estanteDeposito/listar/',views.EstanteGetAll.as_view(),name='listar-estantes'),


     #Bandeja
     path('bandejaEstante/crear/',views.BandejaEstanteCreate.as_view(), name='crear-bandeja'),
     path('bandejaEstante/siguiente-orden/',views.BandejaEstanteGetOrden.as_view(),name='listar-orden-siguiente'),
     path('bandejaEstante/actualizar-bandeja/<str:pk>/',views.BandejaEstanteUpDate.as_view(),name='actualizar-bandejas'),
     path('bandejaEstante/eliminar/<str:pk>/',views.BandejaEstanteDelete.as_view(),name='eliminar-bandeja'),
     path('bandejaEstante/buscar-estante/',views.BandejaEstanteSearch.as_view(), name='buscar-estante'),
     path('bandejaEstante/mover-bandeja/<int:id_bandeja_estante>/',views.BandejaEstanteMove.as_view(), name='mover-bandeja'),
     path('bandejaEstante/listar-bandejas-por-estante/<str:pk>/',views.BandejasByEstanteList.as_view(),name='listar-bandeja-por-estante'),


     #Caja
     path('cajaBandeja/crear/',views.CajaBandejaCreate.as_view(), name='crear-caja'),
     path('cajaBandeja/siguiente-orden/',views.CajaBandejaGetOrden.as_view(), name='listar-orden-siguiente'),
     path('cajaBandeja/listar-cajas-por-bandeja/<int:pk>/',views.CajasByBandejaList.as_view(), name='listar-cajas-por-bandeja'),
     path('cajaBandeja/buscar-estante/',views.CajaEstanteSearch.as_view(), name='buscar-estante'),
     path('cajaBandeja/actualizar-caja/<int:pk>/',views.cajaBandejaUpDate.as_view(),name='actualizar-caja'),
     path('cajaBandeja/mover-caja/<int:id_caja_estante>/',views.CajaEstanteBandejaMove.as_view(), name='mover-caja'),
     path('cajaBandeja/busqueda-avanzada-caja/',views.CajaEstanteSearchAdvanced.as_view(), name='buscar-avanzada'),
     path('cajaBandeja/eliminar/<str:pk>/',views.CajaEstanteDelete.as_view(),name='eliminar-caja'),
     path('cajaBandeja/listar-info-caja/<str:pk>/',views.CajaBandejaInfo.as_view(),name='listar-info-por-caja'),



     #Carpetas
     path('carpetaCaja/crear/',views.CarpetaCajaCreate.as_view(), name='crear-carpeta'),
     path('carpetaCaja/siguiente-orden/',views.CarpetaCajaGetOrden.as_view(),name='listar-orden-siguiente'),
     path('carpetaCaja/busqueda-caja/',views.CarpetaCajaSearch.as_view(), name='buscar-caja'),
     path('carpetaCaja/listar-carpetas-por-caja/<str:pk>/',views.CarpetasByCajaList.as_view(),name='listar-carpetas-por-caja'),
     path('carpetaCaja/eliminar/<str:pk>/',views.CarpetaCajaDelete.as_view(),name='eliminar-carpeta'),
     path('carpetaCaja/actualizar-carpeta/<int:pk>/',views.CarpetaCajaUpDate.as_view(),name='actualizar-carpeta'),



     
     




















     
]