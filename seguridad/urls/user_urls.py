from django.urls import path
from seguridad.views import user_views as views
from rest_framework_simplejwt.views import (TokenRefreshView)

urlpatterns = [
    
    path('login/', views.LoginApiView.as_view(), name='token_obtain_pair'),
    path('upload/', views.uploadImage, name="image-upload"),

    path('register/', views.RegisterView.as_view(), name='register'),
    path('register-externo/', views.RegisterExternoView.as_view(), name='register-externo'),
    path('update/<str:pk>/', views.UpdateUser.as_view(), name='register-users'),
    
    path('profile/', views.getUserProfile, name="users-profile"),
    path('profile/update/', views.UpdateUserProfile.as_view(), name="profile-update"),
   
    path('roles/', views.roles, name='roles'),
    path("get/", views.getUsers, name="get-users"),
    path('verify/', views.Verify.as_view(), name='verify'),
    path("get/<str:pk>/", views.getUserById, name="get-users"), 
    path('get-by-numero-documento/<str:keyword1>/<str:keyword2>/', views.GetUserByPersonDocument.as_view(), name='get-users-by-doc'),
    path('get-by-email/<str:email>/', views.GetUserByEmail.as_view(), name='get-user-by-email-person'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/<str:uidb64>/<token>/', views.PasswordTokenCheckApi.as_view(), name='password-reset-confirm'),
    path('request-reset-email/', views.RequestPasswordResetEmail.as_view(),name='request-reset-email'),
    path('pasword-reset-complete', views.SetNewPasswordApiView.as_view(),name='pasword-reset-complete'), 
    path('delegate-rol-super-usuario/<str:id_persona>/', views.AsignarRolSuperUsuario.as_view(), name='delegar-rol-super-usuario'),
    path('get-nuevo-super-usuario/<str:tipo_documento>/<str:numero_documento>/', views.GetNuevoSuperUsuario.as_view(), name='get-nuevo-super-usuario'),
    path('get-nuevo-super-usuario-filters/', views.GetNuevoSuperUsuarioFilters.as_view(),name='get-nuevo-super-usuario-filters'),
    path('get-user-by-nombre-de-usuario/',views.BusquedaNombreUsuario.as_view(),name='get-user-by-nombre-de-usuario'),
    path('get-buscar-by-id-persona/<str:id_persona>/',views.BuscarIdPersona.as_view(),name='get-buscar-id-persona'),#creado 5
    path('unblock/', views.UnblockUser.as_view(), name='unblock-user'),
    path('password-unblock-complete/', views.UnBlockUserPassword.as_view(), name='password-unblock-complete'),
    path('reenviar-correo-verificacion-usuario/<str:id_usuario>/', views.ReenviarCorreoVerificacionDeUsuario.as_view(), name='reenviar-correo-verificacion-usuario'),

    #Login
    path('login/get-list/', views.LoginListApiViews.as_view(),name='login-get'),
    path('login/get-by-id/<str:pk>/', views.LoginConsultarApiViews.as_view(),name='login-id-get'),
    #LoginErroneo
    path('login-erroneo/get-list/', views.LoginErroneoListApiViews.as_view(),name='login-erroneo-get'),
    path('login-erroneo/get-by-id/<str:pk>/', views.LoginErroneoConsultarApiViews.as_view(),name='login-erroneo-id-get'),
    path('deactivate/<str:id_persona>/', views.DeactivateUsers.as_view(),name='deactivate-user'),
    path('historico-activacion/<str:id_usuario_afectado>/', views.BusquedaHistoricoActivacion.as_view(),name='historico-activacion'),
    path('usuario/interno-a-externo/<str:id_usuario>/', views.UsuarioInternoAExterno.as_view(), name='usuario-interno-a-externo'),

    
]