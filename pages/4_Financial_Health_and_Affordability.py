# pages/4_Financial_Health_and_Affordability.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.prep import load_and_clean_data
from utils.filters import get_global_filters, apply_global_filters  # import filter functions

# ---------------------------
# Load data
# ---------------------------
@st.cache_data
def get_data():
    df = load_and_clean_data("data/application_train_clean.csv")
    # Ensure financial columns exist and compute derived ratios safely
    for col in ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE"]:
        if col not in df.columns:
            df[col] = np.nan

    # Safe DTI and LTI (avoid division by zero)
    df["DTI"] = df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"].replace({0: np.nan})
    df["LTI"] = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"].replace({0: np.nan})

    # Income bracket (if not present)
    if "INCOME_BRACKET" not in df.columns:
        try:
            df["INCOME_BRACKET"] = pd.qcut(
                df["AMT_INCOME_TOTAL"].fillna(df["AMT_INCOME_TOTAL"].median()),
                q=[0, 0.25, 0.75, 1.0],
                labels=["Low", "Mid", "High"]
            )
        except Exception:
            df["INCOME_BRACKET"] = "Unknown"

    return df

df = get_data()

# ---------------------------
# Page title & palette
# ---------------------------
st.set_page_config(layout="wide", page_title="Page 4 — Financial Health & Affordability")
st.title("💳 Page 4 — Financial Health & Affordability")
st.markdown("Assess repayment ability, affordability ratios and where stress points appear.")

PALETTE = ["#0F4C81", "#1982C4", "#66A182", "#F4D06F", "#F28C28"]  # blue -> green -> warm

# ---------------------------
# Sidebar Filters
# ---------------------------
filters, apply_filters, reset_filters = get_global_filters(df)

if apply_filters:
    filtered_df = apply_global_filters(df, filters)
else:
    filtered_df = df.copy()

if reset_filters:
    filtered_df = df.copy()

# ---------------------------
# KPIs (10)
# ---------------------------
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)
col7, col8, col9 = st.columns(3)
col10, _, _ = st.columns(3)

avg_income = filtered_df["AMT_INCOME_TOTAL"].mean()
median_income = filtered_df["AMT_INCOME_TOTAL"].median()
avg_credit = filtered_df["AMT_CREDIT"].mean()
avg_annuity = filtered_df["AMT_ANNUITY"].mean()
avg_goods = filtered_df["AMT_GOODS_PRICE"].mean() if "AMT_GOODS_PRICE" in filtered_df.columns else np.nan

avg_dti = filtered_df["DTI"].mean()
avg_lti = filtered_df["LTI"].mean()

income_nondef = filtered_df.loc[filtered_df["TARGET"] == 0, "AMT_INCOME_TOTAL"].mean()
income_def = filtered_df.loc[filtered_df["TARGET"] == 1, "AMT_INCOME_TOTAL"].mean()
income_gap = (income_nondef - income_def) if not (np.isnan(income_nondef) or np.isnan(income_def)) else np.nan

credit_nondef = filtered_df.loc[filtered_df["TARGET"] == 0, "AMT_CREDIT"].mean()
credit_def = filtered_df.loc[filtered_df["TARGET"] == 1, "AMT_CREDIT"].mean()
credit_gap = (credit_nondef - credit_def) if not (np.isnan(credit_nondef) or np.isnan(credit_def)) else np.nan

pct_high_credit = (filtered_df["AMT_CREDIT"] > 1_000_000).mean() * 100

col1.metric("Avg Annual Income", f"{avg_income:,.0f}")
col2.metric("Median Annual Income", f"{median_income:,.0f}")
col3.metric("Avg Credit Amount", f"{avg_credit:,.0f}")

col4.metric("Avg Annuity", f"{avg_annuity:,.0f}")
col5.metric("Avg Goods Price", f"{avg_goods:,.0f}" if not np.isnan(avg_goods) else "N/A")
col6.metric("Avg DTI", f"{avg_dti:.2f}")

col7.metric("Avg LTI", f"{avg_lti:.2f}")
col8.metric("Income Gap (Non-def − Def)", f"{income_gap:,.0f}" if not np.isnan(income_gap) else "N/A")
col9.metric("Credit Gap (Non-def − Def)", f"{credit_gap:,.0f}" if not np.isnan(credit_gap) else "N/A")
col10.metric("% High Credit (>1M)", f"{pct_high_credit:.2f}%")

