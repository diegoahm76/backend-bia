from django.urls import path
from tramites.views import tramites_views as views

urlpatterns = [
    # OPAS
    path('opa/tramites/get-list/<str:cod_tipo_permiso_ambiental>/', views.ListTramitesGetView.as_view(), name='list-tramites-get'),
    path('opa/tramites/persona-titular/get-info/<str:id_persona>/', views.PersonaTitularInfoGetView.as_view(), name='persona-titular-get-info'),
    path('opa/tramites/inicio-tramite/create/', views.InicioTramiteCreateView.as_view(), name='inicio-tramite-create'),
]