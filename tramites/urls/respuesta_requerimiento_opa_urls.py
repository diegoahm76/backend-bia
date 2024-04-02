

from django.urls import path
from tramites.views import respuesta_requerimiento_opa_views as views


#RespuestaRequerimientoOpaTramiteCreate

urlpatterns = [
    path('respuesta/create/', views.RespuestaRequerimientoOpaTramiteCreate.as_view(), name='crear-requerimiento'),

]