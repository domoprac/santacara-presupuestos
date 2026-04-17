import requests
from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos
        # Tu clave AQ
        self.api_key = "AQ.Ab8RN6J0xuNIVoGlxF3TemgZfcbkZEpxbAXxNrwSx3nSL_oINw" 
        
        try:
            # Forzamos gemini-1.5-pro que suele estar disponible en proyectos AQ
            # Eliminamos cualquier rastro de v1beta usando el motor estable
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=self.api_key,
                temperature=0.3 # Más bajo para evitar alucinaciones
            )
        except Exception as e:
            self.llm = None

    def obtener_superficie_catastro(self, cod_muni, pol, par):
        url = f"https://catastro.navarra.es/ref_catastral/unidades.aspx?C={cod_muni}&PO={pol}&PA={par}&lang=es"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
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
        if not self.llm:
            return "⚠️ IA no inicializada."
        
        prompt = f"""Como experto en energía en Santacara, Navarra:
        - Obra: {presupuesto}€
        - Ayuda: {ayuda}€
        - Mejora: {self.datos['letra_actual']} -> {self.datos['letra_objetivo']}
        Resume en 3 puntos claros por qué es una buena inversión. Responde en español."""
        
        try:
            # Llamada directa al modelo
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            # Si vuelve a dar 404, el problema es la activación de la API en tu consola
            return f"❌ Error: {str(e)}"
        
        try:
            # LangChain gestiona mejor las claves tipo AQ/OAuth
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=self.api_key,
                temperature=0.7
            )
        except Exception as e:
            print(f"Error inicializando LLM: {e}")
            self.llm = None

    def obtener_superficie_catastro(self, cod_muni, pol, par):
        url = f"https://catastro.navarra.es/ref_catastral/unidades.aspx?C={cod_muni}&PO={pol}&PA={par}&lang=es"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
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
        if not self.llm:
            return "⚠️ IA no configurada."
        
        prompt = f"""Como experto en Santacara, analiza:
        Inversión: {presupuesto}€, Ayuda: {ayuda}€. 
        Mejora de letra {self.datos['letra_actual']} a {self.datos['letra_objetivo']}. 
        Resume en 3 puntos por qué es positivo."""
        
        try:
            # Invocación estilo LangChain
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"❌ Error de IA: {str(e)}"
