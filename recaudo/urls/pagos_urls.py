from django.urls import path
from recaudo.views import pagos_views as views

urlpatterns = [
    path('facilidades-pagos-deudor/<int:id>/', views.DatosDeudorView.as_view(), name='facilidades-pagos-deudor'),
    path('tipos-calidad-actuacion/', views.TipoActuacionView.as_view(), name='tipos-calidad-actuacion'),
    path('crear-facilidad-pago/', views.CrearFacilidadPagoView.as_view(), name='crear-facilidad-pago'),
    path('asignar-facilidad-pago/<int:id>/', views.FacilidadPagoUpdateView.as_view(), name='asignar-facilidad-pago'),
    path('funcionarios/', views.FuncionariosView.as_view(), name='funcionarios'),
    path('listado-obligaciones/', views.ListadoObligacionesViews.as_view(),name='listado-obligaciones'),
    path('consulta-obligaciones/<int:id_obligaciones>/', views.ConsultaObligacionesViews.as_view(), name='consulta-obligaciones'),
    path('listado-deudores/', views.ListadoDeudoresViews.as_view(),name='listado-deudores'),
    path('consulta-deudores/<int:identificacion>/', views.ConsultaDeudoresViews.as_view(),name='consulta-deudores'),
    path('listado-facilidades-pagos/', views.ListadoFacilidadesPagoViews.as_view(),name='listado-facilidades-pagos'),
    path('consulta-facilidades-pagos/<int:id>/', views.ConsultaFacilidadesPagosViews.as_view(), name='consulta-facilidades'),
    ]
    