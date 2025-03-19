import scrapy
import json
from urllib.parse import urlparse
import hashlib
import os

class WebSpider(scrapy.Spider):
    name = "web_agent"
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 8,  # Más hilos para sitios grandes
        'DOWNLOAD_DELAY': 1,       # Evitar bloqueos
        'RETRY_TIMES': 2,          # Reintentar peticiones fallidas
        'HTTPERROR_ALLOW_ALL': True # No detenerse por errores HTTP
    }

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url]
        self.base_domain = urlparse(url).hostname
        self.allowed_domains = [self.base_domain]
        self.base_path = f"data/raw/{self.base_domain}"

    def parse(self, response):
        try:
            # Crear estructura de carpetas
            os.makedirs(f"{self.base_path}/pages", exist_ok=True)
            os.makedirs(f"{self.base_path}/assets/images", exist_ok=True)
            os.makedirs(f"{self.base_path}/assets/scripts", exist_ok=True)
            
            # Guardar datos principales
            data = self.extract_data(response)
            self.save_page(response.url, data)
            
            # Guardar assets
            self.save_assets(response)

        except Exception as e:
            self.logger.error(f"Error en {response.url}: {str(e)}")

        yield from self.follow_links(response)

        self.logger.info(f"Scraping completado para {response.url}")
        print(f"\n✅ ¡Listo! Se han scrapeado {self.crawler.stats.get_value('downloader/response_count')} páginas.")

    def extract_data(self, response):
        return {
            "url": response.url,
            "title": response.css("title::text").get(),
            "headers": {
                "h1": response.css("h1::text").getall(),
                "h2": response.css("h2::text").getall(),
                "h3": response.css("h3::text").getall()
            },
            "text": self.clean_text(response.css("body *::text").getall()),  # ¡Selector mejorado!
            "buttons": response.xpath("//button//text()").getall(),
            "forms": response.xpath("//form").getall(),
            "links": self.extract_links(response),
            "metadata": {
                "images": response.css("img::attr(src)").getall(),
                "scripts": response.css("script::attr(src)").getall()
            }
        }

    def clean_text(self, text_list):
        return [text.strip() for text in text_list if text.strip() and len(text.strip()) > 1]

    def extract_links(self, response):
        all_links = response.xpath("//a/@href").getall()
        return {
            "internal": [link for link in all_links if self.is_internal(link)],
            "external": [link for link in all_links if not self.is_internal(link)]
        }

    def is_internal(self, link):
        return self.base_domain in link or link.startswith(('/','#','?'))

    def follow_links(self, response):
        for link in response.xpath("//a/@href").getall():
            if self.is_internal(link):
                yield response.follow(link, callback=self.parse)

    def save_page(self, url, data):
        url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
        filename = f"{self.base_path}/pages/{url_hash}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Página guardada: {filename}")

    def save_assets(self, response):
        # Guardar imágenes
        for img in response.css("img::attr(src)").getall():
            if img.startswith(('http', '/')):
                yield response.follow(img, callback=self.save_image)

        # Guardar scripts
        for script in response.css("script::attr(src)").getall():
            if script.startswith(('http', '/')):
                yield response.follow(script, callback=self.save_script)

    def save_image(self, response):
        filename = os.path.basename(urlparse(response.url).path)
        with open(f"{self.base_path}/assets/images/{filename}", "wb") as f:
            f.write(response.body)

    def save_script(self, response):
        filename = os.path.basename(urlparse(response.url).path)
        with open(f"{self.base_path}/assets/scripts/{filename}", "wb") as f:
            f.write(response.body)