from __future__ import annotations
import pandas as pd

def forecast_revenue(units: pd.Series, price: pd.Series) -> pd.Series:
    if len(units) != len(price):
        raise ValueError("units and price must have the same length")
    return units * price

def operating_profit(revenue: pd.Series, variable_cost: pd.Series, fixed_cost: pd.Series) -> pd.Series:
    return revenue - variable_cost - fixed_cost
