from django.urls import path
from tramites.views import tramites_views as views

urlpatterns = [
    # TRAMITES
    path('general/create/', views.GeneralTramitesCreateView.as_view(), name='general-tramites-create'),
    #Tramites Pivot Table T318
    path('general/get/', views.TramitesPivotGetView.as_view(), name='general-tramites-pivot-get'),
    
    # OPAS
    path('opa/tramites/get-list/<str:cod_tipo_permiso_ambiental>/', views.ListTramitesGetView.as_view(), name='list-tramites-get'),
    path('opa/tramites/persona-titular/get-info/<str:id_persona>/', views.PersonaTitularInfoGetView.as_view(), name='persona-titular-get-info'),
    path('opa/tramites/list/<str:id_persona_titular>/', views.TramiteListGetView.as_view(), name='tramite-list-get'),
    path('opa/tramites/inicio-tramite/create/', views.InicioTramiteCreateView.as_view(), name='inicio-tramite-create'),
    path('opa/tramites/inicio-tramite/update/<str:id_solicitud_tramite>/', views.InicioTramiteUpdateView.as_view(), name='inicio-tramite-update'),
    path('opa/tramites/anexos/update/<str:id_solicitud_tramite>/', views.AnexosUpdateView.as_view(), name='anexos-update'),
    path('opa/tramites/anexos-metadatos/update/<str:id_solicitud_tramite>/', views.AnexosMetadatosUpdateView.as_view(), name='anexos-metadatos-update'),
    path('opa/tramites/anexos/get/<str:id_solicitud_tramite>/', views.AnexosGetView.as_view(), name='anexos-get'),
    path('opa/tramites/radicar/create/<str:id_solicitud_tramite>/', views.RadicarCreateView.as_view(), name='radicar-create'),
    path('opa/tramites/radicar/get/<str:id_solicitud_tramite>/', views.RadicarGetView.as_view(), name='radicar-get'),
    path('opa/tramites/radicar/volver-enviar/<str:id_solicitud_tramite>/', views.RadicarVolverEnviarGetView.as_view(), name='radicar-volver-enviar'),

    #Permisos_Menores
    path('pm/tramites/get-list/<str:cod_tipo_permiso_ambiental>/', views.ListTramitesGetView.as_view(), name='list-tramites-get'),
    path('pm/tramites/persona-titular/get-info/<str:id_persona>/', views.PersonaTitularInfoGetView.as_view(), name='persona-titular-get-info'),
    path('pm/tramites/list/<str:id_persona_titular>/', views.TramiteListGetViewPM.as_view(), name='tramite-list-get-PM'),   
    path('pm/tramites/inicio-tramite/create/', views.InicioTramiteCreateView.as_view(), name='inicio-tramite-create'),
    path('pm/tramites/inicio-tramite/update/<str:id_solicitud_tramite>/', views.InicioTramiteUpdateView.as_view(), name='inicio-tramite-update'),
    path('pm/tramites/anexos/update/<str:id_solicitud_tramite>/', views.AnexosUpdatePMView.as_view(), name='anexos-update'),
    path('pm/tramites/anexos-metadatos/update/<str:id_solicitud_tramite>/', views.AnexosMetadatosUpdatePMView.as_view(), name='anexos-metadatos-update'),
    path('pm/tramites/anexos/get/<str:id_solicitud_tramite>/', views.AnexosGetPMView.as_view(), name='anexos-get'),
    path('pm/tramites/radicar/create/<str:id_solicitud_tramite>/', views.RadicarCreatePMView.as_view(), name='radicar-create'),
    path('pm/tramites/radicar/get/<str:id_solicitud_tramite>/', views.RadicarGetPMView.as_view(), name='radicar-get'),
    path('pm/tramites/radicar/volver-enviar/<str:id_solicitud_tramite>/', views.RadicarVolverEnviarGetPMView.as_view(), name='radicar-volver-enviar'),


    #Consulta_Estado_Solicitud_OPAS_130
    path('opa/tramites/consulta-estado-opas/', views.ConsultaEstadoOPAS.as_view(), name='listar-OPAS-solicitud'),

    #Tipos Tramites CRUD
    path('tipos/filter/get/', views.GetTiposTramitesByFilterView.as_view(), name='tipos-tramites-get-by-filter'),
    path('tipos/create/', views.CreateTiposTramitesView.as_view(), name='tipos-tramites-create'),
    path('tipos/update/<str:pk>/', views.UpdateTiposTramitesView.as_view(), name='tipos-tramites-update'),
    path('tipos/delete/<str:pk>/', views.DeleteTiposTramitesView.as_view(), name='tipos-ramites-delete'),
]