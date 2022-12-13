from rest_framework import generics,status
from rest_framework.response import Response
from django.db.models import Q
import copy
from datetime import datetime
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from almacen.serializers.organigrama_serializers import UnidadesGetSerializer
from almacen.models.organigrama_models import UnidadesOrganizacionales
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from seguridad.serializers.personas_serializers import CargosSerializer
from gestion_documental.serializers.tca_serializers import (
    TCASerializer,
    TCAPostSerializer,
    TCAPutSerializer,
    ClasifSerieSubserieUnidadTCASerializer,
    ClasifSerieSubserieUnidadTCAPutSerializer,
    ClasifSerieSubseriUnidadTCA_activoSerializer
)
from gestion_documental.models.ccd_models import (
    SeriesSubseriesUnidadOrg,
    CuadrosClasificacionDocumental,
    SeriesDoc
)
from almacen.models.organigrama_models import (
    Organigramas
)
from gestion_documental.models.tca_models import (
    TablasControlAcceso,
    Clasif_Serie_Subserie_Unidad_TCA,
    ClasificacionExpedientes,
    Historico_Clasif_S_Ss_UndOrg_TCA
)
from seguridad.models import Cargos,Personas
from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES

class GetUnidadesbyCCD(generics.ListAPIView):
    serializer_class=UnidadesGetSerializer
    queryset=UnidadesOrganizacionales.objects.all()
    def get(self,request,pk):
        ccd=CuadrosClasificacionDocumental.objects.filter(id_ccd=pk).first()
        if ccd: 
            unidades=UnidadesOrganizacionales.objects.filter(id_organigrama=ccd.id_organigrama.id_organigrama)
            serializador=self.serializer_class(unidades,many=True)
            return Response({'success':True,'detail':'El ccd cuenta con las siguientes unidades','unidades':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':False,'detail':'El ccd no cuenta con unidades'},status=status.HTTP_403_FORBIDDEN)
class GetCargosByUnidades(generics.ListAPIView):
    serializer_class=CargosSerializer
    queryset=Cargos.objects.all()
    def get (self,request):
        cargos_true=request.query_params.get('check')
        unidad=request.query_params.get('unidad')
        if cargos_true=='true':
            unidad_intance=UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=unidad).first()
            if unidad:
                personas=Personas.objects.filter(id_unidad_organizacional_actual=unidad_intance.id_unidad_organizacional)
                list_cargos=[cargo.id_cargo.id_cargo for cargo in personas]
                cargos=Cargos.objects.filter(id_cargo__in=list_cargos)
                serializador=self.serializer_class(cargos,many=True)
                return Response ({'success':True,'detail':'Se encontraron cargos','Cargos':serializador.data},status=status.HTTP_200_OK)
            return Response ({'success':False,'detail':'No existe unidad'},status=status.HTTP_403_FORBIDDEN)
        else:
            cargos=Cargos.objects.filter(activo=True).values()
            return Response ({'success':True,'Cargos':cargos},status=status.HTTP_200_OK)
    
class PostTablaControlAcceso(generics.CreateAPIView):
    serializer_class = TCAPostSerializer
    queryset = TablasControlAcceso
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            pass
        except:
            return Response({'success': False, 'detail': 'Valide la información ingresada, el id_ccd es requerido, el nombre y la versión son requeridos y deben ser únicos'}, status=status.HTTP_400_BAD_REQUEST)

        #Validación de seleccionar solo ccd terminados
        ccd = serializer.validated_data.get('id_ccd')
        ccd_instance = CuadrosClasificacionDocumental.objects.filter(id_ccd=ccd.id_ccd).first()
        if ccd_instance:
            if ccd_instance.fecha_terminado == None:
                return Response({'success': False, 'detail': 'No se pueden seleccionar Cuadros de Clasificación Documental que no estén terminados'}, status=status.HTTP_403_FORBIDDEN)

            serializado = serializer.save()

            #Auditoria Crear TCA
            usuario = request.user.id_usuario
            descripcion = {"Nombre": str(serializado.nombre), "Versión": str(serializado.version)}
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 31,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
            }
            Util.save_auditoria(auditoria_data)

            return Response({'success': True, 'detail': 'TCA creada exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'No existe un Cuadro de Clasificación Documental con el id_ccd enviado'}, status=status.HTTP_400_BAD_REQUEST)

class UpdateTablaControlAcceso(generics.RetrieveUpdateAPIView):
    serializer_class = TCAPutSerializer
    queryset = TablasControlAcceso.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        tca = TablasControlAcceso.objects.filter(id_tca=pk).first()
        if tca:
            if not tca.fecha_retiro_produccion:
                if not tca.fecha_terminado:
                    previous_tca = copy.copy(tca)

                    serializer = self.serializer_class(tca, data=request.data)
                    try:
                        serializer.is_valid(raise_exception=True)
                        pass
                    except:
                        return Response({'success': False, 'detail': 'Validar data enviada, el nombre y la versión son requeridos y deben ser únicos'}, status=status.HTTP_400_BAD_REQUEST)
                    serializer.save()

                    # AUDITORIA DE UPDATE DE TCA
                    user_logeado = request.user.id_usuario
                    dirip = Util.get_client_ip(request)
                    descripcion = {'nombre':str(previous_tca.nombre), 'version':str(previous_tca.version)}
                    valores_actualizados={'previous':previous_tca, 'current':tca}
                    auditoria_data = {
                        'id_usuario': user_logeado,
                        'id_modulo': 31,
                        'cod_permiso': 'AC',
                        'subsistema': 'GEST',
                        'dirip': dirip,
                        'descripcion': descripcion,
                        'valores_actualizados': valores_actualizados
                    }
                    Util.save_auditoria(auditoria_data)

                    return Response({'success': True, 'detail': 'Tabla de Control de Acceso actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success': False,'detail': 'No se puede actualizar una TCA terminada, intente reanudar primero'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'success': False,'detail': 'No puede realizar cambios a una TCA que ya fue retirada de producción'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No existe ninguna Tabla de Control de Acceso con los parámetros ingresados'}, status=status.HTTP_404_NOT_FOUND)

class ClasifSerieSubserieUnidadTCA(generics.CreateAPIView):
    serializer_class = ClasifSerieSubserieUnidadTCASerializer
    queryset = Clasif_Serie_Subserie_Unidad_TCA.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, id_tca):
        data = request.data
        tca = TablasControlAcceso.objects.filter(id_tca=id_tca).first()
        if tca:
            if not tca.fecha_retiro_produccion:
                if not tca.fecha_terminado:
                    if not tca.actual:
                        # Validar existencia de expediente
                        expediente = SeriesSubseriesUnidadOrg.objects.filter(id_serie_subserie_doc=data['id_serie_subserie_unidad']).first()
                        if not expediente:
                            return Response({'success':False, 'detail':'Debe ingresar un expediente que exista'}, status=status.HTTP_400_BAD_REQUEST)
                        
                        # Validad existencia del tipo clasificación
                        dict_tipo_clasificacion = dict(tipo_clasificacion_CHOICES)
                        if data['cod_clas_expediente'] not in dict_tipo_clasificacion:
                            return Response({'success':False, 'detail':'Debe ingresar un código de clasificación que exista'}, status=status.HTTP_400_BAD_REQUEST)
                        
                        data['id_tca'] = id_tca
                        serializer = self.serializer_class(data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()

                        return Response({'success': True, 'detail': 'Se realizó la clasificación del expediente exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'success': False,'detail': 'No puede realizar esta acción a una TCA actual'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response({'success': False,'detail': 'No puede realizar cambios a una TCA terminada, intente reanudar primero'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'success': False,'detail': 'No puede realizar cambios a una TCA que ya fue retirada de producción'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No existe ninguna Tabla de Control de Acceso con los parámetros ingresados'}, status=status.HTTP_404_NOT_FOUND)

class UpdateClasifSerieSubserieUnidadTCA(generics.UpdateAPIView):
    serializer_class = ClasifSerieSubserieUnidadTCAPutSerializer
    queryset = Clasif_Serie_Subserie_Unidad_TCA.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class_2=ClasifSerieSubseriUnidadTCA_activoSerializer
    def put(self, request, pk):
    
        data = request.data
        clasif_s_ss_unidad_tca = Clasif_Serie_Subserie_Unidad_TCA.objects.filter(id_clasif_serie_subserie_unidad_tca=pk).first()
        clasif__previous=copy.copy(clasif_s_ss_unidad_tca)
        if clasif_s_ss_unidad_tca:
            if not clasif_s_ss_unidad_tca.id_tca.fecha_retiro_produccion:
                if not clasif_s_ss_unidad_tca.id_tca.fecha_terminado:
                    if not clasif_s_ss_unidad_tca.id_tca.actual:
                        # Validad existencia del tipo clasificación
                        dict_tipo_clasificacion = dict(tipo_clasificacion_CHOICES)
                        if data['cod_clas_expediente'] not in dict_tipo_clasificacion:
                            return Response({'success':False, 'detail':'Debe ingresar un código de clasificación que exista'}, status=status.HTTP_400_BAD_REQUEST)
                        
                        serializer = self.serializer_class(clasif_s_ss_unidad_tca, data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()

                        return Response({'success': True, 'detail': 'Se actualizó la clasificación del expediente exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
                    else:
                        dict_tipo_clasificacion = dict(tipo_clasificacion_CHOICES)
                        if data['cod_clas_expediente'] not in dict_tipo_clasificacion:
                            return Response({'success':False, 'detail':'Debe ingresar un código de clasificación que exista'}, status=status.HTTP_400_BAD_REQUEST)
                        serializer= self.serializer_class_2(clasif_s_ss_unidad_tca, data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save() 
                        
                        persona=request.user.persona.id_persona
                        persona_intance=Personas.objects.filter(id_persona=persona).first()
                        datos_actualizados=[]
                        
                        del clasif__previous.__dict__["_state"]
                        del clasif__previous.__dict__["_django_version"]
                        
                        for field, value in clasif__previous.__dict__.items():
                            new_value = getattr(clasif_s_ss_unidad_tca,field)
                            new_value = new_value if new_value != '' else None
                            value = value if value != '' else None
                            if value != new_value:
                                datos_actualizados.append({field: value})
                        if datos_actualizados:  
                            Historico_Clasif_S_Ss_UndOrg_TCA.objects.create(
                                id_clasif_s_ss_unidad_tca = clasif_s_ss_unidad_tca,
                                cod_clasificacion_exp = clasif__previous.cod_clas_expediente,
                                justificacion_del_cambio = clasif__previous.justificacion_cambio,
                                ruta_archivo_cambio = clasif__previous.ruta_archivo_cambio,
                                id_persona_cambia = persona_intance
                            )
                        return Response({'success': True, 'detail': 'Se actualizó la clasificación del expediente exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success': False,'detail': 'No se puede actualizar una TCA terminada, intente reanudar primero'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'success': False,'detail': 'No puede realizar cambios a una TCA que ya fue retirada de producción'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No existe ninguna clasificación del expediente con los parámetros ingresados'}, status=status.HTTP_404_NOT_FOUND)

class ReanudarTablaControlAcceso(generics.UpdateAPIView):
    serializer_class = TCAPostSerializer
    queryset = TablasControlAcceso

    def put(self, request, pk):
        tca = TablasControlAcceso.objects.filter(id_tca=pk).first()
        if tca:
            if tca.fecha_terminado:
                if tca.fecha_retiro_produccion:
                    return Response({'success': False, 'detail': 'No se puede reanudar un cuadro de clasificación documental que ya fue retirado de producción'}, status=status.HTTP_403_FORBIDDEN)
                tca.fecha_terminado = None
                tca.save()
                return Response({'success': True, 'detail': 'Se reanudó el TCA'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'detail': 'No puede reanudar un TCA no terminado'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No se encontró ningún TCA con estos parámetros'}, status=status.HTTP_404_NOT_FOUND)    