import requests
from bs4 import BeautifulSoup
from groq import Groq

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos
        # 🔑 PEGA AQUÍ TU CLAVE DE GROQ (gsk_...)
        self.api_key = "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"
        
        try:
            self.client = Groq(api_key=self.api_key)
        except Exception:
            self.client = None

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
        if not self.api_key or "gsk" not in self.api_key:
            return "⚠️ Error: Falta la clave de Groq en agentes.py"
        
        prompt = f"""Actúa como experto en energía para el Ayuntamiento de Santacara.
        Analiza: Obra de {presupuesto}€, Ayuda de {ayuda}€.
        Mejora de letra {self.datos['letra_actual']} a {self.datos['letra_objetivo']}.
        Resume en 3 puntos claros por qué es una excelente inversión para el vecino. 
        Responde en español de España de forma profesional."""
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"❌ Error de Groq: {str(e)}"
