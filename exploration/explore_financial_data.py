from financial_data import (
    listar_empresas,
    listar_conceptos_por_palabra,
    obtener_dato_anual
)

from dic_financial_terms import CONCEPTOS_FINANCIEROS

## ==========================================================
#  1. DIAGNOSTICAR CONCEPTOS DE INGRESOS
## ==========================================================


def diagnosticar_conceptos_ingresos():

    empresas_configuradas = CONCEPTOS_FINANCIEROS["revenue"]

    empresas = [
    empresa
    for empresa in listar_empresas()
    if empresa["ticker"] in empresas_configuradas
]

    conceptos_configurados = CONCEPTOS_FINANCIEROS.get(
        "revenue", {}
    )

    print("\n" + "=" * 90)
    print("DIAGNÓSTICO DE CONCEPTOS DE INGRESOS")
    print("=" * 90)

    for empresa in empresas:

        ticker = empresa["ticker"]

        # Saltamos las empresas que ya tienen conceptos configurados.
        if ticker in conceptos_configurados:
            continue

        print(f"\n{'=' * 70}")
        print(f"EMPRESA: {ticker}")
        print("=" * 70)

        conceptos_encontrados = {}

        # Buscamos conceptos relacionados con ingresos y ventas.
        for palabra in ["Revenue", "Sales"]:

            registros = listar_conceptos_por_palabra(
                ticker=ticker,
                palabra=palabra,
                limite=10
            )

            for registro in registros:

                concepto = registro["concept"]

                conceptos_encontrados[concepto] = registro

        if not conceptos_encontrados:
            print("No se encontraron conceptos candidatos.")
            continue

        for concepto, registro in conceptos_encontrados.items():

            print(
                f"{concepto}\n"
                f"  Etiqueta: {registro['label']}\n"
                f"  Registros: {registro['numero_registros']}\n"
                f"  Última publicación: {registro['ultima_publicacion']}\n"
            )

## ==========================================================
# 2. PROBAR CONCEPTOS CANDIDATOS
## ==========================================================
def probar_conceptos_candidatos(fecha_corte="2026-11-15"):

    candidatos = {
        "BA": ["Revenues"],
        "CRM": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "CVX": ["Revenues"],
        "DIS": ["Revenues"],
        "DOW": ["Revenues"],
        "HD": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "HON": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "IBM": ["Revenues"],
        "JNJ": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "MCD": ["Revenues"],
        "MMM": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "MRK": ["Revenues"],
        "NKE": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "PG": ["Revenues"],
        "SHW": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "TRV": ["Revenues"],
        "UNH": ["Revenues"],
        "V": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "VZ": ["Revenues"],
        "WMT": ["RevenueFromContractWithCustomerExcludingAssessedTax"]
    }

    for ticker, conceptos in candidatos.items():

        print(f"\n{'=' * 70}")
        print(f"EMPRESA: {ticker}")
        print("=" * 70)

        encontrado = False

        for ejercicio in range(int(fecha_corte[:4]), 1989, -1):

            for concepto in conceptos:

                resultado = obtener_dato_anual(
                    ticker=ticker,
                    concepto=concepto,
                    ejercicio=ejercicio,
                    fecha_corte=fecha_corte
                )

                if resultado is not None:

                    print("Ejercicio:", ejercicio)
                    print("Ingresos:", resultado["value"])
                    print("Concepto:", resultado["concept"])
                    print(
                        "Periodo:",
                        resultado["start_date"],
                        "-",
                        resultado["end_date"]
                    )
                    print("Publicado:", resultado["filed_date"])

                    encontrado = True
                    break

            if encontrado:
                break

        if not encontrado:
            print("No se encontraron datos para el concepto candidato.")


## ==========================================================
# 3. COMPARAR CONCEPTOS DE INGRESOS TEMPORALES
## ==========================================================

def comparar_conceptos_ingresos(
    ticker,
    ejercicio,
    fecha_corte
):
    conceptos = [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax"
    ]

    print(f"\nEMPRESA: {ticker}")
    print(f"EJERCICIO: {ejercicio}")
    print("-" * 65)

    for concepto in conceptos:

        resultado = obtener_dato_anual(
            ticker=ticker,
            concepto=concepto,
            ejercicio=ejercicio,
            fecha_corte=fecha_corte
        )

        if resultado is None:
            print(f"{concepto}: Sin datos")
            continue

        print(f"\nConcepto: {concepto}")
        print(f"Valor: {resultado['value']:,.0f}")
        print(f"Periodo: {resultado['start_date']} - {resultado['end_date']}")
        print(f"Publicado: {resultado['filed_date']}")