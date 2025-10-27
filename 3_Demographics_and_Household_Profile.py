# pages/3_Demographics_and_Household_Profile.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.prep import load_and_clean_data
from utils.filters import get_global_filters, apply_global_filters

# ——— Load data ———
@st.cache_data
def get_data():
    return load_and_clean_data("data/application_train_clean.csv")

df = get_data()

# ——— Page configuration ———
st.set_page_config(layout="wide", page_title="Page 3 — Demographics & Household Profile")
st.title("👪 Page 3 — Demographics & Household Profile")
st.markdown("Explore who the applicants are and how demographic and household factors relate to default risk.")

# ——— Sidebar Filters ———
filters, apply_filters, reset_filters = get_global_filters(df)

if apply_filters:
    filtered_df = apply_global_filters(df, filters)
else:
    filtered_df = df.copy()

if reset_filters:
    filtered_df = df.copy()

# ——— KPIs (10 metrics) ———
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)
col7, col8, col9 = st.columns(3)
col10, _, _ = st.columns(3)

def safe_apply(series, func):
    if series is not None and not series.empty:
        return func(series)
    return np.nan

pct_male = safe_apply(filtered_df.get('CODE_GENDER', pd.Series()), lambda s: (s == 'M').mean() * 100)
pct_female = safe_apply(filtered_df.get('CODE_GENDER', pd.Series()), lambda s: (s == 'F').mean() * 100)
avg_age_def = safe_apply(filtered_df[filtered_df['TARGET'] == 1].get('AGE_YEARS', pd.Series()), lambda s: s.mean())
avg_age_nondef = safe_apply(filtered_df[filtered_df['TARGET'] == 0].get('AGE_YEARS', pd.Series()), lambda s: s.mean())
pct_with_children = safe_apply(filtered_df.get('CNT_CHILDREN', pd.Series()), lambda s: (s > 0).mean() * 100)
avg_family_size = safe_apply(filtered_df.get('CNT_FAM_MEMBERS', pd.Series()), lambda s: s.mean())
pct_married = safe_apply(filtered_df.get('NAME_FAMILY_STATUS', pd.Series()), lambda s: (s == 'Married').mean() * 100)

if 'NAME_EDUCATION_TYPE' in filtered_df:
    edu = filtered_df['NAME_EDUCATION_TYPE'].fillna("")
    pct_higher_edu = safe_apply(edu, lambda s: (s.str.contains('Higher|Academic|Bachelor', case=False)).mean() * 100)
else:
    pct_higher_edu = np.nan

pct_with_parents = safe_apply(filtered_df.get('NAME_HOUSING_TYPE', pd.Series()), lambda s: (s == 'With parents').mean() * 100)
pct_working = safe_apply(filtered_df.get('EMPLOYMENT_YEARS', pd.Series()), lambda s: s.notnull().mean() * 100)
avg_emp_years = safe_apply(filtered_df['EMPLOYMENT_YEARS'].dropna(), lambda s: s.mean())

col1.metric("% Male", f"{pct_male:.1f}%" if not np.isnan(pct_male) else "N/A")
col2.metric("% Female", f"{pct_female:.1f}%" if not np.isnan(pct_female) else "N/A")
col3.metric("Avg Age — Defaulters", f"{avg_age_def:.1f} yrs" if not np.isnan(avg_age_def) else "N/A")
col4.metric("Avg Age — Non‑Defaulters", f"{avg_age_nondef:.1f} yrs" if not np.isnan(avg_age_nondef) else "N/A")
col5.metric("% With Children", f"{pct_with_children:.1f}%" if not np.isnan(pct_with_children) else "N/A")
col6.metric("Avg Family Size", f"{avg_family_size:.2f}" if not np.isnan(avg_family_size) else "N/A")
col7.metric("% Married", f"{pct_married:.1f}%" if not np.isnan(pct_married) else "N/A")
col8.metric("% Higher Education", f"{pct_higher_edu:.1f}%" if not np.isnan(pct_higher_edu) else "N/A")
col9.metric("% Living With Parents", f"{pct_with_parents:.1f}%" if not np.isnan(pct_with_parents) else "N/A")
col10.metric("% Currently Working", f"{pct_working:.1f}%" if not np.isnan(pct_working) else "N/A")
st.markdown(f"**Avg Employment Years (workers)**: {avg_emp_years:.1f} yrs" if not np.isnan(avg_emp_years) else "**Avg Employment Years (workers)**: N/A")

st.markdown("---")

# ——— Charts (10 visualizations, 3 per row) ———
PALETTE_1 = ["#0D3B66", "#FAF0CA", "#F4D35E", "#EE964B", "#F95738"]
PALETTE_2 = ["#1B998B", "#2D3047", "#FF6B6B", "#FFD166", "#6A4C93"]
PALETTE_3 = ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"]

figs = []

# 1. Histogram — Age distribution (all)
if "AGE_YEARS" in filtered_df and filtered_df["AGE_YEARS"].nunique() > 1:
    figs.append(px.histogram(filtered_df, x="AGE_YEARS", nbins=40, title="Age distribution (all)", color_discrete_sequence=[PALETTE_1[0]]))

