from django.urls import path
from recaudo.views import pagos_views as views

urlpatterns = [
    path('facilidades-pagos-deudor/<int:id>/', views.DatosDeudorView.as_view(), name='facilidades-pagos-deudor'),
    path('calidad-actuacion/<int:id>/', views.TipoActuacionView.as_view(), name='calidad-actuacion'),
    path('crear-facilidad-pago/', views.CrearFacilidadPagoView.as_view(), name='crear-facilidad-pago'),
    path('asignar-facilidad-pago/<int:id>/', views.FacilidadPagoUpdateView.as_view(), name='asignar-facilidad-pago'),
    path('funcionarios/', views.FuncionariosView.as_view(), name='funcionarios')
]