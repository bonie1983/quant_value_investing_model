# Quantitative Value Model

**Sistema cuantitativo de inversión en valor basado en la metodología de _Quantitative Value_.**

Proyecto desarrollado en Python para construir un modelo sistemático de inversión en valor (*Quantitative Value Investing*), utilizando información financiera oficial de la SEC (XBRL) y datos históricos de mercado.

El objetivo es evaluar empresas mediante filtros de riesgo financiero y contable, métricas de valoración y criterios de calidad empresarial, para construir una cartera diversificada de compañías infravaloradas.

El universo inicial está formado por 25 empresas del Dow Jones. Las entidades financieras que requieren un tratamiento específico quedan excluidas del modelo principal.

---

## 1. Objetivos del proyecto

El sistema pretende:

- Obtener información financiera directamente de las fuentes oficiales de la SEC.
- Conservar la trazabilidad de los datos financieros y sus fechas de publicación.
- Identificar empresas con señales de riesgo contable, manipulación financiera o dificultades económicas.
- Clasificar empresas según su valoración relativa mediante EBIT/TEV.
- Evaluar la calidad y solidez financiera de las compañías.
- Construir un ranking cuantitativo que permita seleccionar potenciales inversiones.
- Facilitar la evaluación histórica de la metodología mediante pruebas retrospectivas (*backtesting*).

La metodología toma como referencia principal el libro *Quantitative Value*, de Wesley R. Gray y Tobias E. Carlisle, y el trabajo académico de Hjalti Þór Skaftason.

## 2. Arquitectura del proyecto

El proyecto utiliza una arquitectura modular para separar la extracción, almacenamiento, exploración, validación y procesamiento de la información financiera.

```text
quant_val_model/
│
├── database/                  # Base de datos SQLite (no versionada)
├── data_cache/                # Datos originales y caché (no versionados)
│
├── exploration/
│   ├── __init__.py
│   └── explore_financial_data.py
│
├── validations/
│   ├── __init__.py
│   └── validate_revenue.py
│
├── database_manager.py        # Gestión de la base de datos
├── dic_companies.py           # Universo de empresas y CIK
├── dic_financial_terms.py     # Conceptos financieros de la SEC
├── financial_data.py          # Consultas y extracción financiera
│
├── filters_fun.py             # Filtros de seguridad
├── quality_fun.py             # Métricas de calidad empresarial
├── ranking_fun.py             # Rankings cuantitativos
├── EBIT_TEV.py                 # Cálculo de valoración EBIT/TEV
│
├── main.py                    # Punto de entrada del sistema
├── requirements.txt           # Dependencias de Python
├── README.md
└── .gitignore
```

Los módulos de filtros, calidad, ranking y valoración forman parte de la arquitectura prevista del modelo y se irán implementando y validando progresivamente.

## 3. Fuente y gestión de datos financieros

### SEC EDGAR y XBRL

La fuente principal de información financiera es la base de datos pública de la SEC, a través de sus datos XBRL.

El sistema obtiene información de los informes financieros anuales, principalmente formularios 10-K.

Cada observación financiera conserva información de procedencia, incluyendo:

- Empresa y concepto contable.
- Taxonomía y unidad de medida.
- Valor financiero.
- Fecha de inicio y finalización del periodo.
- Número de acceso (*accession number*).
- Ejercicio fiscal y tipo de formulario.
- Fecha de presentación ante la SEC (*filed date*).
- Identificador del periodo, cuando está disponible.

Esta información permite controlar qué datos estaban publicados en una fecha determinada y constituye la base para evitar sesgos de anticipación (*look-ahead bias*) en los futuros backtests.

### Base de datos

Los datos se almacenan localmente en SQLite.

La base de datos y los archivos originales de caché no se incluyen en GitHub. Pueden reconstruirse mediante los procesos de extracción del proyecto.

## 4. Metodología cuantitativa

El modelo seguirá una secuencia de evaluación en tres grandes bloques.

### Fase 1. Filtros de seguridad

El primer objetivo es reducir el riesgo de pérdida permanente de capital, identificando empresas con posibles anomalías contables o problemas financieros.

Los indicadores previstos incluyen:

- **STA:** indicador relacionado con los accruals y la calidad de los beneficios contables.
- **SNOA:** activos operativos netos, para detectar posibles crecimientos desproporcionados.
- **PMAN:** probabilidad asociada a señales de manipulación contable, basada en el modelo Beneish M-Score.
- **PFD:** probabilidad de dificultades financieras, basada en el modelo de Campbell, Hilscher y Szilagyi.

