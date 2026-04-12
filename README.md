# 🏡 Santacara Sostenible: Agente de Rehabilitación Energética

Este proyecto despliega una aplicación web interactiva diseñada para la gestión técnica y económica de la rehabilitación de edificios municipales en **Santacara (Navarra)**, con especial foco en la **Casa del Médico**.

## 🚀 Funcionalidades Clave

* **Agente Inteligente de Subvenciones:** Implementa una lógica basada en la normativa de Navarra (PREE 5000 / Fondos NextGen) para calcular ayudas de hasta el 70% según el salto en la certificación energética (Letra G/E -> A/B).
* **Conexión con Repositorio de Precios:** El sistema consulta en tiempo real un archivo de referencia en el repositorio de **Domoprac** para aplicar costes de mercado actualizados por m².
* **Integración con Catastro (Tracasa):** Incluye un módulo de consulta dinámica al portal de Catastro de Navarra para la verificación de superficies por municipio, polígono y parcela.
* **Interfaz de Usuario con Streamlit:** Dashboard intuitivo que permite realizar simulaciones de inversión bruta vs. inversión neta tras ayudas.

## 🛠️ Arquitectura Técnica

El ecosistema se basa en una estructura de micro-servicios desacoplados:

1.  **Frontend:** `app.py` (Streamlit Cloud).
2.  **Lógica de Negocio:** `agentes.py` (Clase Python `AgenteNavarra`).
3.  **Fuentes de Datos Externas:**
    * **GitHub Raw:** Para la obtención de costes base.
    * **Web Scraping (BeautifulSoup4):** Para la extracción de datos desde el portal oficial de Tracasa.

## 📦 Instalación y Uso Local

Si deseas ejecutar este proyecto en tu ordenador, sigue estos pasos:

1. Clonar el repositorio.
2. Instalar las dependencias necesarias:
   ```bash
   pip install streamlit requests beautifulsoup4
