
from database_manager import obtener_conexion

conceptos = [
    "PensionExpense",
    "NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent",
    "DefinedBenefitPlanRecognizedNetGainLossDueToSettlementsAndCurtailments1"
]

with obtener_conexion() as conexion:

    for concepto in conceptos:

        print("\n" + "=" * 100)
        print(concepto)
        print("=" * 100)

        resultado = conexion.execute(
            """
            SELECT taxonomy, concept, label, description
            FROM fact_definitions
            WHERE concept = ?
            """,
            (concepto,)
        ).fetchall()

        if not resultado:
            print("Definición no encontrada.")
            continue

        for fila in resultado:
            print("Taxonomía:", fila["taxonomy"])
            print("Etiqueta:", fila["label"])
            print("Descripción:", fila["description"])
