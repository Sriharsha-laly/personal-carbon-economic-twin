
from itertools import product

# Illustrative prototype assumptions only.
# Replace these with documented, region-appropriate factors for real use.
FACTORS = {
    "transport_km": 0.12,
    "electricity_kwh": 0.70,
    "food_meals": 1.80,
    "shopping_spend": 0.0002,
}

CATEGORIES = {
    "transport_km": "Transport",
    "electricity_kwh": "Electricity",
    "food_meals": "Food",
    "shopping_spend": "Shopping",
}


def nonnegative(value):
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0


def carbon_analysis(lifestyle, factors=None):
    factors = factors or FACTORS
    breakdown = {}

    for field, category in CATEGORIES.items():
        activity = nonnegative(lifestyle.get(field, 0))
        factor = nonnegative(factors.get(field, FACTORS[field]))
        breakdown[category] = activity * factor

    return {
        "total": round(sum(breakdown.values()), 2),
        "breakdown": {
            category: round(value, 2)
            for category, value in breakdown.items()
        },
    }


def financial_analysis(income, expenses):
    income = nonnegative(income)

    normalized = {
        category: nonnegative(value)
        for category, value in expenses.items()
    }

    total_expenses = sum(normalized.values())
    balance = income - total_expenses

    return {
        "income": round(income, 2),
        "expenses": round(total_expenses, 2),
        "balance": round(balance, 2),
        "savings_rate": round(balance / income * 100, 1)
        if income > 0 else 0.0,
        "breakdown": normalized,
    }


def simulate_lifestyle(lifestyle, reductions, factors=None):
    alternative = {
        field: nonnegative(lifestyle.get(field, 0))
        for field in CATEGORIES
    }

    for field, percentage in reductions.items():
        if field in alternative:
            percentage = max(0.0, min(100.0, float(percentage)))
            alternative[field] *= 1 - percentage / 100

    before = carbon_analysis(lifestyle, factors)
    after = carbon_analysis(alternative, factors)
    saved = before["total"] - after["total"]

    return {
        "before": before,
        "after": after,
        "alternative": alternative,
        "carbon_saved": round(saved, 2),
        "reduction_percent": round(
            saved / before["total"] * 100, 1
        ) if before["total"] else 0.0,
    }


def rank_opportunities(lifestyle, expenses, factors=None):
    baseline = carbon_analysis(lifestyle, factors)
    opportunities = []

    for field, category in CATEGORIES.items():
        emissions = baseline["breakdown"][category]
        spending = nonnegative(expenses.get(category, 0))

        opportunities.append({
            "Category": category,
            "Baseline emissions (kg CO2e)": emissions,
            "Potential emissions avoided (kg CO2e)": round(
                emissions * 0.20, 2
            ),
            "Potential spending reduction (INR)": round(
                spending * 0.20, 2
            ),
            "Assumption": (
                "Illustrative 20% activity and related-spending reduction"
            ),
        })

    return sorted(
        opportunities,
        key=lambda item: (
            item["Potential emissions avoided (kg CO2e)"],
            item["Potential spending reduction (INR)"],
        ),
        reverse=True,
    )


def generate_scenarios(lifestyle, expenses, income, factors=None):
    fields = list(CATEGORIES.keys())
    levels = [0, 10, 20, 30]
    finance = financial_analysis(income, expenses)
    scenarios = []

    for values in product(levels, repeat=len(fields)):
        reductions = dict(zip(fields, values))
        simulation = simulate_lifestyle(
            lifestyle, reductions, factors
        )

        # Simplified assumption: spending falls in proportion
        # to the selected reduction for its corresponding category.
        cash_saved = sum(
            nonnegative(expenses.get(CATEGORIES[field], 0))
            * reductions[field] / 100
            for field in fields
        )

        effort_index = sum(values) / (len(fields) * 100)

        label = " + ".join(
            f"{CATEGORIES[field]} {value}%"
            for field, value in reductions.items()
            if value > 0
        ) or "Current lifestyle"

        scenarios.append({
            "Scenario": label,
            "Carbon saved (kg CO2e)": simulation["carbon_saved"],
            "Money saved (INR/month)": round(cash_saved, 2),
            "Projected monthly balance (INR)": round(
                finance["balance"] + cash_saved, 2
            ),
            "Effort index": round(effort_index, 3),
            "Emissions remaining (kg CO2e)": (
                simulation["after"]["total"]
            ),
            "Reductions": reductions,
        })

    # Pareto-efficient candidates: no other scenario is at least as
    # good on all three objectives and strictly better on one.
    pareto = []

    for candidate in scenarios:
        dominated = any(
            other["Carbon saved (kg CO2e)"]
            >= candidate["Carbon saved (kg CO2e)"]
            and other["Money saved (INR/month)"]
            >= candidate["Money saved (INR/month)"]
            and other["Effort index"] <= candidate["Effort index"]
            and (
                other["Carbon saved (kg CO2e)"]
                > candidate["Carbon saved (kg CO2e)"]
                or other["Money saved (INR/month)"]
                > candidate["Money saved (INR/month)"]
                or other["Effort index"] < candidate["Effort index"]
            )
            for other in scenarios
        )

        if not dominated:
            pareto.append(candidate)

    return scenarios, pareto


def monthly_projection(
    income,
    monthly_expenses,
    additional_savings=0,
    months=12,
):
    income = float(income)
    monthly_expenses = float(monthly_expenses)
    additional_savings = max(0.0, float(additional_savings))

    current_balance = 0.0
    alternative_balance = 0.0
    results = []

    for month in range(1, int(months) + 1):
        current_balance += income - monthly_expenses
        alternative_balance += (
            income - monthly_expenses + additional_savings
        )

        results.append({
            "Month": month,
            "Current plan (INR)": round(current_balance, 2),
            "Alternative plan (INR)": round(
                alternative_balance, 2
            ),
        })

    return results


def generate_insights(carbon, finance, opportunities):
    insights = []

    if finance["balance"] < 0:
        insights.append(
            "Entered monthly expenses exceed entered income. Review "
            "spending and include irregular costs before relying on "
            "projections."
        )
    elif finance["savings_rate"] < 10:
        insights.append(
            "The entered monthly balance is less than 10% of income. "
            "Explore realistic expense changes and keep an emergency "
            "buffer in mind."
        )
    else:
        insights.append(
            "Entered income exceeds expenses. Check that irregular "
            "costs are included before using this balance for planning."
        )

    if opportunities:
        best = opportunities[0]
        insights.append(
            f"{best['Category']} ranks highest under the current model "
            "inputs. Validate the activity data and assumptions before acting."
        )

    insights.append(
        "Carbon and financial outputs are estimates, not audited "
        "measurements, guaranteed savings, or financial advice."
    )

    return insights
