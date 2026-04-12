import requests

class AgenteNavarra:
    def __init__(self, datos_vivienda):
        self.datos = datos_vivienda
        # Simulación de base de datos de subvenciones 2026
        self.catalogo_ayudas = [
            {"nombre": "PREE 5000 (Municipios pequeños)", "ahorro": 0.70, "tipo": "Rehabilitación"},
            {"nombre": "Deducción Fiscal Navarra Renovables", "ahorro": 0.15, "tipo": "Energía"},
            {"nombre": "Ayuda Autoconsumo (NextGen)", "ahorro": 0.40, "tipo": "Placas"}
        ]

    def calcular_presupuesto_neto(self, coste_bruto):
        print(f"Analizando ayudas para {self.datos['municipio']}...")
        ahorro_total = 0
        detalles = []
        
        # Lógica del agente: Aplicar PREE 5000 si es Santacara (<5000 hab)
        if self.datos['poblacion_menor_5000']:
            ayuda = self.catalogo_ayudas[0]
            descuento = coste_bruto * ayuda['ahorro']
            ahorro_total += descuento
            detalles.append(f"{ayuda['nombre']}: -{descuento:,.2f}€")
            
        coste_final = coste_bruto - ahorro_total
        return coste_final, detalles