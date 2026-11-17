"""
Diccionario de conceptos SEC utilizados para construir EBIT.

Cada empresa puede tener diferentes conceptos contables
y distintas alternativas de cálculo.

Este archivo identifica los conceptos disponibles.
No define todavía las reglas matemáticas del cálculo.
"""



EBIT_CONCEPTS = {
    "NKE": {
        "pretax_income": [
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"
        ],
        "interest_expense": [],
        "operating_income": [
            "OperatingIncomeLoss"
        ]
    },

    "CVX": {
        "pretax_income": [
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"
        ],
        "interest_expense": [
            "InterestExpenseDebt"
        ],
        "operating_income": []
    },

    "DOW": {
        "pretax_income": [
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"
        ],
        "interest_expense": [
            "InterestExpenseDebt"
        ],
        "interest_income": [
            "InterestIncomeOther"
        ],
        "nonoperating_income_expense": [
            "NonoperatingIncomeExpense"
        ],
        "equity_method_income": [
            "IncomeLossFromEquityMethodInvestments"
        ],
        "restructuring_charges": [
            "RestructuringCostsAndAssetImpairmentCharges"
        ],
        "finance_lease_interest": [
            "FinanceLeaseInterestExpense"
        ],
        "operating_income": []
    }
}
