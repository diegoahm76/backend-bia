from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionPQR, ComplementosUsu_PQR, Estados_PQR, EstadosSolicitudes, MetadatosAnexosTmp, SolicitudDeDigitalizacion, T262Radicados
from gestion_documental.serializers.permisos_serializers import DenegacionPermisosGetSerializer, PermisosGetSerializer, PermisosPostDenegacionSerializer, PermisosPostSerializer, PermisosPutDenegacionSerializer, PermisosPutSerializer, SerieSubserieUnidadCCDGetSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import AnexoArchivosDigitalesSerializer, AnexosComplementoGetSerializer, AnexosDocumentoDigitalGetSerializer, AnexosGetSerializer, AsignacionPQRGetSerializer, AsignacionPQRPostSerializer, ComplementosUsu_PQRGetSerializer, ComplementosUsu_PQRPutSerializer, Estados_PQRPostSerializer, Estados_PQRSerializer, EstadosSolicitudesGetSerializer, LiderGetSerializer, MetadatosAnexosTmpSerializerGet, PQRSDFCabezeraGetSerializer, PQRSDFDetalleSolicitud, PQRSDFGetSerializer, PQRSDFHistoricoGetSerializer, PQRSDFPutSerializer, PQRSDFTitularGetSerializer, SolicitudDeDigitalizacionGetSerializer, SolicitudDeDigitalizacionPostSerializer, UnidadesOrganizacionalesSecSubVentanillaGetSerializer
from seguridad.utils import Util
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from transversal.models.lideres_models import LideresUnidadesOrg
from django.db.models import Max
from transversal.models.organigrama_models import Organigramas, UnidadesOrganizacionales



class EstadosSolicitudesGet(generics.ListAPIView):
    serializer_class = EstadosSolicitudesGetSerializer
    queryset =EstadosSolicitudes.objects.all()
    permission_classes = [IsAuthenticated]
    def get (self, request):
        instance = self.get_queryset().filter(aplica_para_pqrsdf=True)
        instance = self.get_queryset().filter(aplica_para_pqrsdf=True, id_estado_solicitud__in=[2,3,4,5])


        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    
#PQRSDF
class PQRSDFGet(generics.ListAPIView):
    serializer_class = PQRSDFGetSerializer
    #queryset =PQRSDF.objects.all()
    queryset = PQRSDF.objects.annotate(mezcla=Concat(F('id_radicado__prefijo_radicado'), Value('-'), F('id_radicado__agno_radicado'),
                                                      Value('-'), F('id_radicado__nro_radicado'), output_field=CharField()))
                                              
    permission_classes = [IsAuthenticated]


    def get (self, request):
        tipo_busqueda = 'PQRSDF'
        data_respuesta = []
        filter={}
        
        for key, value in request.query_params.items():

            if key == 'radicado':
                if value !='':
                    filter['mezcla__icontains'] = value
            if key =='estado_actual_solicitud':
                if value != '':
                    filter['id_estado_actual_solicitud__nombre__icontains'] = value    
            if key == 'tipo_solicitud':
                if value != '':
                    tipo_busqueda = False
        
        if tipo_busqueda == 'PQRSDF':
            instance = self.get_queryset().filter(**filter).order_by('fecha_radicado')

            if not instance:
                raise NotFound("No existen registros")

            serializador = self.serializer_class(instance,many=True)
            data_respuesta = serializador.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_respuesta,}, status=status.HTTP_200_OK)
    

