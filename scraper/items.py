import scrapy

class WebItem(scrapy.Item):
    # Campos básicos para almacenar datos extraídos
    url = scrapy.Field()          # URL de la página
    title = scrapy.Field()        # Título de la página
    text = scrapy.Field()         # Texto principal (body)
    buttons = scrapy.Field()      # Texto de los botones
    links = scrapy.Field()        # Enlaces (internos y externos)
    xpaths = scrapy.Field()       # XPaths de elementos clave
    headers = scrapy.Field()      # Encabezados (h1, h2, h3)
    forms = scrapy.Field()        # Formularios