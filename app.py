import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

from utils import kpi_card, product_by_business_lines, rwa_by_products, fees_overtime, \
    signing_to_settlement, map_plot, top_investors, investors_table

# ------------------------------ Page Configuration------------------------------
st.set_page_config(page_title="Data Insights", page_icon="📊", layout="wide")
# ----------------------------------- Page Styling ------------------------------

with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid=stHeader] {
        display:none;
    }
    [data-testid=block-container] {
        padding-top: 0px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------- Data Loading ------------------------------
data = pd.read_csv("./data/deals.csv", delimiter=";")

# --------------------------- Data Pre-processing -------------------------------

data["reportingDate"] = pd.to_datetime(data["reportingDate"])
data["signingDate"] = pd.to_datetime(data["signingDate"])
data["settlementDate"] = pd.to_datetime(data["settlementDate"])
data["signingMonth"] = data["signingDate"].dt.month_name()
data["signingMonthNum"] = data["signingDate"].dt.month
data = data.sort_values(by="signingMonthNum", ascending=True)

df = data.copy()
# ---------------------------- Side Bar -----------------------------------------
with st.sidebar:
    selected_date = st.date_input(label="Reporting Date", min_value=data["reportingDate"].min(),
                                  max_value=data["reportingDate"].max(), value=data["reportingDate"].iloc[0])
    business_line = st.multiselect(label="Business Line", options=data["businessLine"].unique(), placeholder="All")
    product_line = st.multiselect(label="Product Line", options=data["productLine"].unique(), placeholder="All")
    product_name = st.multiselect(label="Product", options=data["productName"].unique(), placeholder="All")
    currency = st.multiselect(label="Currency", options=data["currency"].unique(), placeholder="All")

# ----------------------------- Data Filtering -----------------------------------

if selected_date:
    df = df[df["reportingDate"] == pd.to_datetime(selected_date)]
if business_line:
    df = df[df["businessLine"].isin(business_line)]
if product_line:
    df = df[df["productLine"].isin(product_line)]
if product_name:
    df = df[df["productName"].isin(product_name)]
if currency:
    df = df[df["currency"].isin(currency)]

# ----------------------------------- Menu --------------------------------------
menu = option_menu(menu_title=None, menu_icon=None, orientation="horizontal",
                   options=["Overview", "Breakdown", "League Tables",
                            "Ventilation", "Historical Values"])
if menu == "Overview":
    # ----------------------------- Metrics ------------------------------------------
    kpi_row = st.columns(5)

    kpi_row[0].plotly_chart(kpi_card(label="Net Volume", data=df, col="productVolume"), use_container_width=True)
    kpi_row[1].plotly_chart(kpi_card(label="Upfront Fees", data=df, col="upfrontFees"), use_container_width=True)
    kpi_row[2].plotly_chart(kpi_card(label="Added Value", data=df, col="eva"), use_container_width=True)
    kpi_row[3].plotly_chart(kpi_card(label="Net Margin", data=df, col="netMargin"), use_container_width=True)
    kpi_row[4].plotly_chart(kpi_card(label="Gross Margin", data=df, col="grossMargin"), use_container_width=True)

    # ------------------------------ Comp --------------------------------------------
    charts_row = st.columns((3, 4))
    #  product across different business lines
    charts_row[0].plotly_chart(product_by_business_lines(df), use_container_width=True)
    # product volume across different products within a specific business line
    charts_row[1].plotly_chart(fees_overtime(df), use_container_width=True)

    # RWA metrics across different products or business lines
    charts_row[0].plotly_chart(rwa_by_products(df), use_container_width=True)
    charts_row[1].plotly_chart(signing_to_settlement(df), use_container_width=True)

    st.plotly_chart(map_plot(df), use_container_width=True)

if menu == "League Tables":
    row_1 = st.columns((1, 5))
    row_1[0].write("# ")
    row_1[0].write("# ")
    col = row_1[0].selectbox(label="Metric", options=["grossMargin", "productVolume", "eva", "netMargin",
                                                      "upfrontFees"])
    num = row_1[0].number_input(label="No. of Investors", min_value=5, max_value=15, value=10, step=1)
    row_1[1].plotly_chart(top_investors(df, col, num, col), use_container_width=True)
    st.plotly_chart(investors_table(df, col, num), use_container_width=True)

