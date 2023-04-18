# COMANDOS

# CORRER PROYECTO CON DOCKER-COMPOSE (ACTUALIZACIÓN 17/04/2023)
Se implementó dockerización en el proyecto, por lo cual ahora simplemente se debe ejecutar el siguiente comando para crear y correr los contenedores necesarios:

```bash
docker-compose up
```

Si falla, por favor eliminar la carpeta de migrations en las siguientes aplicaciones:

    - almacen/migrations/
    - conservacion/migrations/
    - estaciones/migrations/
    - gestion_documental/migrations/
    - seguridad/migrations/

Hay que tener en cuenta que en sus equipos deben tener instalado docker y docker-compose. En nuestro caso, solo fue suficiente con instalar Docker Desktop en Windows, ya que incluye todo lo necesario.

Si quieren acceder a la base de datos del contenedor, pueden probar con los siguientes datos:
```bash
# CREDENCIALES PARA DB LOCAL
BIA_DB_HOST=localhost
BIA_DB_NAME=bia
BIA_DB_PASSWORD=1234
BIA_DB_PORT=5435
BIA_DB_USER=postgres
```

# CORRER PROYECTO SIN DOCKER
La versión de Python usada para el desarrollo del proyecto es la 3.11.0

## CREAR BASES DE DATOS LOCALES

Se necesitan crear dos bases de datos locales con la siguiente información:

```bash
# CREDENCIALES PARA DB LOCAL
BIA_DB_HOST=localhost
BIA_DB_NAME=bia
BIA_DB_PASSWORD=1234
BIA_DB_PORT=5432
BIA_DB_USER=postgres
```

```bash
# CREDENCIALES PARA DB ESTACIONES LOCAL
BIA_ESTACIONES_HOST=localhost
BIA_ESTACIONES_NAME=bia_estaciones
BIA_ESTACIONES_PASSWORD=1234
BIA_ESTACIONES_PORT=5432
BIA_ESTACIONES_USER=postgres
```

Se pueden cambiar los datos siempre y cuando lo modifiquen también en sus .env respectivos.

## INSTALAR REQUIREMENTS

```bash
pip install -r requirements.txt
```

## REALIZAR MIGRACIONES DE SUBSISTEMAS ACTUALES

- Crear migraciones:
```bash
python manage.py makemigrations almacen conservacion gestion_documental seguridad estaciones
```
- Aplicar migraciones:
```bash
python manage.py migrate
```
```bash
python manage.py migrate estaciones --database=bia-estaciones
```

## CARGAR FIXTURES CON DATA INICIAL

```bash
python manage.py loaddata paises_fixtures.json departamentos_fixtures.json municipios_fixtures.json estadocivil_fixtures.json clases_tercero_fixtures.json operaciones_sobre_usuario_fixtures.json tipodocumento_fixtures.json modulos_fixtures.json permisos_fixtures.json roles_fixtures.json permisos_modulo_fixtures.json permisos_modulo_rol_fixtures.json persona_fixtures.json usuario_fixtures.json usuarios_rol_fixtures.json estados_articulo_fixtures.json magnitudes_fixtures.json porcentajes_iva_fixtures.json unidades_medidas_fixtures.json tipos_medios_doc_fixture.json formatos_tipos_medio.json tipos_activo_fixtures.json tipos_depreciacion_activos_fixtures.json metodos_valoracion_articulos_fixtures.json tipos_entrada_fixtures.json permisos_gd_fixtures.json
```

## CORRER SERVIDOR

```bash
python manage.py runserver
```

# LINK A LA DOCUMENTACIÓN DE POSTMAN

https://documenter.getpostman.com/view/24721873/2s8YzS1Pjk