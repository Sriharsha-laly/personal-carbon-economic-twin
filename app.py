
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from engine import (
    carbon_analysis,
    financial_analysis,
    simulate_lifestyle,
    generate_scenarios,
    rank_opportunities,
    monthly_projection,
    generate_insights,
)

from advanced_analytics import (
    DEFAULT_FACTORS,
    validate_history,
    calculate_historical_emissions,
    trend_summary,
    trend_forecast,
    sensitivity_analysis,
)


# ===================== PAGE CONFIG =====================

st.set_page_config(
    page_title="EcoTwin Nexus | Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ===================== PREMIUM UI =====================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at top right, #163b31 0%, transparent 38%),
        linear-gradient(135deg, #07130f 0%, #0a1713 60%, #10221b 100%);
    color: #edf7f0;
}

[data-testid="stSidebar"] {
    background: #091710;
    border-right: 1px solid #254538;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #ecfff2 !important;
}

.hero {
    padding: 30px 32px;
    border-radius: 22px;
    background: linear-gradient(120deg, #163d30, #10251e 65%, #17382b);
    border: 1px solid #37634d;
    margin-bottom: 22px;
}

.eyebrow {
    color: #8fe0ae;
    font-size: 12px;
    letter-spacing: 2px;
    font-weight: 700;
}

.hero h1 {
    font-size: clamp(30px, 4vw, 48px);
    line-height: 1.08;
    margin: 8px 0;
}

.hero p {
    color: #c0d9c9;
    max-width: 800px;
    font-size: 15px;
}

.panel {
    padding: 18px 20px;
    border: 1px solid #29493a;
    background: rgba(16, 37, 29, 0.82);
    border-radius: 16px;
    margin-bottom: 14px;
}

.small-muted {
    color: #a8c3b2;
    font-size: 12px;
}

div[data-testid="stMetric"] {
    background: rgba(19, 48, 36, 0.9);
    border: 1px solid #2e5742;
    padding: 16px;
    border-radius: 14px;
}

div[data-testid="stMetricLabel"] {
    color: #b9d8c5;
}

.stButton > button, .stDownloadButton > button {
    border-radius: 10px;
    border: 1px solid #4a8663;
    background: #1b563a;
    color: white;
    font-weight: 600;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    background: #26764d;
    border-color: #83d8a4;
    color: white;
}

hr {
    border-color: #294638;
}
</style>
""", unsafe_allow_html=True)


# ===================== HELPERS =====================

def inr(value):
    return f"₹{value:,.0f}"


def style_chart(fig, height=350):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dcefe2", family="DM Sans"),
        margin=dict(l=10, r=10, t=45, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        hoverlabel=dict(
            bgcolor="#10251b",
            font_color="#f0fff4",
        ),
    )
    fig.update_xaxes(
        gridcolor="#244235",
        zerolinecolor="#355846",
    )
    fig.update_yaxes(
        gridcolor="#244235",
        zerolinecolor="#355846",
    )
    return fig


def metric_row(items):
    columns = st.columns(len(items))

    for column, item in zip(columns, items):
        column.metric(
            item["label"],
            item["value"],
            item.get("delta"),
            help=item.get("help"),
        )


# ===================== SIDEBAR =====================

st.sidebar.markdown("## 🌿 EcoTwin Nexus")
st.sidebar.caption("Personal carbon & economic intelligence")
st.sidebar.divider()

st.sidebar.markdown("### Monthly financial profile")

income = st.sidebar.number_input(
    "Monthly income (₹)",
    min_value=0.0,
    max_value=100000000.0,
    value=30000.0,
    step=1000.0,
)

transport_expense = st.sidebar.number_input(
    "Transport spending (₹)",
    min_value=0.0,
    value=2500.0,
    step=100.0,
)

electricity_expense = st.sidebar.number_input(
    "Electricity spending (₹)",
    min_value=0.0,
    value=1000.0,
    step=100.0,
)

food_expense = st.sidebar.number_input(
    "Food spending (₹)",
    min_value=0.0,
    value=5000.0,
    step=250.0,
)

shopping_expense = st.sidebar.number_input(
    "Shopping spending (₹)",
    min_value=0.0,
    value=2000.0,
    step=250.0,
)

other_expense = st.sidebar.number_input(
    "Other spending (₹)",
    min_value=0.0,
    value=3000.0,
    step=250.0,
)

expenses = {
    "Transport": transport_expense,
    "Electricity": electricity_expense,
    "Food": food_expense,
    "Shopping": shopping_expense,
    "Other": other_expense,
}

st.sidebar.divider()
st.sidebar.markdown("### Monthly lifestyle activity")

transport_km = st.sidebar.number_input(
    "Transport distance (km)",
    min_value=0.0,
    value=300.0,
    step=10.0,
)

electricity_kwh = st.sidebar.number_input(
    "Electricity used (kWh)",
    min_value=0.0,
    value=120.0,
    step=5.0,
)

food_meals = st.sidebar.number_input(
    "Meals counted by this model",
    min_value=0.0,
    value=60.0,
    step=1.0,
)

shopping_spend = st.sidebar.number_input(
    "Shopping spend used for carbon proxy (₹)",
    min_value=0.0,
    value=2000.0,
    step=100.0,
)

lifestyle = {
    "transport_km": transport_km,
    "electricity_kwh": electricity_kwh,
    "food_meals": food_meals,
    "shopping_spend": shopping_spend,
}

st.sidebar.divider()
st.sidebar.caption(
    "Prototype mode: emission factors are illustrative. "
    "Results depend on inputs and assumptions."
)


# ===================== INITIAL ANALYSIS =====================

carbon = carbon_analysis(lifestyle)
finance = financial_analysis(income, expenses)

opportunities = rank_opportunities(
    lifestyle, expenses
)

insights = generate_insights(
    carbon, finance, opportunities
)


# ===================== HERO =====================

st.markdown("""
<div class="hero">
    <div class="eyebrow">
        PERSONAL INTELLIGENCE SYSTEM / VERSION 2.0
    </div>
    <h1>EcoTwin Nexus</h1>
    <p>
        Explore the relationship between lifestyle choices, estimated
        emissions, and personal finances. Simulate alternatives, compare
        trade-offs, and inspect the assumptions behind every estimate.
    </p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "Prototype estimates only. Emission factors are illustrative "
    "and results are not audited measurements."
)


# ===================== NAVIGATION =====================

(
    overview_tab,
    twin_tab,
    optimizer_tab,
    future_tab,
    intelligence_tab,
    history_tab,
    sensitivity_tab,
) = st.tabs([
    "◈ Command Center",
    "⇄ Parallel-Life Lab",
    "⌘ Pareto Optimizer",
    "↗ Economic Time Machine",
    "✦ Intelligence Report",
    "▤ Historical Intelligence",
    "◉ Sensitivity Lab",
])


# ===================== TAB 1: COMMAND CENTER =====================

with overview_tab:
    st.subheader("Your monthly snapshot")

    metric_row([
        {
            "label": "Estimated emissions",
            "value": f"{carbon['total']:,.1f} kg",
            "help": "Estimated monthly kg CO2e using prototype factors.",
        },
        {
            "label": "Monthly income",
            "value": inr(finance["income"]),
        },
        {
            "label": "Monthly expenses",
            "value": inr(finance["expenses"]),
        },
        {
            "label": "Monthly balance",
            "value": inr(finance["balance"]),
            "delta": f"{finance['savings_rate']:.1f}% balance / income",
        },
    ])

    left, right = st.columns(2)

    with left:
        st.markdown("### Emissions composition")

        emission_df = pd.DataFrame(
            list(carbon["breakdown"].items()),
            columns=["Category", "Estimated kg CO2e"],
        )

        if emission_df["Estimated kg CO2e"].sum() > 0:
            fig = px.pie(
                emission_df,
                names="Category",
                values="Estimated kg CO2e",
                hole=0.65,
                title="Share by category",
            )
            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
            )

            st.plotly_chart(
                style_chart(fig, 370),
                use_container_width=True,
            )
        else:
            st.info(
                "Enter some lifestyle activity to see the emissions breakdown."
            )

    with right:
        st.markdown("### Expense structure")

        expense_df = pd.DataFrame(
            list(finance["breakdown"].items()),
            columns=["Category", "Monthly spending (INR)"],
        ).sort_values(
            "Monthly spending (INR)",
            ascending=True,
        )

        fig = px.bar(
            expense_df,
            x="Monthly spending (INR)",
            y="Category",
            orientation="h",
            title="Entered spending by category",
            color="Monthly spending (INR)",
            color_continuous_scale=["#285a42", "#67d49a"],
        )

        fig.update_layout(coloraxis_showscale=False)

        st.plotly_chart(
            style_chart(fig, 370),
            use_container_width=True,
        )

    st.markdown("### Initial intelligence signals")

    for item in insights:
        st.markdown(
            f'<div class="panel">{item}</div>',
            unsafe_allow_html=True,
        )


