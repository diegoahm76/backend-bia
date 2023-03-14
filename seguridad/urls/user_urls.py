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
    path('profile/update-interno/', views.UpdateUserProfileInterno.as_view(), name="profile-update-interno"), 
    path('profile/update-externo/', views.UpdateUserProfileExterno.as_view(), name="profile-update-externo"), 
   
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
    path('get-nombre-super-usuario/', views.GetNombreSuperUsuario.as_view(), name='get-nombre-super-usuario'), #creado
    path('get-nuevo-super-usuario/', views.GetNuevoSuperUsuario.as_view(), name='get-nuevo-super-usuario'), #creado2
    path('get-busqueda-avanzada/', views.Busqueda_Avanzada.as_view(),name='get-busqueda-avanzada'), #creado3
    path('unblock/', views.UnblockUser.as_view(), name='unblock-user'),
    path('password-unblock-complete/', views.UnBlockUserPassword.as_view(), name='password-unblock-complete'),

    #Login
    path('login/get-list/', views.LoginListApiViews.as_view(),name='login-get'),
    path('login/get-by-id/<str:pk>/', views.LoginConsultarApiViews.as_view(),name='login-id-get'),
    #LoginErroneo
    path('login-erroneo/get-list/', views.LoginErroneoListApiViews.as_view(),name='login-erroneo-get'),
    path('login-erroneo/get-by-id/<str:pk>/', views.LoginErroneoConsultarApiViews.as_view(),name='login-erroneo-id-get'),
    path('deactivate/<str:id_persona>/', views.DeactivateUsers.as_view(),name='deactivate-user'),

    
]