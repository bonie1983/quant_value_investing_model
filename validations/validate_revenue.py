
from datetime import datetime

from financial_terms.dic_financial_terms import (
    CONCEPTOS_FINANCIEROS
)

from financial_terms.revenue import obtener_ingresos

from exploration.financial_data_queries import (
    listar_empresas
)


# ==========================================================
# VALIDAR INGRESOS DE TODAS LAS EMPRESAS
# ==========================================================

def validar_ingresos_todas_empresas(
    fecha_corte="2026-11-15",
    ejercicio_minimo=1990
):

    """
    Valida los ingresos de todas las empresas de la base de datos.

    Busca el último ejercicio anual disponible para cada empresa,
    respetando la fecha de corte.

    Estados posibles:
    - OK: ingresos encontrados.
    - SIN_CONFIGURAR: empresa sin conceptos configurados.
    - SIN_DATOS: no se encontraron datos anuales.
    - ERROR: se produjo un error durante la consulta.
    """

    # ------------------------------------------------------
    # VALIDAR PARÁMETROS
    # ------------------------------------------------------

    try:
        fecha = datetime.strptime(fecha_corte, "%Y-%m-%d")

    except (TypeError, ValueError):
        raise ValueError(
            "La fecha de corte debe tener el formato YYYY-MM-DD."
        )

    if (
        not isinstance(ejercicio_minimo, int)
        or isinstance(ejercicio_minimo, bool)
        or ejercicio_minimo < 1900
        or ejercicio_minimo > fecha.year
    ):
        raise ValueError("El ejercicio mínimo no es válido.")

    empresas_configuradas = CONCEPTOS_FINANCIEROS.get(
        "revenue", {}
    )

    # Recuperamos todas las empresas, incluidas las que
    # todavía no tienen conceptos configurados.
    empresas = listar_empresas()

    resultados = []

    ultimo_ejercicio = fecha.year

    print("\n" + "=" * 90)
    print("VALIDACIÓN GENERAL DE INGRESOS")
    print(f"Fecha de corte: {fecha_corte}")
    print(f"Empresas encontradas: {len(empresas)}")
    print("=" * 90)

    # ------------------------------------------------------
    # PROCESAR EMPRESAS
    # ------------------------------------------------------

    for empresa in empresas:

        ticker = empresa["ticker"]

        resultado_encontrado = None
        ejercicio_encontrado = None
        estado = "SIN_DATOS"
        error = None

        # Comprobar si la empresa tiene conceptos configurados.
        if ticker not in empresas_configuradas:

            resultados.append({
                "ticker": ticker,
                "ejercicio": None,
                "ingresos": None,
                "concepto": None,
                "periodo_inicio": None,
                "periodo_fin": None,
                "fecha_publicacion": None,
                "formulario": None,
                "estado": "SIN_CONFIGURAR",
                "error": None
            })

            continue

        # Buscar desde el ejercicio más reciente hacia atrás.
        for ejercicio in range(
            ultimo_ejercicio,
            ejercicio_minimo - 1,
            -1
        ):

            try:

                resultado = obtener_ingresos(
                    ticker=ticker,
                    ejercicio=ejercicio,
                    fecha_corte=fecha_corte
                )

                if resultado is not None:

                    resultado_encontrado = resultado
                    ejercicio_encontrado = ejercicio
                    estado = "OK"

                    break

            except Exception as e:

                # Registramos el error para poder investigarlo.
                error = f"{type(e).__name__}: {e}"
                estado = "ERROR"

                break

        # --------------------------------------------------
        # GUARDAR RESULTADOS
        # --------------------------------------------------

        if resultado_encontrado is not None:

            resultados.append({
                "ticker": ticker,
                "ejercicio": ejercicio_encontrado,
                "ingresos": resultado_encontrado["value"],
                "concepto": resultado_encontrado["concept"],
                "periodo_inicio": resultado_encontrado["start_date"],
                "periodo_fin": resultado_encontrado["end_date"],
                "fecha_publicacion": resultado_encontrado["filed_date"],
                "formulario": resultado_encontrado["form"],
                "estado": estado,
                "error": None
            })

        else:

            resultados.append({
                "ticker": ticker,
                "ejercicio": None,
                "ingresos": None,
                "concepto": None,
                "periodo_inicio": None,
                "periodo_fin": None,
                "fecha_publicacion": None,
                "formulario": None,
                "estado": estado,
                "error": error
            })

    # ======================================================
    # MOSTRAR RESULTADOS
    # ======================================================

    print("\nRESULTADOS POR EMPRESA")
    print("-" * 90)

    for resultado in resultados:

        print(
            f"{resultado['ticker']:8} | "
            f"{str(resultado['ejercicio']):6} | "
            f"{str(resultado['ingresos']):20} | "
            f"{resultado['estado']}"
        )

        if resultado["error"] is not None:
            print(f"  Error: {resultado['error']}")

    # ======================================================
    # RESUMEN DE VALIDACIÓN
    # ======================================================

    total_ok = sum(
        r["estado"] == "OK" for r in resultados
    )

    total_sin_configurar = sum(
        r["estado"] == "SIN_CONFIGURAR" for r in resultados
    )

    total_sin_datos = sum(
        r["estado"] == "SIN_DATOS" for r in resultados
    )

    total_errores = sum(
        r["estado"] == "ERROR" for r in resultados
    )

    print("\n" + "=" * 90)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 90)

    print(f"Empresas analizadas:       {len(resultados)}")
    print(f"Correctas:                 {total_ok}")
    print(f"Sin configurar:            {total_sin_configurar}")
    print(f"Sin datos anuales:         {total_sin_datos}")
    print(f"Errores:                   {total_errores}")

    return resultados


# ==========================================================
# EJECUCIÓN PRINCIPAL
# ==========================================================

if __name__ == "__main__":

    resultados = validar_ingresos_todas_empresas(
        fecha_corte="2026-11-15"
    )
