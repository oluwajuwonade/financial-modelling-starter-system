# Financial Modelling Starter System

> Reusable FP&A-style financial model covering assumptions, forecasting, scenarios, sensitivities, and model QA.

## Business Problem

Decision-makers need a model that links assumptions to revenue, costs, cash generation, and downside/upside outcomes without becoming a black box.

## Analytical Questions

- Where is the forecast most sensitive to operating assumptions?\n- What drives the largest profit and cash changes?\n- What happens under base, upside, and downside scenarios?\n- Which model controls should be checked before decision use?

## Deliverables

- Assumptions input layer\n- Revenue and cost forecast\n- Three-statement-style model structure\n- Scenario manager\n- Sensitivity tables\n- Model QA checklist\n- Executive summary

## Suggested Repository Structure

```text
financial-modelling-starter-system/
├── data/
├── notebooks/
├── src/
├── tests/
├── outputs/
├── README.md
└── requirements.txt
```

## Stack

Python, pandas, NumPy, Excel-compatible outputs, Plotly

## Method

1. Define the decision context and metric definitions.
2. Profile and validate the data.
3. Build reproducible transformations and calculations.
4. Quantify the main drivers, scenarios, or failure modes.
5. Validate outputs and document limitations.
6. Produce an executive-ready decision narrative.

## Portfolio Standard

Use synthetic or public data with documented provenance. Clearly distinguish measured results from assumptions and illustrative scenarios.
