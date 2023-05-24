from django.urls import path
from recaudo.views import pagos_views as views

urlpatterns = [
    path('facilidades-pagos-deudor/<int:id>/', views.DatosDeudorView.as_view(), name='facilidades-pagos-deudor'),
    path('datos-contacto-deudor/<int:id>/', views.DatosContactoDeudorView.as_view(), name='datos-contacto-deudor'),
    path('tipos-calidad-actuacion/', views.TipoActuacionView.as_view(), name='tipos-calidad-actuacion'),
    path('crear-facilidad-pago/', views.CrearFacilidadPagoView.as_view(), name='crear-facilidad-pago'),
    path('asignar-facilidad-pago/<int:id>/', views.FacilidadPagoUpdateView.as_view(), name='asignar-facilidad-pago'),
    path('funcionarios/', views.FuncionariosView.as_view(), name='funcionarios'),
    path('listado-obligaciones/', views.ListadoObligacionesViews.as_view(),name='listado-obligaciones'),
    path('consulta-obligaciones/<int:id_obligaciones>/', views.ConsultaObligacionesViews.as_view(), name='consulta-obligaciones'),
    path('listado-deudores/', views.ListadoDeudoresViews.as_view(),name='listado-deudores'),
    path('consulta-deudores-obligaciones/<int:identificacion>/', views.ConsultaObligacionesDeudoresViews.as_view(),name='consulta-deudores-obligaciones'),
    path('listado-facilidades-pagos/', views.ListadoFacilidadesPagoViews.as_view(),name='listado-facilidades-pagos'),
    path('consulta-facilidades-pagos/<int:id>/', views.ConsultaFacilidadesPagosViews.as_view(), name='consulta-facilidades'),
    path('listado-facilidades-funcionarios/', views.ListadoFacilidadesPagoFuncionariosViews.as_view(), name='listado-facilidades-funcionario'),
    path('autorizacion-notificaciones/<int:pk>/', views.AutorizacionNotificacionesView.as_view(), name='autorizacion-notificaciones'),
    path('requisitos-actuacion/<int:id>/', views.RequisitosActuacionView.as_view(), name='requisitos-actuacion'),
    path('cumplimiento-requisitos/', views.AgregarDocumentosRequisitosView.as_view(), name='cumplimiento-requisitos'),
    path('cumplimiento-requisitos-cargados/<int:id>/', views.DocumentosRequisitosView.as_view(), name='cumplimiento-requisitos-cargados'),
    path('respuesta-funcionario/', views.RespuestaSolicitudFacilidadView.as_view(), name='respuesta-funcionario'),
    
    ]
    