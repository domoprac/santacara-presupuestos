import requests
from bs4 import BeautifulSoup
from groq import Groq

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos
        # 🔑 PEGA AQUÍ TU CLAVE DE GROQ (empieza por gsk_...)
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
        monto_rehab = coste * porc
        
        detalles = [{
            "nombre": "Ayuda Rehabilitación (PRTR Navarra)", 
            "monto": monto_rehab, 
            "razon": f"Subvención por salto térmico {l_act} -> {l_obj}",
            "tramite": "Expediente de Calificación Energética"
        }]
        
        if self.datos.get('placas'):
            detalles.append({
                "nombre": "Subvención Y (Fotovoltaica)", 
                "monto": 3000.0, 
                "razon": "Bonus Autoconsumo - Documento X",
                "fecha_limite": "31 de diciembre de 2026",
                "tramite": "Registro Industrial Documento X"
            })
        
        monto_total = sum(d['monto'] for d in detalles)
        return monto_total, detalles

    def explicar_con_ia(self, presupuesto, ayuda_total, detalles):
        """Esta función recibe self + 3 argumentos = 4 en total."""
        if not self.client:
            return "⚠️ Error: Cliente Groq no configurado."
        
        texto_detalles = "\n".join([f"- {d['nombre']}: {d['monto']:,.2f}€ (Trámite: {d.get('tramite', 'N/A')}). Plazo: {d.get('fecha_limite', 'Abierto')}" for d in detalles])
        
        prompt = f"""
        Actúa como consultor del Ayuntamiento de Santacara.
        Inversión: {presupuesto:,.2f}€ | Ayuda: {ayuda_total:,.2f}€
        
        DESGLOSE:
        {texto_detalles}
        
        TAREAS:
        1. Explica que los 3.000€ son de la 'Subvención Y' y requieren el 'Documento X'.
        2. Indica que la fecha límite es el '31 de diciembre de 2026'.
        3. Valora el paso de letra {self.datos['letra_actual']} a {self.datos['letra_objetivo']}.
        Responde de forma profesional y estructurada.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"❌ Error de Groq: {str(e)}"
