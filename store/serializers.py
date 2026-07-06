from rest_framework import serializers

from store.models import Category, Product, CartItem, Cart, OrderItem, Order


class CategorySerializer(serializers.ModelSerializer):
    """
        Serializer per il modello Category.
        Espone id, name e slug.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    """
        Serializer per il modello Product.
        - category: oggetto Category annidato, restituito in lettura
        - category_id: accetta l'ID della categoria in scrittura (POST/PUT/PATCH)
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category', 'category_id']


class CartItemSerializer(serializers.ModelSerializer):
    """
        Serializer per il modello CartItem.
        - product: oggetto Product annidato, restituito in lettura
        - product_id: accetta l'ID del prodotto in scrittura (POST)
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    """
       Serializer per il modello Cart.
       Espone il carrello con la lista degli articoli annidati (items).
    """
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'items']


class OrderItemSerializer(serializers.ModelSerializer):
    """
        Serializer per il modello OrderItem.
        Espone il prodotto annidato con il prezzo al momento dell'acquisto.
    """
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_at_purchase']


class OrderSerializer(serializers.ModelSerializer):
    """
        Serializer per il modello Order.
        Espone l'ordine con la lista degli item annidati e lo stato corrente.
    """
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'items']