La metodología contempla excluir las empresas situadas en los peores percentiles de estos indicadores.

### Fase 2. Valoración: EBIT / TEV

El objetivo es identificar compañías cuyo beneficio operativo sea elevado en relación con su valor empresarial.

**EBIT (Earnings Before Interest and Taxes)**

Beneficio antes de intereses e impuestos.

**TEV (Total Enterprise Value)**

Valor empresarial calculado considerando la capitalización bursátil, la deuda y otros ajustes relevantes:

- Capitalización bursátil.
- Deuda financiera.
- Caja excedentaria.
- Acciones preferentes, cuando corresponda.
- Intereses minoritarios, cuando corresponda.

**EBIT/TEV**

\[
EBIT/TEV = \frac{EBIT}{TEV}
\]

Un resultado más elevado representa una mayor rentabilidad operativa en relación con el valor empresarial y, por tanto, una valoración potencialmente más atractiva.

### Fase 3. Calidad empresarial

La última fase busca distinguir las empresas baratas de aquellas que, además, presentan buenos fundamentos económicos.

Se contemplan dos grandes componentes:

**Franchise Power**

Evaluación de la capacidad de generar rentabilidad y mantener ventajas económicas a largo plazo, utilizando indicadores como ROA, ROC, generación de caja y márgenes.

**Financial Strength**

Evaluación de la solidez financiera y la evolución de los fundamentales mediante señales inspiradas en el modelo de Piotroski.

El resultado combinará ambos componentes para obtener una puntuación de calidad empresarial.

---

## 5. Estado actual del desarrollo

El proyecto se está desarrollando por etapas. El estado de implementación es el siguiente:

| Componente | Estado |
|---|---|
| Universo inicial de empresas | Implementado |
| Descarga de datos SEC XBRL | Implementada |
| Almacenamiento en SQLite | Implementado |
| Caché de datos originales | Implementada |
| Trazabilidad de observaciones financieras | Implementada |
| Diccionario de conceptos financieros | Implementado |
| Extracción de ingresos anuales | Implementada |
| Validación de ingresos de las 25 empresas | Superada |
| Cálculo de EBIT | Pendiente de completar |
| Cálculo de capitalización bursátil | Pendiente de completar |
| Cálculo de TEV y EBIT/TEV | Pendiente de completar |
| Filtros de seguridad | Pendiente de validar |
| Ranking de calidad | Pendiente de validar |
| Construcción de cartera | Pendiente |
| Backtesting histórico | Pendiente |

**Último hito:** extracción y validación de los ingresos anuales de las 25 empresas configuradas, utilizando información de la SEC y fechas de publicación.

## 6. Instalación y configuración

### Requisitos

- Python 3.13.
- Git.
- Visual Studio Code (recomendado).

### Clonar el repositorio

```bash
git clone https://github.com/bonie1983/quant_val_model.git
cd quant_val_model
```

### Crear el entorno virtual

En macOS:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### Instalar dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Es importante utilizar el intérprete situado en `.venv/bin/python` también en Visual Studio Code.

### Ejecutar el proyecto

El punto de entrada general será:

```bash
python main.py
```

Los procesos de validación se ejecutan como módulos desde la raíz del proyecto.

Por ejemplo, para validar los ingresos:

```bash
python -m validations.validate_revenue
```

## 7. Control de versiones y reproducibilidad

El proyecto utiliza Git y GitHub para mantener un historial de cambios del código.

Se excluyen del control de versiones:

- Entornos virtuales.
- Bases de datos locales.
- Archivos de caché.
- Credenciales y variables de entorno.
- Archivos temporales de Python.

Las dependencias se documentan en `requirements.txt`.

La reproducibilidad del modelo será un principio fundamental: las futuras evaluaciones históricas deberán conservar las fechas de publicación de los datos, las versiones del código, los precios utilizados, las puntuaciones calculadas y las decisiones de selección de cartera.

---

## 8. Filosofía del proyecto

El objetivo no es predecir los movimientos del mercado a corto plazo, sino desarrollar un proceso sistemático, disciplinado y fundamentado en datos para identificar empresas con valoraciones atractivas y buenos fundamentos financieros.

La metodología deberá evaluarse con datos históricos, teniendo en cuenta los costes de transacción, la rotación de cartera, la disponibilidad real de información y los posibles sesgos estadísticos.

Los resultados históricos no garantizan rentabilidades futuras.

**La prioridad es construir un modelo robusto, transparente, reproducible y capaz de tomar decisiones de inversión sin depender de impulsos emocionales.**