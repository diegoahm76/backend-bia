from rest_framework import generics,status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
import copy, pytz
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
    ClasifSerieSubseriUnidadTCA_activoSerializer,
    PermisosCargoUnidadSerieSubserieUnidadTCASerializer,
    Cargos_Unidad_S_Ss_UndOrg_TCASerializer,
    CatalogosSeriesUnidadClasifSerializer,
    CatalogosSeriesUnidadClasifPermisosSerializer

)
from gestion_documental.models.ccd_models import (
    CatalogosSeriesUnidad,
    CuadrosClasificacionDocumental,
    SeriesDoc,
)
from almacen.models.organigrama_models import (
    Organigramas
)
from gestion_documental.models.tca_models import (
    TablasControlAcceso,
    Clasif_Serie_Subserie_Unidad_TCA,
    ClasificacionExpedientes,
    Cargos_Unidad_S_Ss_UndOrg_TCA,
    PermisosCargoUnidadSerieSubserieUnidadTCA,
    PermisosGD,
    Historico_Clasif_S_Ss_UndOrg_TCA, 
    HistoricoCargosUnidadSerieSubserieUnidadTCA
)
from seguridad.models import Cargos,Personas
from gestion_documental.choices.tipo_clasificacion_choices import tipo_clasificacion_CHOICES

