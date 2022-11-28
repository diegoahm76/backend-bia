from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from seguridad.models import UsuariosRol, Auditorias
from datetime import datetime
from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    
# @receiver(post_save, sender=UsuariosRol)
# def create_auditoria(sender, instance, created, **kwargs):
#     print(IsAuthenticated.has_permission)
#     if created:
#         now = datetime.now()
#         print("now =", now)
#         # dd/mm/YY H:M:S
#         dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
#         print("date and time =", dt_string)
#         Auditorias.objects.create(fecha_accion = dt_string)    