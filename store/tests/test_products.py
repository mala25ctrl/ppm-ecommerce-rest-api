from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Category, Product

User = get_user_model()


class ProductTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer', password='customer12345', role='CUSTOMER'
        )
        self.manager = User.objects.create_user(
            username='manager', password='manager12345', role='MANAGER'
        )
        self.category = Category.objects.create(name='Elettronica', slug='elettronica')
        self.product = Product.objects.create(
            name='Laptop',
            description='a high-performance laptop',
            price=999.99,
            stock=10,
            category=self.category,
        )

    def _get_token(self, username, password):
        response = self.client.post('/api/auth/login/', {
            'username': username,
            'password': password
        })
        return response.data['access']

    def test_list_products_without_token(self):
        """
        Verifica che la lista dei prodotti sia accessibile senza autenticazione.
        """
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_products_without_token(self):
        """
        Verifica che il dettaglio di un prodotto sia accessibile senza autenticazione.
        """
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptop')

    def test_create_products_as_manager(self):
        """
        Verifica che un manager possa creare un nuovo prodotto.
        """
        token = self._get_token('manager', 'manager12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/products/', {
            'name': 'Smartphone',
            'description': 'a new smartphone',
            'price': 499.99,
            'stock': 20,
            'category_id': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Smartphone')

    def test_create_products_as_customer_forbidden(self):
        """
        Verifica che un cliente non possa creare un nuovo prodotto.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/products/', {
            'name': 'Smartphone',
            'description': 'a new smartphone',
            'price': 499.99,
            'stock': 20,
            'category_id': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_without_token_unauthorized(self):
        """
        Verifica che l'endpoint per creare un prodotto non sia accessibile senza autenticazione.
        """
        response = self.client.post('/api/products/', {
            'name': 'Smartphone',
            'description': 'a new smartphone',
            'price': 499.99,
            'stock': 20,
            'category_id': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_product_as_manager(self):
        """
        Verifica che un manager possa aggiornare un prodotto esistente.
        """
        token = self._get_token('manager', 'manager12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(f'/api/products/{self.product.id}/', {
            'price': 899.99,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], '899.99')

    def remove_product_as_manager(self):
        """
        Verifica che un manager possa eliminare un prodotto esistente.
        """
        token = self._get_token('manager', 'manager12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def remove_product_as_customer_forbidden(self):
        """
        Verifica che un cliente non possa eliminare un prodotto esistente.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_contains_category_nested(self):
        """
        Verifica che il dettaglio di un prodotto contenga le informazioni della categoria annidata.
        """
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('category', response.data)
        self.assertEqual(response.data['category']['name'], 'Elettronica')