# filters_fun.py
# Módulo para calcular los filtros de seguridad (Paso 1: Manipulación contable)

import os
import json
import pandas as pd

# Importamos el diccionario de prueba desde tu archivo externo
from dic_companies import EMPRESAS_DOWJONES

CACHE_DIR = "data_cache"

def extraer_partida_sec(ticker: str, conceptos: list) -> float:
    """
    Función genérica para buscar la partida anual (10-K) más reciente en el JSON de la SEC.
    """
    cache_file = os.path.join(CACHE_DIR, f"{ticker.upper()}_sec.json")
    if not os.path.exists(cache_file):
        print(f"[{ticker}] No se encontró el archivo caché de la SEC.")
        return None
        
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        units = data.get("facts", {}).get("us-gaap", {})
        
        for concepto in conceptos:
            if concepto in units:
                datos_concepto = units[concepto]["units"]
                # Buscar en la unidad USD
                if "USD" in datos_concepto:
                    registros = datos_concepto["USD"]
                    anuales = [x for x in registros if x.get("form") == "10-K"]
                    if anuales:
                        anuales_ordenados = sorted(anuales, key=lambda x: x.get("end", ""), reverse=True)
                        return anuales_ordenados[0].get("val")
        return None
    except Exception as e:
        print(f"Error procesando partidas para {ticker}: {e}")
        return None

# ----------------------------------------------------------------------------------------------------
# Calcular filtro sta de manipulación contable (Accruals Totales) y snoa (Accruals Netos de Operación)
# ----------------------------------------------------------------------------------------------------

def calcular_sta(ticker: str) -> float:
    """
    Calcula los Accruals Totales (STA): (Net Income - Operating Cash Flow) / Total Assets
    """
    print(f"[{ticker}] Calculando filtro STA (Accruals Totales)...")
    
    # 1. Beneficio Neto (Net Income)
    conceptos_ni = ["NetIncomeLoss", "ProfitLoss"]
    net_income = extraer_partida_sec(ticker, conceptos_ni)
    
    # 2. Flujo de Caja Operativo (Operating Cash Flow)
    conceptos_ocf = ["NetCashProvidedByUsedInOperatingActivities", "OperatingCashFlow"]
    ocf = extraer_partida_sec(ticker, conceptos_ocf)
    
    # 3. Activos Totales (Total Assets)
    conceptos_assets = ["Assets"]
    total_assets = extraer_partida_sec(ticker, conceptos_assets)
    
    # Validar que tengamos todos los datos necesarios
    if net_income is None or ocf is None or total_assets is None or total_assets == 0:
        print(f"[{ticker}] ⚠️ Faltan datos contables clave para calcular STA.")
        return None
        
    # Cálculo de Accruals Totales (¡Aquí faltaba el operador '-')
    sta = (net_income - ocf) / total_assets
    return sta

# ---------------------------------------------------------------------------
# Calcular filtro snoa de manipulación contable (Accruals Netos de Operación)
# ---------------------------------------------------------------------------

def calcular_snoa(ticker: str) -> float:
    """
    Calcula los Accruals Netos de Operación (SNOA) con un diccionario XBRL ampliado
    para evitar que devuelva ceros en empresas con nomenclaturas distintas.
    """
    print(f"[{ticker}] Calculando filtro SNOA (Accruals Netos de Operación)...")
    
    # 1. Activos Totales (Estándar en casi todas: "Assets")
    total_assets = extraer_partida_sec(ticker, ["Assets"])
    
    # 2. Caja y equivalentes (Variantes amplias de la SEC)
    cash = extraer_partida_sec(ticker, [
        "CashAndCashEquivalentsAtCarryingValue", 
        "Cash", 
        "CashAndCashEquivalentsPeriodIncreaseDecrease",
        "CashCashEquivalentsAndShortTermInvestments"
    ]) or 0
    
    # 3. Pasivos Totales (Variantes comunes: "Liabilities" o "LiabilitiesCurrent" + "LiabilitiesNoncurrent")
    total_liabilities = extraer_partida_sec(ticker, ["Liabilities"])
    if total_liabilities is None:
        # Si no existe la partida de pasivos totales directa, intentamos sumar corriente y no corriente
        pasivo_corr = extraer_partida_sec(ticker, ["LiabilitiesCurrent"]) or 0
        pasivo_no_corr = extraer_partida_sec(ticker, ["LiabilitiesNoncurrent"]) or 0
        if pasivo_corr > 0 or pasivo_no_corr > 0:
            total_liabilities = pasivo_corr + pasivo_no_corr

    # 4. Deuda Total (Variantes amplias de deuda a corto y largo plazo)
    long_term_debt = extraer_partida_sec(ticker, [
        "LongTermDebtNoncurrent", 
        "LongTermDebtAndFinanceLeaseObligations",
        "LongTermDebt",
        "BondsPayable"
    ]) or 0
    
    short_term_debt = extraer_partida_sec(ticker, [
        "ShortTermBorrowings", 
        "DebtCurrent",
        "CommercialPaper",
        "LongTermDebtCurrent"
    ])or 0
    
    total_debt = long_term_debt + short_term_debt
    
    # Validaciones de seguridad
    if total_assets is None or total_assets == 0:
        print(f"[{ticker}] ⚠️ No se pudieron obtener los Activos Totales para SNOA.")
        return None
        
    if total_liabilities is None:
        print(f"[{ticker}] ⚠️ No se pudieron obtener los Pasivos Totales para SNOA.")
        return None
        
    # Cálculo de Activos Operativos y Pasivos Operativos
    operating_assets = total_assets - cash
    operating_liabilities = total_liabilities - total_debt
    
    # SNOA normalizado por los Activos Totales
    snoa = (operating_assets - operating_liabilities) / total_assets
    return snoa

