from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='mario',
            password='mario12345',
            email='mario@test.com',
            role='CUSTOMER'
        )

    def test_login_success(self):
        """
        Verifica che un utente possa effettuare il login con successo e ricevere i token di accesso e refresh.
        """
        response = self.client.post('/api/auth/login/', {
            'username': 'mario',
            'password': 'mario12345'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        """
        Verifica che un utente non possa effettuare il login con una password errata.
        """
        response = self.client.post('/api/auth/login/', {
            'username': 'mario',
            'password': 'sbagliata'
        })
        self.assertEqual(response.status_code, 401)

    def test_login_user_not_exists(self):
        """
        Verifica che un utente non possa effettuare il login se l'utente non esiste.
        """
        response = self.client.post('/api/auth/login/', {
            'username': 'nonexistent',
            'password': 'mario12345'
        })
        self.assertEqual(response.status_code, 401)
