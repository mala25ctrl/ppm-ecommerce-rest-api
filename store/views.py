from drf_spectacular.utils import extend_schema_view, extend_schema, inline_serializer
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from store.models import Category, Product, Cart, CartItem, Order, OrderItem
from store.serializers import CategorySerializer, ProductSerializer, CartSerializer, CartItemSerializer, OrderSerializer
from users.permissions import IsManagerOrAdmin


@extend_schema_view(
    list=extend_schema(tags=['Categories'], summary='Lista categorie',
                       description='Restituisce la lista di tutte le categorie disponibili.'),
    retrieve=extend_schema(tags=['Categories'], summary='Dettaglio categoria',
                           description='Restituisce i dettagli di una singola categoria.'),
    create=extend_schema(tags=['Categories'], summary='Crea categoria — solo Manager/Admin',
                         description='Crea una nuova categoria.'),
    update=extend_schema(tags=['Categories'], summary='Aggiorna categoria — solo Manager/Admin',
                         description='Aggiorna una categoria esistente.'),
    partial_update=extend_schema(tags=['Categories'], summary='Aggiornamento parziale categoria — solo Manager/Admin',
                                 description='Aggiorna parzialmente una categoria esistente.'),
    destroy=extend_schema(tags=['Categories'], summary='Elimina categoria — solo Manager/Admin',
                          description='Elimina una categoria esistente.'),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet per la gestione delle categorie.
    - GET list/retrieve: accessibile a tutti (anche non autenticati)
    - POST/PUT/PATCH/DELETE: solo Manager o Admin
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        """
            Restituisce i permessi in base all'azione richiesta.
            :return: Lista di permessi
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsManagerOrAdmin()]


@extend_schema_view(
    list=extend_schema(tags=['Products'], summary='Lista prodotti',
                       description='Restituisce la lista di tutti i prodotti disponibili.'),
    retrieve=extend_schema(tags=['Products'], summary='Dettaglio prodotto',
                           description='Restituisce i dettagli di un singolo prodotto.'),
    create=extend_schema(tags=['Products'], summary='Crea prodotto — solo Manager/Admin',
                         description='Crea un nuovo prodotto.'),
    update=extend_schema(tags=['Products'], summary='Aggiorna prodotto — solo Manager/Admin',
                         description='Aggiorna un prodotto esistente.'),
    partial_update=extend_schema(tags=['Products'], summary='Aggiornamento parziale prodotto — solo Manager/Admin',
                                 description='Aggiorna parzialmente un prodotto esistente.'),
    destroy=extend_schema(tags=['Products'], summary='Elimina prodotto — solo Manager/Admin',
                          description='Elimina un prodotto esistente.'),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet per la gestione dei prodotti.
    - GET list/retrieve: accessibile a tutti (anche non autenticati)
    - POST/PUT/PATCH/DELETE: solo Manager o Admin
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        """
            Restituisce i permessi in base all'azione richiesta.
            :return: Lista di permessi
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsManagerOrAdmin()]


class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Recupera il carrello dell'utente autenticato, o lo crea se non esiste.
        :return: Istanza di Cart
        """
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @extend_schema(tags=['Cart'], summary='Visualizza il proprio carrello')
    @action(detail=False, methods=['get'])
    def me(self, request):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @extend_schema(tags=['Cart'], summary='Aggiunge un prodotto al carrello', request=CartItemSerializer)
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

    @extend_schema(tags=['Cart'], summary='Rimuovi articolo dal carrello')
    @action(detail=False, methods=['delete'], url_path='remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        cart = self.get_object()
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(tags=['Cart'], summary='Svuota il carrello')
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = self.get_object()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.GenericViewSet):
    """
        ViewSet per la gestione degli ordini.
        - I customer vedono solo i propri ordini.
        - Admin e Manager vedono tutti gli ordini e possono aggiornarne lo stato.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Restituisce gli ordini visibili all'utente autenticato.
        Admin e Manager vedono tutti gli ordini, i customer solo i propri
        :return: Queryset di Order
        """
        user = self.request.user
        if user.role in ('ADMIN', 'MANAGER'):
            return Order.objects.all()
        return Order.objects.filter(user=user)

    @extend_schema(tags=['Orders'], summary='Visualizza i propri ordini')
    @action(detail=False, methods=['get'])
    def me(self, request):
        orders = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Orders'], summary='Visualizza tutti gli ordini - solo Manager/Admin')
    @action(detail=False, methods=['get'])
    def all(self, request):
        if request.user.role not in ('ADMIN', 'MANAGER'):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        orders = Order.objects.all()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Orders'], summary='Checkout - crea un ordine dal carrello')
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        items = cart.items.select_related('product').all()

        if not items.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica disponibilità stock prima di creare l'ordine
        for item in items:
            if item.product.stock < item.quantity:
                return Response({'detail': f'Insufficient stock for {item.product.name}.'},
                                status=status.HTTP_400_BAD_REQUEST)

        # Crea ordine
        order = Order.objects.create(user=request.user)
        for item in items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity,
                                     price_at_purchase=item.product.price)
            item.product.stock -= item.quantity
            item.product.save()

        # Svuota il carrello dopo il checkout
        cart.items.all().delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=['Orders'], summary='Aggiorna lo stato di un ordine - solo Manager/Admin',
                   request=inline_serializer(
                       name='UpdateStatusSerializer',
                       fields={'status': serializers.ChoiceField(choices=Order.Status.choices)}
                   ))
    @action(detail=True, methods=['patch'], url_path='update_status')
    def update_status(self, request, pk=None):
        if request.user.role not in ('ADMIN', 'MANAGER'):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in Order.Status.values:
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
