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
    def get_cantidad_posible(id_bien, id_bodega, id_despacho):
        inventario = Inventario.objects.filter(id_bien=id_bien, id_bodega=id_bodega).first()
        saldo_actual = inventario.cantidad_entrante_consumo - (inventario.cantidad_saliente_consumo if inventario.cantidad_saliente_consumo else 0)
        
        despacho = DespachoConsumo.objects.filter(id_despacho_consumo=id_despacho).first()
        
        entradas = EntradasAlmacen.objects.filter(fecha_entrada__gte=despacho.fecha_despacho, entrada_anulada=None)
        cantidad_disponible = saldo_actual
        cantidad_total_entradas = 0
        cantidad_posible = 0
        
        # HALLAR CANTIDAD DISPONIBLE
        
        if entradas:
            entradas_id = [entrada.id_entrada_almacen for entrada in entradas] if entradas else []
            cantidad_total_entradas = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_id, id_bien=id_bien, id_bodega=id_bodega).aggregate(cantidad=Sum('cantidad'))
            cantidad_total_entradas = cantidad_total_entradas['cantidad'] if cantidad_total_entradas else 0
            
            cantidad_disponible = saldo_actual - (cantidad_total_entradas if cantidad_total_entradas else 0)
        
        despachos = DespachoConsumo.objects.filter(fecha_despacho__gte=despacho.fecha_despacho, despacho_anulado=None)
        
        if despachos:
            despachos_id = [despacho.id_despacho_consumo for despacho in despachos] if despachos else []
            
            cantidad_total_despachos = ItemDespachoConsumo.objects.filter(id_despacho_consumo__in=despachos_id, id_bien_despachado=id_bien, id_bodega=id_bodega).aggregate(cantidad=Sum('cantidad_despachada'))
            
            cantidad_disponible = cantidad_disponible + (cantidad_total_despachos['cantidad'] if cantidad_total_despachos and cantidad_total_despachos['cantidad'] else 0)
            
            # HALLAR CANTIDAD POSIBLE
            
            despachos_id.remove(despacho.id_despacho_consumo)
            
            if despachos_id:
                cantidad_total_despachos_except = ItemDespachoConsumo.objects.filter(id_despacho_consumo__in=despachos_id, id_bien_despachado=id_bien, id_bodega=id_bodega).aggregate(cantidad=Sum('cantidad_despachada'))
                
                cantidad_posible = cantidad_disponible - (cantidad_total_despachos_except['cantidad'] if cantidad_total_despachos_except['cantidad'] else 0) + cantidad_total_entradas
            else:
                cantidad_posible = cantidad_disponible
            
        return cantidad_posible

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
                    tipo_documento=F('id_entrada_almacen__id_tipo_entrada__nombre')).annotate(cantidad_total_entrada=Sum('cantidad'))
        
        item_despachado=ItemDespachoConsumo.objects.filter(id_bien_despachado=id_bien,id_entrada_almacen_bien=id_entrada).values('id_bien_despachado','id_entrada_almacen_bien').annotate(cantidad_total_despachada=Sum('cantidad_despachada'))
        
        cantidad_por_distribuir=item_entrada[0]['cantidad_total_entrada'] - item_despachado[0]['cantidad_total_despachada'] if item_despachado and item_despachado[0]['cantidad_total_despachada'] else item_entrada[0]['cantidad_total_entrada']
        
        return cantidad_por_distribuir