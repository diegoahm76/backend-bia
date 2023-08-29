from django.urls import path
from recaudo.views import facilidades_pagos_views as views


urlpatterns = [

    # OBLIGACIONES PARA UNA FACILIDAD DE PAGO
    path('listado-obligaciones/', views.ListadoCarteraViews.as_view(),name='listado-obligaciones'),
    path('listado-deudores/', views.ListadoDeudoresViews.as_view(),name='listado-deudores'),
    path('consulta-obligaciones-deudores/<str:identificacion>/', views.ConsultaCarteraDeudoresViews.as_view(),name='consulta-obligaciones-deudores'),
    path('consulta-obligaciones/<int:id_obligaciones>/', views.ConsultaCarteraViews.as_view(), name='consulta-obligaciones'),
    path('lista-obligaciones-ids/', views.ListaCarteraDeudorSeleccionadasIds.as_view(), name='lista-obligaciones-ids'),

    # CREAR UNA SOLICITUD DE FACILIDAD DE PAGOS
    path('datos-deudor/<int:id>/', views.DatosDeudorView.as_view(), name='datos-deudor'), 
    path('tipos-calidad-actuacion/', views.TipoActuacionView.as_view(), name='tipos-calidad-actuacion'),       
    path('datos-contacto-deudor/<int:id>/', views.DatosContactoDeudorView.as_view(), name='datos-contacto-deudor'),
    path('requisitos-actuacion/<int:id>/', views.RequisitosActuacionView.as_view(), name='requisitos-actuacion'),
    path('tipos-bienes/', views.TiposBienesView.as_view(), name='tipos-bienes'),
    path('avaluo/create/', views.AvaluoCreateView.as_view(), name='crear-avaluo'),
    path('bien/create/', views.BienCreateView.as_view(), name='crear-bien'),
    path('detalles-bien/create/', views.DetallesBienFacilidadPagoCreateView.as_view(), name='crear-detalles-bien'),
    path('garantias-facilidad/create/', views.GarantiasFacilidadCreateView.as_view(), name='crear-garantias-facilidad'),
    path('cumplimiento-requisitos/create/', views.CumplimientoRequisitosCreateView.as_view(), name='crear-cumplimiento-requisitos'),
    path('detalles-cartera/create/', views.DetallesFacilidadPagoCreateView.as_view(), name='crear-detalles-cartera'),
    path('create/', views.FacilidadPagoCreateView.as_view(), name='crear-facilidad-pago'),

    # ASIGNAR UN FUNCIONARIO A LA FACILIDAD DE PAGOS
    path('listado-administrador/list/', views.ListadoFacilidadesPagoAdminViews.as_view(),name='listado-facilidades-pagos-administrador'),
    path('listado-funcionario/list/', views.ListadoFacilidadesPagoFuncionarioViews.as_view(),name='listado-facilidades-pagos-funcionario'),
    path('funcionarios/', views.FuncionariosView.as_view(), name='funcionarios'),
    path('asignar-funcionario/put/<int:id>/', views.FacilidadPagoFuncionarioUpdateView.as_view(), name='asignar-funcionario'),

    # MOSTRAR UNA FACILIDAD DE PAGOS
    path('documentos-deudor/get/<int:id_facilidad_pago>/', views.CumplimientoRequisitosGetView.as_view(), name='documentos-deudor-facilidad-pago'),
    path('documento-garantia/get/<int:id_facilidad_pago>/', views.GarantiasFacilidadGetView.as_view(), name='documento-garantia-facilidad-pago'),
    path('bienes-deudor/get/<int:id_deudor>/', views.ListaBienesDeudorView.as_view(), name='bienes-deudor'),
    path('get-id/<int:id>/', views.FacilidadPagoGetByIdView.as_view(), name='obtener-facilidad-pago'),

    # RESPUESTA FACILIDAD DE PAGO
    path('respuesta-solicitud-funcionario/create/', views.RespuestaSolicitudFacilidadView.as_view(), name='respuesta-solicitud-funcionario'),
    path('respuesta-solicitud-funcionario/get/<int:id_facilidad_pago>/', views.RespuestaSolicitudFacilidadGetView.as_view(), name='obtener-respuesta-solicitud-funcionario'),
    path('seguimiento/', views.FacilidadesPagosSeguimientoListView.as_view(), name='seguimiento'),



]