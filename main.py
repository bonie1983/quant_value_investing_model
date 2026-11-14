
# main.py
# Script principal para gestionar la caché local de datos SEC EDGAR.
# Proyecto: Modelo de Valor Cuantitativo

import os
import json
import time
import requests
import pandas as pd

from datetime import datetime, timezone

from dic_companies import EMPRESAS_DOWJONES


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CACHE_DIR = os.path.join(BASE_DIR, "data_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

SEC_USER_AGENT = "MiProyectoQuant steverozad@gmail.com"

SEC_BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{}.json"

TIMEOUT_SEC = 30

# Pausa entre descargas para respetar los límites de la SEC.
PAUSA_ENTRE_DESCARGAS = 0.3

# False: utiliza la caché si existe y es válida.
# True: intenta descargar nuevamente los datos de todas las empresas.
FORCE_REFRESH = False


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_rutas_cache(ticker: str) -> tuple:
    """Devuelve las rutas del archivo de datos y sus metadatos."""

    ticker = ticker.upper()

    archivo_datos = os.path.join(
        CACHE_DIR,
        f"{ticker}_sec.json"
    )

    archivo_metadata = os.path.join(
        CACHE_DIR,
        f"{ticker}_sec_meta.json"
    )

    return archivo_datos, archivo_metadata


def leer_cache(archivo: str, cik: str = None) -> dict:
    """Lee la caché y comprueba su estructura y CIK."""

    if not os.path.exists(archivo):
        return {}

    try:
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if not isinstance(datos, dict) or not isinstance(datos.get("facts"), dict):
            print("  [AVISO] Estructura de caché no válida.")
            return {}

        # Comprobamos que el archivo corresponde a la empresa esperada.
        if cik is not None:
            cik_archivo = str(datos.get("cik", "")).zfill(10)
            cik_esperado = str(cik).zfill(10)

            if cik_archivo != cik_esperado:
                print(
                    f"  [AVISO] CIK incorrecto en caché. "
                    f"Esperado: {cik_esperado}, encontrado: {cik_archivo}"
                )
                return {}

        return datos

    except (json.JSONDecodeError, OSError) as e:
        print(f"  [AVISO] No se pudo leer la caché: {e}")
        return {}


def obtener_fecha_cache(archivo: str) -> str:
    """Obtiene la fecha de última modificación del archivo de caché."""

    if not os.path.exists(archivo):
        return "No disponible"

    timestamp = os.path.getmtime(archivo)

    return datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc
    ).isoformat(timespec="seconds")


def guardar_metadata(archivo: str, ticker: str, cik: str, datos: dict):
    """Guarda información de control sin modificar el JSON original de SEC."""

    metadata = {
        "ticker": ticker,
        "cik": str(cik).zfill(10),
        "fecha_descarga_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "empresa_sec": datos.get("entityName")
    }

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


# ============================================================
# SISTEMA DE CACHÉ SEC EDGAR
# ============================================================

def obtener_datos_sec(
    ticker: str,
    cik: str,
    force_refresh: bool = False
) -> tuple:
    """
    Obtiene los datos SEC de una empresa.

    Devuelve:
        datos: diccionario Company Facts.
        estado: estado de la operación.
        fecha_cache: fecha de modificación de la caché.
    """

    ticker = ticker.upper()

    archivo_datos, archivo_metadata = obtener_rutas_cache(ticker)

    # Comprobamos si ya existe una caché válida.
    datos_cache = leer_cache(archivo_datos, cik)

    if datos_cache and not force_refresh:
        fecha_cache = obtener_fecha_cache(archivo_datos)

        print(f"[{ticker}] Caché local encontrada. No se descarga.")

        return datos_cache, "CACHE OK", fecha_cache

    if force_refresh:
        print(f"[{ticker}] Actualización forzada de datos SEC...")
    else:
        print(f"[{ticker}] No existe caché válida. Descargando datos SEC...")

    # Construimos la URL oficial de la SEC.
    cik_formateado = str(cik).zfill(10)

    url = SEC_BASE_URL.format(cik_formateado)

    headers = {
        "User-Agent": SEC_USER_AGENT,
        "Accept-Encoding": "gzip, deflate"
    }

    archivo_temporal = archivo_datos + ".tmp"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=TIMEOUT_SEC
        )

        response.raise_for_status()

        datos = response.json()

        # Validación de la respuesta.
        if not isinstance(datos, dict) or not isinstance(datos.get("facts"), dict):
            raise ValueError("Respuesta SEC no válida.")

        cik_respuesta = str(datos.get("cik", "")).zfill(10)

        if cik_respuesta != cik_formateado:
            raise ValueError(
                f"El CIK recibido ({cik_respuesta}) "
                f"no coincide con el solicitado ({cik_formateado})."
            )

        # Guardado temporal del JSON original.
        with open(archivo_temporal, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

        # Sustitución atómica de la caché.
        os.replace(archivo_temporal, archivo_datos)

        # Los metadatos no deben invalidar una descarga correcta.
        try:
            guardar_metadata(
                archivo_metadata,
                ticker,
                cik,
                datos
            )
        except OSError as e:
            print(f"[{ticker}] Aviso: no se pudieron guardar los metadatos: {e}")

        fecha_cache = obtener_fecha_cache(archivo_datos)

        print(f"[{ticker}] Descarga y caché completadas correctamente.")

        time.sleep(PAUSA_ENTRE_DESCARGAS)

        return datos, "DESCARGADA", fecha_cache

    except (requests.RequestException, ValueError, OSError) as e:

        print(f"[{ticker}] Error al obtener datos SEC: {e}")

        if datos_cache:
            fecha_cache = obtener_fecha_cache(archivo_datos)

            print(f"[{ticker}] Se utilizará la caché anterior.")

            return datos_cache, "CACHE ANTERIOR", fecha_cache

        return {}, "ERROR", "No disponible"

    finally:
        # Limpiamos cualquier archivo temporal que haya quedado.
        if os.path.exists(archivo_temporal):
            try:
                os.remove(archivo_temporal)
            except OSError:
                pass



# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def ejecutar_modelo(force_refresh: bool = False):

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


# ========================================================
# RESUMEN FINAL
# ========================================================

    df_resultados = pd.DataFrame(resultados)
    estados = df_resultados["Estado"]

    print("\n" + "=" * 65)
    print("RESUMEN DE CACHÉ DEL UNIVERSO")
    print("=" * 65)

    print(df_resultados.to_string(index=False))

    print("\n" + "-" * 65)
    print("ESTADÍSTICAS DE SINCRONIZACIÓN")
    print("-" * 65)

    estados = df_resultados["Estado"]

    print(f"Empresas totales: {len(df_resultados)}")
    print(f"Cachés disponibles: {df_resultados['SEC Caché OK'].sum()}")
    print(f"Descargas nuevas: {(estados == 'DESCARGADA').sum()}")
    print(f"Cachés reutilizadas: {(estados == 'CACHE OK').sum()}")
    print(f"Cachés anteriores utilizadas: {(estados == 'CACHE ANTERIOR').sum()}")
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
