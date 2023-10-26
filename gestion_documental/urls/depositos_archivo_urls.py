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
     path('deposito/siguiente-actual/',views.DepositoGetOrdenActual.as_view(),name='listar-orden-actual'),
     path('deposito/buscar-deposito/',views.DepositoSearch.as_view(), name='buscar-deposito'),


     #Estante
     path('estanteDeposito/crear/',views.EstanteDepositoCreate.as_view(), name='crear-estanteDeposito'),
     path('estanteDeposito/buscar-deposito/',views.EstanteDepositoSearch.as_view(), name='buscar-deposito'),
     path('estanteDeposito/siguiente-orden/',views.EstanteDepositoGetOrden.as_view(), name='listar-orden-siguiente'),
     path('estanteDeposito/siguiente-actual/',views.EstanteDepositoGetOrdenActual.as_view(), name='listar-orden-actual'),
     path('estanteDeposito/actualizar-estante/<str:pk>/',views.EstanteDepositoUpDate.as_view(), name='actualizar-estante'),
     path('estanteDeposito/eliminar/<str:pk>/',views.EstanteDepositoDelete.as_view(),name='eliminar-estante'),
     path('estanteDeposito/listar-estante-por-deposito/<str:pk>/',views.EstanteGetByDeposito.as_view(),name='listar-estante-por-deposito'),
     path('estanteDeposito/mover-estante/<str:identificacion_por_deposito>/', views.MoveEstante.as_view(), name='mover-estante'),
     path('estanteDeposito/listar/',views.EstanteGetAll.as_view(),name='listar-estantes'),


     #Bandeja
     path('bandejaEstante/crear/',views.BandejaEstanteCreate.as_view(), name='crear-bandeja'),
     path('bandejaEstante/siguiente-orden/',views.BandejaEstanteGetOrden.as_view(),name='listar-orden-siguiente'),
     path('bandejaEstante/siguiente-actual/',views.BandejaEstanteGetOrdenActual.as_view(),name='listar-orden-actual'),
     path('bandejaEstante/actualizar-bandeja/<str:pk>/',views.BandejaEstanteUpDate.as_view(),name='actualizar-bandejas'),
     path('bandejaEstante/eliminar/<str:pk>/',views.BandejaEstanteDelete.as_view(),name='eliminar-bandeja'),
     path('bandejaEstante/buscar-estante/',views.BandejaEstanteSearch.as_view(), name='buscar-estante'),
     path('bandejaEstante/mover-bandeja/<int:id_bandeja_estante>/',views.BandejaEstanteMove.as_view(), name='mover-bandeja'),
     path('bandejaEstante/listar-bandejas-por-estante/<str:pk>/',views.BandejasByEstanteList.as_view(),name='listar-bandeja-por-estante'),
     path('bandejaEstante/listar/',views.BandejaEstanteAll.as_view(),name='listar-bandejas'),


     #Caja
     path('cajaBandeja/crear/',views.CajaBandejaCreate.as_view(), name='crear-caja'),
     path('cajaBandeja/siguiente-orden/',views.CajaBandejaGetOrden.as_view(), name='listar-orden-siguiente'),
     path('cajaBandeja/siguiente-actual/',views.CajaBandejaGetOrdenActual.as_view(), name='listar-orden-actual'),
     path('cajaBandeja/listar-cajas-por-bandeja/<int:pk>/',views.CajasByBandejaList.as_view(), name='listar-cajas-por-bandeja'),
     path('cajaBandeja/buscar-estante/',views.CajaEstanteSearch.as_view(), name='buscar-estante'),
     path('cajaBandeja/actualizar-caja/<int:pk>/',views.cajaBandejaUpDate.as_view(),name='actualizar-caja'),
     path('cajaBandeja/mover-caja/<int:id_caja_bandeja>/',views.CajaEstanteBandejaMove.as_view(), name='mover-caja'),
     path('cajaBandeja/busqueda-avanzada-caja/',views.CajaEstanteSearchAdvanced.as_view(), name='buscar-avanzada'),
     path('cajaBandeja/eliminar/<str:pk>/',views.CajaEstanteDelete.as_view(),name='eliminar-caja'),
     path('cajaBandeja/listar-bandejas-por-caja/<int:id_caja>/',views.CajaListBandejaInfo.as_view(),name='listar-bandejas-por-caja'),
     path('cajaBandeja/listar-estantes-por-caja/<int:id_caja>/',views.CajaListEstanteInfo.as_view(),name='listar-estantes-por-caja'),
     path('cajaBandeja/listar-depositos-por-caja/<int:id_caja>/',views.CajaListDepositoInfo.as_view(),name='listar-depositos-por-caja'),
     path('cajaBandeja/listar/',views.CajaBandejaAll.as_view(),name='listar-cajas'),
     path('cajaBandeja/rotulo/<int:id_caja_bandeja>/',views.CajaRotulo.as_view(),name='rotulo-cajas'),




     #Carpetas
     path('carpetaCaja/crear/',views.CarpetaCajaCreate.as_view(), name='crear-carpeta'),
     path('carpetaCaja/siguiente-orden/',views.CarpetaCajaGetOrden.as_view(),name='listar-orden-siguiente'),
     path('carpetaCaja/siguiente-actual/',views.CarpetaCajaGetOrdenActual.as_view(),name='listar-orden-actual'),
     path('carpetaCaja/busqueda-caja/',views.CarpetaCajaSearch.as_view(), name='buscar-caja'),
     path('carpetaCaja/listar-carpetas-por-caja/<str:pk>/',views.CarpetasByCajaList.as_view(),name='listar-carpetas-por-caja'),
     path('carpetaCaja/eliminar/<str:pk>/',views.CarpetaCajaDelete.as_view(),name='eliminar-carpeta'),
     path('carpetaCaja/actualizar-carpeta/<int:pk>/',views.CarpetaCajaUpDate.as_view(),name='actualizar-carpeta'),
     path('carpetaCaja/listar/',views.CarpetaCajaAll.as_view(),name='listar-carpetas'),
     path('carpetaCaja/listar-cajas-por-carpeta/<int:id_carpeta>/',views.CarpetaListCajaInfo.as_view(),name='listar-cajas-por-carpeta'),
     path('carpetaCaja/listar-bandejas-por-carpeta/<int:id_carpeta>/',views.CarpetaListBandejaInfo.as_view(),name='listar-bandejas-por-carpeta'),
     path('carpetaCaja/listar-estantes-por-carpeta/<int:id_carpeta>/',views.EstanteListCarpetaInfo.as_view(),name='listar-estantes-por-carpeta'),
     path('carpetaCaja/listar-depositos-por-carpeta/<int:id_carpeta>/',views.CarpetaListDepositoInfo.as_view(),name='listar-depositos-por-carpeta'),
     path('carpetaCaja/mover-carpeta/<int:id_carpeta_caja>/',views.CarpetaCajaMove.as_view(), name='mover-carpeta'),
     path('carpetCaja/busqueda-avanzada-carpetas/',views.CarpetaCajaSearchAdvanced.as_view(), name='buscar-avanzada'),
     path('carpetaCaja/rotulo/<int:id_carpeta_caja>/',views.CarpetaRotulo.as_view(),name='rotulo-carpeta'),


     #Archivo Físico
     path('archivoFisico/listar-deposito-id/<int:pk>/',views.DepositoGetById.as_view(),name='listar-por-id-deposito'),
     path('archivoFisico/listar-estante-id/<int:pk>/',views.EstanteGetById.as_view(),name='listar-por-id-estante'),
     path('archivoFisico/listar-bandeja-id/<int:pk>/',views.BandejaGetById.as_view(),name='listar-por-id-bandeja'),
     path('archivoFisico/listar-caja-id/<int:pk>/',views.CajaGetById.as_view(),name='listar-por-id-caja'),
     path('archivoFisico/listar-carpeta-id/<int:pk>/',views.CarpetaGetById.as_view(),name='listar-por-id-carpeta'),
     path('archivoFisico/listar-depositos/',views.DepositoGetAll.as_view(),name='listar-todos-depositos'),
     path('archivoFisico/listar-estantes/<int:id_deposito>/',views.EstanteGetAll.as_view(),name='listar-todos-estantes'),
     path('archivoFisico/listar-bandejas/<int:id_estante_deposito>/',views.BandejaGetAll.as_view(),name='listar-todos-bandejas'),
     path('archivoFisico/listar-cajas/<int:id_bandeja_estante>/',views.CajaGetAll.as_view(),name='listar-todos-cajas'),
     path('archivoFisico/listar-carpetas/<int:id_caja_bandeja>/',views.CarpetaGetAll.as_view(),name='listar-todos-carpetas'),
     path('archivoFisico/consultar-expediente/<int:id_carpeta_caja>/',views.ConsultarNumeroExpediente.as_view(),name='consultar-expediente'),
     path('archivoFisico/ver-expediente/<int:id_carpeta_caja>/',views.ReviewExpediente.as_view(),name='ver-expediente'),
     path('archivoFisico/choices-deposito/',views.DepositoChoices.as_view(),name='choices-deposito'),
     path('archivoFisico/busqueda-avanzada-deposito/',views.BusquedaDepositoArchivoFisico.as_view(),name='busqueda-archivo-fisico-deposito'),
     path('archivoFisico/busqueda-avanzada-estante/',views.BusquedaEstanteArchivoFisico.as_view(),name='busqueda-archivo-fisico-estante'),
     path('archivoFisico/busqueda-avanzada-bandeja/',views.BusquedaBandejaArchivoFisico.as_view(),name='busqueda-archivo-fisico-bandeja'),
     path('archivoFisico/busqueda-avanzada-caja/',views.BusquedaCajaArchivoFisico.as_view(),name='busqueda-archivo-fisico-caja'),
     path('archivoFisico/busqueda-avanzada-carpeta/',views.BusquedaCarpetaArchivoFisico.as_view(),name='busqueda-archivo-fisico-carpeta'),
     path('archivoFisico/detalles_deposito/<int:id_deposito>/', views.ListarInformacion.as_view(), name='listar-informacion'),






     
]