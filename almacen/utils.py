from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from email_validator import validate_email, EmailUndeliverableError
from transversal.models.organigrama_models import UnidadesOrganizacionales
from backend.settings.base import EMAIL_HOST_USER
from almacen.models.inventario_models import (
    Inventario
)
from almacen.models.bienes_models import EntradasAlmacen, ItemEntradaAlmacen
from almacen.models.solicitudes_models import DespachoConsumo, ItemDespachoConsumo
from django.db.models import Q, F
from datetime import datetime, timedelta

class UtilAlmacen:
    
    @staticmethod
    def send_email(data):
        email = EmailMultiAlternatives(subject= data['email_subject'], body=data['template'], to=[data['to_email']], from_email=EMAIL_HOST_USER)
        
        email.content_subtype ='html'
        response = email.send(fail_silently=True)
        print(response)
        return response
       

    @staticmethod
    def validate_dns(email):
        try: 
            validation = validate_email(email, check_deliverability=True)
            validate = validation.email
            return True
        except EmailUndeliverableError as e:
            return False
    
    @staticmethod
    def get_cantidad_disponible(id_bien, id_bodega, fecha_despacho):
        inventario = Inventario.objects.filter(id_bien=id_bien, id_bodega=id_bodega).first()
        saldo_actual = inventario.cantidad_entrante_consumo - (inventario.cantidad_saliente_consumo if inventario.cantidad_saliente_consumo else 0)
        
        entradas = EntradasAlmacen.objects.filter(fecha_entrada__gte=fecha_despacho, entrada_anulada=None)
        cantidad_disponible = saldo_actual
        
        if entradas:
            entradas_id = [entrada.id_entrada_almacen for entrada in entradas] if entradas else []
            cantidad_total_entradas = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_id, id_bien=id_bien, id_bodega=id_bodega).aggregate(cantidad=Sum('cantidad'))
            
            cantidad_disponible = saldo_actual - (cantidad_total_entradas['cantidad'] if cantidad_total_entradas and cantidad_total_entradas['cantidad'] else 0)
            
        return cantidad_disponible
        
    @staticmethod
    def get_cantidades_disponibles(bienes_id, fecha_despacho):
        cantidades_disponibles = []
        inventarios = Inventario.objects.filter(id_bien__in=bienes_id)
        for inventario in inventarios:
            saldo_actual = inventario.cantidad_entrante_consumo - (inventario.cantidad_saliente_consumo if inventario.cantidad_saliente_consumo else 0)
            
            entradas = EntradasAlmacen.objects.filter(fecha_entrada__gte=fecha_despacho, entrada_anulada=None)
            cantidad_total_entradas = [{'id_bien': inventario.id_bien.id_bien, 'id_bodega': inventario.id_bodega.id_bodega, 'cantidad_disponible': saldo_actual}]
            if entradas:
                entradas_id = [entrada.id_entrada_almacen for entrada in entradas] if entradas else []
                cantidad_total_entradas = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_id, id_bien=inventario.id_bien, id_bodega = inventario.id_bodega).values('id_bien', 'id_bodega').annotate(cantidad_disponible=saldo_actual - Sum('cantidad'))  
            cantidades_disponibles.append(cantidad_total_entradas[0])
        
        return cantidades_disponibles

    @staticmethod
    def get_cantidades_disponibles_entregas(id_bien, id_bodega, fecha_entrega):
        inventario = Inventario.objects.filter(id_bien=id_bien, id_bodega=id_bodega).first()
        saldo_actual = inventario.cantidad_entrante_consumo - (inventario.cantidad_saliente_consumo if inventario.cantidad_saliente_consumo else 0)
        
        entradas = EntradasAlmacen.objects.filter(Q(fecha_entrada__gte=fecha_entrega) & Q(entrada_anulada=None)).filter(Q(id_tipo_entrada=2) | Q(id_tipo_entrada=3) | Q(id_tipo_entrada=4))
        cantidad_disponible = saldo_actual
        
        if entradas:
            entradas_id = [entrada.id_entrada_almacen for entrada in entradas] if entradas else []
            cantidad_total_entradas = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_id, id_bien=id_bien, id_bodega=id_bodega).aggregate(cantidad=Sum('cantidad'))
            cantidad_total_entradas = cantidad_total_entradas['cantidad']
            
            cantidad_disponible = saldo_actual - cantidad_total_entradas if cantidad_total_entradas else saldo_actual
            
        return cantidad_disponible

    @staticmethod
    def get_cantidad_por_distribuir(id_bien, id_entrada, fecha_despacho):
        fecha_hace_un_año=datetime.today()-timedelta(days=365)
        cantidad_por_distribuir = 0
        
        item_entrada=ItemEntradaAlmacen.objects.filter(
            id_entrada_almacen=id_entrada,
            id_bien=id_bien,id_entrada_almacen__fecha_entrada__gte=fecha_hace_un_año,
            id_entrada_almacen__fecha_entrada__lte=fecha_despacho).filter(
                Q(id_entrada_almacen__id_tipo_entrada=2) | 
                Q(id_entrada_almacen__id_tipo_entrada=3) | 
                Q(id_entrada_almacen__id_tipo_entrada=4)).values(
                    'id_bien',"id_entrada_almacen",
                    codigo_bien=F('id_bien__codigo_bien'),
                    nombre=F('id_bien__nombre'),
                    numero_documento=F('id_entrada_almacen__numero_entrada_almacen'),
                    tipo_documento=F('id_entrada_almacen__id_tipo_entrada__nombre')).annotate(
                        cantidad_total_entrada=Sum('cantidad'))
        
        item_despachado=ItemDespachoConsumo.objects.filter(
            id_bien_despachado=id_bien,
            id_entrada_almacen_bien=id_entrada).values(
                'id_bien_despachado','id_entrada_almacen_bien').annotate(
                    cantidad_total_despachada=Sum('cantidad_despachada'))
        
        cantidad_por_distribuir=item_entrada[0]['cantidad_total_entrada'] - item_despachado[0]['cantidad_total_despachada'] if item_despachado and item_despachado[0]['cantidad_total_despachada'] else item_entrada[0]['cantidad_total_entrada']
        
        return cantidad_por_distribuir
    
    @staticmethod
    def get_valor_minimo_entradas(id_bien, id_bodega, id_entrada):
        # HALLAR SALDO ACTUAL
        entrada = EntradasAlmacen.objects.filter(id_entrada_almacen=id_entrada).first()
        inventario = Inventario.objects.filter(id_bien=id_bien, id_bodega=id_bodega).first()

        saldo_actual = inventario.cantidad_entrante_consumo - inventario.cantidad_saliente_consumo
        
        # HALLAR REGISTROS DE ENTRADAS POSTERIORES
        entradas_posteriores = EntradasAlmacen.objects.filter(fecha_entrada__gte=entrada.fecha_entrada, entrada_anulada=None)
        entradas_posteriores_id = [entrada_posterior.id_entrada_almacen for entrada_posterior in entradas_posteriores]
        
        registros_entradas_posteriores = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_posteriores_id, id_bien=id_bien, id_bodega=id_bodega).values('cantidad', fecha=F('id_entrada_almacen__fecha_entrada'), id=F('id_entrada_almacen'))
        
        for registro in registros_entradas_posteriores:
            registro['tipo'] = 'E'
        
        cantidad_total_entradas = [registro['cantidad'] for registro in registros_entradas_posteriores]
        cantidad_total_entradas = sum(cantidad_total_entradas)
        
        # HALLAR REGISTROS DE SALIDAS POSTERIORES
        salidas_posteriores = DespachoConsumo.objects.filter(fecha_despacho__gte=entrada.fecha_entrada, despacho_anulado=None)
        salidas_posteriores_id = [salida_posterior.id_despacho_consumo for salida_posterior in salidas_posteriores]
        
        registros_salidas_posteriores = ItemDespachoConsumo.objects.filter(id_despacho_consumo__in=salidas_posteriores_id, id_bien_despachado=id_bien, id_bodega=id_bodega).values(cantidad=F('cantidad_despachada'), fecha=F('id_despacho_consumo__fecha_despacho'), id=F('id_despacho_consumo'))
        
        # HALLAR SALDO EN ENTRADA
        cantidad_total_salidas = [registro['cantidad'] for registro in registros_salidas_posteriores]
        cantidad_total_salidas = sum(cantidad_total_salidas)
        
        saldo_salida = saldo_actual - cantidad_total_entradas + cantidad_total_salidas
        
        for registro in registros_salidas_posteriores:
            registro['tipo'] = 'S'
        
        registros_posteriores = list(registros_entradas_posteriores) + list(registros_salidas_posteriores)
        registros_posteriores = sorted(registros_posteriores, key=lambda x: x["fecha"])
        
        # ALGORITMO OBTENER VALOR MINIMO
        z = 0
        saldo_evento = saldo_salida
        
        for index, registro in enumerate(registros_posteriores):
            if registro['tipo'] == 'S':
                saldo_evento = saldo_evento - registro['cantidad']
            else:
                saldo_evento = saldo_evento + registro['cantidad']
            if index == 0:
                z = saldo_evento
            elif saldo_evento < z:
                z = saldo_evento
        
        cantidad_evento = [item for item in registros_entradas_posteriores if item['id'] == entrada.id_entrada_almacen]
        valor_minimo = cantidad_evento[0]['cantidad'] - z
        if valor_minimo < 0:
            valor_minimo = 0
        
        return valor_minimo
    
    @staticmethod
    def get_valor_maximo_despacho(id_bien, id_bodega, id_despacho):
        # HALLAR SALDO ACTUAL
        salida = DespachoConsumo.objects.filter(id_despacho_consumo=id_despacho).first()
        inventario = Inventario.objects.filter(id_bien=id_bien, id_bodega=id_bodega).first()

        saldo_actual = inventario.cantidad_entrante_consumo - inventario.cantidad_saliente_consumo
        
        # HALLAR REGISTROS DE ENTRADAS POSTERIORES
        entradas_posteriores = EntradasAlmacen.objects.filter(fecha_entrada__gte=salida.fecha_despacho, entrada_anulada=None)
        entradas_posteriores_id = [entrada_posterior.id_entrada_almacen for entrada_posterior in entradas_posteriores]
        
        registros_entradas_posteriores = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_posteriores_id, id_bien=id_bien, id_bodega=id_bodega).values('cantidad', fecha=F('id_entrada_almacen__fecha_entrada'), id=F('id_entrada_almacen'))
        
        for registro in registros_entradas_posteriores:
            registro['tipo'] = 'E'
        
        cantidad_total_entradas = [registro['cantidad'] for registro in registros_entradas_posteriores]
        cantidad_total_entradas = sum(cantidad_total_entradas)
        
        # HALLAR REGISTROS DE SALIDAS POSTERIORES
        salidas_posteriores = DespachoConsumo.objects.filter(fecha_despacho__gte=salida.fecha_despacho, despacho_anulado=None)
        salidas_posteriores_id = [salida_posterior.id_despacho_consumo for salida_posterior in salidas_posteriores]
        
        registros_salidas_posteriores = ItemDespachoConsumo.objects.filter(id_despacho_consumo__in=salidas_posteriores_id, id_bien_despachado=id_bien, id_bodega=id_bodega).values(cantidad=F('cantidad_despachada'), fecha=F('id_despacho_consumo__fecha_despacho'), id=F('id_despacho_consumo'))
        
        # HALLAR SALDO EN SALIDA
        cantidad_total_salidas = [registro['cantidad'] for registro in registros_salidas_posteriores]
        cantidad_total_salidas = sum(cantidad_total_salidas)
        
        saldo_salida = saldo_actual - cantidad_total_entradas + cantidad_total_salidas
        
        for registro in registros_salidas_posteriores:
            registro['tipo'] = 'S'
        
        registros_posteriores = list(registros_entradas_posteriores) + list(registros_salidas_posteriores)
        registros_posteriores = sorted(registros_posteriores, key=lambda x: x["fecha"])
        
        # ALGORITMO OBTENER ACUMULADO
        z = 0
        saldo_evento = saldo_salida
        
        for index, registro in enumerate(registros_posteriores):
            if registro['tipo'] == 'S':
                saldo_evento = saldo_evento - registro['cantidad']
            else:
                saldo_evento = saldo_evento + registro['cantidad']
            if index == 0:
                z = saldo_evento
            elif saldo_evento < z:
                z = saldo_evento
        
        cantidad_evento = [item for item in registros_salidas_posteriores if item['id'] == salida.id_despacho_consumo]
        valor_maximo = cantidad_evento[0]['cantidad'] + z
        
        return valor_maximo
    
    @staticmethod
    def get_unidades_actual_iguales_y_arriba(unidad_instance):
        unidades_iguales_y_arriba = []
        aux_unidades_mismo_nivel = unidad_instance.nombre
        unidades_iguales_y_arriba.append(aux_unidades_mismo_nivel)
        
        if unidad_instance.unidad_raiz == False:
            unidades_arriba = unidad_instance.id_unidad_org_padre.nombre
            unidades_iguales_y_arriba.append(unidades_arriba)
            count = unidad_instance.id_unidad_org_padre.id_nivel_organigrama.orden_nivel - 1
            aux_menor = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = unidad_instance.id_unidad_org_padre.id_unidad_organizacional).first()
            if aux_menor.id_nivel_organigrama.orden_nivel >= 2:
                if aux_menor.id_unidad_org_padre.unidad_raiz == False:
                    print("asdasdasd")
                    unidades_iguales_y_arriba.append(aux_menor.id_unidad_org_padre.nombre)
                    while count >= 1:
                        aux_menor = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional = aux_menor.id_unidad_org_padre.id_unidad_organizacional).first()
                        if aux_menor.id_unidad_org_padre:
                            unidades_iguales_y_arriba.append(aux_menor.id_unidad_org_padre.nombre)
                        count = count - 1
                        
        unidad_raiz = UnidadesOrganizacionales.objects.filter(unidad_raiz=True).first()
        if unidad_raiz.nombre not in unidades_iguales_y_arriba:
            unidades_iguales_y_arriba.append(unidad_raiz.nombre)
        
        return unidades_iguales_y_arriba