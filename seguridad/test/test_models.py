import pytest
from transversal.models.base_models import EstadoCivil

@pytest.mark.django_db
def test_estado_civil():
    estado_civil = EstadoCivil.objects.create(
        cod_estado_civil = 'T',
        nombre = 'test',
        precargado = False
    )
    assert estado_civil.cod_estado_civil == 'T'

@pytest.mark.django_db
def test_update_estado_civil():
    estado_civil = EstadoCivil.objects.create(
        cod_estado_civil = 'T',
        nombre = 'test',
        precargado = False
    )
    estado_civil.nombre = 'test2'
    estado_civil.save()
    
    assert estado_civil.nombre == 'test2'