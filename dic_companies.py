# dic_companies.py
# Este módulo contiene las funciones para obtener o actualizar los universos y índices (S&P 500, Dow Jones, Nasdaq 100)

import os
import pandas as pd

# Directorio de caché local
CACHE_DIR = "data_cache"

def obtener_o_actualizar_universo(nombre_archivo: str, url_github: str) -> pd.DataFrame:
    """
    Función genérica para comprobar si el archivo CSV local de un índice existe. 
    Si no existe, lo descarga desde el repositorio de GitHub indicado, lo guarda 
    en la caché y lo devuelve como DataFrame.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    ruta_csv = os.path.join(CACHE_DIR, nombre_archivo)
    
    if os.path.exists(ruta_csv):
        print(f"Cargando {nombre_archivo} desde el archivo local en caché...")
        return pd.read_csv(ruta_csv)
    else:
        print(f"Descargando {nombre_archivo} desde GitHub...")
        try:
            df_universo = pd.read_csv(url_github)
            df_universo.to_csv(ruta_csv, index=False)
            print(f"¡{nombre_archivo} descargado y guardado con éxito en {CACHE_DIR}/!")
            return df_universo
        except Exception as e:
            print(f"Error al descargar {nombre_archivo}: {e}")
            return pd.DataFrame()

# ---------------------------------------------------------------------------
# 1. UNIVERSOS E ÍNDICES (URLs de fuentes estables en GitHub)
# ---------------------------------------------------------------------------

def obtener_sp500():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    return obtener_o_actualizar_universo("universo_sp500.csv", url)

def obtener_nasdaq_listed():
    # Repositorio público con los componentes limpios del Nasdaq 100
    url = "https://raw.githubusercontent.com/datasets/nasdaq-listings/master/data/nasdaq-listed.csv" 
    # Nota: Si prefieres una lista estricta del Nasdaq 100, puedes usar repos específicos o filtrar por capitalización.
    return obtener_o_actualizar_universo("universo_nasdaq_listed.csv", url)

# 2. Diccionario de Pruebas Rápidas
EMPRESAS_PRUEBA = {
    "AAPL": {"nombre": "Apple Inc.", "cik": "0000320193"},
    "BA":   {"nombre": "Boeing Co.", "cik": "0000012927"},
    "CAT":  {"nombre": "Caterpillar Inc.", "cik": "0000018230"},
}

# 3. Dow Jones Industrial Average (Las 28 empresas en orden alfabético estricto)

# ---------------------------------------------------------------------------
# UNIVERSO INICIAL: DOW JONES (28 EMPRESAS DE NUESTRO DICCIONARIO)
# ---------------------------------------------------------------------------


def obtener_empresa(ticker: str) -> dict:
    """
    Devuelve la información de una empresa a partir de su ticker.
    """
    return EMPRESAS_DOWJONES.get(ticker.upper())


def obtener_universo_dow() -> pd.DataFrame:
    """
    Convierte el diccionario del Dow Jones en un DataFrame.
    """
    return pd.DataFrame.from_dict(
        EMPRESAS_DOWJONES,
        orient="index"
    ).reset_index(drop=True)


def obtener_empresas_por_sector(sector: str) -> pd.DataFrame:
    """
    Devuelve las empresas pertenecientes a un sector.
    """
    df = obtener_universo_dow()

    return df[df["sector"] == sector].reset_index(drop=True)


def obtener_tickers() -> list:
    """
    Devuelve la lista de tickers del universo.
    """
    return list(EMPRESAS_DOWJONES.keys())

EMPRESAS_DOWJONES = {

    "AMGN": {
        "ticker": "AMGN",
        "nombre": "Amgen Inc.",
        "cik": "0000318154",
        "sector": "Healthcare",
        "industria": "Biotechnology",
        "indice": ["Dow Jones"],
        "exchange": "NASDAQ"
    },

    "AXP": {
        "ticker": "AXP",
        "nombre": "American Express Co.",
        "cik": "0000004962",
        "sector": "Financials",
        "industria": "Consumer Finance and Payments",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "BA": {
        "ticker": "BA",
        "nombre": "Boeing Co.",
        "cik": "0000012927",
        "sector": "Industrials",
        "industria": "Aerospace and Defense",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "CAT": {
        "ticker": "CAT",
        "nombre": "Caterpillar Inc.",
        "cik": "0000018230",
        "sector": "Industrials",
        "industria": "Construction and Mining Machinery",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "CRM": {
        "ticker": "CRM",
        "nombre": "Salesforce Inc.",
        "cik": "0001108524",
        "sector": "Information Technology",
        "industria": "Application Software",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "CSCO": {
        "ticker": "CSCO",
        "nombre": "Cisco Systems Inc.",
        "cik": "0000858877",
        "sector": "Information Technology",
        "industria": "Communications Equipment",
        "indice": ["Dow Jones"],
        "exchange": "NASDAQ"
    },

    "CVX": {
        "ticker": "CVX",
        "nombre": "Chevron Corp.",
        "cik": "0000093410",
        "sector": "Energy",
        "industria": "Integrated Oil and Gas",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "DIS": {
        "ticker": "DIS",
        "nombre": "Walt Disney Co.",
        "cik": "0001744489",
        "sector": "Communication Services",
        "industria": "Entertainment and Media",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "DOW": {
        "ticker": "DOW",
        "nombre": "Dow Inc.",
        "cik": "0001751788",
        "sector": "Materials",
        "industria": "Chemicals",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "GS": {
        "ticker": "GS",
        "nombre": "Goldman Sachs Group Inc.",
        "cik": "0000886982",
        "sector": "Financials",
        "industria": "Capital Markets and Investment Banking",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "HD": {
        "ticker": "HD",
        "nombre": "Home Depot Inc.",
        "cik": "0000354950",
        "sector": "Consumer Discretionary",
        "industria": "Home Improvement Retail",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "HON": {
        "ticker": "HON",
        "nombre": "Honeywell International Inc.",
        "cik": "0000773840",
        "sector": "Industrials",
        "industria": "Industrial Automation and Technology",
        "indice": ["Dow Jones"],
        "exchange": "NASDAQ"
    },

    "IBM": {
        "ticker": "IBM",
        "nombre": "International Business Machines Corp.",
        "cik": "0000051143",
        "sector": "Information Technology",
        "industria": "IT Services and Software",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "JNJ": {
        "ticker": "JNJ",
        "nombre": "Johnson & Johnson",
        "cik": "0000200406",
        "sector": "Healthcare",
        "industria": "Pharmaceuticals and Medical Technology",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "JPM": {
        "ticker": "JPM",
        "nombre": "JPMorgan Chase & Co.",
        "cik": "0000019617",
        "sector": "Financials",
        "industria": "Banking",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "KO": {
        "ticker": "KO",
        "nombre": "Coca-Cola Co.",
        "cik": "0000021344",
        "sector": "Consumer Staples",
        "industria": "Non-Alcoholic Beverages",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "MCD": {
        "ticker": "MCD",
        "nombre": "McDonald's Corp.",
        "cik": "0000063908",
        "sector": "Consumer Discretionary",
        "industria": "Restaurants",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "MMM": {
        "ticker": "MMM",
        "nombre": "3M Co.",
        "cik": "0000066740",
        "sector": "Industrials",
        "industria": "Diversified Industrial Products",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "MRK": {
        "ticker": "MRK",
        "nombre": "Merck & Co. Inc.",
        "cik": "0000310158",
        "sector": "Healthcare",
        "industria": "Pharmaceuticals",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "MSFT": {
        "ticker": "MSFT",
        "nombre": "Microsoft Corp.",
        "cik": "0000789019",
        "sector": "Information Technology",
        "industria": "Software and Cloud Computing",
        "indice": ["Dow Jones"],
        "exchange": "NASDAQ"
    },

    "NKE": {
        "ticker": "NKE",
        "nombre": "Nike Inc.",
        "cik": "0000320187",
        "sector": "Consumer Discretionary",
        "industria": "Apparel and Footwear",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "PG": {
        "ticker": "PG",
        "nombre": "Procter & Gamble Co.",
        "cik": "0000080424",
        "sector": "Consumer Staples",
        "industria": "Household and Personal Products",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "SHW": {
        "ticker": "SHW",
        "nombre": "Sherwin-Williams Co.",
        "cik": "0000089800",
        "sector": "Materials",
        "industria": "Specialty Chemicals and Paints",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "TRV": {
        "ticker": "TRV",
        "nombre": "Travelers Cos. Inc.",
        "cik": "0000086312",
        "sector": "Financials",
        "industria": "Property and Casualty Insurance",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "UNH": {
        "ticker": "UNH",
        "nombre": "UnitedHealth Group Inc.",
        "cik": "0000731766",
        "sector": "Healthcare",
        "industria": "Managed Healthcare",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "V": {
        "ticker": "V",
        "nombre": "Visa Inc.",
        "cik": "0001403161",
        "sector": "Financials",
        "industria": "Payment Networks",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "VZ": {
        "ticker": "VZ",
        "nombre": "Verizon Communications Inc.",
        "cik": "0000732712",
        "sector": "Communication Services",
        "industria": "Telecommunications",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    },

    "WMT": {
        "ticker": "WMT",
        "nombre": "Walmart Inc.",
        "cik": "0000104169",
        "sector": "Consumer Staples",
        "industria": "Retail",
        "indice": ["Dow Jones"],
        "exchange": "NYSE"
    }
}

# ---------------------------------------------------------------------------
# FUNCIONES DE VALIDACIÓN DEL UNIVERSO
# ---------------------------------------------------------------------------

def validar_universo(universo: dict) -> bool:
    """
    Comprueba que todas las empresas tienen los campos obligatorios.
    """

    campos_obligatorios = [
        "ticker",
        "nombre",
        "cik",
        "sector",
        "industria",
        "indice",
        "exchange"
    ]

    errores = []

    for ticker, info in universo.items():

        for campo in campos_obligatorios:
            if campo not in info or info[campo] in (None, "", []):
                errores.append(f"{ticker}: falta {campo}")

        if info.get("ticker") != ticker:
            errores.append(f"{ticker}: ticker inconsistente")

        if info.get("cik") and len(info["cik"]) != 10:
            errores.append(f"{ticker}: CIK incorrecto")

    if errores:
        print("\nERRORES EN EL UNIVERSO:")
        for error in errores:
            print(f"- {error}")
        return False

    print("\nUniverso validado correctamente.")
    return True



# ---------------------------------------------------------------------------
# BLOQUE DE PRUEBA INDEPENDIENTE
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("\n--- UNIVERSO DOW JONES ---")

    df_dow = obtener_universo_dow()

    print(df_dow.to_string(index=False))

    print("\n--- RESUMEN DEL UNIVERSO ---")

    print(f"Total empresas: {len(df_dow)}")

    print("\nEmpresas por sector:")

    print(
        df_dow["sector"]
        .value_counts()
        .to_string()
    )

    print("\n--- PRUEBA DE CONSULTA ---")

    empresa = obtener_empresa("MSFT")

    print(empresa)

    print("\n--- EMPRESAS DEL SECTOR FINANCIALS ---")

    df_financials = obtener_empresas_por_sector("Financials")

    print(df_financials[["ticker", "nombre", "industria"]].to_string(index=False))

    validar_universo(EMPRESAS_DOWJONES)