# ===================== TAB 2: PARALLEL-LIFE LAB =====================

with twin_tab:
    st.subheader("Parallel-Life Simulator")

    st.write(
        "Choose reductions and compare your current inputs with "
        "an alternative scenario."
    )

    col1, col2 = st.columns(2)

    with col1:
        transport_reduction = st.slider(
            "Transport reduction (%)", 0, 100, 20, 5
        )
        electricity_reduction = st.slider(
            "Electricity reduction (%)", 0, 100, 15, 5
        )

    with col2:
        food_reduction = st.slider(
            "Meal-related estimate reduction (%)", 0, 100, 10, 5
        )
        shopping_reduction = st.slider(
            "Shopping-proxy reduction (%)", 0, 100, 20, 5
        )

    reductions = {
        "transport_km": transport_reduction,
        "electricity_kwh": electricity_reduction,
        "food_meals": food_reduction,
        "shopping_spend": shopping_reduction,
    }

    comparison = simulate_lifestyle(
        lifestyle, reductions
    )

    metric_row([
        {
            "label": "Current estimate",
            "value": f"{comparison['before']['total']:,.1f} kg",
        },
        {
            "label": "Alternative estimate",
            "value": f"{comparison['after']['total']:,.1f} kg",
        },
        {
            "label": "Estimated difference",
            "value": f"{comparison['carbon_saved']:,.1f} kg",
        },
        {
            "label": "Estimated reduction",
            "value": f"{comparison['reduction_percent']:.1f}%",
        },
    ])

    comparison_df = pd.DataFrame({
        "Category": list(comparison["before"]["breakdown"].keys()),
        "Current": list(comparison["before"]["breakdown"].values()),
        "Alternative": list(comparison["after"]["breakdown"].values()),
    })

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Current lifestyle",
        x=comparison_df["Category"],
        y=comparison_df["Current"],
        marker_color="#5c9d7a",
    ))

    fig.add_trace(go.Bar(
        name="Alternative lifestyle",
        x=comparison_df["Category"],
        y=comparison_df["Alternative"],
        marker_color="#c4e8a4",
    ))

    fig.update_layout(
        barmode="group",
        title="Current versus alternative estimated emissions",
        yaxis_title="Estimated kg CO2e / month",
    )

    st.plotly_chart(
        style_chart(fig, 400),
        use_container_width=True,
    )

    st.markdown("### Category-level changes")

    for category, old_value in comparison["before"]["breakdown"].items():
        new_value = comparison["after"]["breakdown"][category]

        st.write(
            f"**{category}:** {old_value:.2f} → {new_value:.2f} kg CO₂e "
            f"(estimated change: {old_value - new_value:.2f} kg)"
        )

    st.caption(
        "Shopping emissions use a spending proxy, not product-specific "
        "life-cycle data."
    )

