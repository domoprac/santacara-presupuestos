import requests
from bs4 import BeautifulSoup

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos

    def obtener_superficie_catastro(self, url_catastro):
        """
        El agente entra en la web de Tracasa (Catastro de Navarra) 
        y extrae los m2 reales.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            respuesta = requests.get(url_catastro, headers=headers, timeout=10)
            soup = BeautifulSoup(respuesta.text, 'html.parser')
            
            # Buscamos la tabla que contiene la superficie
            tablas = soup.find_all('table')
            for tabla in tablas:
                if "Superficie" in tabla.text:
                    filas = tabla.find_all('tr')
                    for fila in filas:
                        celdas = fila.find_all('td')
                        # Buscamos la fila que dice 'Construida'
                        if len(celdas) >= 2 and "Construida" in celdas[0].text:
                            # Limpiamos el texto para quedarnos solo con el número
                            valor_texto = celdas[1].text.replace(',', '.').strip()
                            # Extraemos solo los números antes del primer espacio (ej: '143,00 m2')
                            valor_num = valor_texto.split()[0]
                            return float(valor_num)
            return 110.0
        except Exception as e:
            # Si falla la conexión o el formato cambia, devuelve el valor por defecto
            return 110.0

    def obtener_precio_referencia(self):
        """Consulta el coste por m2 en el repositorio de Domoprac"""
        url_repo = "https://raw.githubusercontent.com/domoprac/vivienda-pueblo-dinamica/main/presupuesto_base.json"
        try:
            respuesta = requests.get(url_repo, timeout=5)
            datos_repo = respuesta.json()
            return datos_repo['coste_m2_rehabilitacion']
        except:
            return 1200 # Precio de seguridad si falla el repo

    def calcular_subvenciones(self, coste_bruto):
        """Lógica de ayudas basadas en la normativa de Navarra (BON)"""
        detalles = []
        ahorro_acumulado = 0
        
        # 1. Lógica PREE 5000 / Fondos Europeos
        porcentaje_ayuda = 0.20 
        
        # Si hay un salto térmico importante (de E/F/G a A/B)
        if self.datos.get('letra_actual', 'E') >= 'E' and self.datos.get('letra_objetivo', 'A') <= 'B':
            porcentaje_ayuda = 0.70 
            razon = f"Salto energético alto ({self.datos.get('letra_actual')} -> {self.datos.get('letra_objetivo')})"
        else:
