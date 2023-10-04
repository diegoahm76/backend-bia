from django.urls import path
from recaudo.views import cobros_views as views

urlpatterns = [
    path('carteras/', views.CarteraGeneralView.as_view(), name='carteras-todos'),
]
