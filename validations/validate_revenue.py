from dic_financial_terms import CONCEPTOS_FINANCIEROS
from financial_data import (
    listar_empresas,
    obtener_ingresos
)

## ==========================================================
#  VALIDAR INGRESOS DE TODAS LAS EMPRESAS
## ==========================================================

def validar_ingresos_todas_empresas(
    fecha_corte="2026-11-15",
    ejercicio_minimo=1990
):
    """
    Valida los ingresos de todas las empresas de la base de datos.

    Busca el último ejercicio anual disponible para cada empresa,
    respetando la fecha de corte.
    """

    empresas_configuradas = CONCEPTOS_FINANCIEROS["revenue"]

    empresas = [
    empresa
    for empresa in listar_empresas()
    if empresa["ticker"] in empresas_configuradas
]

    resultados = []

    # El último año que buscamos es el año de la fecha de corte.
    ultimo_ejercicio = int(fecha_corte[:4])

    print("\n" + "=" * 90)
    print("VALIDACIÓN GENERAL DE INGRESOS")
    print(f"Fecha de corte: {fecha_corte}")
    print(f"Empresas encontradas: {len(empresas)}")
    print("=" * 90)

    for empresa in empresas:

        ticker = empresa["ticker"]

        resultado_encontrado = None
        estado = "SIN_DATOS"
        ejercicio_encontrado = None
        error = None

        # Buscamos desde el ejercicio más reciente hacia atrás.
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

            except ValueError as e:

                # Empresa sin conceptos configurados.
                error = str(e)
                estado = "SIN_CONFIGURAR"
                break

            except Exception as e:

                # Guardamos cualquier otro error para revisarlo.
                error = str(e)
                estado = "ERROR"
                break

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

    # Mostrar resultados.
    print("\nRESULTADOS POR EMPRESA")
    print("-" * 90)

    for resultado in resultados:

        print(
            f"{resultado['ticker']:8} | "
            f"{str(resultado['ejercicio']):6} | "
            f"{str(resultado['ingresos']):20} | "
            f"{resultado['estado']}"
        )

    # Resumen de estados.
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

## ==========================================================
#  PRUEBAS
## =========================================================

if __name__ == "__main__":

    resultados = validar_ingresos_todas_empresas(
        fecha_corte="2026-11-15"
    )