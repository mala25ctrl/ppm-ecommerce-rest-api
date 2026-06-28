from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.permissions import IsAdminUser
from users.serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['list', 'destroy']:
            return [IsAdminUser()]
        else:  # retrieve, update, partial_update
            return [IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        if self.request.user.role != 'ADMIN' and obj != self.request.user:
            raise PermissionDenied()
        return obj
