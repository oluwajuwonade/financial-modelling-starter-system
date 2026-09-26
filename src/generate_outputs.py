from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from model import forecast_revenue, operating_profit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
DATA.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

SCENARIOS = {
    "Downside": {"volume_growth": 0.015, "price_growth": 0.005, "variable_cost_inflation": 0.030, "fixed_cost_inflation": 0.035},
    "Base": {"volume_growth": 0.030, "price_growth": 0.010, "variable_cost_inflation": 0.020, "fixed_cost_inflation": 0.025},
    "Upside": {"volume_growth": 0.045, "price_growth": 0.015, "variable_cost_inflation": 0.015, "fixed_cost_inflation": 0.020},
}
BASE = {"starting_units": 1000, "starting_price": 120.0, "starting_variable_cost": 58.0, "starting_fixed_cost": 45000.0}


def build_forecast(scenario: str, years: int = 3) -> pd.DataFrame:
    assumptions = SCENARIOS[scenario]
    rows = []
    units = float(BASE["starting_units"])
    price = BASE["starting_price"]
    variable_cost = BASE["starting_variable_cost"]
    fixed_cost = BASE["starting_fixed_cost"]
    for year in range(2026, 2026 + years):
        if year > 2026:
            units *= 1 + assumptions["volume_growth"]
            price *= 1 + assumptions["price_growth"]
            variable_cost *= 1 + assumptions["variable_cost_inflation"]
            fixed_cost *= 1 + assumptions["fixed_cost_inflation"]
        revenue = float(forecast_revenue(pd.Series([units]), pd.Series([price])).iloc[0])
        variable_total = units * variable_cost
        profit = float(operating_profit(pd.Series([revenue]), pd.Series([variable_total]), pd.Series([fixed_cost])).iloc[0])
        rows.append({"scenario": scenario, "year": year, "units": round(units, 1), "price": round(price, 2), "variable_cost_per_unit": round(variable_cost, 2), "fixed_cost": round(fixed_cost, 2), "revenue": round(revenue, 2), "variable_cost": round(variable_total, 2), "operating_profit": round(profit, 2), "operating_margin": round(profit / revenue, 4)})
    return pd.DataFrame(rows)


