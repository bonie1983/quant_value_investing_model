
from database_manager import obtener_conexion


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

CONCEPTOS_PENSION = [
    "PensionExpense",
    "NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent",
    "DefinedBenefitPlanRecognizedNetGainLossDueToSettlementsAndCurtailments1"
]


# ==========================================================
# INSPECCIONAR DEFINICIONES DE CONCEPTOS
# ==========================================================

def inspeccionar_definiciones_pensiones():

    """
    Consulta las definiciones contables de conceptos relacionados
    con pensiones almacenadas en fact_definitions.

    Muestra:
    - Taxonomía.
    - Concepto.
    - Etiqueta.
    - Descripción.
    """

    with obtener_conexion() as conexion:

        for concepto in CONCEPTOS_PENSION:

            print("\n" + "=" * 100)
            print(f"CONCEPTO: {concepto}")
            print("=" * 100)

            consulta = """
                SELECT
                    taxonomy,
                    concept,
                    label,
                    description

                FROM fact_definitions

                WHERE concept = ?

                ORDER BY taxonomy
            """

            resultado = conexion.execute(
                consulta,
                (concepto,)
            ).fetchall()

            if not resultado:

                print("Definición no encontrada.")
                continue

            for fila in resultado:

                print("Taxonomía:", fila["taxonomy"])
                print("Concepto:", fila["concept"])
                print("Etiqueta:", fila["label"])
                print("Descripción:", fila["description"])


# ==========================================================
# EJECUCIÓN
# ==========================================================

if __name__ == "__main__":

    inspeccionar_definiciones_pensiones()
