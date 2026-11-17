
from database_manager import obtener_conexion

from exploration.financial_data_queries import (
    validar_parametros
)


# ==========================================================
# EXPLORAR DATOS FINANCIEROS
# ==========================================================

def explorar_datos_empresa(ticker, limite=20):

    """
    Muestra algunos registros financieros de una empresa.
    """

    ticker = validar_parametros(ticker, limite)

    with obtener_conexion() as conexion:

        consulta = """
            SELECT
                f.ticker,
                f.taxonomy,
                f.concept,
                d.label,
                f.unit,
                f.value,
                f.start_date,
                f.end_date,
                f.fiscal_year,
                f.fiscal_period,
                f.form,
                f.filed_date

            FROM financial_facts AS f

            LEFT JOIN fact_definitions AS d
                ON f.taxonomy = d.taxonomy
                AND f.concept = d.concept

            WHERE f.ticker = ?

            ORDER BY
                f.filed_date DESC,
                f.end_date DESC

            LIMIT ?
        """

        resultado = conexion.execute(
            consulta,
            (ticker, limite)
        )

        registros = resultado.fetchall()

    return [dict(registro) for registro in registros]


# ==========================================================
# CONSULTAR OBSERVACIONES DE UN CONCEPTO SEC
# ==========================================================

def obtener_observaciones_concepto(
    ticker,
    concepto,
    formulario="10-K",
    limite=20
):

    """
    Recupera los registros históricos de un concepto SEC.
    """

    ticker = validar_parametros(ticker, limite)

    if not isinstance(concepto, str) or not concepto.strip():
        raise ValueError("El concepto no puede estar vacío.")

    if not isinstance(formulario, str) or not formulario.strip():
        raise ValueError("El formulario no puede estar vacío.")

    concepto = concepto.strip()
    formulario = formulario.strip()

    with obtener_conexion() as conexion:

        consulta = """
            SELECT
                ticker,
                concept,
                unit,
                value,
                start_date,
                end_date,
                fiscal_year,
                fiscal_period,
                form,
                filed_date,
                accession_number,
                frame

            FROM financial_facts

            WHERE ticker = ?
                AND taxonomy = 'us-gaap'
                AND concept = ?
                AND form = ?

            ORDER BY
                end_date DESC,
                filed_date DESC

            LIMIT ?
        """

        resultado = conexion.execute(
            consulta,
            (
                ticker,
                concepto,
                formulario,
                limite
            )
        )

        registros = resultado.fetchall()

    return [dict(registro) for registro in registros]


# ==========================================================
# OBTENER OBSERVACIONES DE PERIODOS ANUALES
# ==========================================================

def obtener_observaciones_anuales(
    ticker,
    concepto,
    limite=30
):

    """
    Recupera observaciones de duración anual.

    Consideramos anual un periodo de entre 330 y 380 días.

    No eliminamos duplicados: queremos estudiar las distintas
    publicaciones y posibles revisiones de cada ejercicio.
    """

    ticker = validar_parametros(ticker, limite)

    if not isinstance(concepto, str) or not concepto.strip():
        raise ValueError("El concepto no puede estar vacío.")

    concepto = concepto.strip()

    with obtener_conexion() as conexion:

        consulta = """
            SELECT
                ticker,
                concept,
                unit,
                value,
                start_date,
                end_date,

                CAST(
                    julianday(end_date) - julianday(start_date) + 1
                    AS INTEGER
                ) AS period_days,

                fiscal_year,
                fiscal_period,
                form,
                filed_date,
                accession_number,
                frame

            FROM financial_facts

            WHERE ticker = ?
                AND taxonomy = 'us-gaap'
                AND concept = ?
                AND form = '10-K'
                AND unit = 'USD'
                AND start_date IS NOT NULL
                AND end_date IS NOT NULL

                AND (
                    julianday(end_date) - julianday(start_date)
                ) BETWEEN 329 AND 379

            ORDER BY
                end_date DESC,
                filed_date ASC

            LIMIT ?
        """

        resultado = conexion.execute(
            consulta,
            (ticker, concepto, limite)
        )

        registros = resultado.fetchall()

    return [dict(registro) for registro in registros]
