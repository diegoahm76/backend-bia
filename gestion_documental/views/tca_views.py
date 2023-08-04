from rest_framework import generics,status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
import copy, pytz
from datetime import datetime
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from transversal.serializers.organigrama_serializers import UnidadesGetSerializer
from transversal.models.organigrama_models import UnidadesOrganizacionales
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from gestion_documental.models.trd_models import TablaRetencionDocumental, CatSeriesUnidadOrgCCDTRD
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from seguridad.serializers.personas_serializers import CargosSerializer
from gestion_documental.serializers.tca_serializers import (
    GetClasifExpedientesSerializer,
    GetHistoricoTCASerializer,
    TCASerializer,
    TCAPostSerializer,
    TCAPutSerializer,
    ClasifSerieSubserieUnidadTCASerializer,
    ClasifSerieSubserieUnidadTCAPutSerializer,
    ClasifSerieSubseriUnidadTCA_activoSerializer,
    # PermisosCargoUnidadSerieSubserieUnidadTCASerializer,
    # Cargos_Unidad_S_Ss_UndOrg_TCASerializer,
    # CatalogosSeriesUnidadClasifSerializer,
    # CatalogosSeriesUnidadClasifPermisosSerializer,
    BusquedaTCASerializer,

)
from gestion_documental.models.ccd_models import (
    CatalogosSeriesUnidad,
    CuadrosClasificacionDocumental,
    SeriesDoc,
)
from transversal.models.organigrama_models import (
    Organigramas
)
from gestion_documental.models.tca_models import (
    TablasControlAcceso,
    CatSeriesUnidadOrgCCD_TRD_TCA,
    ClasificacionExpedientes,
    # PermisosCatSeriesUnidadOrgTCA,
    # PermisosDetPermisosCatSerieUndOrgTCA,
    # PermisosGD,
    HistoricoCatSeriesUnidadOrgCCD_TRD_TCA, 
    # HistoricoPermisosCatSeriesUndOrgTCA
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
            return Response({'success':True, 'detail':'El ccd cuenta con las siguientes unidades','data':serializador.data}, status=status.HTTP_200_OK)
        raise PermissionDenied('El ccd no cuenta con unidades')
    
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
                    return Response ({'success':True, 'detail':'Se encontraron cargos','data':serializador.data}, status=status.HTTP_200_OK)
                else: raise NotFound('No se encontraron cargos')
            raise PermissionDenied('No existe unidad')
        else:
            cargos=Cargos.objects.filter(activo=True).values()
            return Response ({'success':True, 'detail':'Se encontraron cargos', 'data':cargos}, status=status.HTTP_200_OK)
        
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
        serializer.is_valid(raise_exception=True)

        #Validación de seleccionar solo ccd terminados
        trd = serializer.validated_data.get('id_trd')
        if trd:
            serializado = serializer.save()

            # AUDITORIA CREAR TCA
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

            return Response({'success':True, 'detail':'TCA creada exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No existe la TRD elegida')

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
                        raise ValidationError('Validar data enviada, el nombre y la versión son requeridos y deben ser únicos')
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

                    return Response({'success':True, 'detail':'Tabla de Control de Acceso actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    raise PermissionDenied('No se puede actualizar una TCA terminada, intente reanudar primero')
            else:
                raise PermissionDenied('No puede realizar cambios a una TCA que ya fue retirada de producción')
        else:
            raise NotFound('No existe ninguna Tabla de Control de Acceso con los parámetros ingresados')

class ClasifSerieSubserieUnidadTCA(generics.CreateAPIView):
    serializer_class = ClasifSerieSubserieUnidadTCASerializer
    queryset = CatSeriesUnidadOrgCCD_TRD_TCA.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, id_tca):
        data = request.data
        # if 'id_cat_serie_und' not in data:
        #     raise ValidationError('Debe ingresar un ID de serie y unidad')

        tca = TablasControlAcceso.objects.filter(id_tca=id_tca).first()
        if tca:
            if not tca.fecha_retiro_produccion:
                if not tca.fecha_terminado or tca.actual:
                    # Validar existencia de expediente
                    expediente_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_catserie_unidadorg=data['id_cat_serie_und_ccd_trd']).first()
                    if not expediente_trd:
                        raise ValidationError('Debe ingresar un expediente que exista')

                    # Validad existencia del tipo clasificación
                    dict_tipo_clasificacion = dict(tipo_clasificacion_CHOICES)
                    if data.get('cod_clas_expediente') not in dict_tipo_clasificacion:
                        raise ValidationError('Debe ingresar un código de clasificación que exista')
                    
                    data['id_tca'] = id_tca
                    serializer = self.serializer_class(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

                    return Response({'success':True, 'detail':'Se realizó la clasificación del expediente exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    raise PermissionDenied('No puede realizar cambios a una TCA terminada, intente reanudar primero')
            else:
                raise PermissionDenied('No puede realizar cambios a una TCA que ya fue retirada de producción')
        else:
            raise NotFound('No existe ninguna Tabla de Control de Acceso con los parámetros ingresados')

class UpdateClasifSerieSubserieUnidadTCA(generics.UpdateAPIView):
    serializer_class = ClasifSerieSubserieUnidadTCAPutSerializer
    queryset = CatSeriesUnidadOrgCCD_TRD_TCA.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class_2=ClasifSerieSubseriUnidadTCA_activoSerializer
    def put(self, request, pk):
    
        data = request.data
        clasif_s_ss_unidad_tca = CatSeriesUnidadOrgCCD_TRD_TCA.objects.filter(id_cat_serie_unidad_org_ccd_trd_tca=pk).first()
        clasif__previous=copy.copy(clasif_s_ss_unidad_tca)
        if clasif_s_ss_unidad_tca:
            if not clasif_s_ss_unidad_tca.id_tca.fecha_retiro_produccion:
                if not clasif_s_ss_unidad_tca.id_tca.actual:
                    if not clasif_s_ss_unidad_tca.id_tca.fecha_terminado:
                        # Validad existencia del tipo clasificación
                        dict_tipo_clasificacion = dict(tipo_clasificacion_CHOICES)
                        if data['cod_clas_expediente'] not in dict_tipo_clasificacion:
                            raise ValidationError('Debe ingresar un código de clasificación que exista')
                        
                        serializer = self.serializer_class(clasif_s_ss_unidad_tca, data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()

                        return Response({'success':True, 'detail':'Se actualizó la clasificación del expediente exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
                    else:
                        raise PermissionDenied('No se puede actualizar una TCA terminada, intente reanudar primero')
                else:
                    dict_tipo_clasificacion = dict(tipo_clasificacion_CHOICES)
                    if data['cod_clas_expediente'] not in dict_tipo_clasificacion:
                        raise ValidationError('Debe ingresar un código de clasificación que exista')
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
                            
                    # HISTORICO:
                    if datos_actualizados:
                        HistoricoCatSeriesUnidadOrgCCD_TRD_TCA.objects.create(
                            id_catserie_unidad_org = clasif_s_ss_unidad_tca,
                            cod_clasificacion_exp = clasif__previous.cod_clas_expediente,
                            justificacion_del_cambio = clasif__previous.justificacion_cambio,
                            ruta_archivo_cambio = clasif__previous.ruta_archivo_cambio,
                            id_persona_cambia = persona_intance
                        )
                    return Response({'success':True, 'detail':'Se actualizó la clasificación del expediente exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                raise PermissionDenied('No puede realizar cambios a una TCA que ya fue retirada de producción')
        else:
            raise NotFound('No existe ninguna clasificación del expediente con los parámetros ingresados')

class ReanudarTablaControlAcceso(generics.UpdateAPIView):
    serializer_class = TCAPostSerializer
    queryset = TablasControlAcceso
    permission_classes = [IsAuthenticated]

    def put(self, request, id_tca):
        tca = TablasControlAcceso.objects.filter(id_tca=id_tca).first()
        if tca:
            if not tca.fecha_terminado:
                raise PermissionDenied('No puede reanudar un TCA no terminado')
            if tca.fecha_puesta_produccion:
                raise PermissionDenied('No se puede reanudar una TCA que ya fue puesta en producción')
            # if PermisosCatSeriesUnidadOrgTCA.objects.filter(id_tca=tca.id_tca).exists():
            #     raise PermissionDenied('No se puede reanudar una TCA que está siendo usada en una configuración de permisos')
            tca.fecha_terminado = None
            tca.save()
            return Response({'success':True, 'detail':'Se reanudó el TCA'}, status=status.HTTP_201_CREATED)
        else:
            raise NotFound('No se encontró ningún TCA con estos parámetros')

class EliminarRelaciones(generics.DestroyAPIView):
    serializer_class = GetClasifExpedientesSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        registro_catalogo_tca = CatSeriesUnidadOrgCCD_TRD_TCA.objects.filter(id_cat_serie_unidad_org_ccd_trd_tca=pk).first()
        if not registro_catalogo_tca:
            raise ValidationError('No se encontró el registro del catalogo TCA que desea eliminar')
        
        if registro_catalogo_tca.id_tca.actual:
            raise ValidationError('No puede eliminar un registro del catalogo TCA de un TCA actual')
        if registro_catalogo_tca.id_tca.fecha_terminado:
            raise ValidationError('No puede eliminar un registro del catalogo TCA de un TCA terminado, intente reanudar')

        registro_catalogo_tca.delete()

        return Response({'success':True, 'detail':"El registro del catalogo TCA elegido ha sido eliminado correctamente"}, status=status.HTTP_200_OK)

class FinalizarTablaControlAcceso(generics.UpdateAPIView):
    serializer_class = TCAPostSerializer
    queryset = TablasControlAcceso
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        tca = TablasControlAcceso.objects.filter(id_tca=pk).first()
        if tca:
            #Validacion existencia del tca a finalizar
            if not tca.fecha_terminado:
                trd = tca.id_trd

                # Validacion de clasificacion de expedientes
                cat_series_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_trd=tca.id_trd)
                if cat_series_trd:
                    cat_series_list = [cat_serie.id_catserie_unidadorg for cat_serie in cat_series_trd]

                    clasif_expedientes_tca = CatSeriesUnidadOrgCCD_TRD_TCA.objects.filter(id_cat_serie_und_ccd_trd__in=cat_series_list)
                            
                    if len(cat_series_list) != len(clasif_expedientes_tca):
                        raise PermissionDenied('Debe asignar un tipo de clasificación a todos los expedientes para finalizar TCA')

                else:
                    raise NotFound('No se encontró la TRD correspondiente')

                tca.fecha_terminado = datetime.now(pytz.timezone('America/Bogota'))
                tca.save()
                return Response({'success':True, 'detail':'Finalizado el TCA'}, status=status.HTTP_201_CREATED)
            else:
                raise PermissionDenied('Ya se encuentra finalizado este TCA')
        else:
            raise NotFound('No se encontró ningún TCA con estos parámetros')   

class BusquedaTCA(generics.ListAPIView):
    serializer_class = BusquedaTCASerializer 
    queryset = TablasControlAcceso.objects.all()
    permission_classes = [IsAuthenticated]

    def get (self, request):
        filter={}
        for key, value in request.query_params.items():
            if key in ['nombre','version']:
                if value != '':
                    filter[key+'__icontains'] = value
        
        ccd = self.queryset.filter(**filter)
        serializador = self.serializer_class(ccd,many=True)
        return Response({'succes': True, 'detail':'Resultados de la búsqueda', 'data':serializador.data}, status=status.HTTP_200_OK)

class GetClasifExpedientesTCA(generics.ListAPIView):
    serializer_class = GetClasifExpedientesSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, id_tca):
        queryset = CatSeriesUnidadOrgCCD_TRD_TCA.objects.filter(id_tca=id_tca)

        #VALIDACIÓN SI EXISTE LA TCA ENVIADA
        if not queryset:
            raise NotFound('No se encontró la TCA')  
            
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        return Response({'success':True, 'detail':'Se encontraron los siguientes resultados', 'data': data}, status=status.HTTP_200_OK)
    
class GetHistoricoTCA(generics.ListAPIView):
    serializer_class = GetHistoricoTCASerializer
    queryset = HistoricoCatSeriesUnidadOrgCCD_TRD_TCA.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        id_tca = request.query_params.get('id_tca')
        queryset = self.queryset.all()
        
        if id_tca:
            queryset = queryset.filter(id_catserie_unidad_org__id_tca=id_tca)
            
        serializador = self.serializer_class(queryset, many=True)
                         
        return Response({'succes':True, 'detail':'Se encontró el siguiente histórico','data':serializador.data}, status=status.HTTP_200_OK)
