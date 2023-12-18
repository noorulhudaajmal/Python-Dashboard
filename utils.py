import pandas as pd
import plotly.graph_objects as go
import pycountry
import plotly.express as px
import plotly.figure_factory as ff
from matplotlib import pyplot as plt
from plotly.subplots import make_subplots
from wordcloud import WordCloud


colors = ["#2a9d8f", "#264653", "#e9c46a", "#f4a261", "#e76f51", "#ef233c", "#f6bd60", "#84a59d", "#f95738"]


def preprocess_data(data):
    # Convert column names to title case with spaces
    data.columns = data.columns.str.replace('([A-Z])', r' \1').str.strip().str.title()

    # Convert specified date columns to datetime format
    date_columns = ['Reporting Date', 'Signing Date', 'Settlement Date']
    for col in date_columns:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col])

    # Add new columns for month name and month number
    if 'Signing Date' in data.columns:
        data['Signing Month'] = data['Signing Date'].dt.month_name()
        data['Signing Month Num'] = data['Signing Date'].dt.month

    # Sort the data by 'Signing Month Num'
    if 'Signing Month Num' in data.columns:
        data = data.sort_values(by='Signing Month Num', ascending=True)

    return data


def update_hover_layout(fig):
    fig.update_layout(
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            font_color="black",
            font_size=16,
            font_family="Rockwell"
        ),
        height=400
    )
    return fig


def get_iso_code(country_name):
    try:
        return pycountry.countries.get(name=country_name).alpha_3
    except:
        # Handling cases where the country name is not found
        return None


def kpi_card(label, data, col, prefix=None, suffix=None):
    value = data[col].sum()
    data = data.sort_values(by="Signing Date", ascending=True)
    data["Signing Month"] = data["Signing Date"].dt.month_name()
    data["Signing Month Num"] = data["Signing Date"].dt.month
    plot_data = data.groupby(["Signing Month Num", "Signing Month"])[col].sum().reset_index()
    plot_data = plot_data.sort_values(by="Signing Month Num", ascending=True)
    fig = go.Figure(go.Indicator(
        mode="number",
        value=value,
        number={"prefix": prefix, "suffix": suffix},
        title={"text": label, "font": {"size": 20}},
        domain={'y': [0, 1], 'x': [0.25, 0.75]}
    ))

    fig.add_trace(go.Scatter(
        x=plot_data["Signing Month"],
        y=plot_data[col],
        mode="lines",
        fill='tozeroy',
        name=label,
    ))
    fig.update_xaxes(showticklabels=False, showgrid=False)
    fig.update_yaxes(showticklabels=False, showgrid=False)

    fig.update_layout(height=250, hovermode="x unified",
                      hoverlabel=dict(
                          bgcolor="white",
                          font_color="black",
                          font_size=16,
                          font_family="Rockwell"
                      ))
    return fig


def product_by_business_lines(df):
    fig = px.bar(df, x="Product Name", y="Product Volume", color="Business Line",
                 title="Total Volume of Each Product by Business Line",
                 color_discrete_sequence=colors)
    fig.update_layout(barmode='stack')
    fig = update_hover_layout(fig)

    return fig


def fees_overtime(df):
    df = df.groupby("Signing Date")[["Upfront Fees", "Upfront Fees Skim"]].sum().reset_index()
    fig = go.Figure()
    ind = 1
    for fee in ["Upfront Fees", "Upfront Fees Skim"]:
        fig.add_trace(
            go.Scatter(
                x=df["Signing Date"], y=df[fee], name=fee, mode="markers+lines",
                marker=dict(color=colors[ind]), line=dict(color=colors[ind])
            )
        )
        ind += 1
    fig.update_layout(title="Fees overtime - Signing Date", xaxis_title="Date", yaxis_title="Fee")
    fig = update_hover_layout(fig)

    return fig


def rwa_by_products(df):
    products = df['Product Name'].unique()
    fig = go.Figure()
    ind = 1
    metrics = ['Rwa Spot', 'Rwa Htm', 'Rwa Release']
    for metric in metrics:
        fig.add_trace(go.Bar(name=metric,
                             x=products,
                             y=df.groupby('Product Name')[metric].sum(),
                             marker=dict(color=colors[ind])))
        ind += 1
    fig.update_layout(barmode='group',
                      title="Comparison of RWA Metrics Across Different Products",
                      xaxis_title="Product Name",
                      yaxis_title="RWA Value")
    fig = update_hover_layout(fig)

    return fig


