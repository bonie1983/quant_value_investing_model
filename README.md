# Quantitative Investment System (MVP - Dow Jones Universe)

Pipeline cuantitativo en Python diseñado para evaluar, filtrar y valorar el universo de empresas del **Dow Jones**, automatizando la extracción de datos desde la API de la SEC (XBRL) y la integración de precios históricos locales.

---

## 🏗️ Arquitectura del Sistema

El sistema opera de forma modular a través de dos componentes principales:

1. **`filters_fun.py`**: Módulo central de lógica financiera que procesa los estados financieros anuales (`10-K`) cacheados localmente.
2. **Script Principal de Ejecución (`__main__`)**: Orquesta la carga de datos, la aplicación de filtros de seguridad y el cálculo del ranking de valoración final.

---

## 🛡️ Fases del Pipeline (Metodología *Quantitative Value*)

### Paso 1: Filtros de Seguridad (Mitigación de Pérdida Permanente de Capital)

El sistema evalúa indicadores clave de contabilidad forense y salud financiera para descartar anomalías de riesgo extremo:

* **STA (Accruals / Calidad de Accruals)**: Detecta discrepancias entre el beneficio neto y el flujo de caja operativo real.
* **SNOA (Net Operating Assets)**: Mide el crecimiento desproporcionado de los activos operativos netos.
* **PMAN (Indicador de Fraude / DSRI)**: Identifica anomalías e incrementos inusuales en las cuentas por cobrar.
* **PFD (Probability of Financial Distress)**: Modelo de alerta temprana de bancarrota e insolvencia basado en la liquidez a corto plazo y la productividad de los activos (adaptado del Altman Z-Score).

### Paso 2: Modelo de Valoración (EBIT / TEV)

* **Market Cap Híbrido**: Cruza el número exacto de acciones ordinarias en circulación extraídas de los metadatos oficiales de la SEC (`DEI`) con precios locales normalizados (`CSV`).
* **TEV (*Total Enterprise Value*)**: Calcula el valor empresarial real sumando la deuda y restando la caja disponible.
* **Ratio EBIT/TEV**: Determina la rentabilidad operativa real generada por cada dólar invertido en la empresa, ordenando el universo de más barato a más caro.

---

## 🚀 Instalación y Uso

1. Clona el repositorio e instala las dependencias necesarias:
```bash
pip install pandas requests

```


2. Asegúrate de tener el archivo con los metadatos de las empresas (`dic_companies.py`) y el repositorio de precios locales (`data_cache/precios_dow.csv`).
3. Ejecuta el script principal:
```bash
python main.py

```