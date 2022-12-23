from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('almacen', '0002_initial'),
        ('seguridad', '0001_initial'),
        ('gestion_documental', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipologiasdocumentales',
            name='id_persona_desactiva',
            field=models.ForeignKey(blank=True, db_column='T208Id_PersonaQueDesactiva', null=True, on_delete=django.db.models.deletion.SET_NULL, to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='tipologiasdocumentales',
            name='id_trd',
            field=models.ForeignKey(db_column='T208Id_TRD', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.tablaretenciondocumental'),
        ),
        migrations.AddField(
            model_name='tablascontrolacceso',
            name='id_ccd',
            field=models.ForeignKey(db_column='T216Id_CCD', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.cuadrosclasificaciondocumental'),
        ),
        migrations.AddField(
            model_name='tablaretenciondocumental',
            name='id_ccd',
            field=models.ForeignKey(db_column='T212Id_CCD', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.cuadrosclasificaciondocumental'),
        ),
        migrations.AddField(
            model_name='subseriesdoc',
            name='id_ccd',
            field=models.ForeignKey(db_column='T204Id_CCD', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.cuadrosclasificaciondocumental'),
        ),
        migrations.AddField(
            model_name='seriessubsunidadorgtrdtipologias',
            name='id_serie_subserie_unidadorg_trd',
            field=models.ForeignKey(db_column='T211IdSerie_SubS_UnidadOrg_TRD', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.seriessubsunidadorgtrd'),
        ),
        migrations.AddField(
            model_name='seriessubsunidadorgtrdtipologias',
            name='id_tipologia_doc',
            field=models.ForeignKey(db_column='T211IdTipologiaDoc_TRD', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.tipologiasdocumentales'),
        ),
        migrations.AddField(
            model_name='seriessubsunidadorgtrd',
            name='id_serie_subserie_doc',
            field=models.ForeignKey(db_column='T218Id_SerieSubserieDoc', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.seriessubseriesunidadorg'),
        ),
        migrations.AddField(
            model_name='seriessubsunidadorgtrd',
            name='id_trd',
            field=models.ForeignKey(db_column='T2018Id_TRD', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.tablaretenciondocumental'),
        ),
        migrations.AddField(
            model_name='seriessubseriesunidadorg',
            name='id_serie_doc',
            field=models.ForeignKey(db_column='T205Id_SerieDocCCD', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.seriesdoc'),
        ),
        migrations.AddField(
            model_name='seriessubseriesunidadorg',
            name='id_sub_serie_doc',
            field=models.ForeignKey(blank=True, db_column='T205Id_SubserieDocCCD', null=True, on_delete=django.db.models.deletion.SET_NULL, to='gestion_documental.subseriesdoc'),
        ),
        migrations.AddField(
            model_name='seriessubseriesunidadorg',
            name='id_unidad_organizacional',
            field=models.ForeignKey(db_column='T205Id_UnidadOrganizacional', on_delete=django.db.models.deletion.CASCADE, to='almacen.unidadesorganizacionales'),
        ),
        migrations.AddField(
            model_name='seriesdoc',
            name='id_ccd',
            field=models.ForeignKey(db_column='T203Id_CCD', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.cuadrosclasificaciondocumental'),
        ),
        migrations.AddField(
            model_name='permisoscargounidadseriesubserieunidadtca',
            name='cod_permiso',
            field=models.ForeignKey(db_column='T222_Cod_Permiso', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.permisosgd'),
        ),
        migrations.AddField(
            model_name='permisoscargounidadseriesubserieunidadtca',
            name='id_cargo_unidad_s_ss_unidad_tca',
            field=models.ForeignKey(db_column='T222Id_Cargo_Unidad_S_Ss_UnidadOrg_TCA', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.cargos_unidad_s_ss_undorg_tca'),
        ),
        migrations.AddField(
            model_name='historicosseriesubseriesunidadorgtrd',
            name='id_persona_cambia',
            field=models.ForeignKey(blank=True, db_column='T219Id_PersonaCambia', null=True, on_delete=django.db.models.deletion.SET_NULL, to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='historicosseriesubseriesunidadorgtrd',
            name='id_serie_subs_unidadorg_trd',
            field=models.ForeignKey(db_column='T219IdSerie_SubS_UnidadOrg_TRD', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.seriessubsunidadorgtrd'),
        ),
        migrations.AddField(
            model_name='historicocargosunidadseriesubserieunidadtca',
            name='id_cargo_unidad_s_ss_unidad_tca',
            field=models.ForeignKey(db_column='T223Id_Cargo_Unidad_S_Ss_UndOrg_TCA', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.cargos_unidad_s_ss_undorg_tca'),
        ),
        migrations.AddField(
            model_name='historicocargosunidadseriesubserieunidadtca',
            name='id_persona_cambia',
            field=models.ForeignKey(db_column='T223Id_PersonaCambia', on_delete=django.db.models.deletion.CASCADE, to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='historico_clasif_s_ss_undorg_tca',
            name='id_clasif_s_ss_unidad_tca',
            field=models.ForeignKey(db_column='T220Id_Clasif_S_Ss_UndOrg_TCA', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.clasif_serie_subserie_unidad_tca'),
        ),
        migrations.AddField(
            model_name='historico_clasif_s_ss_undorg_tca',
            name='id_persona_cambia',
            field=models.ForeignKey(db_column='T220Id_personaCambia', on_delete=django.db.models.deletion.CASCADE, to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='formatostiposmediotipodoc',
            name='id_formato_tipo_medio',
            field=models.ForeignKey(db_column='T217Id_Formato_TipoMedio', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.formatostiposmedio'),
        ),
        migrations.AddField(
            model_name='formatostiposmediotipodoc',
            name='id_tipologia_doc',
            field=models.ForeignKey(db_column='T217Id_TipologiaDoc', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.tipologiasdocumentales'),
        ),
        migrations.AlterUniqueTogether(
            name='formatostiposmedio',
            unique_together={('cod_tipo_medio_doc', 'nombre')},
        ),
        migrations.AddField(
            model_name='cuadrosclasificaciondocumental',
            name='id_organigrama',
            field=models.ForeignKey(db_column='T206Id_Organigrama', on_delete=django.db.models.deletion.CASCADE, to='almacen.organigramas'),
        ),
        migrations.AddField(
            model_name='clasif_serie_subserie_unidad_tca',
            name='id_serie_subserie_unidad',
            field=models.ForeignKey(db_column='T215Id_SerieSubserieUnidadOrg', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.seriessubseriesunidadorg'),
        ),
        migrations.AddField(
            model_name='clasif_serie_subserie_unidad_tca',
            name='id_tca',
            field=models.ForeignKey(db_column='T215Id_TCA', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.tablascontrolacceso'),
        ),
        migrations.AddField(
            model_name='cargos_unidad_s_ss_undorg_tca',
            name='id_cargo_persona',
            field=models.ForeignKey(db_column='T221Id_CargoPersona', on_delete=django.db.models.deletion.CASCADE, to='seguridad.cargos'),
        ),
        migrations.AddField(
            model_name='cargos_unidad_s_ss_undorg_tca',
            name='id_clasif_serie_subserie_unidad_tca',
            field=models.ForeignKey(db_column='T221Id_Clasif_S_Ss_UndOrg_TCA', on_delete=django.db.models.deletion.CASCADE, to='gestion_documental.clasif_serie_subserie_unidad_tca'),
        ),
        migrations.AddField(
            model_name='cargos_unidad_s_ss_undorg_tca',
            name='id_unidad_org_cargo',
            field=models.ForeignKey(db_column='T221Id_UnidadOrgCargo', on_delete=django.db.models.deletion.CASCADE, to='almacen.unidadesorganizacionales'),
        ),
        migrations.AlterUniqueTogether(
            name='tipologiasdocumentales',
            unique_together={('id_trd', 'codigo')},
        ),
        migrations.AlterUniqueTogether(
            name='subseriesdoc',
            unique_together={('id_ccd', 'codigo')},
        ),
        migrations.AlterUniqueTogether(
            name='seriessubsunidadorgtrdtipologias',
            unique_together={('id_serie_subserie_unidadorg_trd', 'id_tipologia_doc')},
        ),
        migrations.AlterUniqueTogether(
            name='seriessubsunidadorgtrd',
            unique_together={('id_trd', 'id_serie_subserie_doc')},
        ),
        migrations.AlterUniqueTogether(
            name='permisoscargounidadseriesubserieunidadtca',
            unique_together={('id_permiso_cargo_unidad_s_ss_unidad_tca', 'cod_permiso')},
        ),
        migrations.AlterUniqueTogether(
            name='clasif_serie_subserie_unidad_tca',
            unique_together={('id_tca', 'id_serie_subserie_unidad')},
        ),
        migrations.AlterUniqueTogether(
            name='cargos_unidad_s_ss_undorg_tca',
            unique_together={('id_unidad_org_cargo', 'id_cargo_persona')},
        ),
    ]
