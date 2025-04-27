"""Tool for querying financial data through the Yahoo Finance API."""
from typing import Dict, Any
import json
import yfinance as yf
import pandas as pd
from langchain_core.tools import Tool

def get_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Gets general information about a stock.

    Args:
        ticker: Stock symbol (e.g., AAPL, MSFT)

    Returns:
        Dict: Company and stock information
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        relevant_info = {
            "nombre": info.get("shortName", ""),
            "sector": info.get("sector", ""),
            "industria": info.get("industry", ""),
            "descripcion": info.get("longBusinessSummary", "")[:300] + "...",
            "precio_actual": info.get("currentPrice", 0),
            "cambio_porcentual": info.get("regularMarketChangePercent", 0),
            "precio_apertura": info.get("regularMarketOpen", 0),
            "precio_cierre_anterior": info.get("regularMarketPreviousClose", 0),
            "rango_dia": f"{info.get('regularMarketDayLow', 0)} - {info.get('regularMarketDayHigh', 0)}",
            "rango_52_semanas": f"{info.get('fiftyTwoWeekLow', 0)} - {info.get('fiftyTwoWeekHigh', 0)}",
            "volumen": info.get("regularMarketVolume", 0),
            "capitalizacion_mercado": info.get("marketCap", 0),
            "beta": info.get("beta", 0),
            "PE_ratio": info.get("trailingPE", 0),
            "EPS": info.get("trailingEps", 0),
            "dividendo_yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0,
            "fecha_consulta": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return {
            "success": True,
            "ticker": ticker.upper(),
            "datos": relevant_info
        }
    except Exception as e:
        return {
            "success": False,
            "ticker": ticker,
            "error": str(e)
        }

def get_stock_price_history(
        ticker: str,
        period: str = "1mo",
        interval: str = "1d",
) -> Dict[str, Any]:
    """
    Gets a stock's price history.

    Args:
        ticker: Stock symbol (e.g., AAPL, MSFT)
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Interval between data points (1m, 2m, 
        5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

    Returns:
        Dict: Historical price data
    """
    try:
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
        valid_intervals = ["1m", "2m", "5m", "15m", "30m",
                           "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

        if period not in valid_periods:
            return {
                "success": False,
                "ticker": ticker,
                "error": f"Período inválido. Debe ser uno de: {', '.join(valid_periods)}"
            }

        if interval not in valid_intervals:
            return {
                "success": False,
                "ticker": ticker,
                "error": f"Intervalo inválido. Debe ser uno de: {', '.join(valid_intervals)}"
            }

        stock = yf.Ticker(ticker)
        history = stock.history(period=period, interval=interval)

        price_data = []
        for date, row in history.iterrows():
            price_data.append({
                "fecha": date.strftime("%Y-%m-%d %H:%M:%S"),
                "apertura": round(row["Open"], 2),
                "alto": round(row["High"], 2),
                "bajo": round(row["Low"], 2),
                "cierre": round(row["Close"], 2),
                "volumen": int(row["Volume"])
            })
        return {
            "success": True,
            "ticker": ticker.upper(),
            "period": period,
            "interval": interval,
            "datos": price_data
        }
    except Exception as e:
        return {
            "success": False,
            "ticker": ticker,
            "error": str(e)
        }

def get_financial_statements(ticker: str, statement_type: str = "income") -> Dict[str, Any]:
    """
    Obtains a company's financial statements.

    Args:
        ticker: Stock symbol (e.g., AAPL, MSFT)
        statement_type: Type of financial statement (income, balance, cash)

    Returns:
        Dict: Data from the requested financial statement
    """
    try:
        valid_types = ["income", "balance", "cash"]
        if statement_type not in valid_types:
            return {
                "success": False,
                "ticker": ticker,
                "error": f"Tipo de estado financiero inválido. Debe ser uno de: {', '.join(valid_types)}"
            }

        stock = yf.Ticker(ticker)

        if statement_type == "income":
            statement = stock.income_stmt
            statement_name = "Estado de Resultados"
        elif statement_type == "balance":
            statement = stock.balance_sheet
            statement_name = "Balance General"
        else:
            statement = stock.cashflow
            statement_name = "Flujo de Efectivo"

        if statement.empty:
            return {
                "success": False,
                "ticker": ticker,
                "error": f"No hay datos disponibles para el {statement_name}"
            }

        statement_dict = {}
        for column in statement.columns:
            column_date = pd.to_datetime(column).strftime("%Y-%m-%d")
            statement_dict[column_date] = {}

            for index in statement.index:
                value = statement.loc[index, column]
                # Convertir a número Python nativo (en lugar de numpy.int64, etc.)
                if pd.notnull(value):
                    statement_dict[column_date][index] = float(value)
                else:
                    statement_dict[column_date][index] = None

        return {
            "success": True,
            "ticker": ticker.upper(),
            "statement_type": statement_type,
            "statement_name": statement_name,
            "datos": statement_dict
        }
    except Exception as e:
        return {
            "success": False,
            "ticker": ticker,
            "error": str(e)
        }

def execute_financial_api_query(query: str) -> str:
    """
    Processes a query for the financial API.

    Args:
        query: Query in JSON format

    Returns:
        str: Query result in human-readable format
    """
    try:
        try:
            query_data = json.loads(query)
        except json.JSONDecodeError:
            parts = query.strip().split()
            if len(parts) >= 1:
                action = "info" 
                ticker = parts[0]

                if len(parts) >= 2 and parts[1] in ["info", "price", "history", "financials"]:
                    action = parts[1]

                query_data = {"action": action, "ticker": ticker}

                # Parámetros adicionales
                if len(parts) >= 3 and action == "history":
                    query_data["period"] = parts[2]
                if len(parts) >= 4 and action == "history":
                    query_data["interval"] = parts[3]
                if len(parts) >= 3 and action == "financials":
                    query_data["statement_type"] = parts[2]
            else:
                return "Error: Formato de consulta inválido. Por favor, proporciona al menos un símbolo de ticker."

        if "ticker" not in query_data:
            return "Error: Se requiere un símbolo de ticker (ej: AAPL, MSFT)."

        ticker = query_data["ticker"].upper()
        action = query_data.get("action", "info").lower()

        if action == "info":
            result = get_stock_info(ticker)
        elif action in ["price", "history"]:
            period = query_data.get("period", "1mo")
            interval = query_data.get("interval", "1d")
            result = get_stock_price_history(ticker, period, interval)
        elif action == "financials":
            statement_type = query_data.get("statement_type", "income")
            result = get_financial_statements(ticker, statement_type)
        else:
            return f"Error: Acción '{action}' no reconocida. Las acciones disponibles son: info, price/history, financials."


        if not result["success"]:
            return f"Error al consultar datos para {ticker}: {result.get('error', 'Error desconocido')}"


        if action == "info":
            info = result["datos"]
            response = [
                f"Información de {result['ticker']} - {info['nombre']} ({info['fecha_consulta']})",
                f"Sector: {info['sector']} | Industria: {info['industria']}",
                f"Precio actual: ${info['precio_actual']:.2f} ({info['cambio_porcentual']:.2f}%)",
                f"Rango del día: ${info['rango_dia']}",
                f"Capitalización de mercado: ${info['capitalizacion_mercado']:,.0f}",
                f"P/E ratio: {info['PE_ratio']:.2f} | EPS: ${info['EPS']:.2f}",
                f"Dividendo yield: {info['dividendo_yield']:.2f}%",
                f"\nDescripción: {info['descripcion']}"
            ]
            return "\n".join(response)

        elif action in ["price", "history"]:
            data = result["datos"]
            if not data:
                return f"No hay datos históricos disponibles para {ticker} con período {result['period']} e intervalo {result['interval']}."

            max_items = 5
            if len(data) > max_items * 2:
                visible_data = data[:max_items] + [{"fecha": "...", "apertura": "...", "cierre": "..."}] + data[-max_items:]
            else:
                visible_data = data

            response = [
                f"Historial de precios para {result['ticker']} (Período: {result['period']}, Intervalo: {result['interval']})",
                "\nFecha | Apertura | Cierre | Alto | Bajo | Volumen"
            ]

            for item in visible_data:
                if item["fecha"] == "...":
                    response.append("...")
                else:
                    response.append(
                        f"{item['fecha']} | ${item['apertura']:.2f} | ${item['cierre']:.2f} | "
                        f"${item['alto']:.2f} | ${item['bajo']:.2f} | {item['volumen']:,}"
                    )

            if len(data) >= 2:
                primer_precio = data[0]["cierre"]
                ultimo_precio = data[-1]["cierre"]
                cambio = ultimo_precio - primer_precio
                cambio_pct = (cambio / primer_precio) * 100
                response.append(f"\nVariación en el período: ${cambio:.2f} ({cambio_pct:.2f}%)")

            return "\n".join(response)

        elif action == "financials":
            statement_name = result["statement_name"]
            data = result["datos"]

            response = [f"{statement_name} para {result['ticker']}"]

            periodos = sorted(data.keys())

            if not periodos:
                return f"No hay datos financieros disponibles para {ticker}."

            periodo_muestra = periodos[-1]
            response.append(f"\nPeríodo: {periodo_muestra}")

            muestra_items = list(data[periodo_muestra].items())[:10]
            for concepto, valor in muestra_items:
                if valor is not None:
                    if abs(valor) >= 1e9:
                        valor_fmt = f"${valor/1e9:.2f} mil millones"
                    elif abs(valor) >= 1e6:
                        valor_fmt = f"${valor/1e6:.2f} millones"
                    else:
                        valor_fmt = f"${valor:,.2f}"
                    response.append(f"{concepto}: {valor_fmt}")
                else:
                    response.append(f"{concepto}: No disponible")

            if len(data[periodo_muestra]) > 10:
                response.append("... (se muestran 10 de los conceptos principales)")

            response.append(f"\nPeríodos disponibles: {', '.join(periodos)}")

            return "\n".join(response)

        return "Error: No se pudo procesar la consulta."

    except Exception as e:
        return f"Error al procesar la consulta: {str(e)}"

def create_financial_api_tool() -> Tool:
    """
    Create a tool to query financial data.

    Returns:
        Tool: Tool to query the financial API
    """
    return Tool(
        name="financial_data_api",
        description="""
        Consulta datos financieros actualizados de empresas que cotizan en bolsa.
        Útil para obtener precios actuales, información sobre empresas, datos históricos y estados financieros.
        
        Se debe proporcionar:
        - Un símbolo de ticker (obligatorio): ej. AAPL, MSFT, GOOGL
        - Acción a realizar (opcional):
            - "info": Información general de la empresa y precio actual (default)
            - "history": Historial de precios
            - "financials": Estados financieros
        
        Para historial de precios, se puede especificar:
        - period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        - interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        
        Para estados financieros, se puede especificar:
        - statement_type: income (resultados), balance (balance general), cash (flujo de efectivo)
        
        Formatos de consulta aceptados:
        1. JSON: {"ticker": "AAPL", "action": "info"}
        2. Texto: "AAPL info"
        """,
        func=execute_financial_api_query
    )
