COMANDOS

La versión de Python usada para el desarrollo del proyecto es la 3.11.0

# INSTALAR REQUIREMENTS

1. pip install -r requirements.txt

# REALIZAR MIGRACIONES DE SUBSISTEMAS ACTUALES

2. python manage.py makemigrations almacen conservacion gestion_documental seguridad 

# CARGAR FIXTURES CON DATA INICIAL

3. python manage.py loaddata estadocivil_fixtures.json clases_tercero_fixtures.json operaciones_sobre_usuario_fixtures.json tipodocumento_fixtures.json modulos_fixtures.json permisos_fixtures.json roles_fixtures.json permisos_modulo_fixtures.json permisos_modulo_rol_fixtures.json persona_fixtures.json usuario_fixtures.json usuarios_rol_fixtures.json estados_articulo_fixtures.json magnitudes_fixtures.json porcentajes_iva_fixtures.json unidades_medidas_fixtures.json tipos_medios_doc_fixture.json formatos_tipos_medio.json tipos_activo_fixtures.json tipos_depreciacion_activos_fixtures.json metodos_valoracion_articulos_fixtures.json tipos_entrada_fixtures.json permisos_gd_fixtures.json

# CORRER SERVIDOR

4. python manage.py runserver

# LINK A LA DOCUMENTACIÓN DE POSTMAN

https://documenter.getpostman.com/view/24721873/2s8YzS1Pjk