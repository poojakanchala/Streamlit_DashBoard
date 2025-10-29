import streamlit as st
from utils.filters import load_data, get_global_filters, apply_global_filters
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Home Credit Risk Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load cleaned dataset
df = load_data()

# Sidebar global filters always visible
filters, apply_filters, reset_filters = get_global_filters(df)

# Default: sample of original cleaned data
sample_original_df = df[['SK_ID_CURR', 'TARGET', 'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AGE_YEARS', 'CODE_GENDER']].sample(10)

# Display filtered data if user applies filters, else show original sample
if apply_filters:
    filtered_df = apply_global_filters(df, filters)
    display_df = filtered_df[['SK_ID_CURR', 'TARGET', 'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AGE_YEARS', 'CODE_GENDER']].sample(10)
else:
    display_df = sample_original_df.copy()

# --- Page Content ---
st.title("🏠 Home Credit Default Risk — Overview")

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Applicants", f"{df['SK_ID_CURR'].nunique():,}")
col2.metric("Default Rate (%)", f"{df['TARGET'].mean() * 100:.2f}")
col3.metric("Repaid Rate (%)", f"{(1 - df['TARGET'].mean()) * 100:.2f}")

# Sample Data Display
st.markdown("### 📄 Sample Data (Original or Filtered)")
st.dataframe(display_df, use_container_width=True)
