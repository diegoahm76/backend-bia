from rest_framework import generics,status
from rest_framework.response import Response

from gestion_documental.models.radicados_models import PQRSDF, T262Radicados
from gestion_documental.serializers.radicados_serializers import RadicadosImprimir

class GetRadicadosImprimir(generics.ListAPIView):
    serializer_class = RadicadosImprimir
    queryset = T262Radicados.objects.all()

    def get(self, request):
        try:
            filter = {}
            for key,value in request.query_params.items():
                if key in ['cod_tipo_radicado','prefijo_radicado','agno_radicado','nro_radicado','fecha_radicado']:
                    if key == "nro_radicado":
                        if value != "":
                            filter[key+'__endswith'] = int(value)
                    elif key == "fecha_radicado":
                        if value != "":
                            filter[key+'__contains'] = value
                    else:
                        if value != "":
                            filter[key] = value

            radicados = self.queryset.filter(**filter)

            data_to_serializer = self.set_data(radicados)
            serializer = self.serializer_class(data_to_serializer, many=True)
            return Response({'success':True, 'detail':'Se encontraron los siguientes radicados que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            raise({'success': False, 'detail': str(e)}) 

    def set_data(self, radicados):
        data_radicados = []
        for radicado in radicados:
            pqrsdf_instance = PQRSDF.objects.all()
            if radicado.id_modulo_que_radica == 1:
                pqrsdf = pqrsdf_instance.filter(id_radicado = radicado.id_radicado).first()
                data_radicados.append({"radicado": radicado, "pqrsdf": pqrsdf})

            elif radicado.id_modulo_que_radica == 2:
                pass
            elif radicado.id_modulo_que_radica == 3:
                pass
            elif radicado.id_modulo_que_radica == 4:
                pass
            elif radicado.id_modulo_que_radica == 5:
                pass
            elif radicado.id_modulo_que_radica == 6:
                pass
            elif radicado.id_modulo_que_radica == 7:
                pass
        
        return data_radicados