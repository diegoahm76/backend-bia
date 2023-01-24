
from datetime import date, datetime
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.generics import RetrieveUpdateAPIView
from seguridad.models import Auditorias,Personas,Modulos,User
from seguridad.serializers.auditorias_serializers import AuditoriasSerializers,AuditoriasPostSerializers
from rest_framework.response import Response
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pytz

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAuditorias(request):
    #parametros de entrada
    tipo_documento = request.query_params.get('tipo-documento')
    numero_documento = request.query_params.get('numero-documento')
    rango_inicial_fecha = request.query_params.get('rango-inicial-fecha')
    rango_final_fecha = request.query_params.get('rango-final-fecha')
    modulo = request.query_params.get('modulo')
    subsistema = request.query_params.get('subsistema')
    #validacion de la informacion
    if rango_inicial_fecha==None or rango_final_fecha==None:
        return Response({'success': False, 'detail': 'No se ingresaron parametros de fecha'}, status=status.HTTP_404_NOT_FOUND)

    # formateando las variables de tipo fecha
    start_date=datetime(int(rango_inicial_fecha.split('-')[2]),int(rango_inicial_fecha.split('-')[1]),int(rango_inicial_fecha.split('-')[0]), tzinfo=pytz.timezone('America/Bogota'))
    end_date=datetime(int(rango_final_fecha.split('-')[2]),int(rango_final_fecha.split('-')[1]),int(rango_final_fecha.split('-')[0]),23,59,59,999, tzinfo=pytz.timezone('America/Bogota'))

    if (end_date-start_date).days > 8:
        return Response({'success': False, 'detail': 'El rango de fechas es superior a 8 días'}, status=status.HTTP_404_NOT_FOUND)
    else:
        pass

    def consultaPersona(tipo_documento_ingresado,numero_documento_ingresado):
        try:
            auditoria_persona_id = Personas.objects.get(Q(tipo_documento = tipo_documento_ingresado) & Q(numero_documento=numero_documento_ingresado)).id_persona
            auditoria_usuario_id = User.objects.get(persona=auditoria_persona_id)
            return auditoria_usuario_id.id_usuario
        except:
            raise TypeError('bad type')
    if tipo_documento == '':
        tipo_documento = None
    if numero_documento == '':
        numero_documento = None
    if modulo == '':
        modulo = None
    if subsistema == '':
        subsistema = None
    if tipo_documento != None and numero_documento != None and modulo != None and subsistema != None:
        if int(modulo) in Modulos.objects.values_list('id_modulo', flat=True):
            pass
        else:
            return Response({'success': False, 'detail': 'El modulo ingresado NO existe'}, status=status.HTTP_404_NOT_FOUND)
        if subsistema in Modulos.objects.values_list('subsistema', flat=True):
            pass
        else: 
            return Response({'success': False, 'detail': 'El subsistema ingresado NO existe'}, status=status.HTTP_404_NOT_FOUND)
        tipo_y_numero_id = (tipo_documento, numero_documento)
        persona = Personas.objects.values_list('tipo_documento', 'numero_documento')
        if tipo_y_numero_id in persona:
            pass
        else:
            return Response({'success': False, 'detail': 'La persona consultada NO existe'}, status=status.HTTP_404_NOT_FOUND)
        try:
            id_usuario = consultaPersona(tipo_documento,numero_documento)
            auditorias = Auditorias.objects.filter(fecha_accion__range=[start_date,end_date]).filter(id_usuario=id_usuario).filter(id_modulo = modulo).filter(subsistema = subsistema)
            serializador = AuditoriasSerializers(auditorias, many=True)
            if len(auditorias) == 0:
                return Response({'success': False, 'detail': 'No se encontraron coincidencias con los parametros de busqueda'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'success': True, 'detail': serializador.data}, status=status.HTTP_200_OK)            
        except:
            return Response({'success': False, 'detail': 'Esta persona no tiene un usuario asignado'}, status=status.HTTP_404_NOT_FOUND)
    
    if tipo_documento != None and numero_documento != None and modulo != None and subsistema == None:
        if int(modulo) in Modulos.objects.values_list('id_modulo', flat=True):
            pass
        else:
            return Response({'success': False, 'detail': 'El modulo ingresado NO existe'}, status=status.HTTP_404_NOT_FOUND)
        tipo_y_numero_id = (tipo_documento, numero_documento)
        persona = Personas.objects.values_list('tipo_documento', 'numero_documento')
        if tipo_y_numero_id in persona:
            pass
        else:
            return Response({'success': False, 'detail': 'La persona consultada NO existe'}, status=status.HTTP_404_NOT_FOUND)
        try:
            id_usuario = consultaPersona(tipo_documento,numero_documento)
            auditorias = Auditorias.objects.filter(fecha_accion__range=[start_date,end_date]).filter(id_usuario=id_usuario).filter(id_modulo = modulo)
            serializador = AuditoriasSerializers(auditorias, many=True)
            if len(auditorias) == 0:
                return Response({'success': False, 'detail': 'No se encontraron coincidencias con los parametros de busqueda'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'success': True, 'detail': serializador.data}, status=status.HTTP_200_OK)                        
        except:
            return Response({'success': False, 'detail': 'Esta persona no tiene un usuario asignado'}, status=status.HTTP_404_NOT_FOUND)
         
    if tipo_documento != None and numero_documento != None and modulo == None and subsistema != None:
        if subsistema in Modulos.objects.values_list('subsistema', flat=True):
            pass
        else:
            return Response({'success': False, 'detail': 'El subsistema ingresado NO existe'}, status=status.HTTP_404_NOT_FOUND)
        tipo_y_numero_id = (tipo_documento, numero_documento)
        persona = Personas.objects.values_list('tipo_documento', 'numero_documento')
        if tipo_y_numero_id in persona:
            pass
        else:
            return Response({'success': False, 'detail': 'La persona consultada NO existe'}, status=status.HTTP_404_NOT_FOUND)
        try:
            id_usuario = consultaPersona(tipo_documento,numero_documento)
            auditorias = Auditorias.objects.filter(fecha_accion__range=[start_date,end_date]).filter(id_usuario=id_usuario).filter(subsistema = subsistema)
            serializador = AuditoriasSerializers(auditorias, many=True)
            if len(auditorias) == 0:
                return Response({'success': False, 'detail': 'No se encontraron coincidencias con los parametros de busqueda'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'success': True, 'detail': serializador.data}, status=status.HTTP_200_OK)                 
        except:
            return Response({'success': False, 'detail': 'Esta persona no tiene un usuario asignado'}, status=status.HTTP_404_NOT_FOUND)
        
    if tipo_documento != None and numero_documento != None and modulo == None and subsistema == None:
        tipo_y_numero_id = (tipo_documento, numero_documento)
        persona = Personas.objects.values_list('tipo_documento', 'numero_documento')
        if tipo_y_numero_id in persona:
            pass
        else:
            return Response({'success': False, 'detail': 'La persona consultada NO existe'}, status=status.HTTP_404_NOT_FOUND)
        try:
            id_usuario = consultaPersona(tipo_documento,numero_documento)
            auditorias = Auditorias.objects.filter(fecha_accion__range=[start_date,end_date]).filter(id_usuario=id_usuario)
            serializador = AuditoriasSerializers(auditorias, many=True)
            if len(auditorias) == 0:
                return Response({'success': False, 'detail': 'No se encontraron coincidencias con los parametros de busqueda'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'success': True, 'detail': serializador.data}, status=status.HTTP_200_OK)              
        except: 
            return Response({'success': False, 'detail': 'Esta persona no tiene un usuario asignado'}, status=status.HTTP_404_NOT_FOUND)
    
    if tipo_documento == None and numero_documento == None and modulo != None and subsistema != None:
        if int(modulo) in Modulos.objects.values_list('id_modulo', flat=True):
            pass
        else:
            return Response({'success': False, 'detail': 'El modulo ingresado NO existe'}, status=status.HTTP_404_NOT_FOUND)
        if subsistema in Modulos.objects.values_list('subsistema', flat=True):
            pass
        else:
            return Response({'success': False, 'detail': 'El subsistema ingresado NO existe'}, status=status.HTTP_404_NOT_FOUND)
        auditorias = Auditorias.objects.filter(fecha_accion__range=[start_date,end_date]).filter(id_modulo = modulo).filter(subsistema = subsistema)
        serializador = AuditoriasSerializers(auditorias, many=True)
        if len(auditorias) == 0:
            return Response({'success': False, 'detail': 'No se encontraron coincidencias con los parametros de busqueda'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'success': True, 'detail': serializador.data}, status=status.HTTP_200_OK)              
    
    if tipo_documento == None and numero_documento == None and modulo != None and subsistema == None:
        if int(modulo) in Modulos.objects.values_list('id_modulo', flat=True):
            pass
        else:
            return Response({'success': False, 'detail': 'El modulo ingresado NO existe'}, status=status.HTTP_404_NOT_FOUND)
        auditorias = Auditorias.objects.filter(fecha_accion__range=[start_date,end_date]).filter(id_modulo = modulo)
        serializador = AuditoriasSerializers(auditorias, many=True)
        if len(auditorias) == 0:
            return Response({'success': False, 'detail': 'No se encontraron coincidencias con los parametros de busqueda'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'success': True, 'detail': serializador.data}, status=status.HTTP_200_OK)              
    
    if tipo_documento == None and numero_documento == None and modulo == None and subsistema != None:
        if subsistema in Modulos.objects.values_list('subsistema', flat=True):
            pass
        else:
            return Response({'success': False, 'detail': 'El subsistema ingresado NO existe'}, status=status.HTTP_404_NOT_FOUND)
        auditorias = Auditorias.objects.filter(fecha_accion__range=[start_date,end_date]).filter(subsistema = subsistema)
        serializador = AuditoriasSerializers(auditorias, many=True)
        if len(auditorias) == 0:
            return Response({'success': False, 'detail': 'No se encontraron coincidencias con los parametros de busqueda'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'success': True, 'detail': serializador.data}, status=status.HTTP_200_OK)              
    
    if tipo_documento == None and numero_documento == None and modulo == None and subsistema == None:
        auditorias = Auditorias.objects.filter(fecha_accion__range=[start_date,end_date])
        serializador = AuditoriasSerializers(auditorias, many=True)
        if len(auditorias) == 0:
            return Response({'success': False, 'detail': 'No se encontraron coincidencias con los parametros de busqueda'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'success': True, 'detail': serializador.data}, status=status.HTTP_200_OK)
 
    else:
        return Response({'success': False, 'detail': 'No se encontró una auditoria con estos parámetros de búsqueda'}, status=status.HTTP_404_NOT_FOUND)

class ListApiViews(generics.ListAPIView):
    serializer_class=AuditoriasSerializers
    queryset = Auditorias.objects.all()





