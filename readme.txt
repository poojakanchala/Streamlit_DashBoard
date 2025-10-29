# 📊 Home Credit Risk – Interactive Streamlit Dashboard

An end-to-end **interactive data analytics dashboard** built using Streamlit, Python, and Plotly to explore and analyze the **Home Credit Default Risk** dataset.  
The dashboard provides deep insights into applicant profiles, financial behavior, and credit risk patterns — with rich visualizations and global filters.

---

## 🚀 Live Dashboard  
🔗 **Streamlit App:** https://poojak.streamlit.app/ 
 

---

## 📁 Project Overview

The dashboard is designed as a **multi-page analytical application** that allows users to interactively explore risk factors affecting loan default rates.

### 🔹 Key Pages Included

| Page | Description |
|------|--------------|
| **Overview & Data Quality** | Dataset overview, missing values, and data cleanliness checks |
| **Customer Demographics & Profile** | Age, gender, education, family status, housing, and lifestyle analysis |
| **Financial Health & Affordability** | Income, credit, annuity, employment years, and spending behavior insights |
| **Target & Risk Segmentation** | Default vs. non-default patterns, risk clusters, and repayment behavior analysis |
| **ML Insights & Drivers** | Important factors driving default probability, feature importance visualizations |

---

## 🎯 Dashboard Capabilities

✅ **Multi-Page Streamlit Dashboard**  
✅ **Global Filters** that dynamically apply across all pages  
✅ Interactive analysis with Plotly visualizations  
✅ Perform “Slice-and-Dice” analysis using filters:

- Gender, Education, Family Status, Housing Type  
- Age, Employment Years, Income Range sliders  
- Real-time updates across charts and insights  

---

## 🧠 Skills Demonstrated

- Data Visualization & Analytics  
- Data Wrangling and Cleaning  
- Dashboard UI/UX with Streamlit  
- Data Storytelling & Insight Communication  
- Cloud Deployment using Streamlit Cloud  

---

## 🛠️ Tech Stack

| Category | Tools Used |
|----------|-------------|
| Framework | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly, Seaborn, Matplotlib |
| ML Models | Scikit-learn |
| Deployment | Streamlit Cloud |

---

## 📂 Project Structure

'''Home-Credit-Dashboard/
|
|-- app.py                                  Main Streamlit application
|-- requirements.txt                        Project dependencies
|-- README.md                               Project documentation
|
|-- data/                                   Dataset folder
|    |-- application_train_clean.csv        Cleaned dataset used for dashboard
|
|-- utils/                                  Utility functions
|    |-- filters.py                         Contains load_data() and global filter functions
|    |-- prep.py                            Data preprocessing helper functions
|    |-- __init__.py
|
|-- pages/                                  Streamlit multi-page screens
|    |-- 1_Overview_and_Data_Quality.py
|    |-- 2_Customer_Profile_Analysis.py
|    |-- 3_Financial_Behavior_Insights.py
|    |-- 4_Credit_Risk_Segmentation.py
|    |-- 5_Model_Performance_and_Feature_Importance.py'''



