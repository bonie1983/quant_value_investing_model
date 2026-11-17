
from database_manager import obtener_conexion

conceptos = [
    "NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent",
    "PensionExpense",
    "DefinedBenefitPlanNetPeriodicBenefitCost"
]

with obtener_conexion() as conexion:

    for concepto in conceptos:

        print("\n" + "=" * 100)
        print(f"CONCEPTO: {concepto}")
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
            WHERE ticker = 'CVX'
              AND taxonomy = 'us-gaap'
              AND concept = ?
              AND unit = 'USD'
              AND form = '10-K'
              AND start_date IS NOT NULL
              AND end_date IS NOT NULL
              AND filed_date <= '2026-11-15'
              AND (
                  julianday(end_date) - julianday(start_date)
              ) BETWEEN 329 AND 379
            ORDER BY end_date DESC, filed_date DESC
            LIMIT 5
        """

        resultados = conexion.execute(
            consulta,
            (concepto,)
        ).fetchall()

        if not resultados:
            print("Sin observaciones anuales.")
            continue

        for fila in resultados:
            print(
                f"Valor: {fila['value']:,.0f} USD | "
                f"Periodo: {fila['start_date']} - {fila['end_date']} | "
                f"FY: {fila['fiscal_year']} | "
                f"Publicado: {fila['filed_date']} | "
                f"Accession: {fila['accession_number']}"
            )
