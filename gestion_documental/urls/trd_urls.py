from django.urls import path
from gestion_documental.views import trd_views as views

urlpatterns = [
    # TIPOLOGIAS DOCUMENTALES
    # path('tipologias/update/<str:id_trd>/', views.UpdateTipologiasDocumentales.as_view(), name='update-tipologias-doc'),
    path('crear/tipologia/documental/', views.CrearTipologiaDocumental.as_view(), name='crear-tipologia-documental'),#TRD
    path('eliminar/tipologia/documental/<str:pk>/', views.EliminarTipologiaDocumental.as_view(), name='eliminar-tipologia-documental'),#
    path('update/tipologia/documental/<str:pk>/', views.ModificarTipologiaDocumental.as_view(), name='modificar-tipologia-documental'),#
    path('buscar/tipologia/documental/', views.BuscarTipologia.as_view(),name='buscar-tipologia-documental'),
    path('tipologias/get-by-id/<str:id_trd>/', views.GetTipologiasDocumentales.as_view(),name='id-get-tipologias-doc'),
    path('tipologias/get-formatos/<str:id_tipologia_documental>/', views.GetFormatosTipologiasDocumentales.as_view(),name='get-formatos-tipologias'),
    path('tipologias/desactivar/<str:id_tipologia>/', views.DesactivarTipologiaActual.as_view(),name='desactivar-tipologias-doc'),
    
    # TABLA DE RETENCION DOCUMENTAL
    path('get-terminados/', views.GetTablaRetencionDocumentalTerminados.as_view(), name='trd-terminados-get'),
    path('get-list/', views.GetTablaRetencionDocumental.as_view(), name='trd-get-list'),
    path('create/', views.PostTablaRetencionDocumental.as_view(), name='trd-create'),
    # path('update/<str:pk>/', views.UpdateTablaRetencionDocumental.as_view(), name='trd-update'),
    path('finish/<str:pk>/', views.FinalizarTRD.as_view(), name='trd-finish'),
    path('catalogo-trd/add/<str:id_trd>/',views.CreateSerieSubSeriesUnidadesOrgTRD.as_view(),name='catalogo-trd-create'),
    path('catalogo-trd/update/<str:id_serie_subs_unidadorg_trd>/', views.UpdateSerieSubSeriesUnidadesOrgTRD.as_view(),name='catalogo-trd-update'),
    path('catalogo-trd/delete/<str:id_serie>/',views.EliminarSerieUnidadTRD.as_view(), name='catalogo-trd-delete'),
    # path('serie-subserie-unidad-trd/upload/document/<str:id_serie_subserie_uniorg_trd>/',views.uploadDocument, name='serie-subserie-unidad-trd-upload-document'),
    # path('confirmar-cambios/<str:id_trd>/',views.CambiosPorConfirmar.as_view(),name='confirmar-cambios-trd'),
    path('buscar/trd/nombre-version/',views.BusquedaTRDNombreVersion.as_view(),name='busqueda-usuario-nombre-version'),#
    path('historico/',views.GetHistoricoTRD.as_view(),name='get-historico-trd'),
    path('update/<str:id_trd>/',views.ModificarNombreVersionTRD.as_view(),name='modificar-trd-nombre-version'),#
    path('reanudar/trd/<str:id_trd>/',views.ReanudarTRD.as_view(),name='reanudar-trd'),#


    # FORMATOS TIPOS MEDIO
    path('formatos/get-by-params/', views.GetFormatosTiposMedioByParams.as_view(), name='formatos-get-by-params'),
    path('formatos/get-by-cod/<str:cod_tipo_medio_doc>/', views.GetFormatosTiposMedioByCodTipoMedio.as_view(), name='formatos-get-by-cod'),
    path('formatos/create/', views.RegisterFormatosTiposMedio.as_view(), name='formatos-create'),
    path('formatos/update/<str:pk>/', views.UpdateFormatosTiposMedio.as_view(), name='formatos-update'),
    path('formatos/delete/<str:pk>/', views.DeleteFormatosTiposMedio.as_view(), name='formatos-delete'),
    
    # GetSeriesSubSUnidadOrgTRD 
    path('catalogo-trd/get-list/<str:id_trd>/', views.GetSeriesSubSUnidadOrgTRD.as_view(), name='catalogo-trd-get-list'),
    path('catalogo-trd/get-tipologias/<str:id_catserie_unidadorg>/', views.GetTipologiasSeriesSubSUnidadOrgTRD.as_view(), name='catalogo-trd-get-tipologias'),

    #Configuracion_tipologias_docmentales
    path('configuracion-tipologia/listar-tipologias/', views.ListarTipologiasdocumentales.as_view(),name='listar-tipologias-doc'),
    path('configuracion-tipologia/listar-tipologias-por-año-actual/', views.GetConfiguracionesPorTipologiaAnioActual.as_view(), name='listar-tipologias-por-año-actual'),
    path('configuracion-tipologia/listar-tipologias-por-año-anterior/', views.GetConfiguracionesPorTipologiaAnioAnterior.as_view(), name='listar-tipologias-por-año-anterior'),
    path('configuracion-tipologia/configuracion-tipologia-actual/', views.CrearConfigurarTipologia.as_view(),name='configuracion-tipologias-doc'),
    path('configuracion-tipologia/configuracion-tipologia-empresa/', views.CrearConfigurarTipologiaEmpresa.as_view(),name='configuracion-tipologias-em'),
    path('configuracion-tipologia/configuracion-tipologia-ss/', views.ConfigurarTipologiaSS.as_view(),name='configuracion-tipologias-ss'),
    path('configuracion-tipologia/listar-configuraciones/', views.ListaConfiguraciones.as_view(),name='listar-configuraciones-doc'),
    path('configuracion-tipologia/consulta-años-anteriores/', views.ListaConfiguracionesPorAgnoYTipologia.as_view(),name='consulta-años-anteriores'),
    path('configuracion-tipologia/seccion-subseccion-trd-actual/', views.GetActualSeccionSubsecciones.as_view(),name='consulta-años-anteriores'),
    path('configuracion-tipologia/administrador-numeros-tipologias/', views.AsignarNuevoConsecutivo.as_view(),name='admnistrador-numeros-tipologias'),
    path('configuracion-tipologia/actualizar-tipologia-no-a-em/<int:id_tipologia_doc>/',views.ActualizarConfiguracionEM.as_view(), name='actualizar--NoConsecutivo-a-em'),
    path('configuracion-tipologia/actualizar-tipologia-no-a-ss/<int:id_tipologia_doc>/',views.ActualizarConfiguracionSS.as_view(), name='actualizar-numeros-tipologias'),
    path('configuracion-tipologia/actualizar-tipologia-si-a-no-em/<int:id_tipologia_doc>/', views.ActualizarConfiguracionNoConsecutivoEm.as_view(), name='actualizar-configuracion-no-a-si'),
    path('configuracion-tipologia/actualizar-tipologia-si-a-no-ss/<int:id_tipologia_doc>/', views.ActualizarConfiguracionNoConsecutivoSS.as_view(), name='actualizar-configuracion-no-a-si'),

    


    

    
]