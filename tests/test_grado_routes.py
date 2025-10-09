import unittest
import json
from app import create_app, db, db_client
from unittest.mock import patch, MagicMock

class GradoRoutesTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def tearDown(self):
        if db_client:
            db_client.close()

    @patch('app.db')
    def test_create_grado(self, mock_db):
        mock_db.grados.insert_one.return_value = MagicMock()
        response = self.client.post('/grados/',
                                    data=json.dumps({
                                        "nombre": "Primer Grado",
                                        "descripcion": "Grado para niños de 6 años"
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Grado creado exitosamente', response.get_data(as_text=True))

    @patch('app.db')
    def test_get_grados(self, mock_db):
        mock_db.grados.find.return_value = [
            {
                "_id": "60c72b2f9b1e8a3f4c8e4b1a",
                "nombre": "Primer Grado",
                "descripcion": "Grado para niños de 6 años",
                "estado": True
            }
        ]
        response = self.client.get('/grados/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Primer Grado', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()