from django.urls import path
from tramites.views import tramites_views as views

urlpatterns = [
    # OPAS
    path('opa/tramites/get-list/<str:cod_tipo_permiso_ambiental>/', views.ListTramitesGetView.as_view(), name='list-tramites-get'),
    path('opa/tramites/persona-titular/get-info/<str:id_persona>/', views.PersonaTitularInfoGetView.as_view(), name='persona-titular-get-info'),
    path('opa/tramites/list/<str:id_persona_titular>/', views.TramiteListGetView.as_view(), name='tramite-list-get'),
    path('opa/tramites/inicio-tramite/create/', views.InicioTramiteCreateView.as_view(), name='inicio-tramite-create'),
    path('opa/tramites/inicio-tramite/update/<str:id_solicitud_tramite>/', views.InicioTramiteUpdateView.as_view(), name='inicio-tramite-update'),
    path('opa/tramites/anexos/update/<str:id_solicitud_tramite>/', views.AnexosUpdateView.as_view(), name='anexos-update'),
    path('opa/tramites/anexos/get/<str:id_solicitud_tramite>/', views.AnexosGetView.as_view(), name='anexos-get'),
    path('opa/tramites/radicar/create/<str:id_solicitud_tramite>/', views.RadicarCreateView.as_view(), name='radicar-create'),
    path('opa/tramites/radicar/volver-enviar/<str:id_solicitud_tramite>/', views.RadicarVolverEnviarGetView.as_view(), name='radicar-volver-enviar'),
]