# ===================== TAB 3: PARETO OPTIMIZER =====================

with optimizer_tab:
    st.subheader("Multi-objective scenario explorer")

    st.write(
        "Evaluate 256 combinations of activity reductions and compare "
        "estimated carbon savings, money saved, and modeled effort."
    )

    with st.spinner("Evaluating scenarios..."):
        all_scenarios, pareto_scenarios = generate_scenarios(
            lifestyle, expenses, income
        )

    scenario_df = pd.DataFrame(all_scenarios)
    pareto_df = pd.DataFrame(pareto_scenarios)

    metric_row([
        {
            "label": "Scenarios evaluated",
            "value": f"{len(scenario_df):,}",
        },
        {
            "label": "Pareto-efficient scenarios",
            "value": f"{len(pareto_df):,}",
        },
        {
            "label": "Highest modeled carbon reduction",
            "value": (
                f"{scenario_df['Carbon saved (kg CO2e)'].max():,.1f} kg"
            ),
        },
        {
            "label": "Highest modeled savings",
            "value": inr(
                scenario_df["Money saved (INR/month)"].max()
            ),
        },
    ])

    fig = px.scatter(
        scenario_df,
        x="Effort index",
        y="Carbon saved (kg CO2e)",
        size="Money saved (INR/month)",
        color="Money saved (INR/month)",
        hover_name="Scenario",
        hover_data=[
            "Projected monthly balance (INR)",
            "Emissions remaining (kg CO2e)",
        ],
        title="Scenario trade-offs: effort, carbon, and money",
        color_continuous_scale=["#286348", "#b6e7a2"],
    )

    st.plotly_chart(
        style_chart(fig, 450),
        use_container_width=True,
    )

    st.markdown("### Pareto-efficient candidates")

    st.caption(
        "A scenario is Pareto-efficient when no other evaluated scenario "
        "is at least as good on all three objectives and strictly better "
        "on one. It is not necessarily the best choice for everyone."
    )

    display_columns = [
        "Scenario",
        "Carbon saved (kg CO2e)",
        "Money saved (INR/month)",
        "Projected monthly balance (INR)",
        "Effort index",
    ]

    st.dataframe(
        pareto_df[display_columns].sort_values(
            "Carbon saved (kg CO2e)",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

    downloadable_scenarios = scenario_df.drop(
        columns=["Reductions"]
    )

    st.download_button(
        "Download all scenarios (CSV)",
        data=downloadable_scenarios.to_csv(index=False),
        file_name="ecotwin_scenario_analysis.csv",
        mime="text/csv",
    )

    st.warning(
        "Savings are simplified proportional estimates, not guaranteed "
        "outcomes. The effort index is a model convention."
    )


# ===================== TAB 4: ECONOMIC TIME MACHINE =====================

with future_tab:
    st.subheader("Economic Time Machine")

    st.write(
        "Compare cumulative balances under constant monthly income "
        "and expense assumptions."
    )

    months = st.slider(
        "Projection period (months)",
        min_value=3,
        max_value=36,
        value=12,
        step=1,
    )

    extra_savings = st.number_input(
        "Additional monthly savings assumed (₹)",
        min_value=0.0,
        value=1000.0,
        step=250.0,
    )

    projection = pd.DataFrame(
        monthly_projection(
            income,
            finance["expenses"],
            extra_savings,
            months,
        )
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=projection["Month"],
        y=projection["Current plan (INR)"],
        mode="lines+markers",
        name="Current plan",
        line=dict(width=3, color="#6fb18a"),
    ))

    fig.add_trace(go.Scatter(
        x=projection["Month"],
        y=projection["Alternative plan (INR)"],
        mode="lines+markers",
        name="Alternative plan",
        line=dict(width=3, color="#d0e9a4"),
    ))

    fig.update_layout(
        title="Cumulative balance under constant assumptions",
        xaxis_title="Month",
        yaxis_title="Cumulative balance (INR)",
    )

    st.plotly_chart(
        style_chart(fig, 420),
        use_container_width=True,
    )

    last = projection.iloc[-1]

    metric_row([
        {
            "label": f"Current after {months} months",
            "value": inr(last["Current plan (INR)"]),
        },
        {
            "label": f"Alternative after {months} months",
            "value": inr(last["Alternative plan (INR)"]),
        },
        {
            "label": "Difference",
            "value": inr(
                last["Alternative plan (INR)"]
                - last["Current plan (INR)"]
            ),
        },
    ])

    st.dataframe(
        projection,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download projection (CSV)",
        data=projection.to_csv(index=False),
        file_name="ecotwin_financial_projection.csv",
        mime="text/csv",
    )

    st.caption(
        "This simple projection does not model inflation, investment "
        "returns, changing income, taxes, or emergencies."
    )


# ===================== TAB 5: INTELLIGENCE REPORT =====================

with intelligence_tab:
    st.subheader("Explainable opportunity intelligence")

    opportunity_df = pd.DataFrame(opportunities)

    st.dataframe(
        opportunity_df,
        use_container_width=True,
        hide_index=True,
    )

    fig = px.bar(
        opportunity_df.sort_values(
            "Potential emissions avoided (kg CO2e)"
        ),
        x="Potential emissions avoided (kg CO2e)",
        y="Category",
        orientation="h",
        title="Illustrative carbon-avoidance opportunities",
        color="Potential emissions avoided (kg CO2e)",
        color_continuous_scale=["#285a42", "#a4dfa9"],
    )

    fig.update_layout(coloraxis_showscale=False)

    st.plotly_chart(
        style_chart(fig, 350),
        use_container_width=True,
    )

    st.markdown("### Model transparency")

    for index, item in enumerate(insights, start=1):
        st.markdown(
            f'<div class="panel"><b>Signal {index:02d}</b><br>'
            f'{item}</div>',
            unsafe_allow_html=True,
        )

    st.write(
        "- Shopping uses a simplified spending-based proxy."
    )
    st.write(
        "- Scenario savings assume related spending changes "
        "proportionally with activity."
    )
    st.write(
        "- Forecasting is a separate statistical baseline. The core "
        "dashboard uses deterministic calculations and rules."
    )

    report_rows = [
        ("Monthly estimated emissions (kg CO2e)", carbon["total"]),
        ("Monthly income (INR)", finance["income"]),
        ("Monthly expenses (INR)", finance["expenses"]),
        ("Monthly balance (INR)", finance["balance"]),
        ("Balance / income (%)", finance["savings_rate"]),
    ]

    for category, value in carbon["breakdown"].items():
        report_rows.append((
            f"Emissions: {category} (kg CO2e)",
            value,
        ))

    report_df = pd.DataFrame(
        report_rows,
        columns=["Metric", "Value"],
    )

    st.download_button(
        "Export intelligence report (CSV)",
        data=report_df.to_csv(index=False),
        file_name="ecotwin_intelligence_report.csv",
        mime="text/csv",
    )


# ===================== TAB 6: HISTORICAL INTELLIGENCE =====================

with history_tab:
    st.subheader("Historical Data Intelligence")

    st.write(
        "Upload a monthly CSV to validate activity data, calculate "
        "estimated emissions, analyze trends, and test a baseline forecast."
    )

    uploaded = st.file_uploader(
        "Upload monthly history CSV",
        type=["csv"],
        key="history_upload",
    )

    if uploaded is not None:
        try:
            history = validate_history(uploaded)

            analyzed = calculate_historical_emissions(
                history,
                DEFAULT_FACTORS,
            )

            st.success(
                f"Validated {len(analyzed)} monthly records."
            )

            st.dataframe(
                analyzed,
                use_container_width=True,
                hide_index=True,
            )

            fig = px.line(
                analyzed,
                x="month",
                y="total_emissions",
                markers=True,
                title="Historical estimated emissions",
                labels={
                    "month": "Month",
                    "total_emissions": "Estimated kg CO2e",
                },
            )

            st.plotly_chart(
                style_chart(fig, 380),
                use_container_width=True,
            )

            summary = trend_summary(
                analyzed["total_emissions"]
            )

            if summary["change"] is not None:
                metric_row([
                    {
                        "label": "First recorded estimate",
                        "value": f"{summary['first']:,.2f} kg",
                    },
                    {
                        "label": "Last recorded estimate",
                        "value": f"{summary['last']:,.2f} kg",
                    },
                    {
                        "label": "First-to-last change",
                        "value": f"{summary['change']:+,.2f} kg",
                    },
                ])

                if summary["change_percent"] is not None:
                    st.caption(
                        "First-to-last percentage change: "
                        f"{summary['change_percent']:+.2f}%"
                    )

            if len(analyzed) >= 4:
                result = trend_forecast(
                    analyzed["total_emissions"],
                    horizon=3,
                )

                st.markdown("### Three-step trend baseline")

                st.caption(
                    "This is a trend extrapolation, not a guarantee. "
                    "Small datasets can produce unstable forecasts."
                )

                metric_row([
                    {
                        "label": "Holdout MAE",
                        "value": f"{result['holdout_mae']:.2f} kg",
                        "help": (
                            "Mean absolute error on the chronological "
                            "holdout observations."
                        ),
                    },
                    {
                        "label": "Training observations",
                        "value": str(
                            result["training_observations"]
                        ),
                    },
                    {
                        "label": "Holdout observations",
                        "value": str(
                            result["holdout_observations"]
                        ),
                    },
                ])

                forecast_df = pd.DataFrame({
                    "Step ahead": range(1, 4),
                    "Forecast estimated emissions (kg CO2e)": (
                        result["forecast"]
                    ),
                })

                st.dataframe(
                    forecast_df,
                    use_container_width=True,
                    hide_index=True,
                )

            st.download_button(
                "Download analyzed historical data",
                data=analyzed.to_csv(index=False),
                file_name="ecotwin_historical_analysis.csv",
                mime="text/csv",
            )

        except (
            ValueError,
            KeyError,
            TypeError,
            pd.errors.ParserError,
        ) as error:
            st.error(f"Could not analyze this file: {error}")

    else:
        st.info(
            "Upload a CSV containing these columns: month, transport_km, "
            "electricity_kwh, food_meals, shopping_spend, income."
        )


# ===================== TAB 7: SENSITIVITY LAB =====================

with sensitivity_tab:
    st.subheader("Sensitivity & Uncertainty Lab")

    st.write(
        "Explore how changing one assumed emission factor changes "
        "the model's estimated emissions."
    )

    category = st.selectbox(
        "Select category",
        ["Transport", "Electricity", "Food", "Shopping"],
    )

    field_for_category = {
        "Transport": "transport_km",
        "Electricity": "electricity_kwh",
        "Food": "food_meals",
        "Shopping": "shopping_spend",
    }

    field = field_for_category[category]

    sensitivity_df = sensitivity_analysis(
        lifestyle[field],
        DEFAULT_FACTORS[field],
    )

    st.dataframe(
        sensitivity_df,
        use_container_width=True,
        hide_index=True,
    )

    fig = px.bar(
        sensitivity_df,
        x="Factor scenario",
        y="Estimated emissions (kg CO2e)",
        title=f"{category}: factor sensitivity",
    )

    st.plotly_chart(
        style_chart(fig, 350),
        use_container_width=True,
    )

    st.caption(
        "These are illustrative factor scenarios, not statistical "
        "confidence intervals. Replace prototype factors with documented "
        "sources before making real-world claims."
    )


# ===================== FOOTER =====================

st.divider()

st.markdown("""
<div class="small-muted">
    ECOTWIN NEXUS · PERSONAL CARBON & ECONOMIC INTELLIGENCE<br>
    Research prototype · Outputs depend on data quality and assumptions.
</div>
""", unsafe_allow_html=True)
