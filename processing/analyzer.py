import json
import os
from langchain_ollama import OllamaLLM  # Nombre actualizado
from urllib.parse import urlparse

class ContentAnalyzer:
    def __init__(self, output_dir="data/processed"):
        self.llm = OllamaLLM(
            model="mistral:7b-instruct-v0.3-q5_K_M",
            base_url="http://localhost:11434",
            verbose=False,  # Cambiado a False
            temperature=0.3  # Reduce la creatividad para respuestas más precisas
        )
        self.output_dir = output_dir
    
    def chunk_text(self, text, chunk_size=512):
        words = text.split()
        return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    
    def analyze(self, file_path):
        try:
            # Validar archivo
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
            if os.path.getsize(file_path) == 0:
                raise ValueError("El archivo JSON está vacío")

            # Cargar datos
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"✅ JSON válido: {os.path.basename(file_path)}")

            # Generar prompt estructurado
            prompt = f"""
            **Instrucciones para Analizar {data.get('url')}**:
            1. **Propósito**: Describe en 2 líneas el objetivo principal del sitio.
            2. **Elementos Clave**: Lista hasta 3 elementos con:
               - Texto exacto.
               - XPath válido (usar los del JSON).
               - Tipo (encabezado, enlace, botón).
            3. **Ejemplo de Respuesta**:
               {{
                 "propósito": "Este sitio es un dominio de ejemplo...",
                 "elementos": [
                   {{
                     "texto": "Example Domain",
                     "xpath": "//h1",
                     "tipo": "encabezado"
                   }},
                   {{
                     "texto": "More information...",
                     "xpath": "//a[@href='https://www.iana.org/domains/example']",
                     "tipo": "enlace_externo"
                   }}
                 ]
               }}
            
            **Datos Scrapeados**:
            - Título: {data.get('title', 'N/A')}
            - Encabezados: {data.get('headers', {})}
            - Enlaces Externos: {data.get('links', {}).get('external', [])}
            """
            
            response = self.llm.invoke(prompt)

            # Guardar resultado procesado
            hostname = urlparse(data['url']).hostname
            os.makedirs(f"{self.output_dir}/{hostname}", exist_ok=True)
            output_path = f"{self.output_dir}/{hostname}/{os.path.basename(file_path)}"
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({"analysis": response}, f, indent=2)
            
            return output_path  # Ruta del archivo procesado

        except Exception as e:
            print(f"❌ Error crítico: {str(e)}")
            raise