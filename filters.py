import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_csv("data/application_train_clean.csv")

def get_global_filters(df):
    st.sidebar.header("🔧 Global Filters")

    gender_options = ['All'] + sorted(df['CODE_GENDER'].unique().tolist())
    education_options = ['All'] + sorted(df['NAME_EDUCATION_TYPE'].unique().tolist())
    family_status_options = ['All'] + sorted(df['NAME_FAMILY_STATUS'].unique().tolist())
    housing_options = ['All'] + sorted(df['NAME_HOUSING_TYPE'].unique().tolist())
    income_bracket_options = ['All'] + sorted(df['INCOME_BRACKET'].unique().tolist())

    filters = {
        'gender': st.sidebar.selectbox("Gender", gender_options),
        'education': st.sidebar.selectbox("Education", education_options),
        'family_status': st.sidebar.selectbox("Family Status", family_status_options),
        'housing': st.sidebar.selectbox("Housing Type", housing_options),
        'income_bracket': st.sidebar.selectbox("Income Bracket", income_bracket_options),
        'age_range': st.sidebar.slider(
            "Age Range (Years)", 
            int(df['AGE_YEARS'].min()), 
            int(df['AGE_YEARS'].max()), 
            (25, 60)
        ),
        'employment_years': st.sidebar.slider(
            "Employment Years", 
            int(df['EMPLOYMENT_YEARS'].min()), 
            int(df['EMPLOYMENT_YEARS'].max()), 
            (0, 20)
        ),
    }

    apply_filters = st.sidebar.button("🔍 Apply Filters")
    reset_filters = st.sidebar.button("🔄 Reset Filters")

    return filters, apply_filters, reset_filters

def apply_global_filters(df, filters):
    filtered_df = df.copy()

    if filters['gender'] != 'All':
        filtered_df = filtered_df[filtered_df['CODE_GENDER'] == filters['gender']]

    if filters['education'] != 'All':
        filtered_df = filtered_df[filtered_df['NAME_EDUCATION_TYPE'] == filters['education']]

    if filters['family_status'] != 'All':
        filtered_df = filtered_df[filtered_df['NAME_FAMILY_STATUS'] == filters['family_status']]

    if filters['housing'] != 'All':
        filtered_df = filtered_df[filtered_df['NAME_HOUSING_TYPE'] == filters['housing']]

    if filters['income_bracket'] != 'All':
        filtered_df = filtered_df[filtered_df['INCOME_BRACKET'] == filters['income_bracket']]

    filtered_df = filtered_df[
        (filtered_df['AGE_YEARS'] >= filters['age_range'][0]) &
        (filtered_df['AGE_YEARS'] <= filters['age_range'][1])
    ]

    filtered_df = filtered_df[
        (filtered_df['EMPLOYMENT_YEARS'] >= filters['employment_years'][0]) &
        (filtered_df['EMPLOYMENT_YEARS'] <= filters['employment_years'][1])
    ]

    return filtered_df
