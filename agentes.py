import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

class AgenteNavarra:
    def __init__(self, datos):
        self.datos = datos
        # CONFIGURACIÓN: Pega tu clave aquí abajo
        self.api_key = "AIzaSyDDmQXtx34tEg014lYxTkCUCiVUgxn2kNI" 
        
        try:
            genai.configure(api_key=self.api_key)
            # Usamos una ruta más compatible para evitar el error 404
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        except Exception:
            self.model = None

    def obtener_superficie_catastro(self, cod_muni, pol, par):
        """Intenta extraer la superficie real de Tracasa con headers reforzados."""
        url = f"https://catastro.navarra.es/ref_catastral/unidades.aspx?C={cod_muni}&PO={pol}&PA={par}&lang=es"
        try:
            # Simulamos ser un navegador real para que Tracasa no nos bloquee
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Buscamos en todas las celdas de tabla
            for td in soup.find_all('td'):
                texto = td.get_text(strip=True)
                if "Construida" in texto or "Total" in texto:
                    siguiente = td.find_next('td')
                    if siguiente:
                        valor_raw = siguiente.get_text(strip=True)
                        # Limpiamos: '143,00 m2' -> 143.0
                        valor_limpio = valor_raw.replace(',', '.').split()[0]
                        return float(valor_limpio)
            return None # Si no lo encuentra, devolvemos None
        except Exception:
            return None

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
            return "⚠️ Configura la API Key en agentes.py"
        
        prompt = f"""
        Como consultor del Ayuntamiento de Santacara, analiza:
        - Obra: {presupuesto:,.2f}€
        - Ayudas: {ayuda:,.2f}€
        - Mejora: {self.datos['letra_actual']} a {self.datos['letra_objetivo']}
        Explica en 3 puntos por qué es vital para el pueblo. Sé breve y profesional.
        """
        try:
            # Forzamos la generación de contenido
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error de conexión con Gemini: {str(e)}"
