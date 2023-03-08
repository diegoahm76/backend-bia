from django.urls import path
from gestion_documental.views import ventanilla_views as views
from gestion_documental.views import trd_views as views

urlpatterns = [
    path('tipologias/update/<str:id_trd>/', views.UpdateTipologiasDocumentales.as_view(), name='update-tipologias-doc')
]
