
from datetime import datetime

from financial_data import (
    obtener_dato_anual,
    obtener_ingresos
)

from dic_financial_terms import CONCEPTOS_FINANCIEROS


# ==========================================================
# 1. CONFIGURACIÓN
# ==========================================================

FECHA_CORTE = "2026-11-15"

CONCEPTO = "OperatingIncomeLoss"

TICKERS = sorted(
    CONCEPTOS_FINANCIEROS["revenue"].keys()
)


# ==========================================================
# 2. IDENTIFICAR EL ÚLTIMO EJERCICIO DISPONIBLE
# ==========================================================

def obtener_ultimo_ejercicio(ticker):

    anio_maximo = int(FECHA_CORTE[:4])

    for ejercicio in range(anio_maximo, 1999, -1):

        resultado = obtener_ingresos(
            ticker=ticker,
            ejercicio=ejercicio,
            fecha_corte=FECHA_CORTE
        )

        if resultado is not None:
            return ejercicio

    return None


# ==========================================================
# 3. VALIDAR OPERATING INCOME
# ==========================================================

def validar_operating_income():

    correctas = 0
    sin_datos = 0
    errores = 0

    print("=" * 90)
    print("VALIDACIÓN GENERAL DE OPERATING INCOME")
    print(f"Concepto SEC: {CONCEPTO}")
    print(f"Fecha de corte: {FECHA_CORTE}")
    print(f"Empresas encontradas: {len(TICKERS)}")
    print("=" * 90)

    print("\nRESULTADOS POR EMPRESA")
    print("-" * 90)

    for ticker in TICKERS:

        try:

            ejercicio = obtener_ultimo_ejercicio(ticker)

            if ejercicio is None:
                sin_datos += 1
                print(f"{ticker:8} | Sin ingresos anuales disponibles")
                continue

            resultado = obtener_dato_anual(
                ticker=ticker,
                concepto=CONCEPTO,
                ejercicio=ejercicio,
                fecha_corte=FECHA_CORTE
            )

            if resultado is None:

                sin_datos += 1

                print(
                    f"{ticker:8} | {ejercicio} | "
                    "SIN DATO OPERATING INCOME"
                )

                continue

            correctas += 1

            print(
                f"{ticker:8} | "
                f"{ejercicio} | "
                f"{resultado['value']:20,.2f} | "
                f"{resultado['filed_date']} | OK"
            )

        except Exception as error:

            errores += 1

            print(
                f"{ticker:8} | ERROR | {error}"
            )

    print("\n" + "=" * 90)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 90)

    print(f"Empresas analizadas:       {len(TICKERS)}")
    print(f"Correctas:                 {correctas}")
    print(f"Sin datos anuales:         {sin_datos}")
    print(f"Errores:                   {errores}")


# ==========================================================
# 4. EJECUCIÓN
# ==========================================================

if __name__ == "__main__":
    validar_operating_income()
