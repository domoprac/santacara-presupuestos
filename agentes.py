import requests
from bs4 import BeautifulSoup

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos

    def obtener_superficie_catastro(self, cod_municipio, poligono, parcela):
        """Construye la URL y extrae la superficie real de Tracasa."""
        # Construimos la URL dinámica
        url = f"https://catastro.navarra.es/ref_catastral/unidades.aspx?C={cod_municipio}&PO={poligono}&PA={parcela}&lang=es"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            }
            respuesta = requests.get(url, headers=headers, timeout=10)
            if respuesta.status_code != 200:
                return 110.0
            
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            tablas = soup.find_all('table')
            
            for tabla in tablas:
                filas = tabla.find_all('tr')
                for fila in filas:
                    celdas = fila.find_all('td')
                    if len(celdas) >= 2:
                        texto_izq = celdas[0].get_text(strip=True)
                        # Buscamos 'Construida' o 'Total' que es donde suele estar el dato
                        if "Construida" in texto_izq or "Total" in texto_izq:
                            valor_raw = celdas[1].get_text(strip=True)
                            # Limpiamos el número (ej: '143,00' -> 143.0)
                            valor_limpio = valor_raw.replace(',', '.').split()[0]
                            return float(valor_limpio)
            return 110.0
        except Exception:
            return 110.0

    def obtener_precio_referencia(self):
        url_repo = "https://raw.githubusercontent.com/domoprac/vivienda-pueblo-dinamica/main/presupuesto_base.json"
        try:
            respuesta = requests.get(url_repo, timeout=5)
            return respuesta.json().get('coste_m2_rehabilitacion', 1200)
        except:
            return 1200

    def calcular_subvenciones(self, coste_bruto):
        detalles = []
        ahorro_acumulado = 0
        l_act = self.datos.get('letra_actual', 'E')
        l_obj = self.datos.get('letra_objetivo', 'A')
        
        if l_act >= 'E' and l_obj <= 'B':
            porcentaje = 0.70
            razon = "Máximo salto energético detectado"
        else:
            porcentaje = 0.20
            razon = "Mejora estándar"

        ayuda = coste_bruto * porcentaje
        ahorro_acumulado += ayuda
        detalles.append({"nombre": "Ayuda Gobierno Navarra", "monto": ayuda, "razon": razon})

        if self.datos.get('placas'):
            ahorro_acumulado += 3000.0
            detalles.append({"nombre": "Bonus Autoconsumo", "monto": 3000.0, "razon": "Placas solares"})

        return ahorro_acumulado, detalles
