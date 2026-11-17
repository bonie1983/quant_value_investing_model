
from datetime import datetime

from exploration.financial_data_queries import obtener_dato_anual
from financial_terms.dic_financial_terms import CONCEPTOS_FINANCIEROS


# ==========================================================
# OBTENER INGRESOS ANUALES / REVENUE
# ==========================================================

def obtener_ingresos(ticker, ejercicio, fecha_corte):

    """
    Obtiene los ingresos anuales de una empresa,
    respetando la fecha de corte y la prioridad
    de conceptos definida en dic_financial_terms.py.
    """

    # Validar y normalizar ticker
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError(
            "El ticker debe ser una cadena de texto no vacía."
        )

    ticker = ticker.strip().upper()

    # Validar fecha de corte
    try:
        datetime.strptime(fecha_corte, "%Y-%m-%d")
    except (TypeError, ValueError):
        raise ValueError(
            "La fecha de corte debe tener formato YYYY-MM-DD"
        )

    # Obtener conceptos configurados para la empresa
    conceptos_por_empresa = CONCEPTOS_FINANCIEROS.get("revenue", {})
    conceptos = conceptos_por_empresa.get(ticker, [])

    if not conceptos:
        raise ValueError(
            f"No hay conceptos de ingresos configurados para {ticker}"
        )

    # Probar conceptos siguiendo el orden de prioridad
    for concepto in conceptos:

        resultado = obtener_dato_anual(
            ticker=ticker,
            concepto=concepto,
            ejercicio=ejercicio,
            fecha_corte=fecha_corte
        )

        if resultado is None:
            continue

        # Validar ejercicio fiscal
        if int(resultado["end_date"][:4]) != int(ejercicio):
            continue

        # Validar duración anual
        if not 329 <= resultado["period_days"] <= 379:
            continue

        # Validar fecha de publicación
        if resultado["filed_date"] > fecha_corte:
            continue

        # Validar formulario
        if resultado["form"] != "10-K":
            continue

        return resultado

    return None
