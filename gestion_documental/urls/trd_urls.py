from django.urls import path
from gestion_documental.views import trd_views as views

urlpatterns = [
    # TIPOLOGIAS DOCUMENTALES
    path('tipologias/update/<str:id_trd>/', views.UpdateTipologiasDocumentales.as_view(), name='update-tipologias-doc'),
    path('tipologias/get-by-id/<str:id_trd>/', views.GetTipologiasDocumentales.as_view(),name='id-get-tipologias-doc'),
    path('tipologias/desactivar/<str:id_tipologia>/', views.DesactivarTipologiaActual.as_view(),name='desactivar-tipologias-doc'),
    
    # TABLA DE RETENCION DOCUMENTAL
    path('get-terminados/', views.GetTablaRetencionDocumentalTerminados.as_view(), name='trd-terminados-get'),
    path('get-list/', views.GetTablaRetencionDocumental.as_view(), name='trd-get-list'),
    path('create/', views.PostTablaRetencionDocumental.as_view(), name='trd-create'),
    path('update/<str:pk>/', views.UpdateTablaRetencionDocumental.as_view(), name='trd-update'),
    # path('finish/<str:id_trd>/', views.FinalizarTablaRetencionDocumental.as_view(), name='trd-finish'),
    path('get-ccd-terminados/<str:pk>/', views.GetCCDTerminadoByPk.as_view(), name='ccd-terminados-get-by-id'),
    path('get-trd-terminados/<str:pk>/', views.GetTRDTerminadoByPk.as_view(), name='trd-terminados-get-by-id'),
    path('activar/',views.Activar.as_view(),name='activar'),
    path('serie-subserie-unidad-trd/asignar/<str:id_trd>/',views.CreateSerieSubSeriesUnidadesOrgTRD.as_view(),name='serie-subserie-unidad-trd-create'),
    path('serie-subserie-unidad-trd/update/<str:id_serie_subs_unidadorg_trd>/', views.UpdateSerieSubSeriesUnidadesOrgTRD.as_view(),name='serie-subserie-unidad-trd-update'),
    path('confirmar-cambios/<str:id_trd>/',views.CambiosPorConfirmar.as_view(),name='confirmar-cambios-trd'),
    path('serie-subserie-unidad-trd/delete/<str:id_ssuorg_trd>/',views.DeleteSerieSubserieUnidadTRD.as_view(), name='serie-subserie-unidad-trd-delete'),
    path('serie-subserie-unidad-trd/delete/<str:id_ssuorg_trd>/',views.DeleteSerieSubserieUnidadTRD.as_view(), name='serie-subserie-unidad-trd-delete'),


    # FORMATOS TIPOS MEDIO
    path('formatos/get-by-params/', views.GetFormatosTiposMedioByParams.as_view(), name='formatos-get-by-params'),
    path('formatos/get-by-cod/<str:cod_tipo_medio_doc>/', views.GetFormatosTiposMedioByCodTipoMedio.as_view(), name='formatos-get-by-cod'),
    path('formatos/create/', views.RegisterFormatosTiposMedio.as_view(), name='formatos-create'),
    path('formatos/update/<str:pk>/', views.UpdateFormatosTiposMedio.as_view(), name='formatos-update'),
    path('formatos/delete/<str:pk>/', views.DeleteFormatosTiposMedio.as_view(), name='formatos-delete'),
    
    # GetSeriesSubSUnidadOrgTRD 
    path('get-serie-subserie-unidad-org-TRD/<str:pk>/', views.GetSeriesSubSUnidadOrgTRD.as_view(), name='get-serie-subserie-unidad-org-TRD'),
    path('get-una-serie-subserie-unidad-org-TRD/<str:pk>/', views.GetSeriesSubSUnidadOrgTRDByPk.as_view(), name='get-serie-subserie-unidad-org-TRD')
]