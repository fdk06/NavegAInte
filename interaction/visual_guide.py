from urllib.parse import urlparse  # Añadir esta línea
from playwright.sync_api import sync_playwright

def highlight_element(url, xpath):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            
            # Resaltar elemento
            element = page.locator(xpath)
            element.evaluate("e => e.style.border = '3px solid red'")
            
            # Tomar captura
            page.screenshot(path=f"data/processed/{urlparse(url).hostname}_element.png")
            print(f"📸 Captura guardada en data/processed/{urlparse(url).hostname}_element.png")
            
            browser.close()
    except Exception as e:
        print(f"❌ Error: {str(e)}")