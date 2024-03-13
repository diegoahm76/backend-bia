from django.urls import path
from transversal.views import personas_views as views


urlpatterns = [
    
    # Estado Civil 
    path('estado-civil/get-list/', views.GetEstadoCivil.as_view(), name="estado-civil-get"),
    path('estado-civil/get-by-id/<str:pk>/', views.GetEstadoCivilById.as_view(), name='estado-civil-id-get'),
    path('estado-civil/delete/<str:pk>/', views.DeleteEstadoCivil.as_view(), name='estado-civil-delete'),
    path('estado-civil/create/', views.RegisterEstadoCivil.as_view(), name='estado-civil-register'),
    path('estado-civil/update/<str:pk>/', views.UpdateEstadoCivil.as_view(), name='estado-civil-update'),

    # Tipo Documento 
    path('tipos-documento/get-list/', views.GetTipoDocumento.as_view(), name="tipo-documento-get"),
    path('tipos-documento/get-by-id/<str:pk>/', views.GetTipoDocumentoById.as_view(), name='tipo-documento-id-get'),
    path('tipos-documento/delete/<str:pk>/', views.DeleteTipoDocumento.as_view(), name='tipo-documento-delete'),
    path('tipos-documento/create/', views.RegisterTipoDocumento.as_view(), name='tipo-documento-register'),
    path('tipos-documento/update/<str:pk>/', views.UpdateTipoDocumento.as_view(), name='estado-civil-update'),

    # PERSONAS
    
    # - Consultas
    path('get-by-id/<str:pk>/', views.GetPersonasByID.as_view(), name='persona-id-get'),
    path('get-personas-by-document/<str:tipodocumento>/<str:numerodocumento>/', views.GetPersonasByTipoDocumentoAndNumeroDocumento.as_view(), name='persona-by-document-and-tipo-documento-get'),
    path('get-personas-filters/', views.GetPersonasByFilters.as_view(), name='get-personas-filters'),
    path('get-personas-responsible-filters/', views.GetPersonasResponsibleByFilters.as_view(), name='get-personas-responsible-filters'),
    
    # - Consultas Admin Usuarios
    
    path('get-personas-by-document-admin-user/<str:tipodocumento>/<str:numerodocumento>/', views.GetPersonasByTipoDocumentoAndNumeroDocumentoAdminUser.as_view(), name='persona-by-document-and-tipo-documento-get-admin-user'),
    path('get-personas-filters-admin-user/', views.GetPersonasByFiltersAdminUser.as_view(), name='get-personas-filters-admin-user'),
    
    path('get-persona-juridica/representante-legal/',views.GetPersonaJuridicaByRepresentanteLegal.as_view(),name='verify-persona-juridica'),
    path('buscar-historico-cambios/<str:id_persona>/', views.BusquedaHistoricoCambios.as_view(), name='buscar-historico-cambios'),
    
    # - Registros
    path('persona-natural-and-usuario/create/', views.CreatePersonaNaturalAndUsuario.as_view(), name='persona-natural-and-usuario-create'),
    path('persona-juridica-and-usuario/create/', views.CreatePersonaJuridicaAndUsuario.as_view(), name='persona-juridica-and-usuario-create'),
    # path('persona-natural/create-by-user-interno/', views.RegisterPersonaNaturalByUserInterno.as_view(), name='persona-natural-register-by-user-interno'),
    
    # - Actualizaciones
    path('persona-natural/self/update/', views.UpdatePersonaNaturalByself.as_view(), name='persona-natural-update-by-self'),
    path('persona-juridica/self/update/', views.UpdatePersonaJuridicaBySelf.as_view(), name='persona-juridica-update-by-self'),
    path('update-personas-naturales-restringidos/<str:id_persona>/', views.ActualizarPersonasNatCamposRestringidosView.as_view(), name='update-nat-restringido'),    
    path('update-personas-juridicas-restringidos/<str:id_persona>/', views.ActualizarPersonasJurCamposRestringidosView.as_view(), name='update-jur-restringido'),
    
    # path('persona-natural/user-with-permissions/update/<str:tipodocumento>/<str:numerodocumento>/', views.UpdatePersonaNaturalByUserWithPermissions.as_view(), name='persona-natural-update-by-user-with-permissions'),
    # path('persona-juridica/user-with-permissions/update/<str:tipodocumento>/<str:numerodocumento>/', views.UpdatePersonaJuridicaByUserWithPermissions.as_view(), name='persona-natural-update-by-user-with-permissions'),
    
    path('autorizacion-notificaciones-self/', views.AutorizacionNotificacionesPersonas.as_view(), name='autorizacion-notificaciones-self'),
    
    # - Empresas
    path('get-empresa-by-document/<str:tipo_documento>/<str:numero_documento>/', views.GetEmpresasByTipoDocumentoAndNumeroDocumento.as_view(), name='get-empresa-by-document'),
    path('get-empresas-filters/', views.GetEmpresasByFilters.as_view(), name='get-empresas-filters'),

    #ADMINISTRACIÓ DE PERSONAS
    path('register-persona-natural-admin-personas/', views.RegisterPersonaNaturalAdmin.as_view(), name='register-personal-natural-admin-personas'),
    path('update-persona-natural-admin-personas/<str:id_persona>/', views.UpdatePersonaNaturalAdminPersonas.as_view(), name='update-personal-natural-admin-personas'),
    path('register-persona-juridica-admin-personas/', views.RegisterPersonaJuridicaAdmin.as_view(), name='register-personal-juridica-admin-personas'),
    path('update-persona-juridica-admin-personas/<str:id_persona>/', views.UpdatePersonaJuridicaAdminPersonas.as_view(), name='update-personal-juridica-admin-personas'),
    path('get-clases-tercero-persona/<str:id_persona>/',views.GetClasesTerceroByPersona.as_view(),name='get-clases-tercero-persona'),
    # PENDIENTES POR VALIDAR
    # path('get-list/', views.GetPersonas.as_view(), name="personas-get"),
    # path('get-by-email/<str:pk>/', views.getPersonaByEmail, name='persona-email-get'),
    # path('get-personas-naturales-by-document/<str:tipodocumento>/<str:numerodocumento>/', views.GetPersonaNaturalByTipoDocumentoAndNumeroDocumento.as_view(), name='persona-natural-by-document-and-tipo-documento-get'),
    # path('get-personas-juridicas-by-document/<str:tipodocumento>/<str:numerodocumento>/', views.GetPersonaJuridicaByTipoDocumentoAndNumeroDocumento.as_view(), name='persona-juridica-by-document-and-tipo-documento-get'),
    # path('get-personas-naturales/', views.GetPersonaNatural.as_view(), name='persona-natural-get'),
    # path('get-personas-juridicas/', views.GetPersonaJuridica.as_view(), name='persona-juridica-get'),
    # path('persona-natural/usuario-externo/self/update/', views.UpdatePersonaNaturalExternoBySelf.as_view(), name='persona-natural-externa-update-by-self'),
    # path('persona-juridica/usuario-externo/self/update/', views.UpdatePersonaJuridicaExternoBySelf.as_view(), name='persona-juridica-externa-update-by-self'),
    # path('buscar-persona-natural/', views.BusquedaPersonaNaturalView.as_view(), name='buscar-persona-natural'),
    #Creacion de persona y usuario por portal
    
    # Apoderados Personas
    path('apoderados-personas/get-list/<str:id_poderdante>/', views.GetApoderadosByPoderdanteId.as_view(), name="apoderados-personas-get"),
    #path('apoderados-personas/get-by-id/<str:pk>/', views.getApoderadoPersonaById.as_view(), name='apoderado-persona-id-get'),
    #path('apoderados-personas/delete/<str:pk>/', views.deleteApoderadoPersona.as_view(), name='apoderado-persona-delete'),
    #path('apoderados-personas/update/<str:pk>/', views.updateApoderadoPersona.as_view(), name='apoderado-persona-update'),
    #path('apoderados-personas/create/', views.registerApoderadoPersona.as_view(), name='apoderado-persona-register'),
    
    # # Sucursales Empresas
    # path('sucursales-empresas/get-list/', views.getSucursalesEmpresas.as_view(), name="sucursales-empresas-get"),
    # path('sucursales-empresas/get-by-id/<str:pk>/', views.getSucursalEmpresaById.as_view(), name='sucursal-empresa-id-get'),
    # path('sucursales-empresas/delete/<str:pk>/', views.deleteSucursalEmpresa.as_view(), name='sucursal-empresa-delete'),
    # path('sucursales-empresas/update/<str:pk>/', views.updateSucursalEmpresa.as_view(), name='sucursal-empresa-update'),
    # path('sucursales-empresas/create/', views.registerSucursalEmpresa.as_view(), name='sucursal-empresa-register'),
    
    # Historico Emails
    path('historico-emails/<int:id_persona>/', views.HistoricoEmailsByIdPersona.as_view(), name="historico-emails"),
    
    # Historico Direcciones
    path('historico-direccion/<int:id_persona>/', views.HistoricoDireccionByIdPersona.as_view(), name="historico-direcciones"),
    
    # Historico Notificaciones
    path('historico-notificaciones/<int:id_persona>/', views.HistoricoAutorizacionNotificacionesByIdPersona.as_view(), name="historico-notificaciones"),
    
    # Historico Representante Legal
    path('historico-representante-legal/<int:id_persona_empresa>/', views.HistoricoRepresentLegalView.as_view(), name="historico-representante"),
    # Cargos
    path('cargos/get-list/', views.GetCargosList.as_view(), name="cargos-get"),
    path('cargos/create/', views.RegisterCargos.as_view(), name='cargos-register'),
    path('cargos/update/<str:pk>/', views.UpdateCargos.as_view(), name='cargos-update'),
    path('cargos/delete/<str:pk>/', views.DeleteCargo.as_view(), name='cargos-delete'),
      
    # Clases Tercero
    # path('clases-tercero/get-list/', views.getClasesTercero.as_view(), name="clases-tercero-get"),
    # path('clases-tercero/get-by-id/<str:pk>/', views.getClaseTerceroById.as_view(), name='clase-tercero-id-get'),
    # path('clases-tercero/delete/<str:pk>/', views.deleteClaseTercero.as_view(), name='clase-tercero-delete'),
    # path('clases-tercero/update/<str:pk>/', views.updateClaseTercero.as_view(), name='clase-tercero-update'),
    # path('clases-tercero/create/', views.registerClaseTercero.as_view(), name='clase-tercero-register'),
    
    # Clases Tercero Personas
    # path('clases-tercero-personas/get-list/', views.getClasesTerceroPersonas.as_view(), name="clases-tercero-personas-get"),
    # path('clases-tercero-personas/get-by-id/<str:pk>/', views.getClaseTerceroPersonaById.as_view(), name='clase-tercero-persona-id-get'),
    # path('clases-tercero-personas/delete/<str:pk>/', views.deleteClaseTerceroPersona.as_view(), name='clase-tercero-persona-delete'),
    # path('clases-tercero-personas/update/<str:pk>/', views.updateClaseTerceroPersona.as_view(), name='clase-tercero-persona-update'),
    # path('clases-tercero-personas/create/', views.registerClaseTerceroPersona.as_view(), name='clase-tercero-persona-register'),

    # VALIDACION
    path('validacion-token/', views.ValidacionTokenView.as_view(), name='validacion_token'),


]