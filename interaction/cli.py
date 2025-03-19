import json
import os  # Importar el módulo os
from processing.analyzer import ContentAnalyzer
from interaction.visual_guide import highlight_element
from urllib.parse import urlparse

def start_interaction(processed_file, original_url):
    if not os.path.exists(processed_file):
        print("❌ No hay datos procesados. Ejecuta scraping primero.")
        return
    
    analyzer = ContentAnalyzer()
    
    try:
        print(f"\n📂 Cargando: {processed_file}")
        with open(processed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            context = data.get("analysis", "Sin análisis")
    except FileNotFoundError:
        print("❌ No hay datos procesados. Ejecute scraping primero.")
        return
    except Exception as e:
        print(f"❌ Error en interacción: {str(e)}")
        return
    
    while True:
        question = input("\n🔍 Haz tu pregunta (o 'salir'): ")
        if question.lower() == 'salir':
            break
        
        prompt = f"""
        Contexto: {context}
        Instrucciones:
        - Responde en español de manera clara.
        - Si es una acción (ej: clic), incluye el XPath.
        - Si no hay datos, sugiere alternativas.
        
        Pregunta: {question}
        """
        
        response = analyzer.llm.invoke(prompt)
        print(f"\n🤖 {response}")
        
        # Manejar elementos accionables
        if "XPath:" in response:
            xpath = response.split("XPath: ")[-1].strip()
            highlight_element(original_url, xpath)