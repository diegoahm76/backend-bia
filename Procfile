web: python manage.py makemigrations almacen conservacion gestion_documental seguridad transversal recaudo && python manage.py makemigrations && python manage.py migrate && python manage.py makemigrations estaciones && python manage.py migrate estaciones --database=bia-estaciones && python manage.py loaddata paises_fixtures.json departamentos_fixtures.json municipios_fixtures.json estadocivil_fixtures.json clases_tercero_fixtures.json operaciones_sobre_usuario_fixtures.json tipodocumento_fixtures.json estructura_menus_fixtures.json modulos_fixtures.json permisos_fixtures.json roles_fixtures.json permisos_modulo_fixtures.json permisos_modulo_rol_fixtures.json sexo_fixtures.json persona_fixtures.json usuario_fixtures.json usuarios_rol_fixtures.json estados_articulo_fixtures.json magnitudes_fixtures.json porcentajes_iva_fixtures.json unidades_medidas_fixtures.json tipos_medios_doc_fixture.json formatos_tipos_medio.json tipos_activo_fixtures.json tipos_depreciacion_activos_fixtures.json metodos_valoracion_articulos_fixtures.json tipos_entrada_fixtures.json permisos_gd_fixtures.json cod_disposicion_final_fixtures.json && gunicorn backend.wsgi --timeout 120 --log-file -