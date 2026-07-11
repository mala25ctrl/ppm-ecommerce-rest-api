from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.permissions import IsAdminUser
from users.serializers import UserSerializer

User = get_user_model()

@extend_schema_view(
    list=extend_schema(tags=['Utenti']),
    retrieve=extend_schema(tags=['Utenti']),
    create=extend_schema(tags=['Utenti']),
    update=extend_schema(tags=['Utenti']),
    partial_update=extend_schema(tags=['Utenti']),
    destroy=extend_schema(tags=['Utenti']),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet per la gestione degli utenti.
    - POST (registrazione): accessibile a tutti
    - GET list, DELETE: solo Admin
    - GET retrieve, PUT, PATCH: utente autenticato (solo il proprio profilo, Admin può vedere tutti).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
            Restituisce i permessi in base all'azione richiesta.
            :return: Lista di permessi
        """
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['list', 'destroy']:
            return [IsAdminUser()]
        else:  # retrieve, update, partial_update
            return [IsAuthenticated()]

    def get_object(self):
        """
            Recupera l'oggetto utente richiesto.
            Un utente non Admin può accedere solo al proprio profilo.
            :return: Istanza di User
            :raises PermissionDenied: se un non-Admin tenta di accedere al profilo di un altro utente
        """
        obj = super().get_object()
        if self.request.user.role != 'ADMIN' and obj != self.request.user:
            raise PermissionDenied()
        return obj
