import os
import logging
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from scraper.spider import WebSpider
from processing.analyzer import ContentAnalyzer
from interaction.cli import start_interaction

def configurar_logs(verbose=False):
    """Configura los niveles de logging"""
    nivel = logging.DEBUG if verbose else logging.ERROR
    logging.basicConfig(level=nivel)
    logging.getLogger('scrapy').setLevel(nivel)
    logging.getLogger('httpx').setLevel(nivel)
    logging.getLogger('httpcore').setLevel(nivel)

def main():
    # Configuración inicial
    verbose = input("¿Mostrar logs detallados? (s/n): ").lower() == 's'
    configurar_logs(verbose)

    url = input("🌐 Ingresa la URL a analizar: ")
    hostname = urlparse(url).hostname
    raw_dir = os.path.abspath(f"data/raw/{hostname}/pages")
    processed_dir = os.path.abspath(f"data/processed/{hostname}")

    # Crear directorios
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    # Manejo de scraping
    existing_files = [f for f in os.listdir(raw_dir) if f.endswith(".json")]
    
    # Determinar si debemos hacer scraping
    ejecutar_scraping = False
    
    if existing_files:
        print(f"📂 Se encontraron {len(existing_files)} archivos scrapeados.")
        rescrapear = input("¿Deseas re-scrapear? (s/n): ").lower() == 's'
        if rescrapear:
            ejecutar_scraping = True
    else:
        print("📂 No se encontraron archivos scrapeados. Se iniciará el scraping automáticamente.")
        ejecutar_scraping = True
    
    # Ejecutar el scraping si es necesario
    if ejecutar_scraping:
        print("\n🕷️ Iniciando scraping...")
        process = CrawlerProcess(settings={'LOG_LEVEL': 'ERROR' if not verbose else 'DEBUG'})
        process.crawl(WebSpider, url=url)
        process.start()
        # Actualizar la lista de archivos existentes después del scraping
        existing_files = [f for f in os.listdir(raw_dir) if f.endswith(".json")]

    # Opción de procesamiento
    procesar = True
    if existing_files and not ejecutar_scraping:
        procesar = input("¿Deseas procesar los datos existentes? (s/n): ").lower() == 's'

    # Procesamiento de datos
    processed_files = []
    if procesar and existing_files:  # Asegurarse de que haya archivos para procesar
        analyzer = ContentAnalyzer()
        for file in existing_files:
            full_path = os.path.join(raw_dir, file)
            try:
                processed_file = analyzer.analyze(full_path)
                processed_files.append(processed_file)
                print(f"✅ Procesado: {processed_file}")
            except Exception as e:
                print(f"❌ Error procesando {file}: {str(e)}")

    # Interacción
    if processed_files:
        start_interaction(processed_files[0], url)
    else:
        print("\n⚠️ No hay datos disponibles para interactuar")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Ejecución interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {str(e)}")