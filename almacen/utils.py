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
from django.db.models import Q

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
            
            cantidad_disponible = saldo_actual - cantidad_total_entradas['cantidad']
            
        return cantidad_disponible
        
    @staticmethod
    def get_cantidades_disponibles(bienes_id, fecha_despacho):
        cantidades_disponibles = []
        inventarios = Inventario.objects.filter(id_bien__in=bienes_id)
        for inventario in inventarios:
            saldo_actual = inventario.cantidad_entrante_consumo - (inventario.cantidad_saliente_consumo if inventario.cantidad_saliente_consumo else 0)
            
            entradas = EntradasAlmacen.objects.filter(fecha_entrada__gte=fecha_despacho, entrada_anulada=None)
            cantidad_total_entradas = {'id_bien': inventario.id_bien.id_bien, 'id_bodega': inventario.id_bodega.id_bodega, 'cantidad_disponible': saldo_actual}
            if entradas:
                entradas_id = [entrada.id_entrada_almacen for entrada in entradas] if entradas else []
                cantidad_total_entradas = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_id, id_bien=inventario.id_bien, id_bodega = inventario.id_bodega).values('id_bien', 'id_bodega').annotate(cantidad_disponible=saldo_actual - Sum('cantidad')).first()
            
            cantidades_disponibles.append(cantidad_total_entradas)
            
        return cantidades_disponibles

    @staticmethod
    def get_cantidades_disponibles_entregas(bienes_id, fecha_despacho):
        cantidades_disponibles = []
        inventarios = Inventario.objects.filter(id_bien__in=bienes_id)
        for inventario in inventarios:
            saldo_actual = inventario.cantidad_entrante_consumo - (inventario.cantidad_saliente_consumo if inventario.cantidad_saliente_consumo else 0)
            
            entradas = EntradasAlmacen.objects.filter(Q(fecha_entrada__gte=fecha_despacho) & Q(entrada_anulada=None) & Q(id_tipo_entrada=2) | Q(id_tipo_entrada=3) | Q(id_tipo_entrada=4))
            cantidad_total_entradas = {'id_bien': inventario.id_bien.id_bien, 'id_bodega': inventario.id_bodega.id_bodega, 'cantidad_disponible': saldo_actual}
            if entradas:
                entradas_id = [entrada.id_entrada_almacen for entrada in entradas] if entradas else []
                cantidad_total_entradas = ItemEntradaAlmacen.objects.filter(id_entrada_almacen__in=entradas_id, id_bien=inventario.id_bien, id_bodega = inventario.id_bodega).values('id_bien', 'id_bodega').annotate(cantidad_disponible=saldo_actual - Sum('cantidad')).first()
            
            cantidades_disponibles.append(cantidad_total_entradas)
            
        return cantidades_disponibles
    
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
