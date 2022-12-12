# Generated by Django 4.1.3 on 2022-12-10 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cargos_Unidad_S_Ss_UndOrg_TCA',
            fields=[
                ('id_cargo_unidad_s_subserie_unidad_org_tca', models.AutoField(db_column='T221IdCargo_Unidad_S_Ss_UndOrg_TCA', editable=False, primary_key=True, serialize=False)),
                ('fecha_configuracion', models.DateTimeField(auto_now=True, db_column='T221fechaConfiguracion')),
                ('justificacion_del_cambio', models.CharField(blank=True, db_column='T221justificacionDelCambio', max_length=255, null=True)),
                ('ruta_archivo_cambio', models.FileField(blank=True, db_column='T221rutaArchivoCambio', null=True, upload_to='')),
            ],
            options={
                'verbose_name': 'Cargos unidad serie subserie unidad TCA',
                'verbose_name_plural': 'Cargos unidad serie subserie unidad TCA',
                'db_table': 'T221Cargos_Unidad_S_Ss_UndOrg_TCA',
            },
        ),
        migrations.CreateModel(
            name='CCD_Clasif_Serie_Subserie_TCA',
            fields=[
                ('id_clasif_serie_subserie_unidad_tca', models.AutoField(db_column='T215IdClasif_S_Ss_UndOrg_TCA', primary_key=True, serialize=False)),
                ('fecha_registro', models.DateTimeField(db_column='T215fechaRegistro')),
                ('justificacion_cambio', models.CharField(blank=True, db_column='T215justificacionDelCambio', max_length=255, null=True)),
                ('ruta_archivo_cambio', models.FileField(blank=True, db_column='T215rutaArchivoCambio', null=True, upload_to='')),
            ],
            options={
                'verbose_name': 'Clasificacion Serie Subserie Unidad TCA',
                'verbose_name_plural': 'Clasificacion Serie Subserie Unidad TCA',
                'db_table': 'T215Clasif_S_Ss_UndOrg_TCA',
            },
        ),
        migrations.CreateModel(
            name='ClasificacionExpedientes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_clas_expediente', models.CharField(choices=[('P', 'Público'), ('C', 'Controlado'), ('R', 'Rerservado')], db_column='T214CodClasificacionExp', max_length=1)),
                ('tipo_clasificacion', models.CharField(db_column='T214tipoClasificacion', max_length=20)),
            ],
            options={
                'verbose_name': 'Clasificacion serie sub Doc ',
                'verbose_name_plural': 'Clasificaciones serie sub Doc',
                'db_table': 'T214ClasificacionExpedientes',
            },
        ),
        migrations.CreateModel(
            name='CuadrosClasificacionDocumental',
            fields=[
                ('id_ccd', models.AutoField(db_column='T206IdCCD', editable=False, primary_key=True, serialize=False)),
                ('version', models.CharField(db_column='T206version', max_length=10, unique=True)),
                ('nombre', models.CharField(db_column='T206nombre', max_length=50, unique=True)),
                ('fecha_terminado', models.DateTimeField(blank=True, db_column='T206fechaTerminado', null=True)),
                ('fecha_puesta_produccion', models.DateTimeField(blank=True, db_column='T206fechaPuestaEnProduccion', null=True)),
                ('fecha_retiro_produccion', models.DateTimeField(blank=True, db_column='T206fechaRetiroDeProduccion', null=True)),
                ('justificacion', models.CharField(blank=True, db_column='T206justificacionNuevaVersion', max_length=255, null=True)),
                ('ruta_soporte', models.FileField(blank=True, db_column='T206rutaSoporte', null=True, upload_to='')),
                ('actual', models.BooleanField(db_column='T206actual', default=False)),
            ],
            options={
                'verbose_name': 'Cuadro Clasificacion Documental',
                'verbose_name_plural': 'Cuadros Clasificacion Documental',
                'db_table': 'T206CuadrosClasificacionDoc',
            },
        ),
        migrations.CreateModel(
            name='DisposicionFinalSeries',
            fields=[
                ('cod_disposicion_final', models.CharField(db_column='T207CodDisposicionFinal', editable=False, max_length=1, primary_key=True, serialize=False)),
                ('nombre', models.CharField(db_column='T207nombre', max_length=30)),
            ],
            options={
                'verbose_name': 'Disposición Final Serie',
                'verbose_name_plural': 'Disposición Final Series',
                'db_table': 'T207DisposicionFinalSeries',
            },
        ),
        migrations.CreateModel(
            name='FormatosTiposMedio',
            fields=[
                ('id_formato_tipo_medio', models.AutoField(db_column='T210IdFormato_TipoMedio', editable=False, primary_key=True, serialize=False)),
                ('cod_tipo_medio_doc', models.CharField(choices=[('E', 'Electrónico'), ('F', 'Físico')], db_column='T210Cod_TipoMedioDoc', max_length=1)),
                ('nombre', models.CharField(db_column='T210nombre', max_length=30)),
                ('registro_precargado', models.BooleanField(db_column='T210registroPrecargado', default=False)),
                ('activo', models.BooleanField(db_column='T210activo', default=True)),
                ('item_ya_usado', models.BooleanField(db_column='T210itemYaUsado', default=False)),
            ],
            options={
                'verbose_name': 'Formato Tipo Medio',
                'verbose_name_plural': 'Formatos Tipos Medios',
                'db_table': 'T210Formatos_TiposMedio',
            },
        ),
        migrations.CreateModel(
            name='FormatosTiposMedioTipoDoc',
            fields=[
                ('id_formato_tipomedio_tipo_doc', models.AutoField(db_column='T217IdFormato_TipoMedio_TipoDoc_TRD', editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Formatos Tipos Medio Tipologia Documental TRD',
                'verbose_name_plural': 'Formatos Tipos Medio Tipologia Documental TRD',
                'db_table': 'T217Formatos_TiposMedio_TipoDoc_TRD',
            },
        ),
        migrations.CreateModel(
            name='Historico_Clasif_S_Ss_UndOrg_TCA',
            fields=[
                ('id_historico_clasif_serie_subserie_unidad_tca', models.AutoField(db_column='T220IdHistorico_Clasif_S_Ss_UndOrg_TCA', editable=False, primary_key=True, serialize=False)),
                ('cod_clasificacion_exp', models.CharField(choices=[('P', 'Público'), ('C', 'Controlado'), ('R', 'Rerservado')], db_column='T220CodClasificacionExp', max_length=1)),
                ('fecha_inicio', models.DateTimeField(auto_now_add=True, db_column='T220fechaInicio')),
                ('justificacion_del_cambio', models.CharField(blank=True, db_column='T220justificacionDelCambio', max_length=255, null=True)),
                ('ruta_archivo_cambio', models.FileField(blank=True, db_column='T220rutaArchivoCambio', null=True, upload_to='')),
            ],
            options={
                'verbose_name': 'Historico_clasificacion serie subserie unidad org tca',
                'verbose_name_plural': 'Historico_clasificacion serie subserie unidad org tca',
                'db_table': 'T220Historico_Clasif_S_Ss_UndOrg_TCA',
            },
        ),
        migrations.CreateModel(
            name='HistoricoCargosUnidadSerieSubserieUnidadTCA',
            fields=[
                ('id_historico_cargos_unidad_s_ss_unidad_tca', models.AutoField(db_column='T223IdHistorico_Cargos_Unidad_S_Ss_UndOrg_TCA', editable=False, primary_key=True, serialize=False)),
                ('fecha_inicio', models.DateTimeField(auto_now_add=True, db_column='T223FechaIncio')),
                ('nombre_permisos', models.CharField(db_column='T223nombrePermisos', max_length=255)),
                ('justificacion', models.CharField(blank=True, db_column='T223justificacion', max_length=255, null=True)),
                ('ruta_archivo', models.FileField(blank=True, db_column='T223rutaArchivo', null=True, upload_to='')),
            ],
            options={
                'verbose_name': 'Historico Cargo Unidad Serie Subserie Unidad TCA',
                'verbose_name_plural': 'Historicos Cargos Unidades Series Subseries Unidades TCA',
                'db_table': 'T223Historico_Cargos_Unidad_S_Ss_UndOrg_TCA',
            },
        ),
        migrations.CreateModel(
            name='HistoricosSerieSubSeriesUnidadOrgTRD',
            fields=[
                ('historico_serie_subs_unidadorg_trd', models.AutoField(db_column='T219Historico_Serie_SubS_UnidadOrg_TRD', editable=False, primary_key=True, serialize=False)),
                ('cod_disposicion_final', models.CharField(db_column='T219CodDisposicionFinal', max_length=1)),
                ('digitalizacion_disp_final', models.BooleanField(db_column='T219digitalizacionDispFinal', default=False)),
                ('tiempo_retencion_ag', models.PositiveSmallIntegerField(db_column='T219tiempoRetencionAG')),
                ('tiempo_retencion_ac', models.PositiveSmallIntegerField(db_column='T219tiempoRetencionAC')),
                ('descripcion_procedimiento', models.TextField(db_column='T219descripcionProcedimiento', max_length=500)),
                ('fecha_registro_historico', models.DateTimeField(auto_now=True, db_column='T219FechaRegistroDelHisto')),
                ('justificacion', models.CharField(blank=True, db_column='T219justificacion', max_length=255, null=True)),
                ('ruta_archivo', models.CharField(blank=True, db_column='T219rutaArchivo', max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Historicos Serie SubSeries UnidadOrg TRD',
                'verbose_name_plural': 'Historicos Serie SubSeries UnidadOrg TRD',
                'db_table': 'T219Historicos_Serie_SubS_UnidadOrg_TRD',
            },
        ),
        migrations.CreateModel(
            name='PermisosCargoUnidadSerieSubserieUnidadTCA',
            fields=[
                ('id_permiso_cargo_unidad_s_ss_unidad_tca', models.AutoField(db_column='T222IdPermiso_Cargo_Unidad_S_Ss_UndOrg_TCA', editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Permiso Cargo Unidad Serie Subserie Unidad TCA',
                'verbose_name_plural': 'Permisos Cargos Unidades Series Subseries Unidades TCA',
                'db_table': 'T222Permisos_Cargo_Unidad_S_Ss_UndOrg_TCA',
            },
        ),
        migrations.CreateModel(
            name='PermisosGD',
            fields=[
                ('permisos_GD', models.AutoField(db_column='T213IdPermisosGD', editable=False, primary_key=True, serialize=False)),
                ('tipo_permiso', models.CharField(db_column='T213tipoPermiso', max_length=20)),
            ],
            options={
                'verbose_name': 'Permiso GD',
                'verbose_name_plural': 'Permisos GD',
                'db_table': 'T213PermisosGD',
            },
        ),
        migrations.CreateModel(
            name='SeriesDoc',
            fields=[
                ('id_serie_doc', models.AutoField(db_column='T203IdSerieDocCCD', editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(db_column='T203nombre', max_length=200)),
                ('codigo', models.PositiveBigIntegerField(db_column='T203codigo')),
            ],
            options={
                'verbose_name': 'Serie',
                'verbose_name_plural': 'Series',
                'db_table': 'T203SeriesDoc_CCD',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='SeriesSubseriesUnidadOrg',
            fields=[
                ('id_serie_subserie_doc', models.AutoField(db_column='T205IdSerieSubserieDoc', editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Serie Subserie Unidad',
                'verbose_name_plural': 'Series Subseries Unidades',
                'db_table': 'T205Series_Subseries_UnidadOrg_CCD',
            },
        ),
        migrations.CreateModel(
            name='SeriesSubSUnidadOrgTRD',
            fields=[
                ('id_serie_subs_unidadorg_trd', models.AutoField(db_column='T218IdSerie_SubS_UnidadOrg_TRD', editable=False, primary_key=True, serialize=False)),
                ('cod_disposicion_final', models.CharField(blank=True, choices=[('CT', 'Conservación Total'), ('E', 'Eliminación'), ('S', 'Selección')], db_column='T218Cod_DisposicionFinal', max_length=20, null=True)),
                ('digitalizacion_dis_final', models.BooleanField(blank=True, db_column='T218digitalizacionDispFinal', null=True)),
                ('tiempo_retencion_ag', models.PositiveSmallIntegerField(blank=True, db_column='T218tiempoRetencionAG', null=True)),
                ('tiempo_retencion_ac', models.PositiveSmallIntegerField(blank=True, db_column='T218tiempoRetencionAC', null=True)),
                ('descripcion_procedimiento', models.TextField(blank=True, db_column='T218descripcionProcedimiento', max_length=500, null=True)),
                ('fecha_registro', models.DateTimeField(auto_now=True, db_column='T218fechaRegistro')),
                ('justificacion_cambio', models.CharField(blank=True, db_column='T218JustificacionCambio', max_length=255, null=True)),
                ('ruta_archivo_cambio', models.FileField(blank=True, db_column='T218RutaArchivoCambio', null=True, upload_to='')),
            ],
            options={
                'verbose_name': 'Series Subseries Unidades Organizacionales TRD',
                'db_table': 'T218Series_SubS_UnidadOrg_TRD',
            },
        ),
        migrations.CreateModel(
            name='SeriesSubSUnidadOrgTRDTipologias',
            fields=[
                ('id_serie_subserie_tipologia', models.AutoField(db_column='T211IdSerieSubserieTipologia', editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Series SubSeries Unidad Organizacional TRD Tipologias',
                'verbose_name_plural': 'Series SubSeries Unidad Organizacional TRD Tipologias',
                'db_table': 'T211Series_SubS_UnidadOrg_TRD_Tipologias',
            },
        ),
        migrations.CreateModel(
            name='SubseriesDoc',
            fields=[
                ('id_subserie_doc', models.AutoField(db_column='T204IdSubserieDocCCD', editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(db_column='T204nombre', max_length=200)),
                ('codigo', models.PositiveBigIntegerField(db_column='T204codigo')),
            ],
            options={
                'verbose_name': 'Subserie',
                'verbose_name_plural': 'Subseries',
                'db_table': 'T204SubseriesDoc_CDD',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='TablaRetencionDocumental',
            fields=[
                ('id_trd', models.AutoField(db_column='T212IdTRD', editable=False, primary_key=True, serialize=False)),
                ('version', models.CharField(db_column='T212version', max_length=10, unique=True)),
                ('nombre', models.CharField(db_column='T212nombre', max_length=50, unique=True)),
                ('fecha_terminado', models.DateTimeField(blank=True, db_column='T212fechaTerminado', null=True)),
                ('fecha_puesta_produccion', models.DateTimeField(blank=True, db_column='T212fechaPuestaEnProduccion', null=True)),
                ('fecha_retiro_produccion', models.DateTimeField(blank=True, db_column='T212fechaRetiroDeProduccion', null=True)),
                ('justificacion', models.CharField(blank=True, db_column='T212justificacionNuevaVersion', max_length=255, null=True)),
                ('ruta_soporte', models.FileField(blank=True, db_column='T212rutaSoporte', null=True, upload_to='')),
                ('actual', models.BooleanField(db_column='T212actual', default=False)),
                ('cambios_por_confirmar', models.BooleanField(db_column='T212cambiosPorConfirmar', default=False)),
            ],
            options={
                'verbose_name': 'Tabla de Retención Documental',
                'verbose_name_plural': 'Tablas de Retención Documental',
                'db_table': 'T212TablasRetencionDoc',
            },
        ),
        migrations.CreateModel(
            name='TablasControlAcceso',
            fields=[
                ('id_tca', models.AutoField(db_column='T216IdTCA', editable=False, primary_key=True, serialize=False)),
                ('version', models.CharField(db_column='T216version', max_length=30, unique=True)),
                ('nombre', models.CharField(db_column='T216nombre', max_length=200, unique=True)),
                ('fecha_terminado', models.DateTimeField(blank=True, db_column='T216fechaTerminado', null=True)),
                ('fecha_puesta_produccion', models.DateTimeField(blank=True, db_column='T216fechaPuestaEnProduccion', null=True)),
                ('fecha_retiro_produccion', models.DateTimeField(blank=True, db_column='T216fechaRetiroDeProduccion', null=True)),
                ('justificacion_nueva_version', models.CharField(blank=True, db_column='T216justificacionNuevaVersion', max_length=255, null=True)),
                ('ruta_soporte', models.FileField(blank=True, db_column='T216rutaSoporte', null=True, upload_to='')),
                ('actual', models.BooleanField(db_column='T216actual', default=False)),
            ],
            options={
                'verbose_name': 'Tabla de control de acceso',
                'verbose_name_plural': 'Tablas de control de acceso',
                'db_table': 'T216TablasControlAcceso',
            },
        ),
        migrations.CreateModel(
            name='TipologiasDocumentales',
            fields=[
                ('id_tipologia_documental', models.AutoField(db_column='T208IdTipologiaDoc_TRD', editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(db_column='T208nombre', max_length=10)),
                ('codigo', models.PositiveSmallIntegerField(db_column='T208codigo')),
                ('cod_tipo_medio_doc', models.CharField(choices=[('E', 'Electrónico'), ('F', 'Físico'), ('H', 'Híbrido')], db_column='T208Cod_TipoMedioDoc', max_length=1)),
                ('activo', models.BooleanField(db_column='T208activo', default=True)),
                ('justificacion_desactivacion', models.CharField(blank=True, db_column='T208justificacionDesactivacion', max_length=255, null=True)),
                ('fecha_desactivacion', models.DateTimeField(blank=True, db_column='T208FechaDesactivacion', null=True)),
            ],
            options={
                'verbose_name': 'Tipologia Documental',
                'verbose_name_plural': 'Tipologias Documentales',
                'db_table': 'T208TipologiasDocumentales',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='TiposMediosDocumentos',
            fields=[
                ('cod_tipo_medio_doc', models.CharField(db_column='T209CodTipoMedioDoc', editable=False, max_length=1, primary_key=True, serialize=False)),
                ('nombre', models.CharField(db_column='T209nombre', max_length=11)),
            ],
            options={
                'verbose_name': 'Tipo Medio Documento',
                'verbose_name_plural': 'Tipos Medios Documentos',
                'db_table': 'T209TiposMediosDocumentos',
            },
        ),
    ]
