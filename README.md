
# EcoTwin Nexus 2.0
## Personal Carbon & Economic Intelligence Platform

EcoTwin Nexus is a sustainability and personal-finance analytics prototype
that combines interactive scenario modeling, historical data analysis,
baseline forecasting, sensitivity analysis, and transparent reporting.

### Features

- Interactive sustainability and finance dashboard
- Current-versus-alternative lifestyle simulation
- Multi-objective scenario analysis across 256 combinations
- Pareto-efficient scenario identification
- Cumulative financial balance projections
- CSV upload and data validation
- Historical emissions analysis
- Linear trend forecast with chronological holdout MAE
- Emission-factor sensitivity analysis
- Downloadable CSV reports
- Premium dark-green Streamlit interface

### Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- scikit-learn

### Project Structure

```text
personal-carbon-economic-twin/
├── app.py
├── engine.py
├── advanced_analytics.py
├── requirements.txt
├── README.md
└── data/
    └── lifestyle_data.csv
```

### Installation on Windows

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

### Historical CSV Columns

The uploaded CSV must contain:

- month
- transport_km
- electricity_kwh
- food_meals
- shopping_spend
- income

Use one row per month.

### Model Limitations

The initial emission factors are illustrative prototype assumptions,
not verified local factors or audited emissions measurements.

Shopping emissions are estimated from spending, not product-level
life-cycle data. Financial savings are simplified assumptions and
are not guaranteed outcomes.

The forecast is a linear regression baseline. It may perform poorly
on small datasets and is not a guarantee of future emissions.

This version uses deterministic calculations and rule-based insights.
It does not include a live generative AI integration.

### Portfolio Purpose

Demonstrates interactive analytics, data validation, scenario analysis,
multi-objective optimization, forecast evaluation, and transparent
decision-support design.
