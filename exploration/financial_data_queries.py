
from datetime import datetime

from database_manager import obtener_conexion


# ==========================================================
# VALIDACIÓN DE PARÁMETROS
# ==========================================================

def validar_parametros(ticker, limite):

    """
    Normaliza y valida los parámetros comunes de consulta.
    """

    if not isinstance(ticker, str):
        raise ValueError("El ticker debe ser una cadena de texto.")

    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("El ticker no puede estar vacío.")

    if (
        not isinstance(limite, int)
        or isinstance(limite, bool)
        or limite <= 0
    ):
        raise ValueError("El límite debe ser un entero positivo.")

    return ticker


# ==========================================================
# LISTAR EMPRESAS
# ==========================================================

def listar_empresas():

    """
    Recupera las empresas registradas en la base de datos.
    """

    with obtener_conexion() as conexion:

        consulta = """
            SELECT
                ticker,
                name,
                sector

            FROM companies

            ORDER BY ticker
        """

        resultado = conexion.execute(consulta)
        registros = resultado.fetchall()

    return [dict(registro) for registro in registros]


# ==========================================================
# BUSCAR CONCEPTOS CONTABLES
# ==========================================================

def listar_conceptos_por_palabra(
    ticker,
    palabra,
    limite=50,
    taxonomy=None
):

    """
    Busca conceptos contables por nombre técnico o etiqueta.

    Si taxonomy es None, busca en todas las taxonomías.
    Si se indica una taxonomía, limita la búsqueda a ella.
    """

    ticker = validar_parametros(ticker, limite)

    if not isinstance(palabra, str) or not palabra.strip():
        raise ValueError("La palabra de búsqueda no puede estar vacía.")

    palabra = palabra.strip()

    if taxonomy is not None:

        if not isinstance(taxonomy, str) or not taxonomy.strip():
            raise ValueError("La taxonomía debe ser una cadena no vacía.")

        taxonomy = taxonomy.strip()

    with obtener_conexion() as conexion:

        consulta = """
            SELECT
                f.taxonomy,
                f.concept,
                d.label,
                f.unit,
                COUNT(*) AS numero_registros,
                MAX(f.filed_date) AS ultima_publicacion

            FROM financial_facts AS f

            LEFT JOIN fact_definitions AS d
                ON f.taxonomy = d.taxonomy
                AND f.concept = d.concept

            WHERE f.ticker = ?
                AND f.form IN ('10-K', '10-Q')
                AND (
                    f.concept LIKE ?
                    OR d.label LIKE ?
                )
        """

        parametros = [
            ticker,
            f"%{palabra}%",
            f"%{palabra}%"
        ]

        if taxonomy is not None:

            consulta += " AND f.taxonomy = ?"
            parametros.append(taxonomy)

        consulta += """
            GROUP BY
                f.taxonomy,
                f.concept,
                d.label,
                f.unit

            ORDER BY
                ultima_publicacion DESC

            LIMIT ?
        """

        parametros.append(limite)

        resultado = conexion.execute(
            consulta,
            parametros
        )

        registros = resultado.fetchall()

    return [dict(registro) for registro in registros]


# ==========================================================
# OBTENER DATO FINANCIERO ANUAL
# ==========================================================

def obtener_dato_anual(
    ticker,
    concepto,
    ejercicio,
    fecha_corte
):

    """
    Recupera el dato anual más reciente disponible para un
    concepto y ejercicio fiscal determinados.

    Criterios:
    - Taxonomía US-GAAP.
    - Formulario 10-K.
    - Unidad USD.
    - Duración entre 329 y 379 días de diferencia.
    - Ejercicio fiscal solicitado.
    - Fecha de publicación <= fecha de corte.

    Se selecciona la publicación más reciente disponible
    hasta la fecha de corte.
    """

    ticker = validar_parametros(ticker, 1)

    if not isinstance(concepto, str) or not concepto.strip():
        raise ValueError("El concepto no puede estar vacío.")

    concepto = concepto.strip()

    if (
        not isinstance(ejercicio, int)
        or isinstance(ejercicio, bool)
        or ejercicio < 1900
    ):
        raise ValueError("El ejercicio fiscal no es válido.")

    try:
        datetime.strptime(fecha_corte, "%Y-%m-%d")

    except (TypeError, ValueError):
        raise ValueError(
            "La fecha de corte debe tener el formato YYYY-MM-DD."
        )

    with obtener_conexion() as conexion:

        consulta = """
        SELECT
            ticker,
            taxonomy,
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
            AND unit = 'USD'
            AND form = '10-K'
            AND substr(end_date, 1, 4) = ?
            AND filed_date <= ?
            AND start_date IS NOT NULL
            AND end_date IS NOT NULL

            AND (
                julianday(end_date) - julianday(start_date) + 1
            ) BETWEEN 329 AND 379

        ORDER BY
            filed_date DESC,
            accession_number DESC

        LIMIT 1
        """

        resultado = conexion.execute(
            consulta,
            (
                ticker,
                concepto,
                str(ejercicio),
                fecha_corte
            )
        )

        registro = resultado.fetchone()

    return dict(registro) if registro else None
