# pages/5_Correlations_and_Drivers.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.prep import load_and_clean_data
from utils.filters import get_global_filters, apply_global_filters

# --------------------------- Load & Prep ---------------------------
@st.cache_data
def get_data():
    df = load_and_clean_data("data/application_train_clean.csv")
    # Derived fields
    df["DTI"] = df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"].replace({0: np.nan})
    df["LTI"] = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"].replace({0: np.nan})
    df["ANNUITY_TO_CREDIT"] = df["AMT_ANNUITY"] / df["AMT_CREDIT"].replace({0: np.nan})
    return df

df = get_data()
corr_matrix = df.corr(numeric_only=True)

# --------------------------- Page Config ---------------------------
st.set_page_config(layout="wide", page_title="Page 5 — Correlations & Drivers")
st.title("🔍 Page 5 — Correlations, Drivers & Interactive Slice-and-Dice")

# --------------------------- Sidebar Filters ---------------------------
filters, apply_filters, reset_filters = get_global_filters(df)

if apply_filters:
    filtered_df = apply_global_filters(df, filters)
else:
    filtered_df = df.copy()

if reset_filters:
    filtered_df = df.copy()

# --------------------------- KPIs ---------------------------
st.subheader("📌 Correlation KPIs")
filtered_corr = filtered_df.corr(numeric_only=True)

def safe_corr(col1, col2):
    try:
        return filtered_corr.loc[col1, col2]
    except:
        return np.nan

top_corr_pos = filtered_corr["TARGET"].drop("TARGET").sort_values(ascending=False).head(5)
top_corr_neg = filtered_corr["TARGET"].drop("TARGET").sort_values().head(5)
var_explained = sum(abs(filtered_corr["TARGET"].drop("TARGET").sort_values(ascending=False).head(5)))

with st.expander("Correlation-Based KPIs"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Top +Corr with TARGET", ", ".join(top_corr_pos.index))
    c2.metric("Top −Corr with TARGET", ", ".join(top_corr_neg.index))
    c3.metric("Variance Explained (Top 5)", f"{var_explained:.2f}")

    c4, c5, c6 = st.columns(3)
    c4.metric("Most Corr w/ Income", filtered_corr["AMT_INCOME_TOTAL"].drop("AMT_INCOME_TOTAL").abs().idxmax())
    c5.metric("Most Corr w/ Credit", filtered_corr["AMT_CREDIT"].drop("AMT_CREDIT").abs().idxmax())
    c6.metric("Corr(Income, Credit)", f"{safe_corr('AMT_INCOME_TOTAL','AMT_CREDIT'):.2f}")

    c7, c8, c9 = st.columns(3)
    c7.metric("Corr(Age, TARGET)", f"{safe_corr('AGE_YEARS','TARGET'):.2f}")
    c8.metric("Corr(Employment Years, TARGET)", f"{safe_corr('EMPLOYMENT_YEARS','TARGET'):.2f}")
    c9.metric("Corr(Family Size, TARGET)", f"{safe_corr('CNT_FAM_MEMBERS','TARGET'):.2f}")

    c10, _, _ = st.columns(3)
    c10.metric("# Features with |corr| > 0.5", f"{(filtered_corr['TARGET'].abs() > 0.5).sum()}")

st.markdown("---")

# --------------------------- Correlation Heatmap ---------------------------
st.subheader("📊 Correlation Heatmap")
numeric_cols = filtered_df.select_dtypes(include=np.number).columns.tolist()
selected_cols = st.multiselect(
    "Select numeric features to compare:", 
    options=numeric_cols,
    default=["AGE_YEARS", "EMPLOYMENT_YEARS", "AMT_INCOME_TOTAL", "AMT_CREDIT", "DTI", "LTI", "TARGET"]
)

if len(selected_cols) >= 2:
    corr_subset = filtered_df[selected_cols].corr()
    fig_heat = go.Figure(data=go.Heatmap(
        z=corr_subset.values,
        x=corr_subset.columns,
        y=corr_subset.index,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        colorbar=dict(title="corr")
    ))
    fig_heat.update_layout(title="Correlation Matrix (Selected Features)", height=600)
    st.plotly_chart(fig_heat, use_container_width=True)

# --------------------------- |Correlation| vs TARGET Bar ---------------------------
st.subheader("📉 |Correlation| of Features vs TARGET")
target_corrs = filtered_corr["TARGET"].drop("TARGET").abs().sort_values(ascending=False).head(20)
fig_corr_bar = px.bar(target_corrs, title="Top |Correlations| with TARGET", labels={"value": "|corr|"}, height=400)
st.plotly_chart(fig_corr_bar, use_container_width=True)

# --------------------------- All Scatter/Box/Bar/Pairplot in 3 per row ---------------------------
st.subheader("🧮 Visual Correlations & Drivers")
figs = []

# Scatter / Box / Bar plots
figs.append(px.scatter(filtered_df, x="AGE_YEARS", y="AMT_CREDIT", color="TARGET", title="Age vs Credit", opacity=0.5))
figs.append(px.scatter(filtered_df, x="AGE_YEARS", y="AMT_INCOME_TOTAL", color="TARGET", title="Age vs Income", opacity=0.5))
figs.append(px.scatter(filtered_df, x="EMPLOYMENT_YEARS", y="TARGET", title="Employment Years vs TARGET", opacity=0.4))

figs.append(px.box(filtered_df, x="NAME_EDUCATION_TYPE", y="AMT_CREDIT", color="TARGET", title="Credit by Education"))
figs.append(px.box(filtered_df, x="NAME_FAMILY_STATUS", y="AMT_INCOME_TOTAL", color="TARGET", title="Income by Family Status"))

sample_df = filtered_df[["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "TARGET"]].dropna().sample(min(len(filtered_df), 3000))
figs.append(px.scatter_matrix(sample_df, dimensions=["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY"], color="TARGET", title="Scatter Matrix"))

df_g = filtered_df.groupby("CODE_GENDER")["TARGET"].mean().reset_index()
figs.append(px.bar(df_g, x="CODE_GENDER", y="TARGET", title="Default Rate by Gender", labels={"TARGET":"Default Rate"}).update_yaxes(tickformat=".0%"))

df_e = filtered_df.groupby("NAME_EDUCATION_TYPE")["TARGET"].mean().reset_index()
figs.append(px.bar(df_e, x="NAME_EDUCATION_TYPE", y="TARGET", title="Default Rate by Education", labels={"TARGET":"Default Rate"}).update_yaxes(tickformat=".0%"))

# Display plots in rows of 3
for i in range(0, len(figs), 3):
    cols = st.columns(3)
    for j, fig in enumerate(figs[i:i+3]):
        cols[j].plotly_chart(fig, use_container_width=True)

# --------------------------- Narrative ---------------------------
st.markdown("---")
st.subheader("📘 Interpretation & Policy Candidates")
st.write("""
- Features like **LTI, DTI, Age, Employment Years, Family Size** show significant correlation with TARGET.
- Consider thresholds based on **LTI > 6**, **DTI > 0.35**, or **Low Income Brackets**.
- Use Education and Gender filtering to explore subgroup behavior and tailor policy accordingly.
""")
