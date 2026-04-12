import requests
from bs4 import BeautifulSoup # Necesitaremos añadir esta librería

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos

    def obtener_superficie_catastro(self, url_catastro):
        """Busca la superficie real en el portal de Catastro de Navarra"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            respuesta = requests.get(url_catastro, headers=headers, timeout=10)
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            
            # Buscamos en las tablas de la web de Tracasa
            tablas = soup.find_all('table')
            for tabla in tablas:
                if "Superficie" in tabla.text:
                    filas = tabla.find_all('tr')
                    for fila in filas:
                        celdas = fila.find_all('td')
                        if len(celdas) >= 2 and "Construida" in celdas[0].text:
                            # Extrae el número (ej: 110,00) y lo convierte a float
                            valor = celdas[1].text.replace(',', '.').split()[0]
                            return float(valor)
            return 110.0 # Valor por defecto si no lo encuentra
        except Exception as e:
            print(f"Error en Catastro: {e}")
            return 110.0

    def obtener_precio_referencia(self):
        url_repo = "https://raw.githubusercontent.com/domoprac/vivienda-pueblo-dinamica/main/presupuesto_base.json"
        try:
            respuesta = requests.get(url_repo, timeout=5)
            return respuesta.json()['coste_m2_rehabilitacion']
        except:
            return 1200 

    def calcular_subvenciones(self, coste_bruto):
        detalles = []
        ahorro_acumulado = 0
        porcentaje_ayuda = 0.20 
        
        if self.datos['letra_actual'] >= 'E' and self.datos['letra_objetivo'] <= 'B':
            porcentaje_ayuda = 0.70 
            razon = f"Salto de eficiencia alto ({self.datos['letra_actual']} -> {self.datos['letra_objetivo']})"
        else:
            razon = "Mejora energética estándar"

        monto_pree = coste_bruto * porcentaje_ayuda
        ahorro_acumulado += monto_pree
        detalles.append({"nombre": "PREE 5000 Navarra", "monto": monto_pree, "razon": razon})

        if self.datos['placas']:
            ahorro_acumulado += 3000 
            detalles.append({"nombre": "Ayuda Autoconsumo IDAE", "monto": 3000, "razon": "Instalación fotovoltaica"})

        return ahorro_acumulado, detalles
