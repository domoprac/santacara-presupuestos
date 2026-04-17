import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos
        # CONFIGURACIÓN: Pega tu clave aquí abajo entre las comillas
        self.api_key = "AIzaSyDDmQXtx34tEg014lYxTkCUCiVUgxn2kNI" 
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception:
            self.model = None

    def obtener_superficie_catastro(self, cod_muni, pol, par):
        url = f"https://catastro.navarra.es/ref_catastral/unidades.aspx?C={cod_muni}&PO={pol}&PA={par}&lang=es"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            for td in soup.find_all('td'):
                if "Construida" in td.get_text():
                    valor = td.find_next('td').get_text().replace(',', '.').split()[0]
                    return float(valor)
            return 110.0
        except:
            return 110.0

    def obtener_precio_referencia(self):
        url = "https://raw.githubusercontent.com/domoprac/vivienda-pueblo-dinamica/main/presupuesto_base.json"
        try:
            res = requests.get(url, timeout=5)
            return res.json().get('coste_m2_rehabilitacion', 1200)
        except:
            return 1200

    def calcular_subvenciones(self, coste):
        l_act = self.datos.get('letra_actual', 'E')
        l_obj = self.datos.get('letra_objetivo', 'A')
        porcentaje = 0.70 if l_act >= 'E' and l_obj <= 'B' else 0.20
        monto = coste * porcentaje
        detalles = [{"nombre": "Ayuda Navarra", "monto": monto, "razon": "Salto térmico"}]
        if self.datos.get('placas'):
            monto += 3000.0
            detalles.append({"nombre": "Deducción Solar", "monto": 3000.0, "razon": "Fotovoltaica"})
        return monto, detalles

    def explicar_con_ia(self, presupuesto, ayuda):
        if "AIza" not in self.api_key:
            return "⚠️ Falta configurar la API Key de Google en agentes.py"
        
        prompt = f"""
        Actúa como un experto en eficiencia energética y consultor del Ayuntamiento de Santacara.
        Analiza estos datos de rehabilitación:
        - Presupuesto bruto: {presupuesto:,.2f}€
        - Subvenciones estimadas: {ayuda:,.2f}€
        - Mejora de certificado: de {self.datos['letra_actual']} a {self.datos['letra_objetivo']}
        
        Escribe un informe breve de 3 puntos explicando por qué es una inversión 
        estratégica para el pueblo. Sé profesional y utiliza un tono motivador.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error en la IA (Nube): {str(e)}"
