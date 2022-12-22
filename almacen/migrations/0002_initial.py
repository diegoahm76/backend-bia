# Generated by Django 4.1.3 on 2022-12-22 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('almacen', '0001_initial'),
        ('seguridad', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitudesconsumibles',
            name='id_funcionario_responsable_unidad',
            field=models.ForeignKey(db_column='T081Id_FuncionarioResponsableUnidad', on_delete=django.db.models.deletion.CASCADE, related_name='funcionario_responsable_unidad', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='solicitudesconsumibles',
            name='id_persona_solicita',
            field=models.ForeignKey(db_column='T081Id_PersonaSolicita', on_delete=django.db.models.deletion.CASCADE, related_name='persona_solicita_solicitud', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='solicitudesconsumibles',
            name='id_unidad_org_del_responsable',
            field=models.ForeignKey(db_column='T081Id_UnidadOrgDelResponsable', on_delete=django.db.models.deletion.CASCADE, related_name='unidad_org_del_responsable', to='almacen.unidadesorganizacionales'),
        ),
        migrations.AddField(
            model_name='solicitudesconsumibles',
            name='id_unidad_org_del_solicitante',
            field=models.ForeignKey(db_column='T081Id_UnidadOrgDelSolicitante', on_delete=django.db.models.deletion.CASCADE, related_name='unidad_organizacional_solicitante', to='almacen.unidadesorganizacionales'),
        ),
        migrations.AddField(
            model_name='solicitudesconsumibles',
            name='id_unidad_para_la_que_solicita',
            field=models.ForeignKey(db_column='T081Id_UnidadParaLaQueSolicita', on_delete=django.db.models.deletion.CASCADE, related_name='unidad_para_la_que_solicita', to='almacen.unidadesorganizacionales'),
        ),
        migrations.AddField(
            model_name='registromantenimientos',
            name='cod_estado_anterior',
            field=models.ForeignKey(db_column='T070codEstadoAnterior', on_delete=django.db.models.deletion.CASCADE, related_name='cod_estado_anterior', to='almacen.estadosarticulo'),
        ),
        migrations.AddField(
            model_name='registromantenimientos',
            name='cod_estado_final',
            field=models.ForeignKey(db_column='T070Cod_EstadoFinal', on_delete=django.db.models.deletion.CASCADE, related_name='cod_estado_final_Registro', to='almacen.estadosarticulo'),
        ),
        migrations.AddField(
            model_name='registromantenimientos',
            name='id_articulo',
            field=models.ForeignKey(db_column='T070Id_Articulo', on_delete=django.db.models.deletion.CASCADE, to='almacen.catalogobienes'),
        ),
        migrations.AddField(
            model_name='registromantenimientos',
            name='id_persona_diligencia',
            field=models.ForeignKey(db_column='T070Id_PersonaDiligencia', on_delete=django.db.models.deletion.CASCADE, related_name='id_persona_diligencia', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='registromantenimientos',
            name='id_persona_realiza',
            field=models.ForeignKey(db_column='T070Id_PersonaRealiza', on_delete=django.db.models.deletion.CASCADE, related_name='id_persona_realiza', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='registromantenimientos',
            name='id_programacion_mtto',
            field=models.ForeignKey(blank=True, db_column='T070Id_ProgramacionMtto', null=True, on_delete=django.db.models.deletion.SET_NULL, to='almacen.programacionmantenimientos'),
        ),
        migrations.AddField(
            model_name='programacionmantenimientos',
            name='id_articulo',
            field=models.ForeignKey(db_column='T069Id_Articulo', on_delete=django.db.models.deletion.CASCADE, to='almacen.catalogobienes'),
        ),
        migrations.AddField(
            model_name='programacionmantenimientos',
            name='id_persona_anula',
            field=models.ForeignKey(blank=True, db_column='T069Id_PersonaAnula', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='persona_anula', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='programacionmantenimientos',
            name='id_persona_solicita',
            field=models.ForeignKey(blank=True, db_column='T069Id_PersonaSolicita', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='persona_solicita_programacion', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='nivelesorganigrama',
            name='id_organigrama',
            field=models.ForeignKey(db_column='T018Id_Organigrama', on_delete=django.db.models.deletion.CASCADE, to='almacen.organigramas'),
        ),
        migrations.AddField(
            model_name='itemssolicitudconsumible',
            name='id_bien',
            field=models.ForeignKey(db_column='T082Id_Bien', on_delete=django.db.models.deletion.CASCADE, to='almacen.catalogobienes'),
        ),
        migrations.AddField(
            model_name='itemssolicitudconsumible',
            name='id_solicitud_consumibles',
            field=models.ForeignKey(db_column='T082Id_SolicitudConsumibles', on_delete=django.db.models.deletion.CASCADE, to='almacen.solicitudesconsumibles'),
        ),
        migrations.AddField(
            model_name='itemssolicitudconsumible',
            name='id_unidad_medida',
            field=models.ForeignKey(db_column='T082Id_UnidadMedida', on_delete=django.db.models.deletion.CASCADE, to='almacen.unidadesmedida'),
        ),
        migrations.AddField(
            model_name='itementradaalmacen',
            name='id_bien',
            field=models.ForeignKey(db_column='T064Id_Bien', on_delete=django.db.models.deletion.CASCADE, to='almacen.catalogobienes'),
        ),
        migrations.AddField(
            model_name='itementradaalmacen',
            name='id_bodega',
            field=models.ForeignKey(db_column='T064Id_Bodega', on_delete=django.db.models.deletion.CASCADE, to='almacen.bodegas'),
        ),
        migrations.AddField(
            model_name='itementradaalmacen',
            name='id_entrada_almacen',
            field=models.ForeignKey(db_column='T064Id_EntradaAlmacen', on_delete=django.db.models.deletion.CASCADE, to='almacen.entradasalmacen'),
        ),
        migrations.AddField(
            model_name='itementradaalmacen',
            name='id_unidad_medida_vida_util',
            field=models.ForeignKey(blank=True, db_column='T064Id_UnidadMedidaVidaUtil', null=True, on_delete=django.db.models.deletion.SET_NULL, to='almacen.unidadesmedida'),
        ),
        migrations.AddField(
            model_name='itementradaalmacen',
            name='porcentaje_iva',
            field=models.ForeignKey(db_column='T064porcentajeIVA', on_delete=django.db.models.deletion.CASCADE, to='almacen.porcentajesiva'),
        ),
        migrations.AddField(
            model_name='inventario',
            name='cod_tipo_entrada',
            field=models.ForeignKey(blank=True, db_column='T062Cod_TipoEntrada', null=True, on_delete=django.db.models.deletion.SET_NULL, to='almacen.tiposentradas'),
        ),
        migrations.AddField(
            model_name='inventario',
            name='id_bien',
            field=models.ForeignKey(db_column='T062Id_Bien', on_delete=django.db.models.deletion.CASCADE, to='almacen.catalogobienes'),
        ),
        migrations.AddField(
            model_name='inventario',
            name='id_bodega',
            field=models.ForeignKey(db_column='T062Id_Bodega', on_delete=django.db.models.deletion.CASCADE, to='almacen.bodegas'),
        ),
        migrations.AddField(
            model_name='inventario',
            name='id_persona_origen',
            field=models.ForeignKey(blank=True, db_column='T062Id_PersonaOrigen', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='persona_origen', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='inventario',
            name='id_persona_responsable',
            field=models.ForeignKey(blank=True, db_column='T062Id_PersonaResponsable', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='persona_responsable', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='hojadevidavehiculos',
            name='id_articulo',
            field=models.ForeignKey(blank=True, db_column='T066Id_Articulo', null=True, on_delete=django.db.models.deletion.SET_NULL, to='almacen.catalogobienes'),
        ),
        migrations.AddField(
            model_name='hojadevidavehiculos',
            name='id_proveedor',
            field=models.ForeignKey(blank=True, db_column='T066Id_Proveedor', null=True, on_delete=django.db.models.deletion.SET_NULL, to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='hojadevidavehiculos',
            name='id_vehiculo_arrendado',
            field=models.ForeignKey(blank=True, db_column='T066Id_VehiculoArrendado', null=True, on_delete=django.db.models.deletion.SET_NULL, to='almacen.vehiculosarrendados'),
        ),
        migrations.AddField(
            model_name='hojadevidaotrosactivos',
            name='id_articulo',
            field=models.ForeignKey(db_column='T067Id_Articulo', on_delete=django.db.models.deletion.CASCADE, to='almacen.catalogobienes'),
        ),
        migrations.AddField(
            model_name='hojadevidacomputadores',
            name='id_articulo',
            field=models.ForeignKey(db_column='T065Id_Articulo', on_delete=django.db.models.deletion.CASCADE, to='almacen.catalogobienes'),
        ),
        migrations.AddField(
            model_name='entradasalmacen',
            name='id_bodega',
            field=models.ForeignKey(db_column='T063Id_BodegaGral', on_delete=django.db.models.deletion.CASCADE, to='almacen.bodegas'),
        ),
        migrations.AddField(
            model_name='entradasalmacen',
            name='id_creador',
            field=models.ForeignKey(db_column='T063Id_PersonaCrea', on_delete=django.db.models.deletion.CASCADE, related_name='persona_crea_entrada', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='entradasalmacen',
            name='id_persona_anula',
            field=models.ForeignKey(blank=True, db_column='T063Id_PersonaAnula', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='persona_anula_entrada', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='entradasalmacen',
            name='id_persona_ult_act_dif_creador',
            field=models.ForeignKey(blank=True, db_column='T063Id_PersonaUltActualizacionDifACrea', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='persona_actualiza_entrada', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='entradasalmacen',
            name='id_proveedor',
            field=models.ForeignKey(db_column='T063Id_Proveedor', on_delete=django.db.models.deletion.CASCADE, related_name='persona_provee_entrada', to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='entradasalmacen',
            name='id_tipo_entrada',
            field=models.ForeignKey(db_column='T063Cod_TipoEntrada', on_delete=django.db.models.deletion.CASCADE, to='almacen.tiposentradas'),
        ),
        migrations.AddField(
            model_name='documentosvehiculo',
            name='id_articulo',
            field=models.ForeignKey(db_column='T068Id_Articulo', on_delete=django.db.models.deletion.CASCADE, to='almacen.catalogobienes'),
        ),
        migrations.AddField(
            model_name='documentosvehiculo',
            name='id_empresa_proveedora',
            field=models.ForeignKey(blank=True, db_column='T068Id_EmpresaProveedora', null=True, on_delete=django.db.models.deletion.SET_NULL, to='seguridad.personas'),
        ),
        migrations.AddField(
            model_name='catalogobienes',
            name='id_bien_padre',
            field=models.ForeignKey(blank=True, db_column='T057Id_BienPadre', null=True, on_delete=django.db.models.deletion.SET_NULL, to='almacen.catalogobienes'),
        ),
        migrations.AddField(
            model_name='catalogobienes',
            name='id_marca',
            field=models.ForeignKey(blank=True, db_column='T057Id_Marca', null=True, on_delete=django.db.models.deletion.SET_NULL, to='almacen.marcas'),
        ),
        migrations.AddField(
            model_name='catalogobienes',
            name='id_porcentaje_iva',
            field=models.ForeignKey(db_column='T057Id_PorcentajeIVA', on_delete=django.db.models.deletion.CASCADE, to='almacen.porcentajesiva'),
        ),
        migrations.AddField(
            model_name='catalogobienes',
            name='id_unidad_medida',
            field=models.ForeignKey(db_column='T057Id_UnidadMedida', on_delete=django.db.models.deletion.CASCADE, related_name='unidad_medida', to='almacen.unidadesmedida'),
        ),
        migrations.AddField(
            model_name='catalogobienes',
            name='id_unidad_medida_vida_util',
            field=models.ForeignKey(blank=True, db_column='T057Id_UnidadMedidaVidaUtil', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='unidad_medida_vida_util', to='almacen.unidadesmedida'),
        ),
        migrations.AddField(
            model_name='bodegas',
            name='id_responsable',
            field=models.ForeignKey(db_column='T056Id_Responsable', on_delete=django.db.models.deletion.CASCADE, to='seguridad.personas'),
        ),
        migrations.AlterUniqueTogether(
            name='unidadesorganizacionales',
            unique_together={('id_organigrama', 'codigo')},
        ),
        migrations.AlterUniqueTogether(
            name='solicitudesconsumibles',
            unique_together={('es_solicitud_de_conservacion', 'nro_solicitud_por_tipo')},
        ),
        migrations.AlterUniqueTogether(
            name='nivelesorganigrama',
            unique_together={('id_organigrama', 'orden_nivel')},
        ),
        migrations.AlterUniqueTogether(
            name='itemssolicitudconsumible',
            unique_together={('id_solicitud_consumibles', 'id_bien')},
        ),
        migrations.AlterUniqueTogether(
            name='inventario',
            unique_together={('id_bien', 'id_bodega')},
        ),
        migrations.AlterUniqueTogether(
            name='documentosvehiculo',
            unique_together={('id_articulo', 'cod_tipo_documento', 'nro_documento')},
        ),
        migrations.AlterUniqueTogether(
            name='catalogobienes',
            unique_together={('codigo_bien', 'nro_elemento_bien')},
        ),
    ]
