import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos
        # Tu clave de la captura de pantalla
        self.api_key = "AQ.Ab8RN6Ijb_W4luwBxgTQ6IW9zS3CyD05eMj3j9Cv2fU4JsLphA" 
        
        try:
            # Configuramos la conexión
            genai.configure(api_key=self.api_key)
            # Usamos gemini-1.5-flash que es el más rápido y compatible
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            print(f"Error al configurar genai: {e}")
            self.model = None

    def obtener_superficie_catastro(self, cod_muni, pol, par):
        url = f"https://catastro.navarra.es/ref_catastral/unidades.aspx?C={cod_muni}&PO={pol}&PA={par}&lang=es"
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            for td in soup.find_all('td'):
                if "Construida" in td.get_text() or "Total" in td.get_text():
                    sig = td.find_next('td')
                    if sig:
                        v = sig.get_text(strip=True).replace(',', '.').split()[0]
                        return float(v)
            return 110.0
        except:
            return 110.0

    def obtener_precio_referencia(self):
        url = "https://raw.githubusercontent.com/domoprac/vivienda-pueblo-dinamica/main/presupuesto_base.json"
        try:
            res = requests.get(url, timeout=5)
            return float(res.json().get('coste_m2_rehabilitacion', 1200))
        except:
            return 1200.0

    def calcular_subvenciones(self, coste):
        l_act = self.datos.get('letra_actual', 'E')
        l_obj = self.datos.get('letra_objetivo', 'A')
        porc = 0.70 if l_act >= 'E' and l_obj <= 'B' else 0.20
        monto = coste * porc
        detalles = [{"nombre": "Ayuda Navarra", "monto": monto, "razon": "Eficiencia"}]
        if self.datos.get('placas'):
            monto += 3000.0
            detalles.append({"nombre": "Bonus Solar", "monto": 3000.0, "razon": "Fotovoltaica"})
        return monto, detalles

    def explicar_con_ia(self, presupuesto, ayuda):
        prompt = f"""Escribe un informe de 3 frases para el Ayuntamiento de Santacara. 
        Inversión: {presupuesto}€, Ayuda: {ayuda}€. 
        Mejora de letra {self.datos['letra_actual']} a {self.datos['letra_objetivo']}. 
        Explica por qué es una buena decisión."""
        
        try:
            # Intentamos la generación
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Si da error 404, informamos de qué puede ser
            if "404" in str(e):
                return "❌ Error 404: La API de Gemini no está activa para esta clave en Google Cloud Console."
            return f"❌ Error de IA: {str(e)}"