def main() -> None:
    assumptions = pd.DataFrame([{ "scenario": name, **BASE, **values } for name, values in SCENARIOS.items()])
    assumptions.to_csv(DATA / "assumptions.csv", index=False)
    all_forecasts = pd.concat([build_forecast(name) for name in SCENARIOS], ignore_index=True)
    all_forecasts.to_csv(OUTPUTS / "annual_forecast.csv", index=False)
    summary = all_forecasts[all_forecasts["year"] == 2028].copy()
    summary[["scenario", "revenue", "operating_profit", "operating_margin"]].to_csv(OUTPUTS / "scenario_summary.csv", index=False)

    base = all_forecasts[all_forecasts["scenario"] == "Base"]
    prices = np.arange(108, 133, 4)
    growths = np.arange(0.015, 0.051, 0.005)
    sensitivity = []
    for growth in growths:
        for price in prices:
            units = BASE["starting_units"] * (1 + growth) ** 2
            variable = BASE["starting_variable_cost"] * (1 + SCENARIOS["Base"]["variable_cost_inflation"]) ** 2
            fixed = BASE["starting_fixed_cost"] * (1 + SCENARIOS["Base"]["fixed_cost_inflation"]) ** 2
            revenue = units * price
            sensitivity.append({"volume_growth": growth, "price": price, "2028_operating_profit": revenue - units * variable - fixed})
    pd.DataFrame(sensitivity).to_csv(OUTPUTS / "sensitivity_profit.csv", index=False)

    plt.style.use("seaborn-v0_8-whitegrid")
    colors = {"Downside": "#C2413B", "Base": "#2563EB", "Upside": "#15803D"}
    fig, ax = plt.subplots(figsize=(9, 5.2))
    for scenario in SCENARIOS:
        subset = all_forecasts[all_forecasts["scenario"] == scenario]
        ax.plot(subset["year"], subset["operating_profit"] / 1000, marker="o", linewidth=2.5, label=scenario, color=colors[scenario])
    ax.set_title("Illustrative Operating Profit by Scenario", loc="left", weight="bold")
    ax.set_ylabel("Operating profit ($000)")
    ax.set_xlabel("Fiscal year")
    ax.legend(frameon=False, ncol=3)
    fig.tight_layout(); fig.savefig(OUTPUTS / "scenario_operating_profit.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.plot(base["year"], base["revenue"] / 1000, marker="o", linewidth=2.5, label="Revenue", color="#0F766E")
    ax.plot(base["year"], base["operating_profit"] / 1000, marker="o", linewidth=2.5, label="Operating profit", color="#2563EB")
    ax.fill_between(base["year"], base["operating_profit"] / 1000, alpha=0.12, color="#2563EB")
    ax.set_title("Base Case: Revenue and Operating Profit", loc="left", weight="bold")
    ax.set_ylabel("$000"); ax.set_xlabel("Fiscal year"); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(OUTPUTS / "base_case_forecast.png", dpi=180); plt.close(fig)

    pivot = pd.DataFrame(sensitivity).pivot(index="volume_growth", columns="price", values="2028_operating_profit") / 1000
    fig, ax = plt.subplots(figsize=(9, 5.2))
    im = ax.imshow(pivot.values, aspect="auto", cmap="Blues")
    ax.set_title("2028 Operating Profit Sensitivity", loc="left", weight="bold")
    ax.set_xlabel("Price ($)"); ax.set_ylabel("Annual volume growth")
    ax.set_xticks(range(len(pivot.columns))); ax.set_xticklabels([f"${x:.0f}" for x in pivot.columns])
    ax.set_yticks(range(len(pivot.index))); ax.set_yticklabels([f"{x:.1%}" for x in pivot.index])
    fig.colorbar(im, ax=ax, label="Operating profit ($000)")
    fig.tight_layout(); fig.savefig(OUTPUTS / "profit_sensitivity_heatmap.png", dpi=180); plt.close(fig)

    best = summary.loc[summary["operating_profit"].idxmax()]
    worst = summary.loc[summary["operating_profit"].idxmin()]
    (OUTPUTS / "executive_summary.md").write_text(f"""# Executive Summary — Illustrative Scenario Model\n\n**Scope:** Three-year FP&A-style forecast for a fictional subscription business using documented assumptions; no real company or market data is represented.\n\n## Headline results\n\n- Base-case 2028 revenue: **${summary.loc[summary.scenario == 'Base', 'revenue'].iloc[0]:,.0f}**.\n- Base-case 2028 operating profit: **${summary.loc[summary.scenario == 'Base', 'operating_profit'].iloc[0]:,.0f}** (**{summary.loc[summary.scenario == 'Base', 'operating_margin'].iloc[0]:.1%} margin**).\n- 2028 scenario range: **${worst.operating_profit:,.0f}–${best.operating_profit:,.0f}** operating profit.\n\n## Decision readout\n\nThe model is most exposed to the interaction between volume growth and price. Management should monitor realized price, unit growth, and variable cost per unit monthly, and re-run the sensitivity table when those drivers move outside the stated assumptions.\n\n## Controls\n\n- Units and price series have matching lengths before revenue calculation.\n- Revenue equals units multiplied by price.\n- Operating profit equals revenue less variable and fixed costs.\n- Scenario outputs are generated from the same calculation path.\n\n## Limitations\n\nThis is an illustrative portfolio artifact built from synthetic assumptions. It excludes taxes, working capital, financing, seasonality, churn, and balance-sheet mechanics.\n""")


if __name__ == "__main__":
    main()
