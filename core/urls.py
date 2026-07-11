from django.contrib import admin
from django.urls import path, include
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from store.views import CategoryViewSet, ProductViewSet, CartViewSet, OrderViewSet
from users.views import UserViewSet

TokenObtainPairView = extend_schema(
    tags=['Auth'],
    summary='Login — ottieni token JWT',
    description='Effettua il login con username e password e restituisce access e refresh token.'
)(TokenObtainPairView)

TokenRefreshView = extend_schema(
    tags=['Auth'],
    summary='Refresh token JWT',
    description='Genera un nuovo access token a partire dal refresh token.'
)(TokenRefreshView)
router: DefaultRouter = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'message': 'Welcome to the E-Commerce REST API',
        'docs': request.build_absolute_uri('/api/schema/swagger-ui/'),
        'endpoints': {
            'auth': request.build_absolute_uri('/api/auth/login/'),
            'users': request.build_absolute_uri('/api/users/'),
            'categories': request.build_absolute_uri('/api/categories/'),
            'products': request.build_absolute_uri('/api/products/'),
            'cart': request.build_absolute_uri('/api/cart/me/'),
            'orders': request.build_absolute_uri('/api/orders/me/'),
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/session/', include('rest_framework.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
