import requests

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos

    def obtener_precio_referencia(self):
        """El agente mira el 'libro de precios' en el GitHub de Domoprac"""
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
            ayuda_placas = 3000 
            ahorro_acumulado += ayuda_placas
            detalles.append({"nombre": "Ayuda Autoconsumo IDAE", "monto": ayuda_placas, "razon": "Instalación de paneles fotovoltaicos"})

        return ahorro_acumulado, detalles
