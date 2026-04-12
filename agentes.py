import requests
from bs4 import BeautifulSoup

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos

    def obtener_superficie_catastro(self, url_catastro):
        """Intenta extraer la superficie real del portal de Catastro de Navarra."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            respuesta = requests.get(url_catastro, headers=headers, timeout=10)
            if respuesta.status_code != 200:
                return 110.0
            
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            tablas = soup.find_all('table')
            
            for tabla in tablas:
                filas = tabla.find_all('tr')
                for fila in filas:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 2:
                        texto_celda = celdas[0].get_text(strip=True)
                        if "Construida" in texto_celda or "Total" in texto_celda:
                            valor_raw = celdas[1].get_text(strip=True)
                            # Limpieza de número: '143,00 m2' -> 143.0
                            valor_limpio = valor_raw.replace(',', '.').split()[0]
                            return float(valor_limpio)
            return 110.0
        except Exception:
            return 110.0

    def obtener_precio_referencia(self):
        """Consulta el coste por m2 en el repositorio de Domoprac."""
        url_repo = "https://raw.githubusercontent.com/domoprac/vivienda-pueblo-dinamica/main/presupuesto_base.json"
        try:
            respuesta = requests.get(url_repo, timeout=5)
            if respuesta.status_code == 200:
                return respuesta.json().get('coste_m2_rehabilitacion', 1200)
            return 1200
        except:
            return 1200

    def calcular_subvenciones(self, coste_bruto):
        """Calcula ayudas basadas en el salto térmico y equipos instalados."""
        detalles = []
        ahorro_acumulado = 0
        
        # Lógica de salto de letra (PREE 5000 / Navarra)
        letra_ini = self.datos.get('letra_actual', 'E')
        letra_fin = self.datos.get('letra_objetivo', 'A')
        
        if letra_ini >= 'E' and letra_fin <= 'B':
            porcentaje = 0.70
            razon = f"Salto de eficiencia máximo ({letra_ini} -> {letra_fin})"
        else:
            porcentaje = 0.20
            razon = "Mejora energética básica"

        ayuda_pree = coste_bruto * porcentaje
        ahorro_acumulado += ayuda_pree
        detalles.append({"nombre": "Ayuda Rehabilitación (Navarra)", "monto": ayuda_pree, "razon": razon})

        # Ayuda por placas solares
        if self.datos.get('placas'):
            ayuda_solar = 3000.0
            ahorro_acumulado += ayuda_solar
            detalles.append({"nombre": "Fomento Autoconsumo", "monto": ayuda_solar, "razon": "Instalación fotovoltaica"})

        return ahorro_acumulado, detalles
