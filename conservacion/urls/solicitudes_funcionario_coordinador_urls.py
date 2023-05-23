from django.urls import path
from conservacion.views import solicitudes_funcionario_coordinador_views as views 

urlpatterns = [
    #FUNCIONARIO RESPONSABLE
    path('list-solicitudes/', views.ListSolicitudesFuncionarioView.as_view(), name='list-solicitudes-funcionario'),
    path('list-solicitudes-vencidas/', views.ListSolicitudesVencidasFuncionarioView.as_view(), name='list-solicitudes-funcionario'),
    path('get-solicitud/<str:id_solicitud>/', views.DetailSolicitudView.as_view(), name='detail-solicitud-funcionario'),
    path('procesar-solicitud-responsable/<str:id_solicitud>/', views.GestionarSolicitudSupervisorView.as_view(), name='procesar-solicitud-funcionario-responsable'),
    path('procesar-solicitud-vencida-responsable/<str:id_solicitud>/', views.GestionarSolicitudesVencidasSupervisorView.as_view(), name='procesar-solicitud-vencida-funcionario-responsable'),

    #COORDINADOR VIVEROS
    path('coordinador/list-solicitudes/', views.ListSolicitudesCoordinadorView.as_view(), name='list-solicitudes-coordinador'),
    path('coordinador/procesar-solicitud/<str:id_solicitud>/', views.GestionarSolicitudCoordinadorView.as_view(), name='procesar-solicitud-coordinador'),

]