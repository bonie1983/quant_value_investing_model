
from datetime import datetime

from exploration.financial_data_queries import (
    listar_empresas,
    listar_conceptos_por_palabra,
    obtener_dato_anual
)

from financial_terms.dic_financial_terms import (
    CONCEPTOS_FINANCIEROS
)


# ==========================================================
# VALIDAR FECHA DE CORTE
# ==========================================================

def validar_fecha_corte(fecha_corte):

    """
    Comprueba que la fecha de corte tenga formato YYYY-MM-DD.
    """

    try:
        fecha = datetime.strptime(fecha_corte, "%Y-%m-%d")

    except (TypeError, ValueError):
        raise ValueError(
            "La fecha de corte debe tener el formato YYYY-MM-DD."
        )

    return fecha


# ==========================================================
# 1. DIAGNOSTICAR CONCEPTOS DE INGRESOS
# ==========================================================

def diagnosticar_conceptos_ingresos():

    """
    Identifica empresas que todavía no tienen conceptos de
    ingresos configurados y busca posibles conceptos SEC.
    """

    empresas_configuradas = CONCEPTOS_FINANCIEROS.get(
        "revenue", {}
    )

    empresas = [
        empresa
        for empresa in listar_empresas()
        if empresa["ticker"] not in empresas_configuradas
    ]

    print("\n" + "=" * 90)
    print("DIAGNÓSTICO DE CONCEPTOS DE INGRESOS")
    print("=" * 90)

    if not empresas:
        print(
            "Todas las empresas tienen conceptos de ingresos configurados."
        )
        return

    for empresa in empresas:

        ticker = empresa["ticker"]

        print(f"\nEMPRESA: {ticker}")
        print("-" * 70)

        conceptos_encontrados = {}

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


# ==========================================================
# 2. PROBAR CONCEPTOS CANDIDATOS
# ==========================================================

def probar_conceptos_candidatos(fecha_corte="2026-11-15"):

    """
    Comprueba los conceptos de ingresos configurados para cada
    empresa y busca el ejercicio más reciente disponible.

    Respeta la fecha de corte para evitar utilizar información
    publicada posteriormente.
    """

    fecha = validar_fecha_corte(fecha_corte)

    candidatos = CONCEPTOS_FINANCIEROS.get("revenue", {})

    if not candidatos:
        print("No hay conceptos de ingresos configurados.")
        return

    for ticker, conceptos in candidatos.items():

        print(f"\n{'=' * 70}")
        print(f"EMPRESA: {ticker}")
        print("=" * 70)

        encontrado = False

        for ejercicio in range(fecha.year, 1988, -1):

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
            print(
                "No se encontraron datos para los conceptos configurados."
            )


# ==========================================================
# 3. COMPARAR CONCEPTOS DE INGRESOS
# ==========================================================

def comparar_conceptos_ingresos(
    ticker,
    ejercicio,
    fecha_corte
):

    """
    Compara los principales conceptos SEC de ingresos para
    una empresa y ejercicio determinados.
    """

    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("El ticker no puede estar vacío.")

    ticker = ticker.strip().upper()

    validar_fecha_corte(fecha_corte)

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

        print(
            f"Periodo: {resultado['start_date']} "
            f"- {resultado['end_date']}"
        )

        print(f"Publicado: {resultado['filed_date']}")


# ==========================================================
# EJECUCIÓN PRINCIPAL
# ==========================================================

if __name__ == "__main__":

    resultados = listar_conceptos_por_palabra(
        ticker="CVX",
        palabra="Revenue",
        limite=10
    )

    for resultado in resultados:
        print(resultado)
