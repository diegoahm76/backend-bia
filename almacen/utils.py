from django.core.mail import EmailMessage
from django.db.models import Sum
from email_validator import validate_email, EmailNotValidError, EmailUndeliverableError, EmailSyntaxError
from backend.settings.base import EMAIL_HOST_USER, AUTHENTICATION_360_NRS
from seguridad.models import Shortener, User, Modulos, Permisos, Auditorias
from almacen.models.inventario_models import (
    Inventario
)
from almacen.models.bienes_models import EntradasAlmacen, ItemEntradaAlmacen
from almacen.models.solicitudes_models import DespachoConsumo, ItemDespachoConsumo
import re, requests
from django.db.models import Q, F
from datetime import datetime, date,timedelta

class UtilAlmacen:
    
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject= data['email_subject'], body=data['template'], to=[data['to_email']], from_email=EMAIL_HOST_USER)
        
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

            cantidad_disponible = saldo_actual - cantidad_total_entradas['cantidad']
            
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
        # HALLAR CANTIDAD TOTAL DE ENTRADAS ANTERIORES
        entrada = EntradasAlmacen.objects.filter(id_entrada_almacen=id_entrada).first()
        entradas_anteriores = EntradasAlmacen.objects.filter(fecha_entrada__lte=entrada.fecha_entrada, entrada_anulada=None)
        entradas_anteriores_id = [entrada_anterior.id_entrada_almacen for entrada_anterior in entradas_anteriores]
        entradas_anteriores_id.remove(entrada.id_entrada_almacen)
        
        cantidad_entradas_anteriores = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_anteriores_id, id_bien=id_bien, id_bodega=id_bodega).values('id_bien', 'id_bodega').annotate(cantidad_entradas=Sum('cantidad'))
        cantidad_entradas_anteriores = cantidad_entradas_anteriores[0]['cantidad_entradas'] if cantidad_entradas_anteriores else 0
        
        # HALLAR CANTIDAD TOTAL DE SALIDAS ANTERIORES Y EL SALDO
        salidas_anteriores = DespachoConsumo.objects.filter(fecha_despacho__lte=entrada.fecha_entrada, despacho_anulado=None)
        salidas_anteriores_id = [salida_anterior.id_despacho_consumo for salida_anterior in salidas_anteriores]
        
        cantidad_salidas_anteriores = ItemDespachoConsumo.objects.filter(id_despacho_consumo__in=salidas_anteriores_id, id_bien_despachado=id_bien, id_bodega=id_bodega).values('id_bien_despachado', 'id_bodega').annotate(cantidad_salidas=Sum('cantidad_despachada'))
        cantidad_salidas_anteriores = cantidad_salidas_anteriores[0]['cantidad_salidas'] if cantidad_salidas_anteriores else 0
        
        saldo = cantidad_entradas_anteriores - cantidad_salidas_anteriores
        
        # HALLAR REGISTROS DE ENTRADAS POSTERIORES
        entradas_posteriores = EntradasAlmacen.objects.filter(fecha_entrada__gte=entrada.fecha_entrada, entrada_anulada=None)
        entradas_posteriores_id = [entrada_posterior.id_entrada_almacen for entrada_posterior in entradas_posteriores]
        entradas_posteriores_id.remove(entrada.id_entrada_almacen)
        
        registros_entradas_posteriores = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_posteriores_id, id_bien=id_bien, id_bodega=id_bodega).values('cantidad', fecha=F('id_entrada_almacen__fecha_entrada'))
        
        for registro in registros_entradas_posteriores:
            registro['tipo'] = 'E'
        
        # HALLAR REGISTROS DE SALIDAS POSTERIORES
        salidas_posteriores = DespachoConsumo.objects.filter(fecha_despacho__gte=entrada.fecha_entrada, despacho_anulado=None)
        salidas_posteriores_id = [salida_posterior.id_despacho_consumo for salida_posterior in salidas_posteriores]
        
        registros_salidas_posteriores = ItemDespachoConsumo.objects.filter(id_despacho_consumo__in=salidas_posteriores_id, id_bien_despachado=id_bien, id_bodega=id_bodega).values(cantidad=F('cantidad_despachada'), fecha=F('id_despacho_consumo__fecha_despacho'))
        
        for registro in registros_salidas_posteriores:
            registro['tipo'] = 'S'
        
        registros_posteriores = list(registros_entradas_posteriores) + list(registros_salidas_posteriores)
        registros_posteriores = sorted(registros_posteriores, key=lambda x: x["fecha"], reverse=True)
        
        # ALGORITMO OBTENER ACUMULADO
        acum = 0
        valor_ciclo = 0
        salidas = 0
        
        for registro in registros_posteriores:
            if registro['tipo'] == 'S':
                salidas = salidas + registro['cantidad']
            else:
                valor_ciclo = registro['cantidad'] - salidas
                acum = acum + valor_ciclo
                if(valor_ciclo > 0):
                   acum = 0
                salidas = 0
        
        # HALLAR VALOR MINIMO ACTUALIZABLE DE LA ENTRADA
        valor_requerido = salidas - acum
        valor_minimo = valor_requerido - saldo
        
        return valor_minimo
    
    @staticmethod
    def get_valor_maximo_despacho(id_bien, id_bodega, id_despacho):
        # HALLAR CANTIDAD TOTAL DE SALIDAS ANTERIORES
        salida = DespachoConsumo.objects.filter(id_despacho_consumo=id_despacho).first()
        salidas_anteriores = DespachoConsumo.objects.filter(fecha_despacho__lte=salida.fecha_despacho, despacho_anulado=None)
        salidas_anteriores_id = [salida_anterior.id_despacho_consumo for salida_anterior in salidas_anteriores]
        salidas_anteriores_id.remove(salida.id_despacho_consumo)
        
        cantidad_salidas_anteriores = ItemDespachoConsumo.objects.filter(id_despacho_consumo__in=salidas_anteriores_id, id_bien_despachado=id_bien, id_bodega=id_bodega).values('id_bien_despachado', 'id_bodega').annotate(cantidad_salidas=Sum('cantidad_despachada'))
        cantidad_salidas_anteriores = cantidad_salidas_anteriores[0]['cantidad_salidas'] if cantidad_salidas_anteriores else 0
        
        # HALLAR CANTIDAD TOTAL DE ENTRADAS ANTERIORES Y EL SALDO
        entradas_anteriores = EntradasAlmacen.objects.filter(fecha_entrada__lte=salida.fecha_despacho, entrada_anulada=None)
        entradas_anteriores_id = [entrada_anterior.id_entrada_almacen for entrada_anterior in entradas_anteriores]
        
        cantidad_entradas_anteriores = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_anteriores_id, id_bien=id_bien, id_bodega=id_bodega).values('id_bien', 'id_bodega').annotate(cantidad_entradas=Sum('cantidad'))
        cantidad_entradas_anteriores = cantidad_entradas_anteriores[0]['cantidad_entradas'] if cantidad_entradas_anteriores else 0
        
        saldo = cantidad_entradas_anteriores - cantidad_salidas_anteriores
        
        # HALLAR REGISTROS DE ENTRADAS POSTERIORES
        entradas_posteriores = EntradasAlmacen.objects.filter(fecha_entrada__gte=salida.fecha_despacho, entrada_anulada=None)
        entradas_posteriores_id = [entrada_posterior.id_entrada_almacen for entrada_posterior in entradas_posteriores]
        
        registros_entradas_posteriores = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_posteriores_id, id_bien=id_bien, id_bodega=id_bodega).values('cantidad', fecha=F('id_entrada_almacen__fecha_entrada'))
        
        for registro in registros_entradas_posteriores:
            registro['tipo'] = 'E'
        
        salidas_posteriores = DespachoConsumo.objects.filter(fecha_despacho__gte=salida.fecha_despacho, despacho_anulado=None)
        salidas_posteriores_id = [salida_posterior.id_despacho_consumo for salida_posterior in salidas_posteriores]
        salidas_posteriores_id.remove(salida.id_despacho_consumo)
        
        # HALLAR REGISTROS DE SALIDAS POSTERIORES
        registros_salidas_posteriores = ItemDespachoConsumo.objects.filter(id_despacho_consumo__in=salidas_posteriores_id, id_bien_despachado=id_bien, id_bodega=id_bodega).values(cantidad=F('cantidad_despachada'), fecha=F('id_despacho_consumo__fecha_despacho'))
        
        for registro in registros_salidas_posteriores:
            registro['tipo'] = 'S'
        
        registros_posteriores = list(registros_entradas_posteriores) + list(registros_salidas_posteriores)
        registros_posteriores = sorted(registros_posteriores, key=lambda x: x["fecha"], reverse=True)
        
        # ALGORITMO OBTENER ACUMULADO
        acum = 0
        valor_ciclo = 0
        salidas = 0
        
        for registro in registros_posteriores:
            if registro['tipo'] == 'S':
                salidas = salidas + registro['cantidad']
            else:
                valor_ciclo = registro['cantidad'] - salidas
                acum = acum + valor_ciclo
                if(valor_ciclo > 0):
                   acum = 0
                salidas = 0
        
        # HALLAR VALOR MAXIMO ACTUALIZABLE DEL DESPACHO
        valor_requerido = salidas + acum
        valor_maximo = valor_requerido + saldo
        
        return valor_maximo