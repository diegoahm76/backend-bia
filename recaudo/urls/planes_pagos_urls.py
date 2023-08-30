from django.urls import path
from recaudo.views import planes_pagos_views as views

urlpatterns = [

    path('validacion/<int:id_facilidad_pago>/', views.PlanPagosValidationView.as_view(),name='validacion'),
    path('validacion-resolucion/<int:id_facilidad_pago>/', views.PlanPagosResolucionValidationView.as_view(),name='validacion-resolucion'),
    path('datos-facilidad-pago/<int:id_facilidad_pago>/', views.FacilidadPagoDatosPlanView.as_view(),name='datos-facilidad-pago'),
    path('consulta-obligaciones-facilidad/<int:id_facilidad_pago>/', views.CarteraSeleccionadaDeudorListaViews.as_view(),name='consulta-obligaciones-facilidad'),
    path('consulta-obligaciones-facilidad-modificada/<int:id_facilidad_pago>/', views.CarteraSeleccionadaModificadaDeudorListaViews.as_view(),name='consulta-obligaciones-facilidad-modificada'),
    path('plan-obligaciones-facilidad/<int:id_facilidad_pago>/', views.PlanPagosAmortizacionListaViews.as_view(),name='plan-obligaciones-facilidad'),
    path('create/', views.PlanPagosCreateView.as_view(),name='crear-plan-pagos'),
    path('get/<int:id_facilidad_pago>/', views.PlanPagosListGetView.as_view(),name='ver-plan-pagos'),
    path('cuota-by-id/get/<int:id_cuota>/', views.CuotaPlanPagoByIdView.as_view(),name='ver-cuota-by-id'),
    path('resolucion/create/', views.ResolucionPlanPagosCreateView.as_view(),name='crear-resolucion-plan-pagos'),
    path('resoluciones/get/<int:id_facilidad_pago>/', views.ResolucionPlanPagoGetView.as_view(),name='ver-resolucion-plan-pagos'),
    path('resolucion-ultima/get/<int:id_facilidad_pago>/', views.ResolucionUltimaPlanPagoGetView.as_view(),name='ver-ultima-resolucion-plan-pagos'),




    # path('listado-deudores/', views.ListadoDeudoresViews.as_view(),name='listado-deudores'),
    # path('consulta-obligaciones-deudores/<str:identificacion>/', views.ConsultaObligacionesDeudoresViews.as_view(),name='consulta-obligaciones-deudores'),
    # path('consulta-obligaciones/<int:id_obligaciones>/', views.ConsultaObligacionesViews.as_view(), name='consulta-obligaciones'),

    
    ]
    