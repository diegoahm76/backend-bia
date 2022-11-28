import pytest
from django.urls import reverse

from django.core.management import call_command

@pytest.fixture(scope='session')
def django_db_setup(django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tipodocumento_fixtures.json')
        call_command('loaddata', 'estadocivil_fixtures.json')
        call_command('loaddata', 'persona_fixtures.json')
        #call_command('loaddata', 'usuario_fixtures.json')

@pytest.mark.django_db
def test_get_estado_civil(client):
    url = reverse('estado-civil-get')
    response = client.get(url)
    
    assert response.status_code == 200
    
@pytest.mark.django_db
def test_register_persona(client):
    url = reverse('persona-juridica-register')
    content_type = 'application/json'
    data = {
        "tipo_persona": "J",
        "tipo_documento": "NU",
        "numero_documento": "1006856542",
        "digito_verificacion": '',
        "nombre_comercial": "isamc",
        "razon_social": "macarenia",
        "email": "prieto-ruben@javeriana.edu.co",
        "email_empresarial": '',
        "telefono_celular": "+573144198170",
        "direccion_notificaciones": "sdfsdfsdfsdfs",
        "direccion_residencia": '',
        "pais_residencia": '',
        "municipio_residencia": '',
        "cod_municipio_notificacion_nal": '',
        "ubicacion_georeferenciada": "gfdfs",
        "telefono_celular_empresa": '',
        "telefono_empresa_2": '',
        "telefono_empresa": '',
        "acepta_notificacion_sms": True,
        "acepta_notificacion_email": True,
        "acepta_tratamiento_datos": True
    }
    
    response = client.post(url, data, content_type)
    
    print(response.data)
    
    assert response.status_code == 201
    
@pytest.mark.django_db
@pytest.mark.parametrize('execution_number', range(5))
def test_register_user(client, execution_number):
    url = reverse('register')
    content_type = 'application/json'
    data = {
        "email": "youtube_.1034@hotmail.com",
        "nombre_de_usuario": "youtube",
        "persona": 1,
        "password": "youtube12345",
        "id_usuario_creador": '',
        "tipo_usuario": "I",
        "is_active": False,
        "is_blocked": False
    }
    response = client.post(url, data, content_type)
    
    print(response.data)
    
    assert response.status_code == 201