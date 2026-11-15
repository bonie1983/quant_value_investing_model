
# database_manager.py
# Gestion de la base de datos SQLite del Modelo de Valor Cuantitativo.
#
# Funciones:
# 1. Crear la estructura de la base de datos.
# 2. Registrar las empresas del universo.
# 3. Importar los datos financieros de SEC Company Facts.
# 4. Conservar las fechas de publicacion y los ejercicios fiscales.
# 5. Evitar duplicados sin eliminar versiones anteriores de los datos.

import os
import json
import sqlite3
import hashlib

from datetime import datetime, timezone
from contextlib import contextmanager

from dic_companies import EMPRESAS_DOWJONES


# ============================================================
# CONFIGURACION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CACHE_DIR = os.path.join(BASE_DIR, "data_cache")
DATABASE_DIR = os.path.join(BASE_DIR, "database")

DATABASE_FILE = os.path.join(
    DATABASE_DIR,
    "quantitative_value.db"
)

os.makedirs(DATABASE_DIR, exist_ok=True)


# ============================================================
# CONEXION
# ============================================================


@contextmanager
def obtener_conexion():

    """
    Abre una conexión con nuestra base de datos SQLite.
    Activa las claves foráneas y cierra la conexión
    al finalizar.
    """

    conexion = sqlite3.connect(DATABASE_FILE)

    try:
        conexion.execute("PRAGMA foreign_keys = ON")
        conexion.row_factory = sqlite3.Row

        yield conexion

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()



# ============================================================
# CREACION DE TABLAS
# ============================================================

