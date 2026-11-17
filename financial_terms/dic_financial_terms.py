# ==========================================================
# DICCIONARIO DE CONCEPTOS FINANCIEROS
# ==========================================================
#
# Estructura:
#   métrica -> ticker -> lista de conceptos SEC
#
# Los conceptos se prueban en el orden indicado.
# El primero que proporcione un dato válido será utilizado.
#
# ==========================================================

CONCEPTOS_FINANCIEROS = {

    "revenue": {

        "MSFT": [
            "RevenueFromContractWithCustomerExcludingAssessedTax"
        ],

        "KO": [
            "Revenues"
        ],

        "AMGN": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues"
        ],

        "CAT": [
            "Revenues"
        ],

        "CSCO": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues"
        ],

        "BA": ["Revenues"],
        "CRM": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "CVX": ["Revenues"],
        "DIS": ["Revenues"],
        "DOW": ["Revenues"],
        "HD": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "HON": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "IBM": ["Revenues"],
        "JNJ": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "MCD": ["Revenues"],
        "MMM": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "MRK": ["Revenues"],
        "NKE": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "PG": ["Revenues"],
        "SHW": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "TRV": ["Revenues"],
        "UNH": ["Revenues"],
        "V": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "VZ": ["Revenues"],
        "WMT": ["RevenueFromContractWithCustomerExcludingAssessedTax"]

    }
}