class PQRSDFGetDetalle(generics.ListAPIView):

    serializer_class = ComplementosUsu_PQRGetSerializer
    queryset =ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pqr):
        
        instance = self.get_queryset().filter(id_PQRSDF=pqr)
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    


        
class Estados_PQRCreate(generics.CreateAPIView):
    serializer_class = Estados_PQRPostSerializer
    queryset =Estados_PQR.objects.all()
    permission_classes = [IsAuthenticated]

    def crear_estado(self,data):
        data_in = data
        

        serializer = Estados_PQRPostSerializer(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo el estado de la solicitud', 'data':serializer.data,}, status=status.HTTP_200_OK)
    
    def post(self, request):
        respuesta = self.crear_estado(request.data)
        return respuesta
    
class Estados_PQRDelete(generics.RetrieveDestroyAPIView):
    serializer_class = Estados_PQRSerializer
    queryset = Estados_PQR.objects.all()

    @transaction.atomic
    def delete(self, id_PQRSDF):
        try:
            with transaction.atomic():
                estado_pqr = self.queryset.filter(PQRSDF = id_PQRSDF).first()
                if estado_pqr:
                    estado_pqr.delete()
                    return Response({'success':True, 'detail':'El estado del pqr ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
                else:
                    raise NotFound('No se encontró ningún estado pqr asociado al anexo')
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

class SolicitudDeDigitalizacionCreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    serializer_pqrs = PQRSDFPutSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    def post(self, request):
        fecha_actual = datetime.now()    
        pqr= PQRSDF.objects.filter(id_PQRSDF=request.data['id_pqrsdf']).first()
        if not pqr:
            raise NotFound("No existe pqrsdf")
        
        if  not pqr.requiere_digitalizacion:
            raise ValidationError("No requiere digitalizacion")
        print(pqr.id_estado_actual_solicitud)
        # if pqr.id_estado_actual_solicitud:
        #     if pqr.id_estado_actual_solicitud.id_estado_solicitud == 3:
        #         raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_pqrsdf=request.data['id_pqrsdf'])
        for solicitude in solicitudes:
            if  not solicitude.fecha_rta_solicitud:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        #CREA UN ESTADO NUEVO DE PQR T255
        data_estado = {}
        data_estado['PQRSDF'] = request.data['id_pqrsdf']
        data_estado['estado_solicitud'] = 3
        data_estado['fecha_iniEstado'] = fecha_actual
        respuesta_estado = self.creador_estados.crear_estado(self,data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['PQRSDF'] = request.data['id_pqrsdf'] 
        data_estado_asociado['estado_solicitud'] = 9
        data_estado_asociado['estado_PQR_asociado'] =data_respuesta_estado_asociado['id_estado_PQR']
        data_estado_asociado['fecha_iniEstado'] = fecha_actual
        respuesta_estado_asociado = self.creador_estados.crear_estado(self,data_estado_asociado)
        
        
        #CAMBIAMOS EL ESTADO ACTUAL DE LA PQRSDF  self.serializer_class(unidad_medida,data)
        serializador_pqrs = self.serializer_pqrs(pqr,data={'id_estado_actual_solicitud':3,'fecha_envio_definitivo_a_digitalizacion':datetime.now(),'fecha_digitalizacion_completada':datetime.now()},partial=True)
        serializador_pqrs.is_valid(raise_exception=True)
        prueba = serializador_pqrs.save()
        
       
        data_in = request.data
        data_in['fecha_solicitud'] = fecha_actual
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'estados':respuesta_estado_asociado.data['data']}, status=status.HTTP_200_OK)
    



class SolicitudDeDigitalizacionComplementoCreate(generics.CreateAPIView):
    serializer_class = SolicitudDeDigitalizacionPostSerializer
    serializer_complemento = ComplementosUsu_PQRPutSerializer
    queryset =SolicitudDeDigitalizacion.objects.all()
    permission_classes = [IsAuthenticated]
    #creador_estados = Estados_PQRCreate
    def post(self, request):
        data_in = request.data

        complemento= ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR=request.data['id_complemento_usu_pqr']).first()
        if not complemento:
            raise NotFound("No existe pqrsdf")
        
        if  not complemento.requiere_digitalizacion:
            raise ValidationError("No requiere digitalizacion")
        data_in['fecha_solicitud'] = datetime.now()
        data_in['digitalizacion_completada'] = False
        data_in['devuelta_sin_completar'] = False
        data_in['id_persona_digitalizo'] = request.user.persona.id_persona

        #print(pqr.id_estado_actual_solicitud)
        #valida si tiene solicitudess pendientes
        solicitudes = SolicitudDeDigitalizacion.objects.filter(id_complemento_usu_pqr=request.data['id_complemento_usu_pqr'])
        for solicitude in solicitudes:
            if  not solicitude.fecha_rta_solicitud:
                raise ValidationError('No se puede realizar la solicitud porque tiene pendientes')
        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        #Actualizacion de fecha de complemento
        data_complemento = {}
        data_complemento['fecha_envio_definitivo_digitalizacion'] = datetime.now()
        complemento_serializer = self.serializer_complemento(complemento,data=data_complemento,partial=True )
        complemento_serializer.is_valid(raise_exception=True)
        complemento_serializer.save()
        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'complemento':complemento_serializer.data}, status=status.HTTP_200_OK)



