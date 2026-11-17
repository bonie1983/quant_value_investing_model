
from database_manager import obtener_conexion
from datetime import datetime
from dic_financial_terms import CONCEPTOS_FINANCIEROS


# ==========================================================
# 1. CONSULTAR EMPRESAS
# ==========================================================

def listar_empresas():

    """
    Devuelve todas las empresas registradas en SQLite.
    """

    with obtener_conexion() as conexion:

        resultado = conexion.execute("""
            SELECT ticker, name, sector
            FROM companies
            ORDER BY ticker
        """)

        empresas = resultado.fetchall()

    return [dict(empresa) for empresa in empresas]



# ==========================================================
# 2. EXPLORAR DATOS FINANCIEROS
# ==========================================================

def explorar_datos_empresa(ticker, limite=20):

    """
    Muestra algunos registros financieros de una empresa.

    ticker: símbolo de la empresa, por ejemplo MSFT.
    limite: número máximo de registros que queremos mostrar.
    """

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
            (ticker.upper(), limite)
        )

        registros = resultado.fetchall()

    return [dict(registro) for registro in registros]



# ==========================================================
# 3. BUSCAR CONCEPTOS CONTABLES
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
            ticker.upper(),
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
# 4. CONSULTAR OBSERVACIONES DE UN CONCEPTO SEC
# ==========================================================

def obtener_observaciones_concepto(
    ticker,
    concepto,
    formulario="10-K",
    limite=20
):

    """
    Recupera los registros históricos de un concepto SEC.

    Ejemplo:
    obtener_observaciones_concepto(
        "MSFT",
        "RevenueFromContractWithCustomerExcludingAssessedTax"
    )
    """

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
                ticker.upper(),
                concepto,
                formulario,
                limite
            )
        )

        registros = resultado.fetchall()

    return [dict(registro) for registro in registros]



# ==========================================================
# 5. OBTENER OBSERVACIONES DE PERIODOS ANUALES
# ==========================================================

def obtener_observaciones_anuales(ticker, concepto, limite=30):

    """
    Recupera observaciones de duración anual.

    Consideramos anual un periodo de entre 330 y 380 días.
    Así evitamos mezclar ingresos trimestrales con anuales.

    No eliminamos duplicados: queremos estudiar las distintas
    publicaciones y posibles revisiones de cada ejercicio.
    """

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
            (ticker.upper(), concepto, limite)
        )

        registros = resultado.fetchall()

    return [dict(registro) for registro in registros]



# ==========================================================
# 6. OBTENER UN DATO ANUAL EN UNA FECHA DETERMINADA
# ==========================================================

def obtener_dato_anual(
    ticker,
    concepto,
    ejercicio,
    fecha_corte
):

    """
    Recupera el dato anual de una empresa para un ejercicio
    fiscal, utilizando únicamente información publicada
    hasta la fecha de corte.

    Parámetros:
        ticker: símbolo de la empresa (MSFT).
        concepto: concepto contable SEC.
        ejercicio: año de finalización del ejercicio fiscal.
        fecha_corte: fecha máxima de publicación (YYYY-MM-DD).

    Devuelve:
        Diccionario con el valor y su procedencia.
        None si no encuentra ningún registro válido.
    """

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
                    julianday(end_date) -
                    julianday(start_date) + 1
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

                AND start_date IS NOT NULL
                AND end_date IS NOT NULL

                -- Ejercicio identificado por el año
                -- de finalización del periodo.
                AND substr(end_date, 1, 4) = ?

                -- Periodo de duración anual.
                AND (
                    julianday(end_date) -
                    julianday(start_date)
                ) BETWEEN 329 AND 379

                -- Evitar información publicada después
                -- de nuestra fecha de análisis.
                AND filed_date <= ?

            ORDER BY
                filed_date DESC,
                accession_number DESC

            LIMIT 1
        """

        resultado = conexion.execute(
            consulta,
            (
                ticker.upper(),
                concepto,
                str(ejercicio),
                fecha_corte
            )
        )

        registro = resultado.fetchone()

    if registro is None:
        return None

    return dict(registro)





# ==========================================================
# 7. OBTENER INGRESOS ANUALES
# ==========================================================

def obtener_ingresos(ticker, ejercicio, fecha_corte):

    """
    Obtiene los ingresos anuales de una empresa,
    respetando la fecha de corte y la prioridad
    de conceptos definida en dic_financial_terms.py.
    """

    # Normalizamos el ticker
    ticker = ticker.strip().upper()

    # Comprobamos que la fecha tenga formato correcto
    try:
        datetime.strptime(fecha_corte, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            "La fecha de corte debe tener formato YYYY-MM-DD"
        )

    # Obtenemos los conceptos configurados para la empresa
    conceptos_por_empresa = CONCEPTOS_FINANCIEROS.get("revenue", {})

    conceptos = conceptos_por_empresa.get(ticker, [])

    if not conceptos:
        raise ValueError(
            f"No hay conceptos de ingresos configurados para {ticker}"
        )

    # Probamos los conceptos siguiendo el orden de prioridad
    for concepto in conceptos:

        resultado = obtener_dato_anual(
            ticker=ticker,
            concepto=concepto,
            ejercicio=ejercicio,
            fecha_corte=fecha_corte
        )

        if resultado is None:
            continue

        # Validación adicional del ejercicio
        if int(resultado["end_date"][:4]) != int(ejercicio):
            continue

        # Validación de la duración anual
        if not 329 <= resultado["period_days"] <= 379:
            continue

        # Validación de la fecha de publicación
        if resultado["filed_date"] > fecha_corte:
            continue

        # Validación del formulario
        if resultado["form"] != "10-K":
            continue

        return resultado

    return None


# ==========================================================
# Prueba de obtener dato anual para una empresa y concepto específico
# ==========================================================

if __name__ == "__main__":

    palabras = [
        "ServiceCost",
        "InterestCost",
        "ExpectedReturnOnPlanAssets",
        "RecognizedNetGainLoss",
        "Settlement",
        "Curtailment"
    ]

    for palabra in palabras:

        print("\n" + "=" * 90)
        print(f"BÚSQUEDA: {palabra}")
        print("=" * 90)

        resultados = listar_conceptos_por_palabra(
            ticker="CVX",
            palabra=palabra,
            limite=100
        )

        for resultado in resultados:
            print(
                resultado["concept"],
                "|",
                resultado["label"],
                "|",
                resultado["unit"],
                "| Registros:",
                resultado["numero_registros"],
                "| Última publicación:",
                resultado["ultima_publicacion"]
            )









