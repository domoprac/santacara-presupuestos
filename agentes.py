import requests
from bs4 import BeautifulSoup
from groq import Groq

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos
        # 🔑 PEGA TU CLAVE DE GROQ AQUÍ
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
        
        # Lógica Navarra: 70% por salto de E a A
        porc = 0.70 if l_act >= 'E' and l_obj <= 'B' else 0.20
        monto_rehab = coste * porc
        
        detalles = [{
            "nombre": "Ayuda Rehabilitación (Fondos PRTR)", 
            "monto": monto_rehab, 
            "razon": f"Subvención por mejora de envolvente y salto de letra {l_act} a {l_obj}",
            "tramite": "Certificado de Eficiencia Energética Final"
        }]
        
        if self.datos.get('placas'):
            detalles.append({
                "nombre": "Subvención Y (Autoconsumo)", 
                "monto": 3000.0, 
                "razon": "Instalación fotovoltaica vinculada al Documento X",
                "fecha_limite": "31 de diciembre de 2026",
                "tramite": "Registro Industrial y Documentación Técnica"
            })
        
        monto_total = sum(d['monto'] for d in detalles)
        return monto_total, detalles

    def explicar_con_ia(self, presupuesto, ayuda_total, detalles):
        if not self.client:
            return "⚠️ Error: Cliente Groq no configurado en agentes.py"
        
        txt_detalles = "\n".join([f"- {d['nombre']}: {d['monto']:,.2f}€ | Trámite: {d.get('tramite', 'N/A')} | Plazo: {d.get('fecha_limite', 'Abierto')}" for d in detalles])
        
        prompt = f"""
        ERES: Un consultor experto para el Ayuntamiento de Santacara, Navarra.
        CASO: Rehabilitación energética integral (Letra {self.datos['letra_actual']} a {self.datos['letra_objetivo']}).
        
        DATOS ECONÓMICOS:
        - Inversión: {presupuesto:,.2f}€
        - Ayuda Total: {ayuda_total:,.2f}€
        - Neto Vecino: {presupuesto - ayuda_total:,.2f}€
        
        DESGLOSE ADMINISTRATIVO:
        {txt_detalles}
        
        TU MISIÓN:
        1. Explica que la ayuda de 3.000€ es la 'Subvención Y' y requiere presentar el 'Documento X'.
        2. Alerta con urgencia de la fecha límite: '31 de diciembre de 2026'.
        3. Valora positivamente el ahorro del {ayuda_total/presupuesto*100:.1f}%.
        4. Usa un tono institucional, claro y directo. Estructura con negritas para resaltar datos clave.
        """
        
        try:
            res = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return res.choices[0].message.content
        except Exception as e:
            return f"❌ Error de Groq: {str(e)}"