class CabezerasPQRSDFGet(generics.ListAPIView):
    serializer_class = PQRSDFCabezeraGetSerializer
    queryset =PQRSDF.objects.all()
    queryset_prueba = PQRSDF.objects.annotate(combinacion=Concat(F('id_radicado__prefijo_radicado'), Value('-'), F('id_radicado__agno_radicado'), Value('-'), F('id_radicado__nro_radicado'), output_field=CharField())
)
    permission_classes = [IsAuthenticated]


        
    def get (self, request):
        tipo_busqueda = 'PQRSDF'
        data_respuesta = []
        filter={}
        historico =Historico_Solicitud_PQRSDFGet()
        data_histo = []
        for key, value in request.query_params.items():

            if key == 'radicado':
                if value !='':
                    filter['combinacion__icontains'] = value
 
            if key =='estado_actual_solicitud':
                if value != '':
                    filter['id_estado_actual_solicitud__estado_solicitud__nombre__icontains'] = value    

        
        
        instance = self.queryset_prueba.filter(**filter).order_by('fecha_radicado')

        if not instance:
            raise NotFound("No existen registros")
        for x in instance:
            print(x.combinacion)
            respuesta = historico.get(self,x.id_PQRSDF)
            #print()
            data_histo.append({'cabecera':self.serializer_class(x).data,'detalle':respuesta.data['data']})

                #data_respuesta.append(historico.get(self,x.id_PQRSDF).data['data'])

            #serializador = self.serializer_class(instance,many=True)
            #data_respuesta = serializador.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_histo,}, status=status.HTTP_200_OK)


class Historico_Solicitud_PQRSDFGet(generics.ListAPIView):
    serializer_class = PQRSDFHistoricoGetSerializer
    queryset =PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pqr):

        instance =PQRSDF.objects.filter(id_PQRSDF=pqr).first()

        if not instance:
                raise NotFound("No existen registros")

        serializador = self.serializer_class(instance)
        data_respuesta = serializador.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_respuesta,}, status=status.HTTP_200_OK)



class PQRSDFInfoGet(generics.ListAPIView):
    serializer_class = AnexosGetSerializer
    queryset =PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pqr):
        data=[]
        instance =PQRSDF.objects.filter(id_PQRSDF=pqr).first()


        if not instance:
                raise NotFound("No existen registros")
        anexos_pqrs = Anexos_PQR.objects.filter(id_PQRSDF=instance)
        for x in anexos_pqrs:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)

class PQRSDFAnexoDocumentoDigitalGet(generics.ListAPIView):
    serializer_class = AnexoArchivosDigitalesSerializer
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
        archivo = meta_data.id_archivo_sistema
        serializer= self.serializer_class(archivo)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)
    

class PQRSDFAnexoMetaDataGet(generics.ListAPIView):
    serializer_class = MetadatosAnexosTmpSerializerGet
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
   
        serializer= self.serializer_class(meta_data)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)

class ComplementoPQRSDFInfoAnexosGet(generics.ListAPIView):
    serializer_class = AnexosComplementoGetSerializer
    queryset =ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
        data=[]
        instance =self.queryset.filter(idComplementoUsu_PQR=pk).first()


        if not instance:
                raise NotFound("No existen registros")
        anexos_pqrs = Anexos_PQR.objects.filter(id_complemento_usu_PQR=instance)
        for x in anexos_pqrs:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)



class ComplementoPQRSDFAnexoDocumentoDigitalGet(generics.ListAPIView):
    serializer_class = AnexoArchivosDigitalesSerializer
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
        archivo = meta_data.id_archivo_sistema
        serializer= self.serializer_class(archivo)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)
    


class ComplementoPQRSDFAnexoMetaDataGet(generics.ListAPIView):
    serializer_class = MetadatosAnexosTmpSerializerGet
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
   
        serializer= self.serializer_class(meta_data)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)
    


#ASIGNACION DE PQRSDF A SECCCION ,SUBSECCION O GRUPO
class SeccionSubseccionVentanillaGet(generics.ListAPIView):
    serializer_class = UnidadesOrganizacionalesSecSubVentanillaGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request):
        organigrama = Organigramas.objects.filter(actual=True)
        if not organigrama:
            raise NotFound('No existe ningún organigrama activado')
        if len(organigrama) > 1:
            raise PermissionDenied('Existe más de un organigrama actual, contacte a soporte')
        organigrama_actual = organigrama.first()
        #unidades_organigrama_actual = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama)

        unidades = UnidadesOrganizacionales.objects.filter(cod_agrupacion_documental__in = ['SEC','SUB'],id_organigrama=organigrama_actual.id_organigrama)
        
        
        serializer = self.serializer_class(unidades,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class SubseccionGrupoVentanillaGet(generics.ListAPIView):
    serializer_class = UnidadesOrganizacionalesSecSubVentanillaGetSerializer
    serializer_unidad = UnidadesOrganizacionalesSecSubVentanillaGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,uni):
        
        unidad = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = uni).first()
        if not unidad:
            raise NotFound("No existen registros")
        unidades = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre = unidad.id_unidad_organizacional)
        
        
        lista = list(unidades)
        lista.insert(0,unidad)
        serializer = self.serializer_class(lista,many=True)

        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    
