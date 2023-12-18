import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

from utils import kpi_card, product_by_business_lines, rwa_by_products, fees_overtime, \
    signing_to_settlement, map_plot, top_investors, investors_table, preprocess_data, investors_wordcloud, \
    metrics_dist_chart, measure_distribution, time_series_trend

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

data = preprocess_data(data)
df = data.copy()
# ---------------------------- Side Bar -----------------------------------------
with st.sidebar:
    selected_date = st.date_input(label="Reporting Date", min_value=data["Reporting Date"].min(),
                                  max_value=data["Reporting Date"].max(), value=data["Reporting Date"].iloc[0])
    business_line = st.multiselect(label="Business Line", options=data["Business Line"].unique(), placeholder="All")
    product_line = st.multiselect(label="Product Line", options=data["Product Line"].unique(), placeholder="All")
    product_name = st.multiselect(label="Product", options=data["Product Name"].unique(), placeholder="All")
    currency = st.multiselect(label="Currency", options=data["Currency"].unique(), placeholder="All")

# ----------------------------- Data Filtering -----------------------------------

if selected_date:
    df = df[df["Reporting Date"] == pd.to_datetime(selected_date)]
if business_line:
    df = df[df["Business Line"].isin(business_line)]
if product_line:
    df = df[df["Product Line"].isin(product_line)]
if product_name:
    df = df[df["Product Name"].isin(product_name)]
if currency:
    df = df[df["Currency"].isin(currency)]

# ----------------------------------- Menu --------------------------------------
menu = option_menu(menu_title=None, menu_icon=None, orientation="horizontal",
                   options=["Overview", "Breakdown", "League Tables",
                            "Ventilation", "Historical Values"])
if menu == "Overview":
    # ----------------------------- Metrics ------------------------------------------
    kpi_row = st.columns(5)

    kpi_row[0].plotly_chart(kpi_card(label="Net Volume", data=df, col="Product Volume"), use_container_width=True)
    kpi_row[1].plotly_chart(kpi_card(label="Upfront Fees", data=df, col="Upfront Fees"), use_container_width=True)
    kpi_row[2].plotly_chart(kpi_card(label="Added Value", data=df, col="Eva"), use_container_width=True)
    kpi_row[3].plotly_chart(kpi_card(label="Net Margin", data=df, col="Net Margin"), use_container_width=True)
    kpi_row[4].plotly_chart(kpi_card(label="Gross Margin", data=df, col="Gross Margin"), use_container_width=True)

    # ------------------------------ Comp --------------------------------------------
    row_1 = st.columns(2)
    #  product across different business lines
    row_1[0].plotly_chart(product_by_business_lines(df), use_container_width=True)
    # RWA metrics across different products or business lines
    row_1[1].plotly_chart(rwa_by_products(df), use_container_width=True)
    st.plotly_chart(map_plot(df), use_container_width=True)

if menu == "Breakdown":
    row_1 = st.columns((1, 6))
    with row_1[0]:
        st.write("# ")
        st.write("# ")
        metric = st.selectbox(label="Metric",
                              options=["Product Name", "Business Line", "Product Line", "Currency", "Region"])
    row_1[1].plotly_chart(metrics_dist_chart(df, metric), use_container_width=True)
    charts_row = st.columns((4, 2))
    charts_row[0].plotly_chart(fees_overtime(df), use_container_width=True)
    charts_row[1].plotly_chart(signing_to_settlement(df), use_container_width=True)

    row_2 = st.columns((1, 6))
    with row_2[0]:
        st.write("# ")
        st.write("# ")
        measure = st.selectbox(label="Measure",
                               options=["Product Volume", "Gross Margin", "Net Margin", "Upfront Fees", "Eva"])
    row_2[1].plotly_chart(measure_distribution(df, measure), use_container_width=True)

if menu == "League Tables":
    row_1 = st.columns((1, 5))
    row_1[0].write("# ")
    row_1[0].write("# ")
    col = row_1[0].selectbox(label="Metric", options=["Gross Margin", "Product Volume", "Eva", "Net Margin",
                                                      "Upfront Fees"])
    num = row_1[0].number_input(label="No. of Investors", min_value=5, max_value=15, value=10, step=1)
    row_1[1].plotly_chart(top_investors(df, col, num, col), use_container_width=True)

    row_2 = st.columns((2, 4))
    row_2[0].plotly_chart(investors_table(df, col, num), use_container_width=True)
    row_2[1].pyplot(investors_wordcloud(df, col, num), use_container_width=True)

if menu == "Historical Values":
    metrics_row = st.columns(3)
    dfm = df.copy()
    dfm['Signing Date'] = pd.to_datetime(dfm['Signing Date']).dt.date
    dfm = dfm.dropna(subset=['Signing Date'])

    # Slider for period selection
    start_date, end_date = metrics_row[0].slider(
        "Select the period",
        value=(dfm['Signing Date'].min(), dfm['Signing Date'].max()),
        format="MM/DD/YYYY"
    )
    selected_metrics = metrics_row[1].multiselect(
        "Select metrics to display",
        options=['Gross Margin', 'Product Volume', 'Eva', 'Net Margin', 'Upfront Fees'],
        default=['Gross Margin', 'Net Margin']
    )
    # start_date = pd.to_datetime(start_date)
    # end_date

    selected_products = metrics_row[2].multiselect(
        "Select products to display",
        options=df['Product Name'].unique(),
        default=df['Product Name'].unique()
    )

    # Filtering the DataFrame
    filtered_data = dfm[
        (dfm['Signing Date'] >= start_date) & (dfm['Signing Date'] <= end_date) &
        (dfm['Product Name'].isin(selected_products))]
    st.plotly_chart(time_series_trend(filtered_data, selected_metrics), use_container_width=True)
