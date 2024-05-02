from django.urls import path

from recaudo.views import referencia_pago_views as views


urlpatterns = [
    path('crear_configuracion/',views.ConfigTipoConsecAgnoCreateView.as_view(), name='iniciar-pago'),
    #ConfigTipoConsecAgnoGetView
    path('configuracion/<str:agno>/<str:uni>/', views.ConfigTipoConsecAgnoGetView.as_view(), name='configuracion-pago'),
    #ConfigRefPagoAgnoUpdate
    path('configuracion/update/<str:pk>/',views.ConfigRefPagoAgnoUpdate.as_view(),name ='conf-pago-actualizar'),
    path('referencia/generar/',views.GenerarRefAgnoGenerarN.as_view(),name='generar-numero-ref'),
    #RefCreateView
    path('referencia/crear/',views.RefCreateView.as_view(),name= 'crear-referencia')

]