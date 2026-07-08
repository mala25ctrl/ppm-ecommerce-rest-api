from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Product, Category, Cart, Order

User = get_user_model()


class OrderTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer', password='customer12345', role='CUSTOMER'
        )
        self.manager = User.objects.create_user(
            username='manager', password='manager12345', role='MANAGER'
        )
        self.category = Category.objects.create(
            name='Elettronica', slug='elettronica'
        )
        self.product = Product.objects.create(
            name='Laptop',
            description='a high-performance laptop',
            price=600.00,
            stock=10,
            category_id=self.category.id,
        )

    def _get_token(self, username: str, password: str) -> str:
        response = self.client.post('/api/auth/login/', {
            'username': username,
            'password': password
        })
        return response.data['access']

    def _add_product_to_cart(self, token: str, product_id: int, quantity: int = 1):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/cart/add_item/', {
            'product_id': product_id,
            'quantity': quantity
        })
        return response

    def test_checkout_create_order(self):
        """
        Verifica che un cliente possa effettuare il checkout e creare un ordine.
        """
        token = self._get_token('customer', 'customer12345')
        self._add_product_to_cart(token, self.product.id, 2)
        response = self.client.post('/api/orders/checkout/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('items', response.data)
        self.assertEqual(len(response.data['items']), 1)

    def test_checkout_decrease_stock(self):
        """
        Verifica che lo stock del prodotto venga decrementato correttamente dopo il checkout.
        """
        token = self._get_token('customer', 'customer12345')
        self._add_product_to_cart(token, self.product.id, 3)
        self.client.post('/api/orders/checkout/')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)  # Stock iniziale 10 - 3 = 7

    def test_checkout_clear_cart(self):
        """
        Verifica che il carrello si svuoti dopo il checkout.
        """
        token = self._get_token('customer', 'customer12345')
        self._add_product_to_cart(token, self.product.id, 2)
        self.client.post('/api/orders/checkout/')
        cart = Cart.objects.get(user=self.customer)
        self.assertEqual(cart.items.count(), 0)

    def test_checkout_with_empty_cart(self):
        """
        Verifica che il checkout fallisca se il carrello è vuoto.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/orders/checkout/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(response.data['detail'], 'Cart is empty.')

    def test_checkout_insufficient_stock(self):
        """
        Verifica che il checkout fallisca se la quantità richiesta supera lo stock disponibile.
        """
        token = self._get_token('customer', 'customer12345')
        self._add_product_to_cart(token, self.product.id, 15)  # Stock disponibile è 10
        response = self.client.post('/api/orders/checkout/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_own_orders(self):
        """
        Verifica che un cliente possa visualizzare i propri ordini.
        """
        token = self._get_token('customer', 'customer12345')
        self._add_product_to_cart(token, self.product.id, 1)
        self.client.post('/api/orders/checkout/')
        response = self.client.get('/api/orders/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_manager_sees_all_orders(self):
        """
        Verifica che un manager possa visualizzare tutti gli ordini.
        """
        # Creazione di un ordine da parte del cliente
        customer_token = self._get_token('customer', 'customer12345')
        self._add_product_to_cart(customer_token, self.product.id, 1)
        self.client.post('/api/orders/checkout/')

        # Accesso come manager
        manager_token = self._get_token('manager', 'manager12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {manager_token}')
        response = self.client.get('/api/orders/all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # Almeno un ordine dovrebbe essere presente):

    def test_customer_does_not_see_all_orders(self):
        """
        Verifica che un cliente non possa visualizzare tutti gli ordini.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/orders/all/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_updates_order_state(self):
        """
        Verifica che un manager possa aggiornare lo stato di un ordine.
        """
        token = self._get_token('customer', 'customer12345')
        self._add_product_to_cart(token, self.product.id, 1)
        self.client.post('/api/orders/checkout/')
        order = Order.objects.get(user=self.customer)
        manager_token = self._get_token('manager', 'manager12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {manager_token}')
        response = self.client.patch(f'/api/orders/{order.id}/update_status/', {
            'status': 'SHIPPED'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'SHIPPED')

    def test_customer_cannot_update_order_state(self):
        """
        Verifica che un cliente non possa aggiornare lo stato di un ordine.
        """
        token = self._get_token('customer', 'customer12345')
        self._add_product_to_cart(token, self.product.id, 1)
        self.client.post('/api/orders/checkout/')
        order = Order.objects.get(user=self.customer)
        response = self.client.patch(f'/api/orders/{order.id}/update_status/', {
            'status': 'SHIPPED'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_order_status_update(self):
        """
        Verifica che un manager non possa aggiornare lo stato di un ordine con uno stato non valido.
        """
        token = self._get_token('customer', 'customer12345')
        self._add_product_to_cart(token, self.product.id, 1)
        self.client.post('/api/orders/checkout/')
        order = Order.objects.get(user=self.customer)
        manager_token = self._get_token('manager', 'manager12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {manager_token}')
        response = self.client.patch(f'/api/orders/{order.id}/update_status/', {
            'status': 'INVALID'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
