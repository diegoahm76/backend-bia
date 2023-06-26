
from django.urls import path
from transversal.views import sucursalesEmpresas_views as views


urlpatterns = [

  # Sucursales Empresas
    path('sucursales-empresa-lista/<str:id>', views.GetSucursalesEmpresasView.as_view(), name="lista-sucursales-empresa"),
    path('sucursal-empresa-id/<str:pk>/', views.getSucursalEmpresaById.as_view(), name='sucursal-empresa-id'),
    path('sucursal-empresa-crear/', views.CrearSucursalEmpresaView.as_view(), name='sucursal-empresa-register'),
    path('sucursales-empresas-actualizar/<str:id>/', views.PutSucursalEmpresa.as_view(), name='sucursal-empresa-actualizar'),
    path('sucursales-empresas-borrar/<str:id>/', views.DeleteSucursalEmpresa.as_view(), name='sucursal-empresa-borrar'),
    path('sucursales-empresas-busqueda/', views.BusquedaSucursalView.as_view(), name='sucursal-empresa-busqueda'),


    
]