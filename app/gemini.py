import google.generativeai as genai
import os

# Configurar la API key de Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("No se encontró la API key de Gemini. Asegúrate de configurar la variable de entorno GEMINI_API_KEY.")

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel('gemini-2.5-pro')

def generar_feedback_ia(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Ocurrió un error al generar contenido con Gemini: {e}")
        return None