# --------------------------------------------------------------------------------
# Función para extraer la serie anual de métricas contables (10-K) y calcular PMAN
# --------------------------------------------------------------------------------

def extraer_serie_anual_sec(ticker: str, conceptos: list) -> list:
    """
    Extrae los valores anuales (10-K) de ejercicios distintos ordenados del más reciente al más antiguo,
    evitando duplicados causados por cifras comparativas de años anteriores.
    """
    cache_file = os.path.join(CACHE_DIR, f"{ticker.upper()}_sec.json")
    if not os.path.exists(cache_file):
        return []
        
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        units = data.get("facts", {}).get("us-gaap", {})
        
        for concepto in conceptos:
            if concepto in units:
                datos_concepto = units[concepto]["units"]
                if "USD" in datos_concepto:
                    registros = datos_concepto["USD"]
                    anuales = [x for x in registros if x.get("form") == "10-K" and x.get("fp") == "FY"]
                    
                    # Eliminamos duplicados quedándonos con un único valor por fecha de cierre ('end')
                    valores_por_fecha = {}
                    for r in anuales:
                        fecha_fin = r.get("end")
                        if fecha_fin:
                            # Sobrescribimos para quedarnos con el dato reportado más recientemente para ese ejercicio
                            valores_por_fecha[fecha_fin] = r.get("val")
                    
                    if len(valores_por_fecha) >= 2:
                        fechas_ordenadas = sorted(valores_por_fecha.keys(), reverse=True)
                        return [valores_por_fecha[fechas_ordenadas[0]], valores_por_fecha[fechas_ordenadas[1]]]
        return []
    except Exception as e:
        print(f"Error extrayendo serie anual para {ticker}: {e}")
        return []

def calcular_pman(ticker: str) -> float:
    """
    Calcula el indicador de riesgo de fraude (PMAN / DSRI simplificado)
    con un abanico ampliado de etiquetas SEC (incluyendo servicios, franquicias y banca).
    """
    print(f"[{ticker}] Calculando filtro PMAN (Riesgo de Fraude)...")
    
    # 1. Cuentas por Cobrar con múltiples sinónimos amplios
    ar_serie = extraer_serie_anual_sec(ticker, [
        "AccountsReceivableNetCurrent", 
        "ReceivablesNetCurrent", 
        "AccountsReceivable",
        "AccountsAndOtherReceivablesNetCurrent",
        "NontradeReceivablesCurrent"
    ])
    
    # 2. Ventas / Ingresos con múltiples sinónimos (industriales, servicios, franquicias)
    rev_serie = extraer_serie_anual_sec(ticker, [
        "Revenues", 
        "SalesRevenueNet", 
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueServicesNet",
        "RevenuesNetOfInterestExpense",
        "NoninterestIncome"
    ])
    
    # Validar que tengamos datos de ambos años para comparar
    if len(ar_serie) < 2 or len(rev_serie) < 2:
        print(f"[{ticker}] ⚠️ Histórico insuficiente para calcular PMAN.")
        return None
        
    ar_t, ar_t1 = ar_serie[0], ar_serie[1]
    rev_t, rev_t1 = rev_serie[0], rev_serie[1]
    
    if ar_t1 is None or rev_t1 is None or ar_t1 == 0 or rev_t1 == 0 or ar_t is None or rev_t is None:
        print(f"[{ticker}] ⚠️ Datos nulos o cero en la serie temporal de PMAN.")
        return None
        
    # DSRI (Days Sales in Receivables Index): (AR_t / Rev_t) / (AR_t-1 / Rev_t-1)
    dsri_t = ar_t / rev_t
    dsri_t1 = ar_t1 / rev_t1
    
    dsri = dsri_t / dsri_t1 if dsri_t1 != 0 else None
    return dsri

