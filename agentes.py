import requests
from bs4 import BeautifulSoup
from langchain_ollama import OllamaLLM

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos
        # Nueva forma oficial de conectar con Ollama
        try:
            self.llm = OllamaLLM(model="llama3.2")
        except Exception:
            self.llm = None

    def obtener_superficie_catastro(self, cod_muni, pol, par):
        """Construye la URL y extrae la superficie de Tracasa."""
        url = f"https://catastro.navarra.es/ref_catastral/unidades.aspx?C={cod_muni}&PO={pol}&PA={par}&lang=es"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code != 200: return 110.0
            
            soup = BeautifulSoup(res.text, 'html.parser')
            for td in soup.find_all('td'):
                if "Construida" in td.get_text():
                    valor = td.find_next('td').get_text().replace(',', '.').split()[0]
                    return float(valor)
            return 110.0
        except Exception:
            return 110.0

    def obtener_precio_referencia(self):
        """Consulta el precio m2 en el repo de Domoprac."""
        url = "https://raw.githubusercontent.com/domoprac/vivienda-pueblo-dinamica/main/presupuesto_base.json"
        try:
            res = requests.get(url, timeout=5)
            return res.json().get('coste_m2_rehabilitacion', 1200)
        except Exception:
            return 1200

    def calcular_subvenciones(self, coste):
        """Lógica de negocio para ayudas de Navarra."""
        l_act = self.datos.get('letra_actual', 'E')
        l_obj = self.datos.get('letra_objetivo', 'A')
        
        porcentaje = 0.70 if l_act >= 'E' and l_obj <= 'B' else 0.20
        monto = coste * porcentaje
        
        detalles = [{"nombre": "Ayuda Rehabilitación Navarra", "monto": monto, "razon": "Basado en salto térmico"}]
        
        if self.datos.get('placas'):
            monto_solar = 3000.0
            monto += monto_solar
            detalles.append({"nombre": "Deducción Autoconsumo", "monto": monto_solar, "razon": "Instalación fotovoltaica"})
            
        return monto, detalles

    def explicar_con_ia(self, presupuesto, ayuda):
        """Genera un informe persuasivo usando Llama 3.2."""
        if not self.llm:
            return "⚠️ Error: No se pudo conectar con Ollama. Asegúrate de tener 'ollama run llama3.2' activo."
        
        prompt = f"""
        Como experto en energía y consultor para el Ayuntamiento de Santacara, analiza:
        - Inversión bruta: {presupuesto:,.2f}€
        - Ayudas totales: {ayuda:,.2f}€
        - Mejora: de letra {self.datos['letra_actual']} a {self.datos['letra_objetivo']}
        
        Escribe un resumen ejecutivo de 3 puntos sobre por qué esta obra es vital para el municipio 
        y cómo ayuda a la economía de los vecinos. Sé breve, profesional y directo.
        """
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            return f"❌ Error de IA: {str(e)}"
