from datetime import datetime

from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.utils import UtilsGestor
from recaudo.serializers.liquidaciones_serializers import HistEstadosLiqPostSerializer
from recaudo.serializers.pagos_serializers import ConsultarPagosSerializer
from seguridad.utils import Util


class UtilsRecaudo:
    @staticmethod
    def pago_exitoso(request, pago):
        print("ENTRÓ A UTIL DE PAGO EXITOSO")
        # GENERAR COMPROBANTE DE PAGO
        client_ip = Util.get_client_ip(request)
        pago_serializado = ConsultarPagosSerializer(pago)
        pago_serializado = pago_serializado.data
        info_archivo = {
            "Nombre Empresa": "CORMACARENA",
            "Fax Empresa": "NA",
            "Dirección Empresa": "CR 43 NO. 20A 47 MZ D CA 8",
            "Teléfono Empresa": 3102268176,
            "NIT Empresa": 9015152013,
            "Nombre Cliente": pago_serializado['nombre_persona_pago'],
            "Email Cliente": pago.id_persona_pago.email,
            "Identificación Cliente": pago.id_persona_pago.numero_documento,
            "Teléfono Cliente": pago.id_persona_pago.telefono_celular,
            "IP Cliente": client_ip,
            "Id Pago": pago.id_pago,
            "Medio Pago": "Pago PSE - débito desde su cuenta corriente o de ahorros",
            "Estado Pago": pago_serializado['desc_estado_pago'],
            "Fecha Pago": datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            "Iva": "0.00",
            "Total Pago": pago.id_liquidacion.valor,
            "Tipo Usuario": f"Persona {pago_serializado['tipo_usuario']}",
            "Descripcion Pago": "Test", # Pendiente por definir
            "Ciclo Transacción": request.query_params.get('ciclo_transaccion'),
            "Código Transacción": request.query_params.get('codigo_transaccion'),
            "Nombre Banco": request.query_params.get('nombre_banco'),
            "Codigo Banco": request.query_params.get('codigo_banco'),
            "Ticket": request.query_params.get('ticketID'),
            "Fecha Solicitud": datetime.now().strftime('%d-%m-%Y'),
            "Código Servicio": "2701"
        }
        comprobante = UtilsGestor.generar_archivo_blanco(info_archivo, f"Comprobante de Pago - Liquidacion {pago.id_liquidacion.id}.pdf", "home,BIA,Recaudo,GDEA,Pagos")
        comprobante_instance = ArchivosDigitales.objects.filter(id_archivo_digital=comprobante.data.get('data').get('id_archivo_digital')).first()

        pago.comprobante_pago = comprobante_instance
        pago.save()

        # Actualizar info en tramite
        tramite = pago.id_liquidacion.id_solicitud_tramite
        if tramite:
            if not tramite.pago:
                tramite.pago = True
                tramite.id_pago_evaluacion = pago
                tramite.save()

        # Actualizar estado en liquidacion
        pago.id_liquidacion.estado = 'PAGADO'
        pago.id_liquidacion.save()

        # Guardar historico liquidacion
        data_historico = {
            'liquidacion_base': pago.id_liquidacion.id,
            'estado_liq': 'PAGADO',
            'fecha_estado': datetime.now()
        }
        serializer_historico = HistEstadosLiqPostSerializer(data=data_historico)
        serializer_historico.is_valid(raise_exception=True)
        serializer_historico.save()