# ---------------------------------------------------------------------------
# Función para calcular un indicador simplificado de Dificultad Financiera / Bancarrota (PFD / Z-Score base)
# ---------------------------------------------------------------------------

def calcular_pfd(ticker: str) -> float:
    """
    Calcula un indicador simplificado de Dificultad Financiera / Bancarrota (PFD / Z-Score base):
    Combina liquidez (Capital de Trabajo), rentabilidad histórica (Utilidades Retenidas) 
    y rendimiento operativo (EBIT) normalizados por los Activos Totales.
    """
    print(f"[{ticker}] Calculando filtro PFD (Riesgo de Quiebra)...")
    
    # 1. Activos Totales y Pasivos Totales (o Corrientes)
    total_assets = extraer_partida_sec(ticker, ["Assets"])
    current_assets = extraer_partida_sec(ticker, ["AssetsCurrent"])
    current_liabilities = extraer_partida_sec(ticker, ["LiabilitiesCurrent"])
    
    # 2. Utilidades Retenidas (Retained Earnings)
    retained_earnings = extraer_partida_sec(ticker, ["RetainedEarningsAccumulatedDeficit", "RetainedEarnings"])
    
    # 3. EBIT (Earnings Before Interest and Taxes)
    ebit = extraer_partida_sec(ticker, ["OperatingIncomeLoss", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeignMinorityInterestAndIncomeLossFromEquityMethodInvestments"])
    
    if total_assets is None or total_assets == 0:
        print(f"[{ticker}] ⚠️ Faltan Activos Totales para calcular PFD.")
        return None
        
    # Asignar ceros por seguridad si alguna partida menor no está explícitamente desglosada
    ca = current_assets or 0
    cl = current_liabilities or 0
    re = retained_earnings or 0
    eb = ebit or 0
    
    # Componentes del Altman Z-Score simplificado:
    # A = Capital de Trabajo / Activos Totales
    working_capital = ca - cl
    a = working_capital / total_assets
    
    # B = Utilidades Retenidas / Activos Totales
    b = re / total_assets
    
    # C = EBIT / Activos Totales
    c = eb / total_assets
    
    # PFD Score ponderado base (un valor global de Z-Score simplificado)
    # Una empresa sana suele tener un Z-score > 1.81 o 2.6; por debajo de 1.1 entra en zona de peligro de quiebra.
    pfd_score = (1.2 * a) + (1.4 * b) + (3.3 * c)
    
    return pfd_score


# ---------------------------------------------------------------------------
# BLOQUE DE PRUEBA PRINCIPAL STA, SNOA, PMAN, PFD)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n--- Evaluando Filtros de Seguridad del Paso 1 al Completo ---")
    
    resultados_filtros = []
    
    # Nota: Usa EMPRESAS_PRUEBA o EMPRESAS_DOWJONES según lo tengas importado
    for ticker, info in EMPRESAS_DOWJONES.items():
        nombre = info["nombre"]
        print(f"\nProcesando filtros de seguridad para: {nombre} ({ticker})...")
        
        sta_valor = calcular_sta(ticker)
        snoa_valor = calcular_snoa(ticker)
        pman_valor = calcular_pman(ticker)
        pfd_valor = calcular_pfd(ticker)
        
        # Criterios de alerta estándar para el MVP
        alerta_sta = sta_valor is not None and sta_valor > 0.05
        alerta_snoa = snoa_valor is not None and snoa_valor > 0.75 
        alerta_pman = pman_valor is not None and pman_valor > 1.30
        alerta_pfd = pfd_valor is not None and pfd_valor < 1.10 # Zona de peligro de quiebra (Z-Score bajo)
        
        estado = "🚩 Alerta (Riesgo / Insolvencia)" if (alerta_sta or alerta_snoa or alerta_pman or alerta_pfd) else "✅ Saludable"
        
        resultados_filtros.append({
            "Ticker": ticker,
            "Empresa": nombre,
            "STA": f"{sta_valor:.4f}" if sta_valor is not None else "N/A",
            "SNOA": f"{snoa_valor:.4f}" if snoa_valor is not None else "N/A",
            "PMAN": f"{pman_valor:.4f}" if pman_valor is not None else "N/A",
            "PFD": f"{pfd_valor:.4f}" if pfd_valor is not None else "N/A",
            "Filtro_Seguridad": estado
        })

    # Mostramos los resultados en un DataFrame limpio al finalizar el bucle
    if resultados_filtros:
        df_filtros = pd.DataFrame(resultados_filtros)
        print("\n" + "="*105)
        print("🛡️ RESUMEN DEL PASO 1: BLOQUE COMPLETO DE SEGURIDAD (CALIDAD + FRAUDE + QUIEBRA)")
        print("="*105)
        print(df_filtros.to_string(index=False))
        print("="*105)
    else:
        print("\n⚠️ No hay resultados de filtros para mostrar.")
