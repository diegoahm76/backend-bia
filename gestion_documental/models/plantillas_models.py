from django.db import models

from gestion_documental.choices import tipo_acceso_choices
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.models.trd_models import FormatosTiposMedio, TipologiasDoc
from transversal.models.organigrama_models import UnidadesOrganizacionales

class PlantillasDoc(models.Model):
    id_plantilla_doc = models.AutoField(primary_key=True, db_column='T200IdPlantillaDoc')
    nombre = models.CharField(max_length=100,unique=True, db_column='T200nombre')
    descripcion = models.CharField(max_length=255, db_column='T200descripcion', null=True, blank=True)
    id_archivo_digital = models.ForeignKey(ArchivosDigitales,on_delete=models.CASCADE,db_column='T200Id_ArchivoDigital')
    id_formato_tipo_medio = models.ForeignKey(FormatosTiposMedio,on_delete=models.CASCADE,db_column='T200Id_Formato_TipoMedio')
    asociada_a_tipologia_doc_trd = models.BooleanField(db_column='T200asociadaATipologiaDocTRD')
    id_tipologia_doc_trd = models.ForeignKey(TipologiasDoc,on_delete=models.CASCADE,db_column='T200Id_TipologiaDocTRD', null=True, blank=True)
    otras_tipologias = models.CharField(max_length=30, db_column='T200otrasTipologias', null=True, blank=True)
    codigo_formato_calidad_asociado = models.CharField(max_length=30, db_column='T200codigoFormatoCalidadAsociado')
    version_formato_calidad_asociado = models.DecimalField(max_digits=5, decimal_places=2, db_column='T200versionFormatoCalidadAsociado')
    cod_tipo_acceso = models.CharField(max_length=2,choices=tipo_acceso_choices.tipo_acceso_CHOICES, db_column='T200codTipoAcceso')
    observacion = models.CharField(max_length=255, db_column='T200observacion', null=True, blank=True)
    activa = models.BooleanField(default=True, db_column='T200activa')
    fecha_creacion = models.DateTimeField(auto_now=True, db_column='T200fechaCreacion')
    id_persona_crea_plantilla = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE, db_column='T200Id_PersonaCreaPlantilla')
    class Meta:
        db_table = 'T200PlantillasDoc'
        

    def __str__(self):
        return self.nombre

class AccesoUndsOrg_PlantillaDoc(models.Model):
    id_acceso_und_org_plantilla_doc = models.AutoField(primary_key=True, db_column='T201IdAccesoUndOrg_PlantillaDoc')
    id_plantilla_doc = models.ForeignKey(PlantillasDoc, on_delete=models.CASCADE, db_column='T201Id_PlantillaDoc')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE,db_column='T201Id_UndOrganizacional')

    class Meta:
        db_table = 'T201AccesoUndsOrg_PlantillaDoc'
        unique_together = ('id_plantilla_doc', 'id_unidad_organizacional')

    def __str__(self):
        return f'Acceso a plantilla {self.id_plantilla_doc} para unidad organizacional {self.id_und_organizacional}'
