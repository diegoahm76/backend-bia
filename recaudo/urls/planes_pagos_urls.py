from django.urls import path
from recaudo.views import planes_pagos_views as views

urlpatterns = [

    path('validacion/<int:id_facilidad_pago>/', views.PlanPagosValidationView.as_view(),name='validacion'),
    path('validacion-resolucion/<int:id_facilidad_pago>/', views.PlanPagosResolucionValidationView.as_view(),name='validacion-resolucion'),



    # path('listado-deudores/', views.ListadoDeudoresViews.as_view(),name='listado-deudores'),
    # path('consulta-obligaciones-deudores/<str:identificacion>/', views.ConsultaObligacionesDeudoresViews.as_view(),name='consulta-obligaciones-deudores'),
    # path('consulta-obligaciones/<int:id_obligaciones>/', views.ConsultaObligacionesViews.as_view(), name='consulta-obligaciones'),

    
    ]
    