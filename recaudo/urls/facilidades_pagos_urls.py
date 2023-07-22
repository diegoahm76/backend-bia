from django.urls import path
from recaudo.views import facilidades_pagos_views as views


urlpatterns = [

    # CREAR UNA SOLICITUD DE FACILIDAD DE PAGOS
    path('tipos-calidad-actuacion/', views.TipoActuacionView.as_view(), name='tipos-calidad-actuacion'),       
    path('datos-contacto-deudor/<int:id>/', views.DatosContactoDeudorView.as_view(), name='datos-contacto-deudor'),
    path('requisitos-actuacion/<int:id>/', views.RequisitosActuacionView.as_view(), name='requisitos-actuacion'),
    path('tipos-bienes/', views.TiposBienesView.as_view(), name='tipos-bienes'),
    path('avaluo/create/', views.AvaluoCreateView.as_view(), name='crear-avaluo'),
    path('bien/create/', views.BienCreateView.as_view(), name='crear-bien'),
    path('detalles-bien/create/', views.DetallesBienFacilidadPagoCreateView.as_view(), name='crear-detalles-bien'),
    path('garantias-facilidad/create/', views.GarantiasFacilidadCreateView.as_view(), name='crear-garantias-facilidad'),
    path('cumplimiento-requisitos/create/', views.CumplimientoRequisitosCreateView.as_view(), name='crear-cumplimiento-requisitos'),
    path('create/', views.FacilidadPagoCreateView.as_view(), name='crear-facilidad-pago'),

    # ASIGNAR UN FUNCIONARIO A LA FACILIDAD DE PAGOS
    path('listado-administrador/list/', views.ListadoFacilidadesPagoAdminViews.as_view(),name='listado-facilidades-pagos-administrador'),
    path('listado-funcionario/list/', views.ListadoFacilidadesPagoFuncionarioViews.as_view(),name='listado-facilidades-pagos-funcionario'),
    path('funcionarios/', views.FuncionariosView.as_view(), name='funcionarios'),
    path('asignar-funcionario/put/<int:id>/', views.FacilidadPagoFuncionarioUpdateView.as_view(), name='asignar-funcionario'),




    path('listar-bienes-deudor/<int:id>', views.ListaBienesDeudorView.as_view(), name='listar-bienes-deudor'),
    




]