st.markdown("---")

# ---------------------------
# Graphs (10) — 3 per row
# ---------------------------
figs = []

# 1. Histogram — Income distribution
figs.append(px.histogram(filtered_df, x="AMT_INCOME_TOTAL", nbins=60, title="Income distribution",
                         labels={"AMT_INCOME_TOTAL": "Annual Income"}, color_discrete_sequence=[PALETTE[0]]))

# 2. Histogram — Credit distribution
figs.append(px.histogram(filtered_df, x="AMT_CREDIT", nbins=60, title="Credit distribution",
                         labels={"AMT_CREDIT": "Credit Amount"}, color_discrete_sequence=[PALETTE[1]]))

# 3. Histogram — Annuity distribution
figs.append(px.histogram(filtered_df, x="AMT_ANNUITY", nbins=60, title="Annuity distribution",
                         labels={"AMT_ANNUITY": "Annuity"}, color_discrete_sequence=[PALETTE[2]]))

# 4. Scatter — Income vs Credit
sample_ic = filtered_df.sample(min(len(filtered_df), 50000))
figs.append(px.scatter(sample_ic, x="AMT_INCOME_TOTAL", y="AMT_CREDIT", title="Income vs Credit (sampled)",
                       opacity=0.5, labels={"AMT_INCOME_TOTAL": "Income", "AMT_CREDIT": "Credit"},
                       color_discrete_sequence=[PALETTE[3]]))

# 5. Scatter — Income vs Annuity
sample_ia = filtered_df.sample(min(len(filtered_df), 50000))
figs.append(px.scatter(sample_ia, x="AMT_INCOME_TOTAL", y="AMT_ANNUITY", title="Income vs Annuity (sampled)",
                       opacity=0.5, labels={"AMT_INCOME_TOTAL": "Income", "AMT_ANNUITY": "Annuity"},
                       color_discrete_sequence=[PALETTE[4]]))

# 6. Boxplot — Credit by Target
figs.append(px.box(filtered_df, x="TARGET", y="AMT_CREDIT", title="Credit by Target",
                   labels={"TARGET": "Target", "AMT_CREDIT": "Credit"}, color_discrete_sequence=[PALETTE[1]]))

# 7. Boxplot — Income by Target
figs.append(px.box(filtered_df, x="TARGET", y="AMT_INCOME_TOTAL", title="Income by Target",
                   labels={"TARGET": "Target", "AMT_INCOME_TOTAL": "Income"}, color_discrete_sequence=[PALETTE[0]]))

# 8. KDE / Density — Joint Income–Credit
sample_density = filtered_df[["AMT_INCOME_TOTAL", "AMT_CREDIT"]].dropna().sample(min(20000, len(filtered_df)))
figs.append(px.density_heatmap(sample_density, x="AMT_INCOME_TOTAL", y="AMT_CREDIT", nbinsx=50, nbinsy=50,
                               title="Joint Income–Credit density",
                               labels={"AMT_INCOME_TOTAL": "Income", "AMT_CREDIT": "Credit"},
                               color_continuous_scale="Viridis"))

# 9. Bar — Income Brackets vs Default Rate
br = filtered_df.groupby("INCOME_BRACKET")["TARGET"].mean().reset_index()
figs.append(px.bar(br, x="INCOME_BRACKET", y="TARGET", title="Income Bracket vs Default Rate",
                   labels={"TARGET": "Default Rate"}, color="INCOME_BRACKET", color_discrete_sequence=PALETTE))

# 10. Heatmap — Financial variable correlations
financial_cols = ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "DTI", "LTI", "TARGET"]
fin_present = [c for c in financial_cols if c in filtered_df.columns]
corr = filtered_df[fin_present].corr()
fig_heat = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index,
                                     colorscale="RdYlBu", zmin=-1, zmax=1,
                                     colorbar=dict(title="corr")))
fig_heat.update_layout(title="Correlation: Income, Credit, Annuity, DTI, LTI, TARGET", width=900, height=500)
figs.append(fig_heat)

# Display 3 charts per row
for i in range(0, len(figs), 3):
    cols = st.columns(3)
    for j, fig in enumerate(figs[i:i+3]):
        cols[j].plotly_chart(fig, use_container_width=True)
