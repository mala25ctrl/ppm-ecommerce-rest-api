from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Category

User = get_user_model()


class CategoryTest(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(username='customer', password='customer12345', role='CUSTOMER')
        self.manager = User.objects.create_user(username='manager', password='manager12345', role='MANAGER')
        self.category = Category.objects.create(name='Elettronica', slug='elettronica')

    def _get_token(self, username, password):
        response = self.client.post('/api/auth/login/', {
            'username': username,
            'password': password
        })
        return response.data['access']

    def test_list_categories_without_token(self):
        """
        Verifica che la lista delle categorie sia accessibile senza autenticazione.
        """
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category_as_manager(self):
        """
        Verifica che un manager possa creare una nuova categoria.
        """
        token = self._get_token('manager', 'manager12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/categories/', {
            'name': 'Abbigliamento',
            'slug': 'abbigliamento'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Abbigliamento')

    def test_create_category_as_customer(self):
        """
        Verifica che un cliente non possa creare una nuova categoria.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post('/api/categories/', {
            'name': 'Abbigliamento',
            'slug': 'abbigliamento'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_as_manager(self):
        """
        Verifica che un manager possa eliminare una categoria esistente.
        """
        token = self._get_token('manager', 'manager12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(f'/api/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_category_as_customer(self):
        """
        Verifica che un cliente non possa eliminare una categoria esistente.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(f'/api/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
