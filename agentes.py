import requests
from bs4 import BeautifulSoup

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos

    def obtener_superficie_catastro(self, url_catastro):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            }
            respuesta = requests.get(url_catastro, headers=headers, timeout=10)
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            tablas = soup.find_all('table')
            for tabla in tablas:
                if "Superficie" in tabla.text:
                    filas = tabla.find_all('tr')
                    for fila in filas:
                        celdas = fila.find_all('td')
                        if len(celdas) >= 2 and "Construida" in celdas[0].text:
                            valor_texto = celdas[1].text.replace(',', '.').strip()
                            valor_num = valor_texto.split()[0]
                            return float(valor_num)
            return 110.0
        except:
            return 110.0

    def obtener_precio_referencia(self):
        url_repo = "https://raw.githubusercontent.com/domoprac/vivienda-pueblo-dinamica/main/presupuesto_base.json"
        try:
            respuesta = requests.get(url_repo, timeout=5)
            datos_repo = respuesta.json()
            return datos_repo['coste_m2_rehabilitacion']
        except:
            return 1200

    def calcular_subvenciones(self, coste_bruto):
        detalles = []
        ahorro_acumulado = 0
        
        # Lógica PREE 5000
        if self.datos.get('letra_actual', 'E') >= 'E' and self.datos.get('letra_objetivo', 'A') <= 'B':
            porcentaje_ayuda = 0.70
            razon = f"Salto energético alto ({self.datos.get('letra_actual')} -> {self.datos.get('letra_objetivo')})"
        else:
            porcentaje_ayuda = 0.20
            razon = "Reforma energética estándar"

        monto_pree = coste_bruto * porcentaje_ayuda
        ahorro_acumulado += monto_pree
        detalles.append({"nombre": "Ayudas Rehabilitación Navarra", "monto": monto_pree, "razon": razon})

        # Ayuda Solar
        if self.datos.get('placas'):
            monto_solar = 3000.0
            ahorro_acumulado += monto_solar
            detalles.append({"nombre": "Deducción Autoconsumo", "monto": monto_solar, "razon": "Instalación fotovoltaica"})

        return ahorro_acumulado, detalles
