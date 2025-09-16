# test_mongo.py
from pymongo import MongoClient

uri = "mongodb+srv://admin:jW0DwZFZuWsTxXym@alberteinstein.lftfvkl.mongodb.net/plataforma_simulacros?retryWrites=true&w=majority&appName=AlbertEinstein"

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Conexión exitosa")
except Exception as e:
    print(f"❌ Error: {e}")