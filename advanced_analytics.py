
import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error


REQUIRED_COLUMNS = [
    "month",
    "transport_km",
    "electricity_kwh",
    "food_meals",
    "shopping_spend",
    "income",
]

DEFAULT_FACTORS = {
    "transport_km": 0.12,
    "electricity_kwh": 0.70,
    "food_meals": 1.80,
    "shopping_spend": 0.0002,
}


def validate_history(uploaded_file):
    """Validate a monthly history CSV."""
    df = pd.read_csv(uploaded_file)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing))
        )

    df = df[REQUIRED_COLUMNS].copy()

    for column in REQUIRED_COLUMNS[1:]:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    if df.isna().any().any():
        raise ValueError(
            "The file contains blank or non-numeric values."
        )

    if (df[REQUIRED_COLUMNS[1:]] < 0).any().any():
        raise ValueError(
            "Negative activity, spending, and income values "
            "are not allowed."
        )

    if df.empty:
        raise ValueError("The CSV contains no records.")

    df["month"] = df["month"].astype(str).str.strip()

    if (df["month"] == "").any():
        raise ValueError("Month values cannot be blank.")

    if df["month"].duplicated().any():
        raise ValueError(
            "Each month must be unique. Use one row per month."
        )

    return df


def calculate_historical_emissions(df, factors=None):
    """Calculate estimated emissions for each historical record."""
    factors = factors or DEFAULT_FACTORS
    result = df.copy()

    result["transport_emissions"] = (
        result["transport_km"] * factors["transport_km"]
    )

    result["electricity_emissions"] = (
        result["electricity_kwh"] * factors["electricity_kwh"]
    )

    result["food_emissions"] = (
        result["food_meals"] * factors["food_meals"]
    )

    result["shopping_emissions"] = (
        result["shopping_spend"] * factors["shopping_spend"]
    )

    emission_columns = [
        "transport_emissions",
        "electricity_emissions",
        "food_emissions",
        "shopping_emissions",
    ]

    result["total_emissions"] = result[
        emission_columns
    ].sum(axis=1)

    # The sample history CSV does not include all expense categories,
    # so do not mislabel income as a calculated financial balance.
    result["income_recorded"] = result["income"]

    return result


def trend_summary(series):
    """Summarize the first-to-last change in a numeric series."""
    values = pd.to_numeric(
        series, errors="coerce"
    ).dropna()

    if len(values) < 2:
        return {
            "first": None,
            "last": None,
            "change": None,
            "change_percent": None,
        }

    first = float(values.iloc[0])
    last = float(values.iloc[-1])
    change = last - first

    percent = (
        change / abs(first) * 100
        if first != 0 else None
    )

    return {
        "first": round(first, 2),
        "last": round(last, 2),
        "change": round(change, 2),
        "change_percent": (
            round(percent, 2)
            if percent is not None else None
        ),
    }


def trend_forecast(values, horizon=3):
    """Linear trend forecast with chronological holdout evaluation."""
    y = pd.to_numeric(
        values, errors="coerce"
    ).to_numpy(dtype=float)

    if len(y) < 4 or not np.isfinite(y).all():
        raise ValueError(
            "Provide at least 4 complete, finite observations."
        )

    if horizon < 1:
        raise ValueError("Forecast horizon must be positive.")

    # Reserve the latest observations for a simple holdout evaluation.
    split = max(2, int(len(y) * 0.75))
    split = min(split, len(y) - 1)

    train_x = np.arange(split).reshape(-1, 1)
    test_x = np.arange(split, len(y)).reshape(-1, 1)

    holdout_model = LinearRegression()
    holdout_model.fit(train_x, y[:split])

    holdout_prediction = holdout_model.predict(test_x)

    mae = mean_absolute_error(
        y[split:], holdout_prediction
    )

    # Fit again on all available observations for future estimates.
    final_model = LinearRegression()
    final_model.fit(
        np.arange(len(y)).reshape(-1, 1), y
    )

    future_x = np.arange(
        len(y), len(y) + horizon
    ).reshape(-1, 1)

    future = final_model.predict(future_x)

    return {
        "forecast": np.round(future, 2).tolist(),
        "holdout_mae": round(float(mae), 2),
        "model": "Linear regression trend baseline",
        "training_observations": len(y),
        "holdout_observations": len(y) - split,
    }


def sensitivity_analysis(
    activity,
    factor,
    percentages=(0.8, 1.0, 1.2),
):
    """Test the effect of alternative emission-factor assumptions."""
    activity = max(0.0, float(activity))
    factor = max(0.0, float(factor))

    return pd.DataFrame([
        {
            "Factor scenario": f"{multiplier:.0%} of baseline",
            "Emission factor": factor * multiplier,
            "Estimated emissions (kg CO2e)": (
                activity * factor * multiplier
            ),
        }
        for multiplier in percentages
    ])
