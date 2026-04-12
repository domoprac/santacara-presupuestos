import requests

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos

    def obtener_precio_referencia(self):
        """El agente mira el 'libro de precios' en el GitHub de Domoprac"""
        url_repo = "https://raw.githubusercontent.com/domoprac/vivienda-pueblo-dinamica/main/presupuesto_base.json"
        try:
            # Intenta leer el precio real del repo
            respuesta = requests.get(url_repo, timeout=5)
            datos_repo = respuesta.json()
            return datos_repo['coste_m2_rehabilitacion']
        except:
            # Si el repo no tiene ese archivo aún o falla el internet, usa este por defecto
            return 1200 

    def calcular_subvenciones(self, coste_bruto):
        detalles = []
        ahorro_acumulado = 0

        # 1. Lógica PREE 5000 (Basado en el salto de letra)
        porcentaje_ayuda = 0.20 
        
        # Nota: En Python, comparar 'E' >= 'B' funciona por orden alfabético. 
        # Aquí la lógica es: si la letra actual es E, F o G (peores) 
        # y la objetivo es A o B (mejores).
        if self.datos['letra_actual'] >= 'E' and self.datos['letra_objetivo'] <= 'B':
            porcentaje_ayuda = 0.70 
            razon = f"Salto de eficiencia alto ({self.datos['letra_actual']} -> {self.datos['letra_objetivo']})"
        else:
            razon = "Mejora energética estándar"

        monto_pree = coste_bruto * porcentaje_ayuda
        ahorro_acumulado += monto_pree
        detalles.append({"nombre": "PREE 5000 Navarra", "monto": monto_pree, "razon": razon})

        # 2. Ayuda específica por Autoconsumo
        if self.datos['placas']:
            ayuda_placas = 3000 
            ahorro_acumulado += ayuda_placas
            detalles.append({"nombre": "Ayuda Autoconsumo IDAE", "monto": ayuda_placas, "razon": "Instalación de paneles fotovoltaicos"})

        return ahorro_acumulado, detalles