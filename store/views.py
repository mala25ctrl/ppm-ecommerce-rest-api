from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from store.models import Category, Product, Cart, CartItem, Order, OrderItem
from store.serializers import CategorySerializer, ProductSerializer, CartSerializer, CartItemSerializer, OrderSerializer
from users.permissions import IsManagerOrAdmin


@extend_schema_view(
    list=extend_schema(tags=['Categorie']),
    retrieve=extend_schema(tags=['Categorie']),
    create=extend_schema(tags=['Categorie']),
    update=extend_schema(tags=['Categorie']),
    partial_update=extend_schema(tags=['Categorie']),
    destroy=extend_schema(tags=['Categorie']),
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
    list=extend_schema(tags=['Prodotti']),
    retrieve=extend_schema(tags=['Prodotti']),
    create=extend_schema(tags=['Prodotti']),
    update=extend_schema(tags=['Prodotti']),
    partial_update=extend_schema(tags=['Prodotti']),
    destroy=extend_schema(tags=['Prodotti']),
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
    """
    ViewSet per la gestione del carrello dell'utente autenticato.
    Ogni utente ha un solo carrello, creato automaticamente al primo accesso.
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Recupera il carrello dell'utente autenticato, o lo crea se non esiste.
        :return: Istanza di Cart
        """
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @extend_schema(tags=['Cart'])
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Restituisce il carrello dell'utente autenticato con tutti gli articoli presenti.
        :param request: Richiesta HTTP
        :return: Dati del carrello serializzati
        """
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @extend_schema(tags=['Cart'])
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Aggiunge un prodotto al carrello.
        Se il prodotto è già presente, incrementa la quantità.
        :param request: Richiesta HTTP con product_id e quantity
        :return: Dati dell'articolo aggiornato
        """
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

    @extend_schema(tags=['Cart'])
    @action(detail=False, methods=['delete'], url_path='remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """
        Rimuove un singolo articolo dal carrello tramite il suo ID.
        :param request: Richiesta HTTP
        :param item_id: Id dell'articolo da rimuovere
        :return: 204 No Content se eliminato, 404 se non trovato.
        """
        cart = self.get_object()
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(tags=['Cart'])
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """
        Svuota completamente il carrello dell'utente autenticato, rimuovendo tutti gli articoli presenti.
        :param request: Richiesta HTTP
        :return: 204 No Content
        """
        cart = self.get_object()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(tags=['Ordini']),
    retrieve=extend_schema(tags=['Ordini']),
    create=extend_schema(tags=['Ordini']),
    update=extend_schema(tags=['Ordini']),
    partial_update=extend_schema(tags=['Ordini']),
    destroy=extend_schema(tags=['Ordini']),
)
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

    @extend_schema(tags=['Orders'])
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Restituisce gli ordini dell'utente autenticato.
        :param request: Richiesta HTTP
        :return: Lista di ordini serializzati
        """
        orders = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Orders'])
    @action(detail=False, methods=['get'])
    def all(self, request):
        """
        Restituisce tutti gli ordini presenti nel sistema.
        Accessibile solo ad Admin e Manager.
        :param request: Richiesta HTTP
        :return: Lista di tutti gli ordini serializzati, 403 se non autorizzato.
        """
        if request.user.role not in ('ADMIN', 'MANAGER'):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        orders = Order.objects.all()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Orders'])
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Crea un ordine a partire dal carrello dell'utente autenticato.
        - Verifica la disponibilità dello stock per ogni prodotto.
        - Crea l'ordine e i relativi OrderItem con il prezzo al momento dell'acquisto
        - Scala lo stock dei prodotti acquistati
        - Svuota il carrello al termine
        :param request: Richiesta HTTP
        :return: Dati dell'ordine creato, 400 se carrello vuoto o stock insufficiente.
        """
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

    @extend_schema(tags=['Orders'])
    @action(detail=True, methods=['patch'], url_path='update_status')
    def update_status(self, request, pk=None):
        """
        Aggiorna lo stato di un ordine specifico.
        Accessibile solo ad Admin e Manager.
        :param request: Richiesta HTTP con il campo status
        :param pk: ID dell'ordine da aggiornare
        :return: Dati dell'ordine aggiornato, 403 se non autorizzato, 404 se non trovato, 400 se stato non valido.
        """
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
