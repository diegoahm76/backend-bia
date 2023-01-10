from almacen.models.bienes_models import CatalogoBienes
from almacen.serializers.bienes_serializers import CatalogoBienesSerializer
from almacen.serializers.despachos_serializers import SerializersDespachoConsumo, SerializersItemDespachoConsumo, SerializersSolicitudesConsumibles, SerializersItemsSolicitudConsumible, SearchBienInventarioSerializer
from rest_framework import generics,status
from rest_framework.response import Response
from seguridad.models import Personas, User
from rest_framework.decorators import api_view
from seguridad.utils import Util
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, date
import copy
from almacen.serializers.despachos_serializers import (
    CerrarSolicitudDebidoInexistenciaSerializer,
    SerializersDespachoConsumo,
    SerializersItemDespachoConsumo,
    SerializersSolicitudesConsumibles,
    SerializersItemsSolicitudConsumible
)
from almacen.models.solicitudes_models import (
    SolicitudesConsumibles, 
    DespachoConsumo, 
    ItemDespachoConsumo, 
    SolicitudesConsumibles, 
    ItemsSolicitudConsumible
)
from seguridad.models import (
    Personas,
    User,
    ClasesTerceroPersona
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales,
    NivelesOrganigrama
)
from almacen.models.generics_models import (
    UnidadesMedida
)
from almacen.models.inventario_models import (
    Inventario
)
from almacen.serializers.solicitudes_serialiers import ( 
    CrearSolicitudesPostSerializer,
    CrearItemsSolicitudConsumiblePostSerializer
    )
from seguridad.serializers.personas_serializers import PersonasSerializer

class CreateDespachoMaestro(generics.UpdateAPIView):
    serializer_class = SerializersDespachoConsumo
    queryset = DespachoConsumo.objects.all()
    
    def put(self, request):
        datos_ingresados = request.data
        user_logeado = request.user
        info_despacho = datos_ingresados['info_despacho']
        items_despacho = datos_ingresados['items_despacho']
        #Validaciones primarias
        if str(user_logeado) == 'AnonymousUser':
            return Response({'success':False,'data':'Esta solicitud solo la puede ejecutar un usuario logueado'},status=status.HTTP_404_NOT_FOUND)
        if info_despacho['es_despacho_conservacion'] != True and info_despacho['es_despacho_conservacion'] != False:
            return Response({'success':False,'data':'El campo (es_despacho_conservacion) debe ser True o False'},status=status.HTTP_404_NOT_FOUND)
        if info_despacho['es_despacho_conservacion'] == False and info_despacho['id_entrada_almacen_cv'] != None:
            return Response({'success':False,'data':'Si ingresa (es_despacho_conservacion) en false, el campo id_entrada_almacen_cv debe ser null'},status=status.HTTP_404_NOT_FOUND)
        if len(info_despacho['motivo']) > 255:
            return Response({'success':False,'data':'El motivo debe tener como máximo 255 caracteres'},status=status.HTTP_404_NOT_FOUND)
        #Validaciones de la solicitud
        instancia_solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=info_despacho['id_solicitud_consumo']).first()
        if not instancia_solicitud:
            return Response({'success':False,'data':'Debe ingresar un id de solicitud válido'},status=status.HTTP_404_NOT_FOUND)
        if instancia_solicitud.solicitud_abierta == False or instancia_solicitud.estado_aprobacion_responsable != 'A':
            return Response({'success':False,'data':'La solicitud a despachar debe de estar aprobada por el funcionario responsable y no debe de estar cerrada'},status=status.HTTP_404_NOT_FOUND)
        #Asignación de fecha de registro
        info_despacho['fecha_registro'] = datetime.now()
        #Se valida que la fecha de la solicitud no sea inferior a (fecha_actual - 8 días) ni superior a la actual
        fecha_despacho = datetime.strptime(info_despacho.get('fecha_despacho'), "%Y-%m-%d %H:%M:%S")
        aux_validacion_fechas = info_despacho['fecha_registro'] - fecha_despacho
        if int(aux_validacion_fechas.days) > 8 or int(aux_validacion_fechas.days) < 0:
            return Response({'success':False,'data':'La fecha ingresada no es permita dentro de los parametros existentes'},status=status.HTTP_404_NOT_FOUND)
        #Se valida que la fecha de aprobación de la solicitud sea inferior a la fecha de despacho
        fecha_aprobacion_solicitud = instancia_solicitud.fecha_aprobacion_responsable
        if fecha_despacho.date() <= fecha_aprobacion_solicitud:
            return Response({'success':False,'data':'La fecha de despacho debe ser mayor o igual a la fecha de aprobación de la solicitud'},status=status.HTTP_404_NOT_FOUND)
        #Consulta y asignación de los campos que se repiten con solicitudes de bienes de consumos
        info_despacho['numero_solicitud_por_tipo'] = instancia_solicitud.nro_solicitud_por_tipo
        info_despacho['fecha_solicitud'] = instancia_solicitud.fecha_solicitud
        info_despacho['id_persona_solicita'] = instancia_solicitud.id_persona_solicita
        info_despacho['id_unidad_para_la_que_solicita'] = instancia_solicitud.id_unidad_para_la_que_solicita
        info_despacho['id_funcionario_responsable_unidad'] = instancia_solicitud.id_funcionario_responsable_unidad
        #Asignación de persona que despacha
        info_despacho['id_persona_despacha'] = user_logeado.persona.id_persona
        #Asignacion de número de despacho
        despachos_existentes = DespachoConsumo.objects.all()
        if despachos_existentes:
            numero_despachos = [i.nro_solicitud_por_tipo for i in despachos_existentes]
            info_despacho['numero_despacho_consumo'] = max(numero_despachos) + 1
        else:
            info_despacho['numero_despacho_consumo'] = 1  

        return Response({'success':True,'data':'Despacho creado con éxito', 'Numero solicitud' : info_despacho["numero_despacho_consumo"]},status=status.HTTP_200_OK)
    
