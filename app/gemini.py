import google.generativeai as genai

genai.configure(api_key="AIzaSyBN02rlJYYfnYw88_zm60OJca5wu1oagqY")

model = genai.GenerativeModel('gemini-2.5-pro')

try:
    response = model.generate_content("¿Qué es un agujero negro?")
    print(response.text)
except Exception as e:
    print(f"Ocurrió un error: {e}")