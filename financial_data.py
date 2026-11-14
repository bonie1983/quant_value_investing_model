
import os
import sqlite3


# ==========================================================
# 1. CONFIGURACIÓN
# ==========================================================

# Directorio principal del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta de nuestra base de datos
DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "quantitative_value.db"
)


# ==========================================================
# 2. CONEXIÓN CON SQLITE
# ==========================================================

def obtener_conexion():

    """
    Abre una conexión con nuestra base de datos SQLite.
    """

    if not os.path.exists(DATABASE_PATH):
        raise FileNotFoundError(
            f"No se encuentra la base de datos: {DATABASE_PATH}"
        )

    conexion = sqlite3.connect(DATABASE_PATH)

    # Permite acceder a las columnas por su nombre
    conexion.row_factory = sqlite3.Row

    return conexion


# ==========================================================
# 3. CONSULTAR EMPRESAS
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
# 4. PRUEBA DEL MÓDULO
# ==========================================================

if __name__ == "__main__":

    empresas = listar_empresas()

    print("\nEMPRESAS REGISTRADAS EN LA BASE DE DATOS")
    print("=" * 50)

    for empresa in empresas:

        print(
            empresa["ticker"],
            "-",
            empresa["name"],
            "-",
            empresa["sector"]
        )

    print("=" * 50)
    print(f"Total de empresas: {len(empresas)}")
