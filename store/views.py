from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from store.models import Category
from store.serializers import CategorySerializer
from users.permissions import IsManagerOrAdmin


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsManagerOrAdmin()]
