from django.urls import path
from recaudo.views import pagos_views as views

urlpatterns = [

    path('listado-obligaciones/', views.ListadoObligacionesViews.as_view(),name='listado-obligaciones'),
    path('listado-deudores/', views.ListadoDeudoresViews.as_view(),name='listado-deudores'),
    path('consulta-deudores-obligaciones/<int:identificacion>/', views.ConsultaObligacionesDeudoresViews.as_view(),name='consulta-deudores-obligaciones'),
    path('facilidades-pagos-deudor/<int:id>/', views.DatosDeudorView.as_view(), name='facilidades-pagos-deudor'), 
    path('consulta-obligaciones/<int:id_obligaciones>/', views.ConsultaObligacionesViews.as_view(), name='consulta-obligaciones'),
    path('consulta-facilidades-pagos/<int:id>/', views.ConsultaFacilidadesPagosViews.as_view(), name='consulta-facilidades'),
    path('cumplimiento-requisitos-cargados/<int:id>/', views.DocumentosRequisitosView.as_view(), name='cumplimiento-requisitos-cargados'),
    path('respuesta-funcionario/', views.RespuestaSolicitudFacilidadView.as_view(), name='respuesta-funcionario'),
    
    ]
    