class CerrarSolicitudDebidoInexistenciaView(generics.RetrieveUpdateAPIView):
    serializer_class = CerrarSolicitudDebidoInexistenciaSerializer
    queryset = SolicitudesConsumibles.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_solicitud):
        data = request.data
        
        #VALIDACIÓN SI EXISTE LA SOLICITUD ENVIADA
        solicitud = SolicitudesConsumibles.objects.filter(id_solicitud_consumibles=id_solicitud).first()
        if not solicitud:
            return Response({'success': False, 'detail': 'No se encontró ninguna solicitud con los parámetros enviados'}, status=status.HTTP_404_NOT_FOUND)
        
        if solicitud.fecha_cierre_no_dispo_alm:
            return Response({'success': False, 'detail': 'No se cerrar una solicitud que ya está cerrada'}, status=status.HTTP_403_FORBIDDEN)
        #SUSTITUIR INFORMACIÓN A LA DATA
        data['fecha_cierre_no_dispo_alm'] = datetime.now()
        data['id_persona_cierre_no_dispo_alm'] = request.user.persona.id_persona
        data['solicitud_abierta'] = False
        data['fecha_cierre_solicitud'] = datetime.now()
        data['gestionada_almacen'] = True

        serializer = self.serializer_class(solicitud, data=data, many=False)
        serializer.is_valid(raise_exception=True)
        serializer.save
        
        #Auditoria Cerrar Solicitud
        usuario = request.user.id_usuario
        descripcion = {"Codigo bien": str(), "Numero elemento bien": str()}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 18,
            "cod_permiso": "BO",
            "subsistema": 'ALMA',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success': False, 'detail': 'Se cerró la solicitud correctamente'}, status=status.HTTP_201_CREATED)
        
    
