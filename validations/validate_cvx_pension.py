
from database_manager import obtener_conexion


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

TICKER = "CVX"

FECHA_CORTE = "2026-11-15"

LIMITE = 5

CONCEPTOS_PENSION = [
    "NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent",
    "PensionExpense",
    "DefinedBenefitPlanNetPeriodicBenefitCost"
]


# ==========================================================
# INSPECCIONAR CONCEPTOS DE PENSIONES
# ==========================================================

def inspeccionar_conceptos_pensiones():

    """
    Inspecciona las observaciones anuales de diferentes
    conceptos contables relacionados con pensiones de Chevron.

    No modifica la base de datos.
    """

    with obtener_conexion() as conexion:

        for concepto in CONCEPTOS_PENSION:

            print("\n" + "=" * 100)
            print(f"EMPRESA: {TICKER}")
            print(f"CONCEPTO: {concepto}")
            print(f"FECHA DE CORTE: {FECHA_CORTE}")
            print("=" * 100)

            consulta = """
                SELECT
                    value,
                    start_date,
                    end_date,
                    fiscal_year,
                    fiscal_period,
                    form,
                    filed_date,
                    accession_number

                FROM financial_facts

                WHERE ticker = ?
                    AND taxonomy = 'us-gaap'
                    AND concept = ?
                    AND unit = 'USD'
                    AND form = '10-K'
                    AND start_date IS NOT NULL
                    AND end_date IS NOT NULL
                    AND filed_date <= ?

                    AND (
                        julianday(end_date) - julianday(start_date)
                    ) BETWEEN 329 AND 379

                ORDER BY
                    end_date DESC,
                    filed_date DESC

                LIMIT ?
            """

            resultados = conexion.execute(
                consulta,
                (
                    TICKER,
                    concepto,
                    FECHA_CORTE,
                    LIMITE
                )
            ).fetchall()

            if not resultados:

                print("Sin observaciones anuales.")
                continue

            for fila in resultados:

                print(
                    f"Valor: {fila['value']:,.0f} USD | "
                    f"Periodo: {fila['start_date']} - "
                    f"{fila['end_date']} | "
                    f"FY: {fila['fiscal_year']} | "
                    f"Publicado: {fila['filed_date']} | "
                    f"Accession: {fila['accession_number']}"
                )


# ==========================================================
# EJECUCIÓN
# ==========================================================

if __name__ == "__main__":

    inspeccionar_conceptos_pensiones()
