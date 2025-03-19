import subprocess
import sys

def install_browsers():
    print("🚀 Instalando navegadores...")
    try:
        # Ejecuta el comando usando el módulo de Python
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ Chromium instalado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error de instalación: {str(e)}")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    install_browsers()