class SearchSolicitudesAprobadasYAbiertos(generics.ListAPIView):
    serializer_class=SerializersSolicitudesConsumibles
    queryset=SolicitudesConsumibles.objects.all()
    
    def get(self,request):
        filter = {}
        fecha_despacho=request.query_params.get('fecha_despacho')
       
        if not fecha_despacho:
            return Response({'success':False,'detail':'Ingresa el parametro de fecha de despacho'},status=status.HTTP_400_BAD_REQUEST)
        
        filter['estado_aprobacion_responsable'] = "A"
        filter['solicitud_abierta'] = True
        fecha_despacho_strptime = datetime.strptime(
                fecha_despacho, '%Y-%m-%d %H:%M:%S')
        solicitudes=SolicitudesConsumibles.objects.filter(**filter).filter(fecha_aprobacion_responsable__lte=fecha_despacho_strptime)
        if solicitudes:
            serializador=self.serializer_class(solicitudes,many = True)
            return Response({'success':True,'detail':'Se encontraron solicitudes aprobadas y abiertas','data':serializador.data},status = status.HTTP_200_OK)
        else:
            return Response({'success':False,'detail':'No se encontraron solicitudes'},status = status.HTTP_404_NOT_FOUND) 
        
class GetDespachoByNumeroDespacho(generics.ListAPIView):
    serializer_class= SerializersDespachoConsumo
    queryset=DespachoConsumo.objects.all()
    
    def get(self,request):
        numero_despacho_consumo=request.query_params.get('numero_despacho_consumo')
        if not numero_despacho_consumo:
            return Response({'success':False,'detail':'Ingresa el parametro de fecha de despacho'},status=status.HTTP_400_BAD_REQUEST)
        
class SearchBienInventario(generics.ListAPIView):
    serializer_class=SearchBienInventarioSerializer
    queryset=Inventario.objects.all()
    
    def get(self,request):
        codigo_bien = request.query_params.get('codigo_bien')
        id_bodega = request.query_params.get('id_bodega')
        fecha_despacho = request.query_params.get('fecha_despacho')
        
        if (not codigo_bien or codigo_bien == '') or (not id_bodega or id_bodega == '') or (not fecha_despacho or fecha_despacho == ''):
            return Response({'success':False, 'detail':'Debe ingresar los parámetros de búsqueda'}, status=status.HTTP_400_BAD_REQUEST)

        bien = CatalogoBienes.objects.filter(codigo_bien=codigo_bien, solicitable_vivero=True, cod_tipo_bien='C', nivel_jerarquico=5).first()
        fecha_despacho_strptime = datetime.strptime(fecha_despacho, '%Y-%m-%d %H:%M:%S')
        
        if bien:
            items_despachados = ItemDespachoConsumo.objects.filter(id_bien_despachado=bien.id_bien, id_despacho_consumo__fecha_despacho__gte=fecha_despacho_strptime)
            print("ID_BIEN: ", bien.id_bien)
            print("FECHA_DESPACHO: ", fecha_despacho_strptime)
            print("ITEMS_DESPACHADOS: ", items_despachados)
            if items_despachados:
                return Response({'success':False, 'detail':'El bien tiene despachos o entregas posteriores a la fecha de despacho elegida', 'data': []}, status=status.HTTP_200_OK)
                
            inventario = Inventario.objects.filter(id_bien=bien.id_bien, id_bodega=id_bodega).first()
            
            serializador_inventario = self.serializer_class(inventario)
            
            return Response({'success':True, 'detail':'Se encontró el siguiente resultado', 'data': serializador_inventario.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'El bien no existe', 'data': []}, status=status.HTTP_200_OK)
        
class SearchBienesInventario(generics.ListAPIView):
    serializer_class=SearchBienInventarioSerializer
    queryset=Inventario.objects.all()
    
    def get(self,request):
        id_bien = request.query_params.get('id_bien')
        
        if not id_bien or id_bien == '':
            return Response({'success':False, 'detail':'Debe ingresar el parámetro de búsqueda'}, status=status.HTTP_400_BAD_REQUEST)

        inventario = Inventario.objects.filter(id_bien=id_bien)
        
        serializador_inventario = self.serializer_class(inventario, many=True)
        
        return Response({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data': serializador_inventario.data}, status=status.HTTP_200_OK)