def signing_to_settlement(df):
    df['Signing To Settlement'] = abs((df['Settlement Date'] - df['Signing Date']).dt.days)
    fig = px.histogram(df, x='Signing To Settlement', opacity=0.5,
                       color_discrete_sequence=colors,
                       labels={"count": "Days"},
                       title='Duration from Signing to Settlement')
    fig = update_hover_layout(fig)
    fig.update_yaxes(showticklabels=False)
    return fig


def map_plot(df):
    df['ISO Code'] = df['Country'].apply(get_iso_code)

    df = df.groupby(["Country", "ISO Code"])["Product Volume"].sum().reset_index()
    fig = px.choropleth(df, locations='ISO Code',
                        color='Product Volume',
                        hover_name='Country',
                        color_continuous_scale=px.colors.sequential.Plasma)
    fig.update_layout(title="Volume Distribution w.r.t Country", width=1600)
    return fig


def top_investors(df, col, num, label):
    investors = df.groupby('Investor Name')[col].sum().sort_values(ascending=True).head(num)
    investors = investors.reset_index()

    fig = px.bar(investors, y='Investor Name', x=col,
                 title=f'Top 10 Investors by {label}',
                 labels={col: label, 'Investor Name': 'Investor Name'},
                 orientation="h",
                 color_discrete_sequence=colors[1:],
                 text=col,
                 )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(xaxis={'categoryorder': 'total ascending'},
                      yaxis_title="Investor",
                      xaxis_title=label)
    fig = update_hover_layout(fig)

    return fig


def investors_table(df, col, num):
    investors = df.groupby('Investor Name')[col].sum().sort_values(ascending=True).head(num)
    investors = investors.reset_index()

    fig = go.Figure(data=[go.Table(
        columnwidth=[1, 1],
        header=dict(
            values=list(investors.columns),
            font=dict(size=20, color='white', family='ubuntu'),
            fill_color='#264653',
            align=['left', 'center'],
            height=60
        ),
        cells=dict(
            values=[investors[K].tolist() for K in investors.columns],
            font=dict(size=16, color="black", family='ubuntu'),
            fill_color='#f5ebe0',
            height=40
        ))]
    )
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), height=450)

    return fig


def investors_wordcloud(df, col, num):
    investors = df.groupby('Investor Name')[col].sum().sort_values(ascending=True).head(num)
    investors = investors.reset_index()

    # Creating a word cloud
    wordcloud = WordCloud(background_color='white', min_font_size=5).generate(
        ' '.join(investors['Investor Name']))

    # Convert the word cloud to an image
    fig = plt.figure(facecolor=None)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=10)

    return fig


def metrics_dist_chart(df, col):
    currency_df = df.groupby(col)["Product Volume", "Gross Margin", "Net Margin",
                                         "Upfront Fees"].sum().reset_index()

    fig = make_subplots(rows=1, cols=4, specs=[[{"type": "domain"}, {"type": "pie"},
                                                {"type": "pie"},{"type": "pie"}]],
                        subplot_titles=["Product Volume", "Gross Margin", "Net Margin", "Upfront Fees"])
    ind = 1
    for i in ["Product Volume", "Gross Margin", "Net Margin", "Upfront Fees"]:
        fig.add_trace(go.Pie(
            values=currency_df[i],
            labels=currency_df[col],
            domain=dict(x=[0, 0.5]),
            hole=0.5,
            name=f"{i} Dist."),
            row=1, col=ind)
        fig.update_traces(hoverinfo='label+percent+name', marker=dict(colors=colors))
        ind += 1
    fig = update_hover_layout(fig)
    fig.update_layout(title_text=f"Metrics Dist. w.r.t {col}")

    return fig


def measure_distribution(df, col):
    df = df.groupby(["Business Line", "Region"])[col].sum().reset_index()
    fig = px.bar(df, x="Business Line", y=col, color="Region", barmode="group",
                 color_discrete_sequence=colors,
                 title=f"Distribution of {col} by Business Line and Region")
    return fig


def time_series_trend(df, metrics):
    df = df.groupby("Signing Date")[metrics].sum().reset_index()

    fig = go.Figure()
    ind = 0
    for metric in metrics:
        fig.add_trace(
            go.Scatter(x=df["Signing Date"], y=df[metric], name=metric, marker=dict(color=colors[ind]))
        )
        ind += 1
    fig = update_hover_layout(fig)
    fig.update_layout(xaxis_title = "Signing Date", yaxis_title="Metric Value")
    return fig