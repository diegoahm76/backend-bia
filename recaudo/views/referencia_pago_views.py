import copy

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date, timedelta
import copy
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from django.utils import timezone
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad

from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from recaudo.models.referencia_pago_models import ConfigReferenciaPagoAgno, Referencia
from recaudo.serializers.referencia_pago_serializers import ConfigTipoRefgnoCreateSerializer, ConfigTipoRefgnoGetSerializer, ConfigTipoRefgnoPutSerializer, ReferenciaCreateSerializer
from transversal.models.organigrama_models import UnidadesOrganizacionales
from seguridad.models import Personas
from seguridad.utils import Util
from django.core.files.base import ContentFile
from gestion_documental.views.pqr_views import RadicadoCreate 
class ConfigTipoConsecAgnoCreateView(generics.CreateAPIView):
    serializer_class = ConfigTipoRefgnoCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request,):
        data_in = request.data
        usuario = request.user.persona.id_persona
        data_in['user'] = usuario #id_persona_config_implementacion
        data_in['direccion']=Util.get_client_ip(request)
        #data_in['fecha_inicial_config_implementacion'] = timezone.now()
       
        respuesta = self.crear_config_tipos_consecutivo_agno(data_in)
        return respuesta

    def crear_config_tipos_consecutivo_agno(self, data):
        data_in = data
        hoy = date.today()
        age = hoy.year

        # unidad_encargada = UnidadesOrganizacionales.objects.filter(nombre ='Oficina Asesora Jurídica' ,id_organigrama__actual=True).first()

        # catalogo = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=unidad_encargada)

        # print(catalogo)


        configuracion = ConfigReferenciaPagoAgno.objects.filter(agno_ref=data_in['agno_ref'] ).first()

        print(age)
        print(age+1)

        if 'agno_ref' in data_in:
            if data_in['agno_ref']!= age and  data_in['agno_ref']!= (age+1):
                raise ValidationError("El año debe ser el actual o el siguiente")
        else:
            raise ValidationError("El año de referencia es requerido")
        
        configuracion = ConfigReferenciaPagoAgno.objects.filter(agno_ref=data_in['agno_ref'] ).first()

        if configuracion:
            raise ValidationError("Ya existe una configuracion para este año.")

        if not data_in['id_catalogo_serie_unidad']:
             cof = ConfigReferenciaPagoAgno.objects.filter(agno_ref=data_in['agno_ref'],id_unidad= data_in['id_unidad'])
             if cof:
                 raise ValidationError("Ya existe una configuracion")
        
        if 'implementar' in data_in and data_in['implementar']:

           
   
            consecutivo_inicial = data.get('consecutivo_inicial')
            cantidad_digitos = data.get('cantidad_digitos')


            if consecutivo_inicial is None:
                raise ValidationError("Se debe asignar un consecutivo inicial.")

            if cantidad_digitos is None:
                raise ValidationError("Se deben asignar una cantidad de dígitos.")

            if cantidad_digitos <= 0:
                raise ValidationError("La cantidad de dígitos debe ser mayor a cero.")
            
            data_in['id_persona_config_implementacion']=data_in['user']
            data_in['fecha_inicial_config_implementacion'] = timezone.now()
            data_in['referencia_actual'] = consecutivo_inicial-1
   
            if 'cantidad_digitos' in data_in and data_in['cantidad_digitos']:
                if data_in['cantidad_digitos'] > 20:
                    raise ValidationError('La cantidad de digitos no puede ser mayor a 20')

            
        print(data_in)
        serializer = ConfigTipoRefgnoCreateSerializer(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()

            # id_modulo=0
            # if instance.agno_radicado==age:
            #     id_modulo=143
            # elif instance.agno_radicado==age+1:
            #     id_modulo=144

            # descripcion = {"AgnoRadicado":instance.agno_radicado,"CodTipoRadicado":instance.cod_tipo_radicado}
            # auditoria_data = {
            # "id_usuario" : data_in['user'],
            # "id_modulo" : id_modulo,
            # "cod_permiso": "CR",
            # "subsistema": 'GEST',
            # "dirip": data_in['direccion'],
            # "descripcion": descripcion, 
            # }
            # Util.save_auditoria(auditoria_data)
        #print(serializer.data)
        #raise ValidationError("Se implementó correctamente")

        return Response({
                'success': True,
                'detail': 'Se creó la configuración de los consecutivos correctamente.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)



class ConfigRefPagoAgnoUpdate(generics.UpdateAPIView):
    serializer_class = ConfigTipoRefgnoCreateSerializer
    queryset = ConfigReferenciaPagoAgno.objects.all()
    permission_classes = [IsAuthenticated]

    def actualizar_config_tipos_consecutivo_agno(self,data,pk):
        
        data_in=data
        hoy = date.today()
        age=hoy.year
        # Obtener la instancia existente para actualizar
        instance =ConfigReferenciaPagoAgno.objects.filter(agno_ref=pk).first()

        # Verificar si la instancia existe
        if not instance:
            return Response({'detail': 'La configuracion no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
        previous=copy.copy(instance)
        if instance.implementar and instance.agno_ref==age:
            raise ValidationError('No se puede modificar la configuracion de un consecutivo si se esta implementando actualmente.')
        if instance.agno_ref < age:
            raise ValidationError('No se puede modificar la configuracion de un consecutivo si es de un año anterior.')
        if 'implementar' in data_in:

            if data_in['implementar']==False and instance.implementar:
                
                 data_in['consecutivo_inicial']=None
                 data_in['cantidad_digitos']=None
            elif data_in['implementar']==True:

              
                #raise ValidationError("No se puede implementar la configuracion si ya esta vigente una de tipo unica")
              
                consecutivo_inicial = data.get('consecutivo_inicial')
                cantidad_digitos = data.get('cantidad_digitos')
                
                # Validar campos almacenados en la instancia actual

                if consecutivo_inicial is None:
                    consecutivo_inicial = instance.consecutivo_inicial
                    
                if cantidad_digitos is None:
                    cantidad_digitos = instance.cantidad_digitos

                
                if consecutivo_inicial  is None:
                    raise ValidationError("Se debe asignar un consecutivo inicial.")
                
                if cantidad_digitos is None:
                    raise ValidationError("se deben asignar una cantidad de digitos.")
                
                if cantidad_digitos <= 0:
                    raise ValidationError("se debe ser mayor a cero.")
                data_in['fecha_inicial_config_implementacion']= timezone.now()
                data_in['id_persona_config_implementacion']=data_in['user']

     

        if 'consecutivo_inicial' in data_in:
            if data_in['consecutivo_inicial']:
                data_in['consecutivo_actual']=data_in['consecutivo_inicial']-1
        if 'cantidad_digitos' in data_in and data_in['cantidad_digitos']:
            if data_in['cantidad_digitos'] > 20:
                raise ValidationError('La cantidad de digitos no puede ser mayor a 20')

        
        serializer = ConfigTipoRefgnoCreateSerializer(instance, data=data_in, partial=True)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()

            # direccion=data_in['direccion']
            # descripcion = {"AgnoRadicado":instance.agno_radicado,"CodTipoRadicado":instance.cod_tipo_radicado}
            
            # valores_actualizados = {'current': instance, 'previous': previous}
            # #print(valores_actualizados)
            # id_modulo=0
            # if instance.agno_radicado==age:
            #     id_modulo=143
            # elif instance.agno_radicado==age+1:
            #     id_modulo=144
            # auditoria_data = {
            #     "id_usuario" : data_in['user'],
            #     "id_modulo" : id_modulo,
            #     "cod_permiso": "AC",
            #     "subsistema": 'GEST',
            #     "dirip": direccion,
            #     "descripcion": descripcion, 
            #     "valores_actualizados": valores_actualizados
            # }
            # Util.save_auditoria(auditoria_data) 


        # Respuesta exitosa con los datos actualizados
        return Response({
            'success': True,
            'detail': 'Se actualizó la configuracion de los  consecutivos correctamente.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        data_in = request.data
        usuario = request.user.persona.id_persona
        #direccion=#
        data_in['user']=usuario#id_persona_config_implementacion
        data_in['direccion']=Util.get_client_ip(request)
        response= self.actualizar_config_tipos_consecutivo_agno(data_in,pk)
        return response
    



class ConfigTipoConsecAgnoGetView(generics.ListAPIView):
    serializer_class = ConfigTipoRefgnoGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = ConfigReferenciaPagoAgno.objects.all()
    
    def get(self, request,agno):
        instance = self.get_queryset().filter(agno_ref=agno)



        if not instance:
            raise NotFound('No existe registro')
        
        serializer = self.serializer_class(instance, many=True)
        
        return Response({'success':True, 'detail':'se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)



class GenerarRefAgnoGenerarN(generics.UpdateAPIView):
    serializer_class = ConfigTipoRefgnoPutSerializer
    queryset = ConfigReferenciaPagoAgno.objects.all()
    permission_classes = [IsAuthenticated]
    vista_creacion_configuracion = ConfigTipoConsecAgnoCreateView()
    def generar_n_radicado(self,data):
        
        data_in=data
        print(data_in)
        hoy = date.today()
        age=hoy.year
        # # Obtener la instancia existente para actualizar

        instance =ConfigReferenciaPagoAgno.objects.filter(agno_ref=age).first()

        if not instance:
           

            auxiliar = ConfigReferenciaPagoAgno.objects.filter(agno_ref=age).first()
            if not auxiliar:
                conf_agno_anterior = ConfigReferenciaPagoAgno.objects.filter(agno_ref=age-1).first()
                if not conf_agno_anterior:
                    raise ValidationError("No se encontro la configuracion.")
              
                nueva_configuracion = {
                                    'user':None,
                                    'direccion' : data_in['direccion'],
                                    'agno_ref':age,
                                    'consecutivo_inicial':1,
                                    'cantidad_digitos':conf_agno_anterior.cantidad_digitos,
                                    'implementar':conf_agno_anterior.implementar,
                                    'id_cat_serie_und': conf_agno_anterior.id_cat_serie_und,
                                    'id_unidad':conf_agno_anterior.id_unidad
                                    }
                respuesta = self.vista_creacion_configuracion.crear_config_tipos_consecutivo_agno(nueva_configuracion)
                if respuesta.status_code != status.HTTP_201_CREATED:
                    return respuesta

            instance =ConfigReferenciaPagoAgno.objects.filter(agno_ref=age).first()

        if not instance.implementar:
            raise ValidationError("La configuracion se encuentra pendiente")


        new_data={}
        new_data['referencia_actual'] = instance.referencia_actual+1
        new_data['id_persona_referencia_actual'] = data_in['id_persona']
        new_data['fecha_consecutivo_actual'] = data_in['fecha_actual']
       ##new_data['id_catalogo'] = data_in['id_cat_serie_und']
         
        serializer =ConfigTipoRefgnoPutSerializer(instance, data=new_data, partial=True)
        serializer.is_valid(raise_exception=True)

        ##buscamos los catalogos de serie subserie de la unidad 
        cod_se_sub = ""
        if instance.id_catalogo_serie_unidad:
            catalogos_unidad=CatalogosSeriesUnidad.objects.filter(id_cat_serie_und=instance.id_catalogo_serie_unidad).first()
            cod_serie = catalogos_unidad.id_catalogo_serie.id_serie_doc.codigo
            cod_se_sub = cod_serie
            if catalogos_unidad.id_catalogo_serie.id_subserie_doc:
                cod_subserie =catalogos_unidad.id_catalogo_serie.id_subserie_doc.codigo
                cod_se_sub = cod_serie+cod_subserie
 
            
            
        instance = serializer.save()
        print('Holaaaa'+str(instance.id_catalogo_serie_unidad))
        numero_con_ceros = str(instance.referencia_actual).zfill(instance.cantidad_digitos)
        if cod_se_sub != "":

            conseg_nuevo = instance.id_unidad.codigo+cod_se_sub+str(instance.agno_ref)[-2:]+numero_con_ceros
        else:
            conseg_nuevo = instance.id_unidad.codigo+str(instance.agno_ref)[-2:]+numero_con_ceros
        
        
        
        return Response({
            'success': True,
            'detail': 'Se actualizó la configuracion de los  consecutivos correctamente.',
            'data': {**serializer.data,'conseg_nuevo':conseg_nuevo}
        }, status=status.HTTP_200_OK)

    def put(self, request):
        data_in = request.data
        usuario = request.user.persona.id_persona
        #direccion=#
        data_in['user']=usuario#id_persona_config_implementacion
        data_in['direccion']=Util.get_client_ip(request)
        response= self.generar_n_radicado(data_in,)
        return response




class RefCreateView(generics.CreateAPIView):
    serializer_class = ReferenciaCreateSerializer
    permission_classes = [IsAuthenticated]
    vista_generadora_numero = GenerarRefAgnoGenerarN()
    vista_archivos = ArchivosDgitalesCreate()

    def post(self, request):
        data_in = request.data
        usuario = request.user.persona.id_persona

        
        respuesta = self.vista_generadora_numero.generar_n_radicado(data_in)

        if respuesta.status_code != status.HTTP_200_OK:
            return respuesta
        
        print(respuesta.data['data'])
        #raise ValidationError("AQUI VAMOS")
        data_respuesta = respuesta.data['data']

        data_consecutivo = {}
        data_consecutivo['id_unidad'] = data_respuesta['id_unidad']

   
        data_consecutivo['id_catalogo'] = data_respuesta['id_catalogo_serie_unidad']
        data_consecutivo['agno_referencia'] = data_respuesta['agno_ref']
        data_consecutivo['nro_consecutivo'] = data_respuesta['referencia_actual']
        data_consecutivo['fecha_consecutivo'] = data_respuesta['fecha_consecutivo_actual']
        data_consecutivo['id_persona_solicita'] = data_respuesta['id_persona_referencia_actual']



        archivos =request.FILES.getlist('archivo')
        data_archivo ={}
        for archivo in archivos:
                
                print(archivo)
                print(archivo.name)
                contenido = archivo.read()
                nombre_nuevo= "Archivo.pdf"
                archivo_modificado = ContentFile(contenido, name=nombre_nuevo)
                print(archivo_modificado)
            
                ruta = "home,BIA,Recaudo,referencia"
                respuesta_archivo = self.vista_archivos.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},archivo_modificado)
                data_archivo = respuesta_archivo.data['data']
                if respuesta_archivo.status_code != status.HTTP_201_CREATED:
                    return respuesta_archivo
                #print(respuesta_archivo.data['data'])
                data_archivo = respuesta_archivo.data['data']


        #RADICAR
        fecha_actual =datetime.now()
        data_radicado = {}
        data_radicado['fecha_actual'] = fecha_actual
        data_radicado['id_persona'] = request.user.persona.id_persona
        data_radicado['tipo_radicado'] = "I" #validar cual tipo de radicado
        data_radicado['modulo_radica'] = 'Respuesta del Titular a Una Solicitud sobre PQRSDF'


     
        radicadoCreate = RadicadoCreate()       
        respuesta_radicado = radicadoCreate.post(data_radicado)
        respuesta_radicado_data = respuesta_radicado
        #print(respuesta_radicado_data['radicado_nuevo'])

        data_in['id_radicado'] = respuesta_radicado['id_radicado']
        data_in['fecha_radicado'] = respuesta_radicado['fecha_radicado']
        data_consecutivo['id_archivo'] = data_archivo['id_archivo_digital']
        serializer = self.serializer_class(data=data_consecutivo)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'succes': True, 'detail':'Se creo el consecutivo correctamente', 'data':{**serializer.data,'radicado_nuevo':respuesta_radicado_data['radicado_nuevo']}}, status=status.HTTP_201_CREATED)






class RefEjemGetView(generics.ListAPIView):
    serializer_class = ConfigTipoRefgnoGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = ConfigReferenciaPagoAgno.objects.all()
    
    def get(self, request):
        hoy = date.today()
        age = hoy.year
        instance = ConfigReferenciaPagoAgno.objects.filter(agno_ref=age).first()


        

        cod_se_sub = ""
        if instance.id_catalogo_serie_unidad:
            catalogos_unidad=CatalogosSeriesUnidad.objects.filter(id_cat_serie_und=instance.id_catalogo_serie_unidad).first()
            cod_serie = catalogos_unidad.id_catalogo_serie.id_serie_doc.codigo
            cod_se_sub = cod_serie
            if catalogos_unidad.id_catalogo_serie.id_subserie_doc:
                cod_subserie =catalogos_unidad.id_catalogo_serie.id_subserie_doc.codigo
                cod_se_sub = cod_serie+cod_subserie


        
        numero_con_ceros = str(instance.referencia_actual+1).zfill(instance.cantidad_digitos)
        if cod_se_sub != "":

            conseg_nuevo = instance.id_unidad.codigo+cod_se_sub+str(instance.agno_ref)[-2:]+numero_con_ceros
        else:
            conseg_nuevo = instance.id_unidad.codigo+str(instance.agno_ref)[-2:]+numero_con_ceros
        
        
        
        if not instance:
            raise NotFound('No existe registro')
        
        serializer = self.serializer_class(instance)
        
        return Response({'success':True, 'detail':'se encontraron los siguientes registros', 'data': serializer.data,'ejemplo':conseg_nuevo}, status=status.HTTP_200_OK)





class ConsecutivoGetView(generics.ListAPIView):
    serializer_class = ReferenciaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Referencia.objects.all()
    
    def get (self, request):

        filter={}
                
        for key, value in request.query_params.items():

            # if key == 'radicado':
            #     if value !='':
            #         filter['mezcla__icontains'] = value
            if key =='unidad':
                if value != '':
                    filter['id_unidad__nombre__icontains'] = value    
            if key == 'agno':
                if value != '':
                     filter['agno_referencia__icontains'] = value   

            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['fecha_consecutivo__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    filter['fecha_consecutivo__lte'] = datetime.strptime(value, '%Y-%m-%d').date()
            # if key == 'modulo':
            #     if value != '':
            #         filter['id_modulo_que_radica__nombre__icontains'] = value


            if key == 'id_persona':
                if value != '':
                    filter['id_id_persona_solicita'] = value
        instance = self.get_queryset().filter(**filter).order_by('fecha_consecutivo')
        
        consecutivo_value = request.query_params.get('consecutivo')
        print(consecutivo_value)
        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        data_respuesta = serializador.data
        data_validada =[]
        if consecutivo_value and consecutivo_value != '':
            data_validada = [item for item in serializador.data if consecutivo_value in item.get('consecutivo', '')]
        else :
            data_validada = data_respuesta


        if not instance:
            raise NotFound("No existen registros asociados.")
        
    
        serializador=self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada}, status=status.HTTP_200_OK)
