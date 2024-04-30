from django.urls import path

from recaudo.views import referencia_pago_views as views


urlpatterns = [
    path('crear_configuracion/',views.ConfigTipoConsecAgnoCreateView.as_view(), name='iniciar-pago'),
    #ConfigTipoConsecAgnoGetView
    path('configuracion/<str:agno>/<str:uni>/', views.ConfigTipoConsecAgnoGetView.as_view(), name='configuracion-pago'),

]