def crear_base_datos():

    print("\nInicializando base de datos SQLite...")

    with obtener_conexion() as conexion:

        cursor = conexion.cursor()

        # ----------------------------------------------------
        # 1. EMPRESAS
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (

                ticker TEXT PRIMARY KEY,
                cik TEXT NOT NULL,
                name TEXT NOT NULL,
                sector TEXT,
                industry TEXT,
                indices TEXT,
                exchange TEXT,
                sec_entity_name TEXT,
                cache_updated_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL

            )
        """)

        # ----------------------------------------------------
        # 2. DEFINICIONES DE CONCEPTOS CONTABLES
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fact_definitions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                taxonomy TEXT NOT NULL,
                concept TEXT NOT NULL,
                label TEXT,
                description TEXT,

                UNIQUE(taxonomy, concept)

            )
        """)

        # ----------------------------------------------------
        # 3. DATOS FINANCIEROS SEC
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_facts (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                fact_key TEXT NOT NULL UNIQUE,

                ticker TEXT NOT NULL,

                taxonomy TEXT NOT NULL,
                concept TEXT NOT NULL,
                unit TEXT NOT NULL,

                value REAL,
                value_raw TEXT,

                start_date TEXT,
                end_date TEXT,

                accession_number TEXT,
                fiscal_year INTEGER,
                fiscal_period TEXT,

                form TEXT,
                filed_date TEXT,
                frame TEXT,

                imported_at TEXT NOT NULL,

                FOREIGN KEY (ticker)
                    REFERENCES companies(ticker)

            )
        """)

        # ----------------------------------------------------
        # 4. HISTORIAL DE IMPORTACIONES
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_log (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                ticker TEXT NOT NULL,
                imported_at TEXT NOT NULL,

                records_read INTEGER DEFAULT 0,
                records_inserted INTEGER DEFAULT 0,

                status TEXT NOT NULL,
                message TEXT

            )
        """)

        # ----------------------------------------------------
        # 5. EJECUCIONES DEL MODELO
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_runs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                run_date TEXT NOT NULL,
                model_version TEXT,
                universe_name TEXT,
                description TEXT

            )
        """)

        # ----------------------------------------------------
        # 6. POSICIONES DE CARTERA
        # ----------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_positions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                model_run_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,

                rank INTEGER,
                score REAL,
                weight REAL,

                FOREIGN KEY (model_run_id)
                    REFERENCES model_runs(id),

                FOREIGN KEY (ticker)
                    REFERENCES companies(ticker),

                UNIQUE(model_run_id, ticker)

            )
        """)

        # ----------------------------------------------------
        # INDICES PARA ACELERAR CONSULTAS
        # ----------------------------------------------------

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facts_ticker_concept
            ON financial_facts(ticker, concept)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facts_end_date
            ON financial_facts(end_date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facts_filed_date
            ON financial_facts(filed_date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facts_accession
            ON financial_facts(accession_number)
        """)

    print("Base de datos creada correctamente.")


# ============================================================
# REGISTRO DE EMPRESAS
# ============================================================

def registrar_empresa(ticker, info, datos_sec, fecha_cache):

    ahora = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )

    cik = str(info["cik"]).zfill(10)

    sec_entity_name = datos_sec.get("entityName")

    with obtener_conexion() as conexion:

        conexion.execute("""
            INSERT INTO companies (

                ticker,
                cik,
                name,
                sector,
                industry,
                indices,
                exchange,
                sec_entity_name,
                cache_updated_at,
                created_at,
                updated_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(ticker) DO UPDATE SET

                cik = excluded.cik,
                name = excluded.name,
                sector = excluded.sector,
                industry = excluded.industry,
                indices = excluded.indices,
                exchange = excluded.exchange,
                sec_entity_name = excluded.sec_entity_name,
                cache_updated_at = excluded.cache_updated_at,
                updated_at = excluded.updated_at

        """, (

            ticker,
            cik,
            info["nombre"],
            info["sector"],
            info["industria"],
            json.dumps(info["indice"]),
            info["exchange"],
            sec_entity_name,
            fecha_cache,
            ahora,
            ahora

        ))


# ============================================================
# GENERACION DE IDENTIFICADOR UNICO
# ============================================================

def generar_fact_key(ticker, taxonomy, concept, unit, registro):

    contenido = {

        "ticker": ticker,
        "taxonomy": taxonomy,
        "concept": concept,
        "unit": unit,

        "start": registro.get("start"),
        "end": registro.get("end"),

        "accn": registro.get("accn"),
        "filed": registro.get("filed"),

        "form": registro.get("form"),
        "fy": registro.get("fy"),
        "fp": registro.get("fp"),

        "frame": registro.get("frame"),
        "val": registro.get("val")

    }

    texto = json.dumps(
        contenido,
        sort_keys=True,
        ensure_ascii=False
    )

    return hashlib.sha256(
        texto.encode("utf-8")
    ).hexdigest()


# ============================================================
# IMPORTACION DE DEFINICIONES CONTABLES
# ============================================================

def importar_definiciones(conexion, taxonomy, concept, metadata):

    conexion.execute("""
        INSERT INTO fact_definitions (
            taxonomy,
            concept,
            label,
            description
        )

        VALUES (?, ?, ?, ?)

        ON CONFLICT(taxonomy, concept) DO UPDATE SET

            label = COALESCE(excluded.label, fact_definitions.label),
            description = COALESCE(
                excluded.description,
                fact_definitions.description
            )

    """, (

        taxonomy,
        concept,
        metadata.get("label"),
        metadata.get("description")

    ))


# ============================================================
# IMPORTACION DE DATOS FINANCIEROS SEC
# ============================================================

def importar_datos_empresa(ticker, info):

    ticker = ticker.upper()

    archivo_json = os.path.join(
        CACHE_DIR,
        f"{ticker}_sec.json"
    )

    if not os.path.exists(archivo_json):

        print(f"[{ticker}] No existe el archivo SEC.")

        return False

    try:

        with open(archivo_json, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if not isinstance(datos, dict) or not isinstance(datos.get("facts"), dict):
            raise ValueError("Estructura Company Facts no válida.")

        cik_json = str(datos.get("cik", "")).zfill(10)
        cik_esperado = str(info["cik"]).zfill(10)

        if cik_json != cik_esperado:
            raise ValueError(
                f"CIK incorrecto. Esperado {cik_esperado}, "
                f"encontrado {cik_json}."
            )

        facts = datos["facts"]

        fecha_cache = datetime.fromtimestamp(
            os.path.getmtime(archivo_json),
            tz=timezone.utc
        ).isoformat(timespec="seconds")

        # Registramos la empresa antes de insertar sus datos.
        registrar_empresa(
            ticker,
            info,
            datos,
            fecha_cache
        )

        registros_leidos = 0
        registros_insertados = 0

        ahora = datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        )

        with obtener_conexion() as conexion:

            for taxonomy, conceptos in facts.items():

                for concept, metadata in conceptos.items():

                    importar_definiciones(
                        conexion,
                        taxonomy,
                        concept,
                        metadata
                    )

                    unidades = metadata.get("units", {})

                    for unit, registros in unidades.items():

                        for registro in registros:

                            registros_leidos += 1

                            valor_original = registro.get("val")

                            try:
                                valor_numerico = (
                                    float(valor_original)
                                    if valor_original is not None
                                    else None
                                )
                            except (ValueError, TypeError):
                                valor_numerico = None

                            fact_key = generar_fact_key(
                                ticker,
                                taxonomy,
                                concept,
                                unit,
                                registro
                            )

                            cursor = conexion.execute("""

                                INSERT OR IGNORE INTO financial_facts (

                                    fact_key,
                                    ticker,
                                    taxonomy,
                                    concept,
                                    unit,
                                    value,
                                    value_raw,
                                    start_date,
                                    end_date,
                                    accession_number,
                                    fiscal_year,
                                    fiscal_period,
                                    form,
                                    filed_date,
                                    frame,
                                    imported_at

                                )

                                VALUES (
                                    ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                    ?, ?, ?, ?, ?, ?, ?
                                )

                            """, (

                                fact_key,
                                ticker,
                                taxonomy,
                                concept,
                                unit,
                                valor_numerico,
                                str(valor_original)
                                if valor_original is not None else None,
                                registro.get("start"),
                                registro.get("end"),
                                registro.get("accn"),
                                registro.get("fy"),
                                registro.get("fp"),
                                registro.get("form"),
                                registro.get("filed"),
                                registro.get("frame"),
                                ahora

                            ))

                            if cursor.rowcount == 1:
                                registros_insertados += 1

        registrar_importacion(
            ticker,
            registros_leidos,
            registros_insertados,
            "OK",
            "Importación completada."
        )

        print(
            f"[{ticker}] Importación correcta. "
            f"Leídos: {registros_leidos:,} | "
            f"Nuevos: {registros_insertados:,}"
        )

        return True

    except Exception as e:

        print(f"[{ticker}] Error de importación: {e}")

        registrar_importacion(
            ticker,
            0,
            0,
            "ERROR",
            str(e)
        )

        return False


# ============================================================
# REGISTRO DE IMPORTACIONES
# ============================================================

def registrar_importacion(
    ticker,
    registros_leidos,
    registros_insertados,
    status,
    message
):

    ahora = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )

    with obtener_conexion() as conexion:

        conexion.execute("""

            INSERT INTO import_log (

                ticker,
                imported_at,
                records_read,
                records_inserted,
                status,
                message

            )

            VALUES (?, ?, ?, ?, ?, ?)

        """, (

            ticker,
            ahora,
            registros_leidos,
            registros_insertados,
            status,
            message

        ))


# ============================================================
# IMPORTACION DE TODO EL UNIVERSO
# ============================================================

def importar_universo():

    print("\n" + "=" * 65)
    print("IMPORTACION SEC EDGAR -> SQLITE")
    print("MODELO DE VALOR CUANTITATIVO")
    print("=" * 65)

    resultados = []

    for numero, (ticker, info) in enumerate(
        EMPRESAS_DOWJONES.items(),
        start=1
    ):

        print(
            f"\n[{numero}/{len(EMPRESAS_DOWJONES)}] "
            f"Procesando {info['nombre']} ({ticker})"
        )

        correcto = importar_datos_empresa(ticker, info)

        resultados.append({
            "Ticker": ticker,
            "Empresa": info["nombre"],
            "Importacion correcta": correcto
        })

    total = len(resultados)

    correctas = sum(
        resultado["Importacion correcta"]
        for resultado in resultados
    )

    print("\n" + "=" * 65)
    print("RESUMEN DE IMPORTACION")
    print("=" * 65)

    print(f"Empresas procesadas: {total}")
    print(f"Importaciones correctas: {correctas}")
    print(f"Errores: {total - correctas}")

    print("=" * 65)


# ============================================================
# CONSULTA RAPIDA DE LA BASE DE DATOS
# ============================================================

def mostrar_resumen():

    with obtener_conexion() as conexion:

        cursor = conexion.cursor()

        empresas = cursor.execute("""
            SELECT COUNT(*) FROM companies
        """).fetchone()[0]

        conceptos = cursor.execute("""
            SELECT COUNT(*) FROM fact_definitions
        """).fetchone()[0]

        registros = cursor.execute("""
            SELECT COUNT(*) FROM financial_facts
        """).fetchone()[0]

        print("\nRESUMEN DE BASE DE DATOS")

        print(f"Empresas registradas: {empresas}")
        print(f"Conceptos contables: {conceptos}")
        print(f"Registros financieros: {registros:,}")


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":

    crear_base_datos()

    importar_universo()

    mostrar_resumen()
