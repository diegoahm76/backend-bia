from django.db import models
from gestion_documental.choices.tipo_dato_alojar_choices import tipo_dato_alojar_CHOICES

#METADATOS_PERSONALIZADOS
class MetadatosPersonalizados(models.Model):

    id_metadato_personalizado= models.AutoField(primary_key=True, db_column='T243IdMetadatoPersonalizado')
    nombre_metadato = models.CharField(max_length=30, db_column='T243nombreMetadato',unique=True)
    nombre_a_mostrar = models.CharField(max_length=50, db_column='T243nombreAMostrar')
    descripcion = models.CharField(max_length=150, db_column='T234descripcion')
    cod_tipo_dato_alojar= models.CharField(max_length=2, choices=tipo_dato_alojar_CHOICES, db_column='T243codTipoDatoAAlojar')
    longitud_dato_alojar = models.SmallIntegerField(blank=True,null=True,db_column='T234longitudDatoAAlojar')
    valor_minimo= models.IntegerField(blank=True,null=True,db_column='T243valorMinimo')
    valor_maximo = models.IntegerField(blank=True,null=True,db_column='T243valorMaximo')
    orden_aparicion= models.SmallIntegerField(db_column='T243ordenDeAparicion')
    esObligatorio= models.BooleanField(default=False, db_column='T243esObligatorio')
    aplica_para_documento= models.BooleanField(default=False, db_column='T243aplicaParaDocumento')
    aplica_para_expediente = models.BooleanField(default=False, db_column='T243aplicaParaExpediente')
    activo = models.BooleanField(default=False, db_column='T243activo')
    item_ya_usado= models.BooleanField(default=False, db_column='T243itemYaUsado')

    class Meta:
            db_table = 'T243MetadatosPersonalizados'
            verbose_name = 'Metadato Personalizado'
            verbose_name_plural = 'Metadatos Personalizados'



#LISTA_METADATOS_PERSONALIZADOS
class ListaValores_MetadatosPers(models.Model):
    
    id_lista_valor_metadato_pers= models.AutoField(primary_key=True, db_column='T244IdListaValor_MetadatoPers')
    id_metadato_personalizado = models.ForeignKey(MetadatosPersonalizados, on_delete=models.CASCADE, db_column='T244Id_MetadatoPersonalizado')
    valor_a_mostrar = models.CharField(max_length=30, db_column='T244valorAMostrar')
    orden_dentro_de_lista = models.SmallIntegerField(blank=True,null=True,db_column='T244ordenDentroDeLaLista')
 
 
    class Meta:
            db_table = 'T244ListaValores_MetadatosPers'
            verbose_name = 'Lista Valor Metadatos'
            verbose_name_plural = 'Lista De Valores De Metadatos'
            unique_together = [('id_metadato_personalizado', 'valor_a_mostrar')]


