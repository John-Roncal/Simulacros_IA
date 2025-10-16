import google.generativeai as genai
import os

# Configurar la API key de Gemini
# Se recomienda usar variables de entorno para la API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("No se encontró la API key de Gemini. Asegúrate de configurar la variable de entorno GEMINI_API_KEY.")

genai.configure(api_key=gemini_api_key)

# Crear el modelo generativo
model = genai.GenerativeModel('gemini-1.5-pro-latest')

def generar_feedback_ia(prompt):
    """
    Genera feedback usando el modelo de Gemini.

    Args:
        prompt (str): El prompt para enviar al modelo de IA.

    Returns:
        str: El texto generado por el modelo de IA.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Ocurrió un error al generar contenido con Gemini: {e}")
        return None