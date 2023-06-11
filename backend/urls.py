"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Server Api Documentation",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html')),

    #USUARIOS
    path('api/users/', include('seguridad.urls.user_urls')),
    path('api/auditorias/', include('seguridad.urls.auditoria_urls')),
    path('api/roles/', include('seguridad.urls.roles_urls')),
    path('api/personas/', include('seguridad.urls.personas_urls')), 
    path('api/permisos/', include('seguridad.urls.permisos_urls')),
    path('api/choices/', include('seguridad.urls.choices_urls')),
    path('api/listas/', include('seguridad.urls.listas_urls')),

    path('api/almacen/',include('almacen.urls.generics_urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    path('short/', include('seguridad.urls.shortener_urls')),

    #TRANSVERSAL
    path('api/transversal/choices/', include('transversal.urls.choices_urls')),
    path('api/transversal/vinculacion/',include('transversal.urls.vinculacion_urls')),
    path('api/transversal/organigrama/', include('transversal.urls.organigrama_urls')),

    #GESTOR DOCUMENTAL
    path('api/gestor/ccd/', include('gestion_documental.urls.ccd_urls')),
    path('api/gestor/activar/', include('gestion_documental.urls.finalizar_urls')),
    path('api/gestor/trd/', include('gestion_documental.urls.trd_urls')),
    path('api/gestor/tca/', include('gestion_documental.urls.tca_urls')),
    path('api/gestor/choices/', include('gestion_documental.urls.choices_urls')),
    path('api/gestor/ventanilla/',include('gestion_documental.urls.ventanilla_urls')),
    
    #ALMACEN
    path('api/almacen/hoja-de-vida/', include('almacen.urls.hoja_de_vida_urls')),
    path('api/almacen/bienes/', include('almacen.urls.bienes_urls')),
    path('api/almacen/solicitudes/', include('almacen.urls.solicitudes_urls')),
    path('api/almacen/solicitudes-vivero/', include('almacen.urls.solicitudes_viveros_urls')),
    path('api/almacen/despachos-vivero/', include('almacen.urls.despachos_viveros_urls')),
    path('api/almacen/despachos/', include('almacen.urls.despachos_urls')),
    path('api/almacen/entregas/', include('almacen.urls.entregas_urls')),
    path('api/almacen/choices/', include('almacen.urls.choices_urls')),
    path('api/almacen/mantenimientos/', include('almacen.urls.mantenimientos_urls')),
    path('api/almacen/vehiculos/', include('almacen.urls.vehiculos_urls')),
    
    # CONSERVACIÓN
    path('api/conservacion/choices/', include('conservacion.urls.choices_urls')),
    path('api/conservacion/viveros/', include('conservacion.urls.viveros_urls')),
    path('api/conservacion/despachos/', include('conservacion.urls.despachos_urls')),
    path('api/conservacion/etapas/', include('conservacion.urls.etapas_urls')),
    path('api/conservacion/camas-siembras/', include('conservacion.urls.camas_siembras_urls')),
    path('api/conservacion/traslados/', include('conservacion.urls.traslados_urls')),
    path('api/conservacion/ingreso-cuarentena/', include('conservacion.urls.ingreso_cuarentena_urls')),
    path('api/conservacion/levantamiento-cuarentena/', include('conservacion.urls.levantamiento_cuarentena_urls')),
    path('api/conservacion/bajas/', include('conservacion.urls.bajas_urls')),
    path('api/conservacion/mortalidad/', include('conservacion.urls.mortalidad_urls')),
    path('api/conservacion/incidencias/', include('conservacion.urls.incidencia_urls')),
    path('api/conservacion/solicitudes/', include('conservacion.urls.solicitudes_urls')),
    path('api/conservacion/mezclas/', include('conservacion.urls.mezclas_urls')),
    path('api/conservacion/funcionario/', include('conservacion.urls.solicitudes_funcionario_coordinador_urls')),

    #ESTACIONES
    path("api/estaciones/",include('estaciones.urls.estaciones_urls')),
    path("api/estaciones/personas/",include('estaciones.urls.personas_estaciones_urls')),
    path("api/estaciones/configuracion/alertas/",include('estaciones.urls.configuracion_alertas_estaciones_urls')),
    path("api/estaciones/datos/", include("estaciones.urls.datos_urls")),
    path('api/estaciones/choices/', include('estaciones.urls.choices_urls')),
    path("api/estaciones/parametros/",include('estaciones.urls.parametros_urls')),
    path("api/estaciones/historial/",include('estaciones.urls.historial_alertas_urls')),
    path("api/estaciones/migracion/",include('estaciones.urls.migracion_estaciones_urls')),

    #FACILIDADES PAGOS
    path('api/recaudo/pagos/', include('recaudo.urls.pagos_urls')),
    path('api/recaudo/garantias/', include('recaudo.urls.garantias_urls')),
    path('api/recaudo/reportes/', include('recaudo.urls.reportes_urls')),

    #Recaudo
    path('api/recaudo/liquidaciones/', include('recaudo.urls.liquidaciones_urls')),
    path('api/recaudo/procesos/', include('recaudo.urls.procesos_urls')),

    #RECURSO HIDRICO
    path('api/hidrico/programas/',include('recurso_hidrico.urls.programas_urls')),

    #NOTIFICACIONES
    path('api/transversal/notificaciones/', include('transversal.urls.notificaciones_urls')),
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)