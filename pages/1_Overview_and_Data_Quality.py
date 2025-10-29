import streamlit as st
import plotly.express as px
from utils.filters import load_data, get_global_filters, apply_global_filters

# --- Load Data + Global Filters ---
df = load_data()
filters, apply_filters, reset_filters = get_global_filters(df)

# By default: use original data
working_df = df.copy()

# Apply global filters only when the user clicks "Apply Filters"
if apply_filters:
    working_df = apply_global_filters(df, filters)

# --- Page Title ---
st.title("📊 Page 1 — Overview & Data Quality")

# --- KPIs (10) ---
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)
col7, col8, col9 = st.columns(3)
col10, _, _ = st.columns(3)

col1.metric("Total Applicants", f"{working_df['SK_ID_CURR'].nunique():,}")
col2.metric("Default Rate (%)", f"{working_df['TARGET'].mean() * 100:.2f}")
col3.metric("Repaid Rate (%)", f"{(1 - working_df['TARGET'].mean()) * 100:.2f}")

col4.metric("Total Features", f"{working_df.shape[1]}")
col5.metric("Avg Missing per Feature (%)", f"{working_df.isnull().mean().mean() * 100:.2f}")

num_features = working_df.select_dtypes(include=['number']).shape[1]
cat_features = working_df.select_dtypes(include=['object']).shape[1]

col6.metric("Numeric Features", f"{num_features}")
col7.metric("Categorical Features", f"{cat_features}")
col8.metric("Median Age (Years)", f"{working_df['AGE_YEARS'].median():.1f}")
col9.metric("Median Income", f"{working_df['AMT_INCOME_TOTAL'].median():,.0f}")
col10.metric("Average Credit", f"{working_df['AMT_CREDIT'].mean():,.0f}")

st.markdown("---")

# ---------------------------
# Charts (10) in rows of 3
# ---------------------------

# Row 1
row1_col1, row1_col2, row1_col3 = st.columns(3)

fig1 = px.pie(working_df, names="TARGET", title="Target Distribution (0 = Repaid, 1 = Default)")
row1_col1.plotly_chart(fig1, use_container_width=True)

missing_pct = working_df.isnull().mean().sort_values(ascending=False).head(20)
fig2 = px.bar(missing_pct, x=missing_pct.index, y=missing_pct.values, title="Top 20 Features by Missing %")
row1_col2.plotly_chart(fig2, use_container_width=True)

fig3 = px.histogram(working_df, x="AGE_YEARS", nbins=30, title="Age Distribution")
row1_col3.plotly_chart(fig3, use_container_width=True)

# Row 2
row2_col1, row2_col2, row2_col3 = st.columns(3)

fig4 = px.histogram(working_df, x="AMT_INCOME_TOTAL", nbins=30, title="Annual Income Distribution")
row2_col1.plotly_chart(fig4, use_container_width=True)

fig5 = px.histogram(working_df, x="AMT_CREDIT", nbins=30, title="Credit Amount Distribution")
row2_col2.plotly_chart(fig5, use_container_width=True)

fig6 = px.box(working_df, y="AMT_INCOME_TOTAL", title="Income Boxplot")
row2_col3.plotly_chart(fig6, use_container_width=True)

# Row 3
row3_col1, row3_col2, row3_col3 = st.columns(3)

fig7 = px.box(working_df, y="AMT_CREDIT", title="Credit Amount Boxplot")
row3_col1.plotly_chart(fig7, use_container_width=True)

fig8 = px.histogram(working_df, x="CODE_GENDER", title="Gender Distribution", text_auto=True)
row3_col2.plotly_chart(fig8, use_container_width=True)

fig9 = px.histogram(working_df, x="NAME_FAMILY_STATUS", title="Family Status Distribution", text_auto=True)
row3_col3.plotly_chart(fig9, use_container_width=True)

# Row 4 (last graph centered)
row4_col1, row4_col2, row4_col3 = st.columns(3)

fig10 = px.histogram(working_df, x="NAME_EDUCATION_TYPE", title="Education Distribution", text_auto=True)
row4_col2.plotly_chart(fig10, use_container_width=True)

# ---------------------------
# Narrative
# ---------------------------
st.markdown("### Insights")
st.write("""
- The dataset shows a **class imbalance** (most applicants repaid, fewer defaults).  
- Some features have **high missingness**, requiring careful treatment.  
- **Income and credit** distributions are highly skewed, with long tails.  
- **Age distribution** is fairly normal, centered in the mid-30s to 40s.  
""")
