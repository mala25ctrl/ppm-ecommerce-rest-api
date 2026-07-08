from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from store.models import Product, Category, Cart, CartItem

User = get_user_model()


class CartTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer', password='customer12345', role='CUSTOMER'
        )
        self.category = Category.objects.create(name='Elettronica', slug='elettronica')
        self.product = Product.objects.create(
            name='Laptop',
            description='a high-performance laptop',
            price=350.50,
            stock=10,
            category=self.category
        )

    def _get_token(self, username: str, password: str) -> str:
        response = self.client.post('/api/auth/login/', {
            'username': username,
            'password': password
        })
        return response.data['access']

    def test_view_cart(self):
        """
        Verifica che il cliente possa visualizzare il carrello e che la risposta contenga la chiave 'items'.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/cart/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)

    def test_automated_created_cart(self):
        """
        Verifica che un carrello venga creato automaticamente per un cliente quando accede alla vista del carrello.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/cart/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)

    def test_add_product_to_cart(self):
        """
        Verifica che un cliente possa aggiungere un prodotto al carrello.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/cart/add_item/', {
            'product_id': self.product.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 2)

    def test_add_same_product_increase_quantity(self):
        """
        Verifica che aggiungere lo stesso prodotto al carrello aumenti la quantità invece di creare una nuova voce.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.client.post('/api/cart/add_item/', {
            'product_id': self.product.id,
            'quantity': 2
        })
        self.client.post('/api/cart/add_item/', {
            'product_id': self.product.id,
            'quantity': 3
        })
        cart = Cart.objects.get(user=self.customer)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 5)

    def test_remove_product_from_cart(self):
        """
        Verifica che un cliente possa rimuovere un prodotto dal carrello.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.client.post('/api/cart/add_item/', {
            'product_id': self.product.id,
            'quantity': 2
        })
        cart = Cart.objects.get(user=self.customer)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        response = self.client.delete(f'/api/cart/remove_item/{cart_item.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

    def test_remove_product_from_cart_not_existing(self):
        """
        Verifica che la rimozione di un prodotto non esistente nel carrello restituisca un errore 404.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete('/api/cart/remove_item/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_clear_cart(self):
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.client.post('/api/cart/add_item/', {
            'product_id': self.product.id,
            'quantity': 2
        })
        response = self.client.delete('/api/cart/clear/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cart = Cart.objects.get(user=self.customer)
        self.assertEqual(cart.items.count(), 0)

    def test_view_cart_unauthenticated(self):
        """
        Verifica che un utente non autenticato non possa visualizzare il carrello.
        """
        response = self.client.get('/api/cart/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

