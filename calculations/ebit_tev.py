import os
import json
import time
import requests
import pandas as pd

# Importamos el diccionario de empresas del Dow Jones
from dic_companies import EMPRESAS_DOWJONES

# Directorio de caché local compartido
CACHE_DIR = "data_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Ruta del archivo CSV de precios descargado de GitHub o generado localmente
CSV_PRECIOS_PATH = os.path.join(CACHE_DIR, "precios_dow.csv")

# ---------------------------------------------------------------------------
# 1. DESCARGA Y CACHÉ DE DATOS DE LA SEC (CON HEADERS OBLIGATORIOS)
# ---------------------------------------------------------------------------
def obtener_datos_sec(ticker: str, cik: str) -> dict:
    cache_file = os.path.join(CACHE_DIR, f"{ticker.upper()}_sec.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    print(f"[{ticker}] Descargando datos desde la API oficial de la SEC...")
    headers = {"User-Agent": "MiProyectoQuant steverozad@gmail.com"}
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
            time.sleep(0.2)
            return data
        else:
            print(f"Error al conectar con la SEC para {ticker}: Código {response.status_code}")
            return {}
    except Exception as e:
        print(f"Excepción en la petición SEC para {ticker}: {e}")
        return {}

# ---------------------------------------------------------------------------
# 2. EXTRACCIÓN DEL EBIT DESDE EL JSON DE LA SEC
# ---------------------------------------------------------------------------
def obtener_ebit_de_sec(ticker: str) -> float:
    cache_file = os.path.join(CACHE_DIR, f"{ticker.upper()}_sec.json")
    if not os.path.exists(cache_file):
        return None
        
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        units = data.get("facts", {}).get("us-gaap", {})
        conceptos_ebit = [
            "OperatingIncomeLoss",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxes",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"
        ]
        
        for concepto in conceptos_ebit:
            if concepto in units and "USD" in units[concepto].get("units", {}):
                datos_concepto = units[concepto]["units"]["USD"]
                anuales = [x for x in datos_concepto if x.get("form") == "10-K"]
                if anuales:
                    anuales_ordenados = sorted(anuales, key=lambda x: x.get("end", ""), reverse=True)
                    return anuales_ordenados[0].get("val")
        return None
    except Exception as e:
        print(f"Error procesando EBIT de {ticker}: {e}")
        return None

# ---------------------------------------------------------------------------
# 3. EXTRACCIÓN DE ACCIONES (SEC) Y PRECIO DESDE CSV (GITHUB)
# ---------------------------------------------------------------------------
def obtener_acciones_de_sec(ticker: str) -> float:
    cache_file = os.path.join(CACHE_DIR, f"{ticker.upper()}_sec.json")
    if not os.path.exists(cache_file):
        print(f"[{ticker}] ⚠️ No existe archivo caché SEC para buscar acciones.")
        return None
        
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        facts = data.get("facts", {})
        dei = facts.get("dei", {})
        us_gaap = facts.get("us-gaap", {})
        
        # 1. PRIORIDAD MÁXIMA: Buscar en el nodo DEI (Acciones ordinarias oficiales en circulación)
        if "EntityCommonStockSharesOutstanding" in dei:
            unidades_dei = dei["EntityCommonStockSharesOutstanding"].get("units", {})
            for medida, registros in unidades_dei.items():
                valido = [x for x in registros if x.get("val") is not None and x.get("form") in ["10-K", "10-Q"]]
                if valido:
                    valido_ordenado = sorted(valido, key=lambda x: x.get("end", ""), reverse=True)
                    return valido_ordenado[0].get("val")

        # 2. FALLBACK: Si no está en DEI, buscar en us-gaap de forma estricta (10-K)
        conceptos_acciones = [
            "CommonStockSharesOutstanding", 
            "WeightedAverageNumberOfSharesOutstandingBasic",
            "WeightedAverageNumberOfDilutedSharesOutstanding"
        ]
        
        for concepto in conceptos_acciones:
            if concepto in us_gaap:
                unidades = us_gaap[concepto].get("units", {})
                for medida, registros in unidades.items():
                    valido = [x for x in registros if x.get("val") is not None and x.get("form") == "10-K"]
                    if valido:
                        valido_ordenado = sorted(valido, key=lambda x: x.get("end", ""), reverse=True)
                        return valido_ordenado[0].get("val")

        print(f"[{ticker}] ⚠️ No se encontró ninguna etiqueta válida de acciones en el JSON.")
        return None
    except Exception as e:
        print(f"Error procesando acciones de {ticker}: {e}")
        return None

def obtener_precio_desde_csv(ticker: str) -> float:
    if not os.path.exists(CSV_PRECIOS_PATH):
        print(f"⚠️ No se encontró el archivo de precios en {CSV_PRECIOS_PATH}")
        return None
        
    try:
        df_precios = pd.read_csv(CSV_PRECIOS_PATH)
        fila = df_precios[df_precios["Ticker"].str.upper() == ticker.upper()]
        if not fila.empty:
            return float(fila["Precio"].values[0])
        else:
            print(f"[{ticker}] No se encontró el precio en el CSV.")
            return None
    except Exception as e:
        print(f"[{ticker}] Error leyendo el CSV de precios: {e}")
        return None

def calcular_market_cap_hibrido(ticker: str) -> float:
    acciones = obtener_acciones_de_sec(ticker)
    if not acciones:
        print(f"[{ticker}] No se pudieron extraer las acciones de la SEC.")
        return None
        
    precio_actual = obtener_precio_desde_csv(ticker)
    if not precio_actual:
        print(f"[{ticker}] No se pudo obtener el precio desde el CSV.")
        return None
        
    return acciones * precio_actual

# ---------------------------------------------------------------------------
# 4. CÁLCULO MATEMÁTICO DEL EBIT / TEV
# ---------------------------------------------------------------------------
def calcular_ebit_tev(ebit: float, market_cap: float, deuda_total: float = 0, caja: float = 0) -> float:
    try:
        if not market_cap or market_cap <= 0 or ebit is None:
            return None
        tev = market_cap + deuda_total - caja
        if tev <= 0:
            return None
        return ebit / tev
    except Exception as e:
        print(f"Error al calcular EBIT/TEV: {e}")
        return None

# ---------------------------------------------------------------------------
# BLOQUE DE PRUEBA MASIVA (RANKING EBIT / TEV)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n--- Iniciando evaluación y ranking EBIT/TEV del universo (Vía CSV GitHub) ---")
    resultados = []
    
    for ticker, info in EMPRESAS_DOWJONES.items():
        nombre = info["nombre"]
        cik = info["cik"]
        
        print(f"\nProcesando EBIT/TEV para: {nombre} ({ticker})...")
        obtener_datos_sec(ticker, cik)
        ebit_anual = obtener_ebit_de_sec(ticker)
        market_cap = calcular_market_cap_hibrido(ticker)
        
        if ebit_anual and market_cap:
            # De momento dejamos deuda y caja en 0 para simplificar el MVP, 
            # luego podemos extraerlas finamente del balance de la SEC si lo deseamos.
            ratio = calcular_ebit_tev(ebit_anual, market_cap, deuda_total=0, caja=0)
            if ratio:
                resultados.append({
                    "Ticker": ticker,
                    "Empresa": nombre,
                    "EBIT": ebit_anual,
                    "Market_Cap": market_cap,
                    "EBIT_TEV": ratio
                })
                print(f"   -> EBIT/TEV calculado: {ratio:.4f}")
        else:
            print(f"   -> ⚠️ Faltan datos (EBIT o Market Cap) para {ticker}")
        
    if resultados:
        df_ranking = pd.DataFrame(resultados).sort_values(by="EBIT_TEV", ascending=False).reset_index(drop=True)
        print("\n" + "="*80)
        print("🏆 RANKING DE VALORACIÓN (EBIT / TEV) - DE MÁS BARATO A MÁS CARO")
        print("="*80)
        print(df_ranking[["Ticker", "Empresa", "EBIT_TEV"]].to_string(index=True))
        print("="*80)
    else:
        print("\n⚠️ No hay resultados de EBIT/TEV para mostrar.")