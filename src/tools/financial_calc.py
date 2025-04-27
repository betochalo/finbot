"""
Herramienta para realizar cálculos financieros.
"""

import json
import math
from typing import Dict, Any, List

import numpy as np
from langchain_core.tools import Tool


def parse_calculation_request(query: str) -> Dict[str, Any]:
    """
    Parses a query for the financial calculator.

    Args:
        query: Query in text or JSON format

    Returns:
        Dict: Parameters for the calculation
    """
    try:
        try:
            params = json.loads(query)
        except json.JSONDecodeError:
            params = parse_text_query(query)

        if "type" not in params:
            return {
                "success": False,
                "error": "Se requiere especificar el tipo de cálculo."
            }

        return {
            "success": True,
            "params": params
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def parse_text_query(query: str) -> Dict[str, Any]:
    """
    Parses a text query into parameters.

    Args:
        query: Text query

    Returns:
        Dict: Extracted parameters
    """
    parts = query.strip().split()

    if not parts:
        raise ValueError("Consulta vacía")

    calc_type = parts[0].lower()
    params = {"type": calc_type}

    if calc_type in ["roi", "retorno"]:
        if len(parts) >= 3:
            params["initial"] = float(parts[1])
            params["final"] = float(parts[2])

    elif calc_type in ["compuesto", "interes_compuesto"]:
        if len(parts) >= 4:
            params["principal"] = float(parts[1])
            params["rate"] = float(parts[2])
            params["periods"] = float(parts[3])
            if len(parts) >= 5:
                params["frequency"] = parts[4]

    elif calc_type in ["prestamo", "loan"]:
        if len(parts) >= 4:
            params["principal"] = float(parts[1])
            params["rate"] = float(parts[2])
            params["periods"] = float(parts[3])

    elif calc_type in ["ratio", "ratios"]:
        if len(parts) >= 2:
            params["ratio_name"] = parts[1]
            params["values"] = [float(p) for p in parts[2:]]

    elif calc_type in ["npv", "van"]:
        if len(parts) >= 3:
            params["rate"] = float(parts[1])
            params["cash_flows"] = [float(p) for p in parts[2:]]

    elif calc_type in ["irr", "tir"]:
        if len(parts) >= 2:
            params["cash_flows"] = [float(p) for p in parts[1:]]

    elif calc_type in ["compare", "comparar"]:
        if len(parts) >= 3:
            params["metric"] = parts[1]
            params["tickers"] = parts[2:]

    else:
        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                try:
                    params[key] = float(value)
                except ValueError:
                    params[key] = value
    return params


def calculate_roi(initial_investment: float, final_value: float) -> Dict[str, Any]:
    """
    Calculates the return on investment (ROI).

    Args:
        initial_investment: Initial investment
        final_value: Final value

    Returns:
        Dict: Calculation result
    """
    if initial_investment <= 0:
        return {
            "success": False,
            "error": "La inversión inicial debe ser mayor que cero."
        }

    roi = (final_value - initial_investment) / initial_investment
    roi_percent = roi * 100
    return {
        "success": True,
        "result": {
            "roi": roi,
            "roi_percent": roi_percent,
            "initial_investment": initial_investment,
            "final_value": final_value,
            "profit_loss": final_value - initial_investment
        }
    }


def calculate_compound_interest(
    principal: float,
    rate: float,
    periods: float,
    frequency: str = "annual"
) -> Dict[str, Any]:
    """
    Calculate compound interest.

    Args:
        Principal: Initial principal
        Rate: Interest rate (in percentage)
        Periods: Number of periods
        Frequency: Compounding frequency

    Returns:
        Dict: Calculation result
    """
    if principal <= 0:
        return {
            "success": False,
            "error": "El capital inicial debe ser mayor que cero."
        }

    if rate <= 0:
        return {
            "success": False,
            "error": "La tasa de interés debe ser mayor que cero."
        }
    rate_decimal = rate / 100

    frequency_map = {
        "annual": 1,
        "semiannual": 2,
        "quarterly": 4,
        "monthly": 12,
        "daily": 365
    }

    compound_frequency = frequency_map.get(frequency.lower(), 1)

    n = compound_frequency * periods
    r = rate_decimal / compound_frequency

    final_amount = principal * math.pow(1 + r, n)
    interest_earned = final_amount - principal

    return {
        "success": True,
        "result": {
            "principal": principal,
            "rate": rate,
            "periods": periods,
            "frequency": frequency,
            "compound_frequency": compound_frequency,
            "final_amount": final_amount,
            "interest_earned": interest_earned
        }
    }


def calculate_loan_payment(
    principal: float,
    rate: float,
    periods: float
) -> Dict[str, Any]:
    """
    Calculate the monthly loan payment.

    Args:
        Principal: Loan amount
        Rate: Annual interest rate (in percentage)
        Periods: Number of periods (months)

    Returns:
        Dict: Calculation result
    """
    if principal <= 0:
        return {
            "success": False,
            "error": "El monto del préstamo debe ser mayor que cero."
        }

    if rate <= 0:
        return {
            "success": False,
            "error": "La tasa de interés debe ser mayor que cero."
        }

    if periods <= 0:
        return {
            "success": False,
            "error": "El número de períodos debe ser mayor que cero."
        }

    monthly_rate = (rate / 100) / 12

    if monthly_rate == 0:
        monthly_payment = principal / periods
    else:
        monthly_payment = principal * (monthly_rate * math.pow(1 + monthly_rate, periods)) / (math.pow(1 + monthly_rate, periods) - 1)

    remaining_balance = principal
    amortization_schedule = []
    total_interest = 0

    for period in range(1, int(periods) + 1):
        interest_payment = remaining_balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        total_interest += interest_payment

        if period <= 5 or period > periods - 5:
            amortization_schedule.append({
                "periodo": period,
                "pago": monthly_payment,
                "principal": principal_payment,
                "interes": interest_payment,
                "balance_restante": max(0, remaining_balance)
            })

    return {
        "success": True,
        "result": {
            "principal": principal,
            "rate": rate,
            "periods": periods,
            "monthly_payment": monthly_payment,
            "total_payments": monthly_payment * periods,
            "total_interest": total_interest,
            "amortization_sample": amortization_schedule
        }
    }


def calculate_financial_ratio(ratio_name: str, values: List[float]) -> Dict[str, Any]:
    """
    Calculates common financial ratios.

    Args:
        ratio_name: Name of the ratio to calculate
        values: Values Required for the calculation

    Returns:
        Dict: Result of the calculation
    """
    ratio_name = ratio_name.lower()

    ratios = {
        "current": {
            "description": "Ratio de liquidez corriente (Activo Corriente / Pasivo Corriente)",
            "required_values": 2,
            "labels": ["Activo Corriente", "Pasivo Corriente"]
        },
        "quick": {
            "description": "Ratio de prueba ácida ((Activo Corriente - Inventarios) / Pasivo Corriente)",
            "required_values": 3,
            "labels": ["Activo Corriente", "Inventarios", "Pasivo Corriente"]
        },
        "debt": {
            "description": "Ratio de endeudamiento (Pasivo Total / Activo Total)",
            "required_values": 2,
            "labels": ["Pasivo Total", "Activo Total"]
        },
        "roe": {
            "description": "Return on Equity - ROE (Beneficio Neto / Patrimonio Neto)",
            "required_values": 2,
            "labels": ["Beneficio Neto", "Patrimonio Neto"]
        },
        "roa": {
            "description": "Return on Assets - ROA (Beneficio Neto / Activos Totales)",
            "required_values": 2,
            "labels": ["Beneficio Neto", "Activos Totales"]
        },
        "profit_margin": {
            "description": "Margen de Beneficio Neto (Beneficio Neto / Ventas Netas)",
            "required_values": 2,
            "labels": ["Beneficio Neto", "Ventas Netas"]
        },
        "pe": {
            "description": "Price-to-Earnings Ratio (Precio por Acción / Beneficio por Acción)",
            "required_values": 2,
            "labels": ["Precio por Acción", "Beneficio por Acción (EPS)"]
        },
        "pb": {
            "description": "Price-to-Book Ratio (Precio por Acción / Valor en Libros por Acción)",
            "required_values": 2,
            "labels": ["Precio por Acción", "Valor en Libros por Acción"]
        }
    }

    if ratio_name not in ratios:
        return {
            "success": False,
            "error": f"Ratio no reconocido. Ratios disponibles: {', '.join(ratios.keys())}"
        }

    ratio_info = ratios[ratio_name]
    required_values = ratio_info["required_values"]

    if len(values) < required_values:
        return {
            "success": False,
            "error": f"El ratio '{ratio_name}' requiere {required_values} valores: {', '.join(ratio_info['labels'])}"
        }

    for i, value in enumerate(values):
        label = ratio_info["labels"][i]
        if "Pasivo" not in label and value < 0:
            return {
                "success": False,
                "error": f"El valor para '{label}' debe ser mayor o igual a cero."
            }

    result = None
    explanation = ""
    
    if ratio_name == "current":
        if values[1] == 0:
            return {
                "success": False,
                "error": "El pasivo corriente no puede ser cero."
            }
        result = values[0] / values[1]
        explanation = (
            f"Un ratio de liquidez corriente de {result:.2f} significa que la empresa "
            f"tiene ${result:.2f} de activos corrientes por cada $1 de pasivos corrientes. "
        )
        if result < 1:
            explanation += "Esto puede indicar problemas para cubrir las obligaciones a corto plazo."
        elif result >= 1 and result < 1.5:
            explanation += "Esto indica una capacidad adecuada para cubrir las obligaciones a corto plazo."
        else:
            explanation += "Esto indica una buena liquidez, aunque un ratio muy alto podría sugerir un uso ineficiente de los activos."

    elif ratio_name == "quick":
        if values[2] == 0:
            return {
                "success": False,
                "error": "El pasivo corriente no puede ser cero."
            }
        result = (values[0] - values[1]) / values[2]
        explanation = (
            f"Un ratio de prueba ácida de {result:.2f} significa que la empresa "
            f"tiene ${result:.2f} de activos líquidos por cada $1 de pasivos corrientes. "
        )
        if result < 1:
            explanation += "Esto podría indicar dificultades para cubrir las obligaciones a corto plazo sin vender inventarios."
        else:
            explanation += "Esto indica una buena capacidad para cubrir las obligaciones a corto plazo sin depender de los inventarios."

    elif ratio_name == "debt":
        if values[1] == 0:
            return {
                "success": False,
                "error": "El activo total no puede ser cero."
            }
        result = values[0] / values[1]
        result_percent = result * 100
        explanation = (
            f"Un ratio de endeudamiento del {result_percent:.2f}% significa que el {result_percent:.2f}% "
            f"de los activos de la empresa están financiados con deuda. "
        )
        if result < 0.4:
            explanation += "Este nivel de endeudamiento es generalmente considerado bajo."
        elif result >= 0.4 and result < 0.6:
            explanation += "Este nivel de endeudamiento es generalmente considerado moderado."
        else:
            explanation += "Este nivel de endeudamiento es generalmente considerado alto."

    elif ratio_name == "roe":
        if values[1] == 0:
            return {
                "success": False,
                "error": "El patrimonio neto no puede ser cero."
            }
        result = values[0] / values[1]
        result_percent = result * 100
        explanation = (
            f"Un ROE del {result_percent:.2f}% significa que la empresa genera un beneficio de "
            f"${result:.2f} por cada $1 invertido por los accionistas. "
        )
        if result < 0.1:
            explanation += "Este retorno es generalmente considerado bajo."
        elif result >= 0.1 and result < 0.2:
            explanation += "Este retorno es generalmente considerado adecuado."
        else:
            explanation += "Este retorno es generalmente considerado bueno."

    elif ratio_name == "roa":
        if values[1] == 0:
            return {
                "success": False,
                "error": "Los activos totales no pueden ser cero."
            }
        result = values[0] / values[1]
        result_percent = result * 100
        explanation = (
            f"Un ROA del {result_percent:.2f}% significa que la empresa genera un beneficio de "
            f"${result:.2f} por cada $1 en activos. "
        )
        if result < 0.05:
            explanation += "Este retorno sobre activos es generalmente considerado bajo."
        elif result >= 0.05 and result < 0.1:
            explanation += "Este retorno sobre activos es generalmente considerado adecuado."
        else:
            explanation += "Este retorno sobre activos es generalmente considerado bueno."

    elif ratio_name == "profit_margin":
        if values[1] == 0:
            return {
                "success": False,
                "error": "Las ventas netas no pueden ser cero."
            }
        result = values[0] / values[1]
        result_percent = result * 100
        explanation = (
            f"Un margen de beneficio neto del {result_percent:.2f}% significa que la empresa "
            f"genera ${result:.2f} de beneficio por cada $1 de ventas. "
        )

        explanation += "La interpretación de este margen depende del sector de la empresa."
    
    elif ratio_name == "pe":
        if values[1] == 0:
            return {
                "success": False,
                "error": "El beneficio por acción (EPS) no puede ser cero."
            }
        result = values[0] / values[1]
        explanation = (
            f"Un ratio P/E de {result:.2f} significa que los inversores están dispuestos a pagar "
            f"${result:.2f} por cada $1 de beneficio por acción. "
        )
        if result < 10:
            explanation += "Este P/E es generalmente considerado bajo, lo que podría indicar que la acción está infravalorada."
        elif result >= 10 and result < 20:
            explanation += "Este P/E es generalmente considerado moderado."
        else:
            explanation += "Este P/E es generalmente considerado alto, lo que podría indicar que los inversores esperan un fuerte crecimiento futuro."

    elif ratio_name == "pb":
        if values[1] == 0:
            return {
                "success": False,
                "error": "El valor en libros por acción no puede ser cero."
            }
        result = values[0] / values[1]
        explanation = (
            f"Un ratio P/B de {result:.2f} significa que los inversores están dispuestos a pagar "
            f"${result:.2f} por cada $1 de valor en libros. "
        )
        if result < 1:
            explanation += "Este P/B es generalmente considerado bajo, lo que podría indicar que la acción está infravalorada."
        elif result >= 1 and result < 3:
            explanation += "Este P/B es generalmente considerado moderado."
        else:
            explanation += "Este P/B es generalmente considerado alto, lo que podría indicar que los inversores esperan un fuerte rendimiento sobre el patrimonio."

    return {
        "success": True,
        "result": {
            "ratio_name": ratio_name,
            "description": ratio_info["description"],
            "values": {ratio_info["labels"][i]: values[i] for i in range(min(len(values), len(ratio_info["labels"])))},
            "ratio_value": result,
            "ratio_percentage": result * 100 if ratio_name in ["debt", "roe", "roa", "profit_margin"] else None,
            "explanation": explanation
        }
    }


def calculate_npv(rate: float, cash_flows: List[float]) -> Dict[str, Any]:
    """
    Calculates the Net Present Value (NPV) of a series of cash flows.

    Args:
        rate: Discount rate (in percentage)
        cash_flows: List of cash flows (the first is usually negative, representing the initial investment)

    Returns:
        Dict: Calculation result
    """
    if not cash_flows:
        return {
            "success": False,
            "error": "Se requiere al menos un flujo de caja."
        }

    rate_decimal = rate / 100

    npv = 0
    for i, cf in enumerate(cash_flows):
        npv += cf / ((1 + rate_decimal) ** i)

    detailed_results = []
    for i, cf in enumerate(cash_flows):
        pv = cf / ((1 + rate_decimal) ** i)
        detailed_results.append({
            "periodo": i,
            "flujo_caja": cf,
            "valor_presente": pv
        })

    return {
        "success": True,
        "result": {
            "npv": npv,
            "rate": rate,
            "cash_flows": cash_flows,
            "detailed_results": detailed_results,
            "interpretation": (
                f"Un VAN de {npv:.2f} significa que el proyecto generará "
                f"{'beneficios' if npv > 0 else 'pérdidas'} por un valor presente de ${abs(npv):.2f}. "
                f"{'El proyecto es financieramente viable.' if npv > 0 else 'El proyecto no es financieramente viable.'}"
            )
        }
    }


def calculate_irr(cash_flows: List[float]) -> Dict[str, Any]:
    """
    Calculates the Internal Rate of Return (IRR) for a series of cash flows.

    Args:
        cash_flows: List of cash flows (the first is usually negative)

    Returns:
        Dict: Result of the calculation
    """
    if not cash_flows:
        return {
            "success": False,
            "error": "Se requiere al menos un flujo de caja."
        }

    has_positive = any(cf > 0 for cf in cash_flows)
    has_negative = any(cf < 0 for cf in cash_flows)

    if not (has_positive and has_negative):
        return {
            "success": False,
            "error": "Para calcular la TIR, se necesitan flujos de caja tanto positivos como negativos."
        }

    try:
        irr = np.irr(cash_flows)
        irr_percent = irr * 100

        return {
            "success": True,
            "result": {
                "irr": irr,
                "irr_percent": irr_percent,
                "cash_flows": cash_flows,
                "interpretation": (
                    f"Una TIR del {irr_percent:.2f}% significa que el proyecto genera un rendimiento del {irr_percent:.2f}%. "
                    f"Para determinar si el proyecto es viable, compare esta TIR con la tasa mínima de rendimiento requerida."
                )
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error al calcular la TIR: {str(e)}"
        }


def execute_financial_calculation(query: str) -> str:
    """
    Runs a financial calculation based on the query.

    Args:
        query: Query with the calculation parameters

    Returns:
        str: Calculation result in human-readable format
    """
    parsed = parse_calculation_request(query)

    if not parsed["success"]:
        return f"Error: {parsed['error']}"

    params = parsed["params"]
    calculation_type = params["type"].lower()

    result = None

    if calculation_type in ["roi", "retorno"]:
        if "initial" not in params or "final" not in params:
            return "Error: Se requieren los valores 'initial' (inversión inicial) y 'final' (valor final)."
        result = calculate_roi(params["initial"], params["final"])

    elif calculation_type in ["compuesto", "interes_compuesto"]:
        if "principal" not in params or "rate" not in params or "periods" not in params:
            return "Error: Se requieren los valores 'principal', 'rate' (tasa) y 'periods' (períodos)."
        frequency = params.get("frequency", "annual")
        result = calculate_compound_interest(params["principal"], params["rate"], params["periods"], frequency)

    elif calculation_type in ["prestamo", "loan"]:
        if "principal" not in params or "rate" not in params or "periods" not in params:
            return "Error: Se requieren los valores 'principal', 'rate' (tasa) y 'periods' (períodos)."
        result = calculate_loan_payment(params["principal"], params["rate"], params["periods"])

    elif calculation_type in ["ratio", "ratios"]:
        if "ratio_name" not in params or "values" not in params:
            return "Error: Se requieren los valores 'ratio_name' (nombre del ratio) y 'values' (valores para el cálculo)."
        result = calculate_financial_ratio(params["ratio_name"], params["values"])

    elif calculation_type in ["npv", "van"]:
        if "rate" not in params or "cash_flows" not in params:
            return "Error: Se requieren los valores 'rate' (tasa de descuento) y 'cash_flows' (flujos de caja)."
        result = calculate_npv(params["rate"], params["cash_flows"])

    elif calculation_type in ["irr", "tir"]:
        if "cash_flows" not in params:
            return "Error: Se requiere el valor 'cash_flows' (flujos de caja)."
        result = calculate_irr(params["cash_flows"])

    else:
        return f"Error: Tipo de cálculo '{calculation_type}' no reconocido."

    if not result["success"]:
        return f"Error en el cálculo: {result['error']}"

    if calculation_type in ["roi", "retorno"]:
        roi_data = result["result"]
        response = [
            f"Análisis de Retorno sobre Inversión (ROI):",
            f"Inversión inicial: ${roi_data['initial_investment']:.2f}",
            f"Valor final: ${roi_data['final_value']:.2f}",
            f"Ganancia/Pérdida: ${roi_data['profit_loss']:.2f}",
            f"ROI: {roi_data['roi_percent']:.2f}%",
            "",
            f"Interpretación: Por cada $1 invertido, {'se ganaron' if roi_data['roi'] > 0 else 'se perdieron'} ${abs(roi_data['roi']):.2f}."
        ]

    elif calculation_type in ["compuesto", "interes_compuesto"]:
        ci_data = result["result"]
        response = [
            f"Cálculo de Interés Compuesto:",
            f"Capital inicial: ${ci_data['principal']:.2f}",
            f"Tasa de interés: {ci_data['rate']:.2f}% ({ci_data['frequency']})",
            f"Período: {ci_data['periods']} años",
            f"Monto final: ${ci_data['final_amount']:.2f}",
            f"Interés ganado: ${ci_data['interest_earned']:.2f}",
            "",
            f"Nota: El interés se capitaliza {ci_data['frequency']} ({ci_data['compound_frequency']} veces por año)."
        ]

    elif calculation_type in ["prestamo", "loan"]:
        loan_data = result["result"]
        response = [
            f"Cálculo de Préstamo:",
            f"Monto del préstamo: ${loan_data['principal']:.2f}",
            f"Tasa de interés anual: {loan_data['rate']:.2f}%",
            f"Plazo: {loan_data['periods']} meses",
            f"Pago mensual: ${loan_data['monthly_payment']:.2f}",
            f"Total a pagar: ${loan_data['total_payments']:.2f}",
            f"Total de intereses: ${loan_data['total_interest']:.2f}",
            "",
            "Calendario de amortización (muestra):"
        ]

        for period in loan_data['amortization_sample']:
            response.append(
                f"Período {period['periodo']}: Pago ${period['pago']:.2f} "
                f"(Principal: ${period['principal']:.2f}, Interés: ${period['interes']:.2f}), "
                f"Balance restante: ${period['balance_restante']:.2f}"
            )

            if period['periodo'] == 5 and loan_data['periods'] > 10:
                response.append("...")

    elif calculation_type in ["ratio", "ratios"]:
        ratio_data = result["result"]

        response = [
            f"Cálculo de Ratio Financiero: {ratio_data['ratio_name']}",
            f"Descripción: {ratio_data['description']}",
            "",
            "Valores utilizados:"
        ]

        for label, value in ratio_data['values'].items():
            response.append(f"- {label}: ${value:.2f}")

        if ratio_data.get('ratio_percentage') is not None:
            response.append(f"\nResultado: {ratio_data['ratio_percentage']:.2f}%")
        else:
            response.append(f"\nResultado: {ratio_data['ratio_value']:.2f}")

        response.append(f"\nInterpretación: {ratio_data['explanation']}")

    elif calculation_type in ["npv", "van"]:
        npv_data = result["result"]

        response = [
            f"Cálculo del Valor Actual Neto (VAN):",
            f"Tasa de descuento: {npv_data['rate']:.2f}%",
            f"Flujos de caja: {', '.join([f'${cf:.2f}' for cf in npv_data['cash_flows']])}",
            f"VAN: ${npv_data['npv']:.2f}",
            "",
            "Detalle por período:"
        ]

        for period in npv_data['detailed_results']:
            response.append(
                f"Período {period['periodo']}: Flujo ${period['flujo_caja']:.2f}, "
                f"Valor presente: ${period['valor_presente']:.2f}"
            )

        response.append(f"\nInterpretación: {npv_data['interpretation']}")

    elif calculation_type in ["irr", "tir"]:
        irr_data = result["result"]

        response = [
            f"Cálculo de la Tasa Interna de Retorno (TIR):",
            f"Flujos de caja: {', '.join([f'${cf:.2f}' for cf in irr_data['cash_flows']])}",
            f"TIR: {irr_data['irr_percent']:.2f}%",
            "",
            f"Interpretación: {irr_data['interpretation']}"
        ]
    return "\n".join(response)


def create_financial_calculator_tool() -> Tool:
    """
    Create a tool for performing financial calculations.

    Returns:
        Tool: Financial Calculator Tool
    """
    return Tool(
        name="financial_calculator",
        description="""
        Realiza cálculos financieros como ROI, interés compuesto, pagos de préstamos, ratios financieros, VAN, y TIR.
        
        Tipos de cálculos disponibles:
        - ROI (Retorno sobre Inversión): "roi initial final"
        - Interés Compuesto: "compuesto principal rate periods [frequency]"
        - Préstamos: "prestamo principal rate periods"
        - Ratios Financieros: "ratio ratio_name value1 value2 ..."
            - Ratios disponibles: current, quick, debt, roe, roa, profit_margin, pe, pb
        - VAN (Valor Actual Neto): "van rate cf0 cf1 cf2 ..."
        - TIR (Tasa Interna de Retorno): "tir cf0 cf1 cf2 ..."
        
        Formatos de consulta aceptados:
        1. JSON: {"type": "roi", "initial": 1000, "final": 1500}
        2. Texto: "roi 1000 1500"
        """,
        func=execute_financial_calculation
    )
