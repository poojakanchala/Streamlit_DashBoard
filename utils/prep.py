import pandas as pd
import numpy as np

def load_and_clean_data(path="data/application_train.csv"):
    # 1. Load raw data
    df = pd.read_csv(path)

    # 2. Derived columns
    df["AGE_YEARS"] = -df["DAYS_BIRTH"] / 365.25

    emp = df["DAYS_EMPLOYED"].copy()
    emp = emp.mask(emp >= 365000, np.nan)  # 365243 = not employed code
    emp = emp.mask(emp > 0, np.nan)        # remove weird positives
    df["EMPLOYMENT_YEARS"] = -emp / 365.25

    # 3. Ratios
    df["DTI"] = df["AMT_ANNUITY"] / df["AMT_INCOME_TOTAL"].replace({0: np.nan})
    df["LOAN_TO_INCOME"] = df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"].replace({0: np.nan})
    df["ANNUITY_TO_CREDIT"] = df["AMT_ANNUITY"] / df["AMT_CREDIT"].replace({0: np.nan})

    # 4. Drop columns > 60% missing
    missing_pct = df.isnull().mean()
    drop_cols = missing_pct[missing_pct > 0.6].index
    df = df.drop(columns=drop_cols)

    # 5. Impute missing values
    for col in df.columns:
        if df[col].dtype in ["float64", "int64"]:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(df[col].mode()[0])

    # 6. Standardize categories (rare -> "Other")
    for col in df.select_dtypes(include="object").columns:
        freqs = df[col].value_counts(normalize=True)
        rare_labels = freqs[freqs < 0.01].index
        df[col] = df[col].replace(rare_labels, "Other")

    # 7. Outlier handling (Winsorize 1%/99%)
    num_cols = ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY", "AGE_YEARS"]
    for col in num_cols:
        lower, upper = df[col].quantile([0.01, 0.99])
        df[col] = df[col].clip(lower, upper)

    # 8. Income brackets
    df["INCOME_BRACKET"] = pd.qcut(
        df["AMT_INCOME_TOTAL"],
        q=[0, 0.25, 0.75, 1],
        labels=["Low", "Mid", "High"]
    )

    return df

if __name__ == "__main__":
    df_clean = load_and_clean_data()
    df_clean.to_csv("data/application_train_clean.csv", index=False)
    print("✅ Cleaned dataset saved to data/application_train_clean.csv")