class PersonaLiderUnidadGet(generics.ListAPIView):
    serializer_class = LiderGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,uni):
        
        unidad = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = uni).first()
        if not unidad:
            raise NotFound("No existen registros")
        
        lider = LideresUnidadesOrg.objects.filter(id_unidad_organizacional = unidad.id_unidad_organizacional).first()
        if not lider:
            raise ValidationError("No tiene lider asignado")
        if not lider.id_persona:
            raise ValidationError("No tiene lider asignado")
        serializer = self.serializer_class(lider)


        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    

class AsignacionPQRCreate(generics.CreateAPIView):
    serializer_class = AsignacionPQRPostSerializer
    queryset =AsignacionPQR.objects.all()
    permission_classes = [IsAuthenticated]
    creador_estados = Estados_PQRCreate
    def post(self, request):
        data_in = request.data

        if not 'id_pqrsdf' in data_in:
            raise ValidationError("No se envio la pqrsdf")
        
        instance= AsignacionPQR.objects.filter(id_pqrsdf = data_in['id_pqrsdf'])
        for asignacion in instance:
            #print(asignacion)
            if asignacion.cod_estado_asignacion == 'Ac':
                raise ValidationError("La solicitud  ya fue Aceptada.")
            if  not asignacion.cod_estado_asignacion:
                raise ValidationError("La solicitud esta pendiente por respuesta.")
        max_consecutivo = AsignacionPQR.objects.filter(id_pqrsdf=data_in['id_pqrsdf']).aggregate(Max('consecutivo_asign_x_pqrsdf'))

        if max_consecutivo['consecutivo_asign_x_pqrsdf__max'] == None:
             ultimo_consec= 1
        else:
            ultimo_consec = max_consecutivo['consecutivo_asign_x_pqrsdf__max'] + 1

        data_in['consecutivo_asign_x_pqrsdf'] = ultimo_consec 
        data_in['fecha_asignacion'] = datetime.now()
        data_in['id_persona_asigna'] = request.user.persona.id_persona
        data_in['cod_estado_asignacion'] = None
        data_in['asignacion_de_ventanilla'] = True


        #ASOCIAR ESTADO
        data_estado_asociado = {}
        data_estado_asociado['PQRSDF'] = request.data['id_pqrsdf'] 
        data_estado_asociado['estado_solicitud'] = 5
        #data_estado_asociado['estado_PQR_asociado'] 
        data_estado_asociado['fecha_iniEstado'] =  datetime.now()
        data_estado_asociado['persona_genera_estado'] = request.user.persona.id_persona

        respuesta_estado_asociado = self.creador_estados.crear_estado(self,data_estado_asociado)
        data_estado = respuesta_estado_asociado.data['data']
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'succes': True, 'detail':'Se creo la solicitud de digitalizacion', 'data':serializer.data,'estado':data_estado}, status=status.HTTP_200_OK)




class AsignacionPQRGet(generics.ListAPIView):
    serializer_class = AsignacionPQRGetSerializer
    queryset = AsignacionPQR.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,pqr):
        
        instance = self.get_queryset().filter(id_pqrsdf=pqr)
        if not instance:
            raise NotFound("No existen registros")
        
        serializer = self.serializer_class(instance,many=True)

        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    

##ENTREGA 99
class PQRSDFPersonaTitularGet(generics.ListAPIView):
    serializer_class = PQRSDFTitularGetSerializer
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,pqr):
        
        instance = self.get_queryset().filter(id_PQRSDF=pqr).first()
        if not instance:
            raise NotFound("No existen registros")
        persona_titular = instance.id_persona_titular 
        serializer = self.serializer_class(instance)

        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)

class PQRSDFPersonaSolicitaGet(generics.ListAPIView):
    serializer_class = PQRSDFTitularGetSerializer
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request):
        persona = request.user.persona
        

        serializer = self.serializer_class(persona)

        #return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'seccion':serializer_unidad.data,'hijos':serializer.data}}, status=status.HTTP_200_OK)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    

class PQRSDFDetalleSolicitudGet(generics.ListAPIView):
    serializer_class = PQRSDFDetalleSolicitud
    queryset = PQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,pqr):
        
        instance = self.get_queryset().filter(id_PQRSDF=pqr).first()
        if not instance:
            raise NotFound("No existen registros")
        persona_titular = instance.id_persona_titular 
        serializer = self.serializer_class(instance)

      
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    

    

