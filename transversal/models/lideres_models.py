from django.db import models
from transversal.models.organigrama_models import UnidadesOrganizacionales

class LideresUnidadesOrg(models.Model):
    id_lider_unidad_org = models.SmallAutoField(primary_key=True, editable=False, db_column='T029IdLider_UnidadOrg')
    id_unidad_organizacional = models.OneToOneField(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T029Id_UnidadOrganizacional')
    id_persona = models.ForeignKey('seguridad.Personas', on_delete=models.SET_NULL, null=True, related_name='id_persona_lider', db_column='T029Id_Persona')
    fecha_asignacion = models.DateTimeField(auto_now_add=True, db_column='T029fechaAsignacion')
    id_persona_asigna = models.ForeignKey('seguridad.Personas', on_delete=models.CASCADE, related_name='id_persona_asigna_lider', db_column='T029Id_PersonaAsigna')
    observaciones_asignacion = models.CharField(max_length=255, db_column='T029observacionesAsignacion')

    def _str_(self):
        return str(self.id_lider_unidad_org)

    class Meta:
        db_table = 'T029Lideres_UnidadesOrg'
        verbose_name = 'Lider de Unidad Organizacional'
        verbose_name_plural = 'Lideres de Unidades Organizacionales'