from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class UserRegistrationTests(APITestCase):

    def test_registrazione_success(self):
        """
        Verifica che la registrazione di un nuovo cliente avvenga con successo e che il ruolo predefinito sia 'CUSTOMER'.
        """
        response = self.client.post("/api/users/",
                                    data={"username": "mrossi", "email": "m.rossi@gami.com", "password": "qwerty"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['role'], 'CUSTOMER')
        self.assertNotIn('password', response.data)

    def test_registrazione_username_duplicato(self):
        """
        Verifica che la registrazione di un nuovo cliente fallisca se lo username è già presente nel database.
        :return:
        """
        User.objects.create_user(username='mario', password='mario12345')
        response = self.client.post('/api/users/', {
            'username': 'mario',
            'password': 'mario12345',
            'email': 'mario2@test.com'
        })
        self.assertEqual(response.status_code, 400)


class UserPermissionsTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer', password='customer12345', role='CUSTOMER'
        )
        self.admin = User.objects.create_user(
            username='admin', password='admin12345', role='ADMIN'
        )

    def _get_token(self, username, password):
        response = self.client.post('/api/auth/login/', {
            'username': username,
            'password': password
        })
        return response.data['access']

    def test_customer_non_vede_lista_utenti(self):
        """
        Verifica che un utente con ruolo 'CUSTOMER' non possa accedere alla lista degli utenti.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 403)

    def test_admin_vede_lista_utenti(self):
        """
        Verifica che un utente con ruolo 'ADMIN' possa accedere alla lista degli utenti.
        """
        token = self._get_token('admin', 'admin12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200)

    def test_customer_non_vede_profilo_altrui(self):
        """
        Verifica che un utente con ruolo 'CUSTOMER' non possa accedere al profilo di un altro utente.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(f'/api/users/{self.admin.id}/')
        self.assertEqual(response.status_code, 403)

    def test_customer_vede_proprio_profilo(self):
        """
        Verifica che un utente con ruolo 'CUSTOMER' possa accedere al proprio profilo.
        """
        token = self._get_token('customer', 'customer12345')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(f'/api/users/{self.customer.id}/')
        self.assertEqual(response.status_code, 200)
