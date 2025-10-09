import unittest
import json
from app import create_app, db, db_client
from unittest.mock import patch, MagicMock

class SeccionRoutesTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def tearDown(self):
        if db_client:
            db_client.close()

    @patch('app.db')
    def test_create_seccion(self, mock_db):
        mock_db.secciones.insert_one.return_value = MagicMock()
        response = self.client.post('/secciones/',
                                    data=json.dumps({
                                        "nombre": "Sección A",
                                        "grado_id": "60c72b2f9b1e8a3f4c8e4b1a"
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Sección creada exitosamente', response.get_data(as_text=True))

    @patch('app.db')
    def test_get_secciones(self, mock_db):
        mock_db.secciones.find.return_value = [
            {
                "_id": "60c72b2f9b1e8a3f4c8e4b1b",
                "nombre": "Sección A",
                "grado_id": "60c72b2f9b1e8a3f4c8e4b1a",
                "estado": True
            }
        ]
        response = self.client.get('/secciones/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Sección A', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()