# 2. Histogram — Age by Target
if all(col in filtered_df for col in ["AGE_YEARS", "TARGET"]):
    fig2 = px.histogram(filtered_df, x="AGE_YEARS", color="TARGET", barmode="overlay", nbins=40,
                        labels={"TARGET": "Target (0=Repaid,1=Default)"}, color_discrete_sequence=[PALETTE_2[0], PALETTE_2[2]])
    fig2.update_traces(opacity=0.6)
    figs.append(fig2)

# 3. Bar — Gender distribution
if "CODE_GENDER" in filtered_df:
    gender_counts = filtered_df["CODE_GENDER"].value_counts().reset_index()
    gender_counts.columns = ["CODE_GENDER", "count"]
    figs.append(px.bar(gender_counts, x="CODE_GENDER", y="count", title="Gender distribution",
                       color="CODE_GENDER", color_discrete_sequence=[PALETTE_3[1], PALETTE_1[0]]))

# 4. Bar — Family Status distribution
if "NAME_FAMILY_STATUS" in filtered_df:
    fam_counts = filtered_df["NAME_FAMILY_STATUS"].value_counts().reset_index()
    fam_counts.columns = ["NAME_FAMILY_STATUS", "count"]
    figs.append(px.bar(fam_counts, x="NAME_FAMILY_STATUS", y="count", title="Family Status distribution",
                       color="NAME_FAMILY_STATUS", color_discrete_sequence=PALETTE_2))

# 5. Bar — Education distribution
if "NAME_EDUCATION_TYPE" in filtered_df:
    edu_counts = filtered_df["NAME_EDUCATION_TYPE"].value_counts().reset_index()
    edu_counts.columns = ["NAME_EDUCATION_TYPE", "count"]
    figs.append(px.bar(edu_counts, x="NAME_EDUCATION_TYPE", y="count", title="Education distribution",
                       color_discrete_sequence=PALETTE_3))

# 6. Bar — Occupation distribution (top 10)
if "OCCUPATION_TYPE" in filtered_df:
    occ_counts = filtered_df["OCCUPATION_TYPE"].value_counts().nlargest(10).reset_index()
    occ_counts.columns = ["OCCUPATION_TYPE", "count"]
    figs.append(px.bar(occ_counts, x="count", y="OCCUPATION_TYPE", orientation="h", title="Top 10 Occupations",
                       color='count', color_continuous_scale=[PALETTE_1[4], PALETTE_1[2]]))

# 7. Pie — Housing Type distribution
if "NAME_HOUSING_TYPE" in filtered_df:
    house_counts = filtered_df["NAME_HOUSING_TYPE"].value_counts().reset_index()
    house_counts.columns = ["NAME_HOUSING_TYPE", "count"]
    figs.append(px.pie(house_counts, names="NAME_HOUSING_TYPE", values="count", title="Housing Type distribution",
                       color_discrete_sequence=PALETTE_1))

# 8. Countplot — Children count
if "CNT_CHILDREN" in filtered_df:
    child_counts = filtered_df["CNT_CHILDREN"].value_counts().sort_index().reset_index()
    child_counts.columns = ["CNT_CHILDREN", "count"]
    figs.append(px.bar(child_counts, x="CNT_CHILDREN", y="count", title="Number of Children distribution",
                       color_discrete_sequence=[PALETTE_2[1]]))

# 9. Boxplot — Age vs Target
if all(col in filtered_df for col in ["AGE_YEARS", "TARGET"]):
    fig9 = px.box(filtered_df, x="TARGET", y="AGE_YEARS", title="Age vs Target (boxplot)",
                  color_discrete_sequence=[PALETTE_3[2]])
    fig9.update_xaxes(tickvals=[0, 1], ticktext=["Repaid (0)", "Default (1)"])
    figs.append(fig9)

# 10. Heatmap — Correlation: age, children, family size, TARGET
heat_cols = [c for c in ["AGE_YEARS", "CNT_CHILDREN", "CNT_FAM_MEMBERS", "TARGET"] if c in filtered_df]
if len(heat_cols) >= 2:
    heat_corr = filtered_df[heat_cols].corr()
    fig10 = go.Figure(data=go.Heatmap(z=heat_corr.values, x=heat_corr.columns, y=heat_corr.index,
                                     colorscale="Viridis", zmin=-1, zmax=1, colorbar=dict(title="corr")))
    fig10.update_layout(title="Correlation: Age, Children, Family Size & TARGET", width=800, height=500)
    figs.append(fig10)

# ——— Display charts 3 per row ———
for i in range(0, len(figs), 3):
    cols = st.columns(3)
    for j, fig in enumerate(figs[i:i+3]):
        cols[j].plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ——— Narrative & Insights ———
st.subheader("Narrative & Key Life‑Stage Insights")
st.write("""
- **Age & Family Structure**: Younger applicants (20s–30s) generally have smaller families, while older groups show larger dynamics.
- **Children & Risk Patterns**: Having children and larger family size seems to influence repayment behavior—perhaps adding stability through support or introducing strain.
- **Employment Presence**: A large share of applicants are currently employed. In exploratory analyses, shorter tenure correlated with marginally higher default.
- **Policy Hypotheses**:
   1. **Young adults with children** and **lower income** may require enhanced affordability verification.
   2. Those **living with parents** might indicate dependency vs independence—use caution in co-signed vs solo applications.
   3. **High-risk occupations** (e.g., seasonal jobs) may benefit from tailored evaluation or scoring adjustments.
""")

st.caption("Note: Charts render only when the corresponding data columns exist and hold meaningful variability.")
