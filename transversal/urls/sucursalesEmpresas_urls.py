
from django.urls import path
from transversal.views import sucursalesEmpresas_views as views


urlpatterns = [

  # Sucursales Empresas
    path('sucursales-empresas/get-list/', views.getSucursalesEmpresas.as_view(), name="sucursales-empresas-get"),
    path('sucursales-empresas/get-by-id/<str:pk>/', views.getSucursalEmpresaById.as_view(), name='sucursal-empresa-id-get'),
    path('sucursales-empresas/delete/<str:pk>/', views.deleteSucursalEmpresa.as_view(), name='sucursal-empresa-delete'),
    path('sucursales-empresas/update/<str:pk>/', views.updateSucursalEmpresa.as_view(), name='sucursal-empresa-update'),
    path('sucursales-empresas/create/', views.registerSucursalEmpresa.as_view(), name='sucursal-empresa-register'),
    
]