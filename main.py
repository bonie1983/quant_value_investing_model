
# main.py
# Script principal del Modelo de Valor Cuantitativo.
# Orquesta la obtención de datos SEC EDGAR.

import pandas as pd

from dic_companies import EMPRESAS_DOWJONES

from financial_data.sec_data import (
    obtener_datos_sec
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

# False: utiliza la caché si existe y es válida.
# True: intenta descargar nuevamente los datos de todas las empresas.

FORCE_REFRESH = False


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def ejecutar_modelo(force_refresh: bool = False):
    """
    Recorre el universo de empresas y obtiene sus datos SEC.

    Utiliza la caché local cuando está disponible y es válida.

    Devuelve:
        DataFrame con el resultado de la sincronización.
    """

    print("\n" + "=" * 65)
    print("INICIALIZACIÓN DE DATOS SEC EDGAR")
    print("MODELO DE VALOR CUANTITATIVO")
    print("=" * 65)

    resultados = []

    total_empresas = len(EMPRESAS_DOWJONES)

    for numero, (ticker, info) in enumerate(
        EMPRESAS_DOWJONES.items(),
        start=1
    ):

        print(
            f"\n[{numero}/{total_empresas}] "
            f"Procesando {info['nombre']} ({ticker})..."
        )

        datos_sec, estado, fecha_cache = obtener_datos_sec(
            ticker=ticker,
            cik=info["cik"],
            force_refresh=force_refresh
        )

        resultados.append({
            "Ticker": ticker,
            "Empresa": info["nombre"],
            "CIK": info["cik"],
            "Sector": info["sector"],
            "Industria": info["industria"],
            "Índice": ", ".join(info["indice"]),
            "Exchange": info["exchange"],
            "SEC Caché OK": bool(datos_sec),
            "Estado": estado,
            "Última actualización caché": fecha_cache
        })

    return generar_resumen(resultados)


# ============================================================
# RESUMEN DE SINCRONIZACIÓN
# ============================================================

def generar_resumen(resultados):
    """
    Genera y muestra el resumen de sincronización SEC.
    """

    df_resultados = pd.DataFrame(resultados)

    estados = df_resultados["Estado"]

    print("\n" + "=" * 65)
    print("RESUMEN DE CACHÉ DEL UNIVERSO")
    print("=" * 65)

    print(df_resultados.to_string(index=False))

    print("\n" + "-" * 65)
    print("ESTADÍSTICAS DE SINCRONIZACIÓN")
    print("-" * 65)

    print(f"Empresas totales: {len(df_resultados)}")
    print(f"Cachés disponibles: {df_resultados['SEC Caché OK'].sum()}")
    print(f"Descargas nuevas: {(estados == 'DESCARGADA').sum()}")
    print(f"Cachés reutilizadas: {(estados == 'CACHE OK').sum()}")
    print(
        "Cachés anteriores utilizadas: "
        f"{(estados == 'CACHE ANTERIOR').sum()}"
    )
    print(f"Errores sin datos disponibles: {(estados == 'ERROR').sum()}")

    print("=" * 65)

    return df_resultados


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":

    df_resultados = ejecutar_modelo(
        force_refresh=FORCE_REFRESH
    )
