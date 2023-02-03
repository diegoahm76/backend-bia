from django.urls import path
from seguridad.views import roles_views as views

urlpatterns = [
    path('get-list/', views.GetRol.as_view(), name='roles'),
    path('get-by-id/<int:pk>/', views.GetRolById.as_view(), name='rol-id'),
    path('get-by-name/', views.GetRolByName.as_view(), name='rol-name'),
    path('create/', views.RegisterRol.as_view(), name='rol-register'),
    path('update/<int:pk>/', views.UpdateRol.as_view(), name='rol-update'),
    path('delete/<int:id_rol>/', views.DeleteRol.as_view(), name='rol-delete'),  
    path('delete_rol_de_usuario/<int:pk>/', views.DeleteUserRol.as_view(), name='rol-delete'),  
    path('detail_roles_usuario/', views.GetRolesByUser.as_view(), name='roles-por-usuario-ver'),
    path('detail_usuarios_rol/', views.GetUsersByRol.as_view(), name='usuarios-por-rol-ver'),
    path('get-roles-by-id-usuario/<str:id_usuario>/', views.GetRolesByIdPersona.as_view(), name='get-roles-by-id-usuario'),
    
    
]