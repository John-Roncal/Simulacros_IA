import unittest
import json
import bcrypt
from app import create_app
from app.models.usuario import Usuario
from unittest.mock import patch

class AuthRoutesTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'

    @patch('app.models.usuario.Usuario.find_by_email')
    def test_login_success(self, mock_find_by_email):
        # Setup: Create a mock user object
        hashed_password = bcrypt.hashpw(b'password123', bcrypt.gensalt())
        mock_user = Usuario(
            usuario_id=1,
            nombre="Test",
            apellido="User",
            correo='test@example.com',
            contraseña_hash=hashed_password,
            rol='Alumno'
        )
        mock_find_by_email.return_value = mock_user

        # Action: Send a POST request to the login endpoint
        response = self.client.post('/usuarios/login',
                                    data=json.dumps({
                                        'correo': 'test@example.com',
                                        'contraseña': 'password123'
                                    }),
                                    content_type='application/json')

        # Assert: Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('token', data)
        self.assertEqual(data['rol'], 'Alumno')

    @patch('app.models.usuario.Usuario.find_by_email')
    def test_login_failure_wrong_password(self, mock_find_by_email):
        # Setup: Create a mock user object
        hashed_password = bcrypt.hashpw(b'password123', bcrypt.gensalt())
        mock_user = Usuario(
            usuario_id=1,
            nombre="Test",
            apellido="User",
            correo='test@example.com',
            contraseña_hash=hashed_password,
            rol='Alumno'
        )
        mock_find_by_email.return_value = mock_user

        # Action: Send a POST request with the wrong password
        response = self.client.post('/usuarios/login',
                                    data=json.dumps({
                                        'correo': 'test@example.com',
                                        'contraseña': 'wrongpassword'
                                    }),
                                    content_type='application/json')

        # Assert: Check the response
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Credenciales inválidas')

    @patch('app.models.usuario.Usuario.find_by_email')
    def test_login_failure_user_not_found(self, mock_find_by_email):
        # Setup: Mock the find_by_email method to return None
        mock_find_by_email.return_value = None

        # Action: Send a POST request for a non-existent user
        response = self.client.post('/usuarios/login',
                                    data=json.dumps({
                                        'correo': 'nonexistent@example.com',
                                        'contraseña': 'password123'
                                    }),
                                    content_type='application/json')

        # Assert: Check the response
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Credenciales inválidas')

if __name__ == '__main__':
    unittest.main()