class GetUnidadesbyCCD(generics.ListAPIView):
    serializer_class=UnidadesGetSerializer
    queryset=UnidadesOrganizacionales.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        ccd=CuadrosClasificacionDocumental.objects.filter(id_ccd=pk).first()
        if ccd: 
            unidades=UnidadesOrganizacionales.objects.filter(id_organigrama=ccd.id_organigrama.id_organigrama)
            serializador=self.serializer_class(unidades,many=True)
            return Response({'success':True,'detail':'El ccd cuenta con las siguientes unidades','data':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':False,'detail':'El ccd no cuenta con unidades'},status=status.HTTP_403_FORBIDDEN)
    
class GetCargosByUnidades(generics.ListAPIView):
    serializer_class=CargosSerializer
    queryset=Cargos.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get (self,request):
        cargos_true=request.query_params.get('check')
        unidad=request.query_params.get('unidad')
        if cargos_true=='true':
            unidad_intance=UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=unidad).first()
            if unidad:
                personas=Personas.objects.filter(id_unidad_organizacional_actual=unidad_intance.id_unidad_organizacional)
                list_cargos=[cargo.id_cargo.id_cargo for cargo in personas if cargo.id_cargo]
                cargos=Cargos.objects.filter(id_cargo__in=list_cargos)
                if cargos:
                    serializador=self.serializer_class(cargos,many=True)
                    return Response ({'success':True,'detail':'Se encontraron cargos','data':serializador.data},status=status.HTTP_200_OK)
                else: return Response ({'success':False,'detail':'No se encontraron cargos'},status=status.HTTP_404_NOT_FOUND)
            return Response ({'success':False,'detail':'No existe unidad'},status=status.HTTP_403_FORBIDDEN)
        else:
            cargos=Cargos.objects.filter(activo=True).values()
            return Response ({'success':True, 'detail':'Se encontraron cargos', 'data':cargos},status=status.HTTP_200_OK)
        
class GetListTca(generics.ListAPIView):
    serializer_class=TCASerializer
    queryset=TablasControlAcceso.objects.all()
    permission_classes = [IsAuthenticated]
    
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
                        expediente = CatalogosSeriesUnidad.objects.filter(id_cat_serie_und=data['id_cat_serie_und']).first()
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
                if not clasif_s_ss_unidad_tca.id_tca.actual:
                    if not clasif_s_ss_unidad_tca.id_tca.fecha_terminado:
                        # Validad existencia del tipo clasificación
                        dict_tipo_clasificacion = dict(tipo_clasificacion_CHOICES)
                        if data['cod_clas_expediente'] not in dict_tipo_clasificacion:
                            return Response({'success':False, 'detail':'Debe ingresar un código de clasificación que exista'}, status=status.HTTP_400_BAD_REQUEST)
                        
                        serializer = self.serializer_class(clasif_s_ss_unidad_tca, data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()

                        return Response({'success': True, 'detail': 'Se actualizó la clasificación del expediente exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'success': False,'detail': 'No se puede actualizar una TCA terminada, intente reanudar primero'}, status=status.HTTP_403_FORBIDDEN)
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
                return Response({'success': False,'detail': 'No puede realizar cambios a una TCA que ya fue retirada de producción'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No existe ninguna clasificación del expediente con los parámetros ingresados'}, status=status.HTTP_404_NOT_FOUND)

class ReanudarTablaControlAcceso(generics.UpdateAPIView):
    serializer_class = TCAPostSerializer
    queryset = TablasControlAcceso
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        tca = TablasControlAcceso.objects.filter(id_tca=pk).first()
        if tca:
            if tca.fecha_terminado:
                if tca.fecha_retiro_produccion:
                    return Response({'success': False, 'detail': 'No se puede reanudar una TCA que ya fue retirada de producción'}, status=status.HTTP_403_FORBIDDEN)
                if tca.actual:
                    return Response({'success': False, 'detail': 'No se puede reanudar una TCA actual'}, status=status.HTTP_403_FORBIDDEN)
                
                tca.fecha_terminado = None
                tca.save()
                return Response({'success': True, 'detail': 'Se reanudó el TCA'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'detail': 'No puede reanudar un TCA no terminado'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No se encontró ningún TCA con estos parámetros'}, status=status.HTTP_404_NOT_FOUND) 

@api_view(['POST'])
def asignar_cargo_unidad_permiso_expediente(request):
    data = request.data
    user = request.user
    
    try:
        clasif_serie_subserie_unidad_TCA= Clasif_Serie_Subserie_Unidad_TCA.objects.get(id_clasif_serie_subserie_unidad_tca=data['id_clasif_serie_subserie_unidad_tca'])
    except:
        return Response({'success':False, 'detail':'No existe expediente relacionado al id de clasificacion serie/subserie/unidad TCA'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        unidad_org_persona = UnidadesOrganizacionales.objects.get(id_unidad_organizacional=data['id_unidad_org_persona'])
    except:
        return Response({'success':False, 'detail':'No existe unidad organisacional con el id unidad organizacional persona ingresado'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        cargo_persona = Cargos.objects.get(id_cargo=data['id_cargo_persona'])
    except:
        return Response({'success':False, 'detail':'No existe id cargo'}, status=status.HTTP_400_BAD_REQUEST)
    
    cargo_unidad = Cargos_Unidad_S_Ss_UndOrg_TCA.objects.filter(id_clasif_serie_subserie_unidad_tca=data['id_clasif_serie_subserie_unidad_tca'],id_cargo_persona=data['id_cargo_persona'],id_unidad_org_cargo=data['id_unidad_org_persona'])
    if cargo_unidad:
        return Response({'success':False, 'detail':'Ya asignó previamente el mismo cargo y la misma unidad para el expediente elegido. Por favor eliminelo primero si desea volverlo a crear'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not data.getlist('permisos'):
        return Response({'success':False, 'detail':'Debe asignar por lo menos un permiso'}, status=status.HTTP_400_BAD_REQUEST)
    
    permisos_validados_list = PermisosGD.objects.filter(cod_permiso_gd__in=data.getlist('permisos'))
    if len(data.getlist('permisos')) != len(permisos_validados_list):
        return Response({'success':False, 'detail':'Uno de los permisos ingresados no existe'}, status=status.HTTP_400_BAD_REQUEST)
    
    match clasif_serie_subserie_unidad_TCA.id_tca.actual:
        case True:
            if not data.get('justificacion_del_cambio') or data['justificacion_del_cambio'] == '':
                return Response({'success':False, 'detail':'Debe ingresar justificación'}, status=status.HTTP_400_BAD_REQUEST)
            if not request.FILES.get('ruta_archivo_cambio'):
                return Response({'success':False, 'detail':'Debe ingresar un documento'}, status=status.HTTP_400_BAD_REQUEST)
            cargo_unidad_serie_subserie_undorg_tca= Cargos_Unidad_S_Ss_UndOrg_TCA.objects.create(
                id_clasif_serie_subserie_unidad_tca = clasif_serie_subserie_unidad_TCA,
                id_cargo_persona = cargo_persona,
                id_unidad_org_cargo = unidad_org_persona,
                justificacion_del_cambio = data['justificacion_del_cambio'],
                ruta_archivo_cambio = request.FILES.get('ruta_archivo_cambio'))
        case False:
            cargo_unidad_serie_subserie_undorg_tca= Cargos_Unidad_S_Ss_UndOrg_TCA.objects.create(
                id_clasif_serie_subserie_unidad_tca = clasif_serie_subserie_unidad_TCA,
                id_cargo_persona = cargo_persona,
                id_unidad_org_cargo = unidad_org_persona
            )
    permisos_serializer_list = []
    for permiso in permisos_validados_list:
        permiso_cargo_unidad_s_ss_unidad_tca = PermisosCargoUnidadSerieSubserieUnidadTCA.objects.create(
            id_cargo_unidad_s_ss_unidad_tca = cargo_unidad_serie_subserie_undorg_tca,
            cod_permiso = permiso 
        )
        permisos_serializer_list.append(permiso_cargo_unidad_s_ss_unidad_tca)
    expediente_serializer = Cargos_Unidad_S_Ss_UndOrg_TCASerializer(cargo_unidad_serie_subserie_undorg_tca,many=False)
    permisos_serializer = PermisosCargoUnidadSerieSubserieUnidadTCASerializer(permisos_serializer_list, many=True)
    serializer_data = expediente_serializer.data
    serializer_data['permisos'] = permisos_serializer.data
    return Response({'success':True, 'detail':'Se asignaron correctamente los permisos al expediente clasificado', 'data':serializer_data},status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def actualizar_cargo_unidad_permiso_expediente(request,pk):
    data = request.data
    try:
        cargo_unidad_serie_subserie_undorg_tca = Cargos_Unidad_S_Ss_UndOrg_TCA.objects.get(id_cargo_unidad_s_subserie_unidad_org_tca=pk)
        entry__previous=copy.copy(cargo_unidad_serie_subserie_undorg_tca)

    except:
        return Response({'success':False,'detail':'El expediente elegido es invalido'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not data.getlist('permisos'):
        return Response({'success':False, 'detail':'Debe elegir por lo menos un permiso'}, status=status.HTTP_400_BAD_REQUEST)
    
    permisos_validados_list = PermisosGD.objects.filter(cod_permiso_gd__in=data.getlist('permisos'))
    if len(data.getlist('permisos')) != len(permisos_validados_list):
        return Response({'success':False, 'detail':'Uno de los permisos ingresados no existe'}, status=status.HTTP_400_BAD_REQUEST)
    
    permisos_validados_list = PermisosCargoUnidadSerieSubserieUnidadTCA.objects.filter(id_cargo_unidad_s_ss_unidad_tca=cargo_unidad_serie_subserie_undorg_tca.id_cargo_unidad_s_subserie_unidad_org_tca)
    lista_de_permisos = [x.cod_permiso.tipo_permiso for x in permisos_validados_list]
    string_permisos = ' | '.join(lista_de_permisos)
    
    lista_permisos = [str(x.cod_permiso.cod_permiso_gd) for x in permisos_validados_list]
    lista_crear = list(set(data.getlist('permisos'))-set(lista_permisos)) 
    permisos_validados_list.exclude(cod_permiso__in= data.getlist('permisos')).delete()
    permisos_serializer_list = []
    
    for permiso in lista_crear:
        permiso_cargo_unidad_s_ss_unidad_tca = PermisosCargoUnidadSerieSubserieUnidadTCA.objects.create(
            id_cargo_unidad_s_ss_unidad_tca = cargo_unidad_serie_subserie_undorg_tca,
            cod_permiso = PermisosGD.objects.get(cod_permiso_gd=permiso) 
        )
        permisos_serializer_list.append(permiso_cargo_unidad_s_ss_unidad_tca)
        
    match cargo_unidad_serie_subserie_undorg_tca.id_clasif_serie_subserie_unidad_tca.id_tca.actual:
        case True:
            justificacion_cambio = data['justificacion_del_cambio']
            ruta_archivo_cambio = request.FILES.get('ruta_archivo_cambio')
            
            if (not justificacion_cambio or justificacion_cambio == '') or not ruta_archivo_cambio:
                return Response({'success':False, 'detail':'Debe enviar una justificación y un archivo de soporte de la actualización de los permisos que desea realizar'}, status=status.HTTP_400_BAD_REQUEST)
            
            cargo_unidad_serie_subserie_undorg_tca.justificacion_del_cambio = justificacion_cambio
            cargo_unidad_serie_subserie_undorg_tca.ruta_archivo_cambio = ruta_archivo_cambio
            cargo_unidad_serie_subserie_undorg_tca.save()
            HistoricoCargosUnidadSerieSubserieUnidadTCA.objects.create(
                id_cargo_unidad_s_ss_unidad_tca = cargo_unidad_serie_subserie_undorg_tca,
                nombre_permisos = string_permisos,
                justificacion= cargo_unidad_serie_subserie_undorg_tca.justificacion_del_cambio,
                ruta_archivo= cargo_unidad_serie_subserie_undorg_tca.ruta_archivo_cambio,
                id_persona_cambia= request.user.persona,
            )
        # case False:
        #     HistoricoCargosUnidadSerieSubserieUnidadTCA.objects.create(
        #         id_cargo_unidad_s_ss_unidad_tca = cargo_unidad_serie_subserie_undorg_tca,
        #         nombre_permisos = string_permisos,
        #         id_persona_cambia= request.user.persona,
        #     )

    expediente_serializer = Cargos_Unidad_S_Ss_UndOrg_TCASerializer(cargo_unidad_serie_subserie_undorg_tca,many=False)
    permisos_serializer = PermisosCargoUnidadSerieSubserieUnidadTCASerializer(permisos_serializer_list, many=True)    
    
    serializer_data = expediente_serializer.data
    serializer_data['permisos'] = permisos_serializer.data
    
    return Response({'success':True, 'detail':'Se actualizaron correctamente los permisos al expediente clasificado', 'data':serializer_data}, status=status.HTTP_201_CREATED)

class EliminarCargoUnidadPermisoExp(generics.DestroyAPIView):
    serializer_class = Cargos_Unidad_S_Ss_UndOrg_TCASerializer
    queryset = Cargos_Unidad_S_Ss_UndOrg_TCA.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        cargo_unidad_exp = self.queryset.all().filter(id_cargo_unidad_s_subserie_unidad_org_tca=pk).first()
        
        if cargo_unidad_exp:
            if cargo_unidad_exp.id_clasif_serie_subserie_unidad_tca.id_tca.fecha_retiro_produccion:
                return Response({'success':False, 'detail':'No se puede eliminar la asociación del cargo, unidad y permisos porque la TCA fue retirada de producción'}, status=status.HTTP_403_FORBIDDEN)
            if cargo_unidad_exp.id_clasif_serie_subserie_unidad_tca.id_tca.actual:
                return Response({'success':False, 'detail':'No se puede eliminar la asociación del cargo, unidad y permisos para una TCA actual'}, status=status.HTTP_403_FORBIDDEN)
            if cargo_unidad_exp.id_clasif_serie_subserie_unidad_tca.id_tca.fecha_terminado:
                return Response({'success':False, 'detail':'No se puede eliminar la asociación del cargo, unidad y permisos porque la TCA fue terminada. Intente reanudar primero'}, status=status.HTTP_403_FORBIDDEN)
            
            cargo_unidad_exp.delete()
            return Response({'success':True, 'detail':'Se ha eliminado la relacion del cargo, unidad y los permisos asignados del expediente elegido'}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No existe la asociación del cargo, unidad y permisos ingresada'}, status=status.HTTP_404_NOT_FOUND)

class FinalizarTablaControlAcceso(generics.UpdateAPIView):
    serializer_class = TCAPostSerializer
    queryset = TablasControlAcceso
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        tca = TablasControlAcceso.objects.filter(id_tca=pk).first()
        if tca:
            #Validacion existencia del tca a finalizar
            if not tca.fecha_terminado:
                ccd = tca.id_ccd
                
                series = SeriesDoc.objects.filter(id_ccd=ccd.id_ccd)
                series_list = [serie.id_serie_doc for serie in series]

                series_subseries_unidades = CatalogosSeriesUnidad.objects.filter(id_catalogo_serie__id_serie_doc__in=series_list)
                series_subseries_unidades_list = [serie_subserie_unidad.id_cat_serie_und for serie_subserie_unidad in series_subseries_unidades]

                clasif_expedientes_tca = Clasif_Serie_Subserie_Unidad_TCA.objects.filter(id_cat_serie_und__in=series_subseries_unidades_list)
                clasif_expedientes_tca_list = [clasif_expediente.id_cat_serie_und.id_cat_serie_und for clasif_expediente in clasif_expedientes_tca]

                if not set(series_subseries_unidades_list).issubset(clasif_expedientes_tca_list):
                    return Response({'success': False, 'detail': 'Debe clasificar todos los expedientes para finalizar TCA'}, status=status.HTTP_403_FORBIDDEN)
                    
                tca.fecha_terminado = datetime.now(pytz.timezone('America/Bogota'))
                tca.save()
                return Response({'success': True, 'detail': 'Finalizado el TCA'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'detail': 'Ya se encuentra finalizado este TCA'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No se encontró ningún TCA con estos parámetros'}, status=status.HTTP_404_NOT_FOUND)   

class GetClasifSerieSubserieUnidad(generics.ListAPIView):
    serializer_class = CatalogosSeriesUnidadClasifSerializer
    queryset = TablasControlAcceso.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_tca):
        tca = self.queryset.all().filter(id_tca=id_tca).first()
        if tca:
            serie_subserie_unidad = CatalogosSeriesUnidad.objects.filter(id_catalogo_serie__id_serie_doc__id_ccd = tca.id_ccd.id_ccd).distinct('id_unidad_organizacional', 'id_serie_doc')
            serie_subserie_unidad = [ssu for ssu in serie_subserie_unidad if ssu.clasif_serie_subserie_unidad_tca_set.all()]
            serializer = self.serializer_class(serie_subserie_unidad, many=True, context={'id_tca': id_tca})
            return Response({'success':True, 'detail':'Se encontraron las siguientes clasificaciones', 'data':serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No existe la TCA ingresada'}, status=status.HTTP_404_NOT_FOUND)
        
class GetCargoUnidadPermisos(generics.ListAPIView):
    serializer_class = CatalogosSeriesUnidadClasifPermisosSerializer
    queryset = TablasControlAcceso.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_tca):
        tca = self.queryset.all().filter(id_tca=id_tca).first()
        if tca:
            serie_subserie_unidad = CatalogosSeriesUnidad.objects.filter(id_catalogo_serie__id_serie_doc__id_ccd = tca.id_ccd.id_ccd)
            clasif_serie_subserie_unidad = [ssu.clasif_serie_subserie_unidad_tca_set.all().first() for ssu in serie_subserie_unidad if ssu.clasif_serie_subserie_unidad_tca_set.all()]
            serie_subserie_unidad = [cssu.id_catalogo_serie for cssu in clasif_serie_subserie_unidad if cssu.cargos_unidad_s_ss_undorg_tca_set.all()]
            serializer = self.serializer_class(serie_subserie_unidad, many=True, context={'id_tca': id_tca})
            return Response({'success':True, 'detail':'Se encontraron las siguientes clasificaciones', 'data':serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No existe la TCA ingresada'}, status=status.HTTP_404_NOT_FOUND)