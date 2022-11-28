from django.urls import path

# Import the home view
from seguridad.views.shortener_views import redirect_url_view

appname = "shortener"

urlpatterns = [
    path('<str:shortened_part>', redirect_url_view, name='redirect'),
]