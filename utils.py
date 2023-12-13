import plotly.graph_objects as go
import pycountry
import plotly.express as px

colors = ["#2a9d8f", "#264653", "#e9c46a", "#f4a261", "#e76f51", "#ef233c", "#f6bd60", "#84a59d", "#f95738"]


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
    data = data.sort_values(by="signingDate", ascending=True)
    data["signingMonth"] = data["signingDate"].dt.month_name()
    data["signingMonthNum"] = data["signingDate"].dt.month
    plot_data = data.groupby(["signingMonthNum", "signingMonth"])[col].sum().reset_index()
    plot_data = plot_data.sort_values(by="signingMonthNum", ascending=True)
    fig = go.Figure(go.Indicator(
        mode="number",
        value=value,
        number={"prefix": prefix, "suffix": suffix},
        title={"text": label, "font": {"size": 20}},
        domain={'y': [0, 1], 'x': [0.25, 0.75]}
    ))

    fig.add_trace(go.Scatter(
        x=plot_data["signingMonth"],
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
    fig = px.bar(df, x="productName", y="productVolume", color="businessLine",
                 title="Total Volume of Each Product by Business Line",
                 labels={"productVolume": "Product Volume", "productName": "Product Name",
                         "businessLine": "Business Line"},
                 color_discrete_sequence=colors)

    fig.update_layout(barmode='stack')
    fig = update_hover_layout(fig)

    return fig


def fees_overtime(df):
    df = df.groupby("signingDate")[["upfrontFees", "upfrontFeesSkim"]].sum().reset_index()
    fig = go.Figure()
    ind = 1
    for fee in ["upfrontFees", "upfrontFeesSkim"]:
        fig.add_trace(
            go.Scatter(
                x=df["signingDate"], y=df[fee], name=fee, mode="markers+lines",
                marker=dict(color=colors[ind]), line=dict(color=colors[ind])
            )
        )
        ind += 1
    fig.update_layout(title="Fees overtime - Signing Date", xaxis_title="Date", yaxis_title="Fee")
    fig = update_hover_layout(fig)

    return fig


def rwa_by_products(df):
    products = df['productName'].unique()
    fig = go.Figure()
    ind = 1
    metrics = ['rwaSpot', 'rwaHtm', 'rwaRelease']
    for metric in metrics:
        fig.add_trace(go.Bar(name=metric,
                             x=products,
                             y=df.groupby('productName')[metric].sum(),
                             marker=dict(color=colors[ind])))
        ind += 1
    fig.update_layout(barmode='group',
                      title="Comparison of RWA Metrics Across Different Products",
                      xaxis_title="Product Name",
                      yaxis_title="RWA Value")
    fig = update_hover_layout(fig)

    return fig


def signing_to_settlement(df):
    df['signing_to_settlement'] = abs((df['settlementDate'] - df['signingDate']).dt.days)
    fig = px.histogram(df, x='signing_to_settlement', opacity=0.5,
                       color_discrete_sequence=colors,
                       labels={"count": "Days"},
                       title='Duration from Signing to Settlement')
    fig = update_hover_layout(fig)

    return fig


def map_plot(df):
    df['iso_code'] = df['country'].apply(get_iso_code)

    df = df.groupby(["country", "iso_code"])["productVolume"].sum().reset_index()
    fig = px.choropleth(df, locations='iso_code',
                        color='productVolume',
                        hover_name='country',
                        color_continuous_scale=px.colors.sequential.Plasma)
    fig.update_layout(title="Volume Distribution w.r.t Country")
    return fig


def top_investors(df, col, num, label):
    investors = df.groupby('investorName')[col].sum().sort_values(ascending=True).head(num)
    investors = investors.reset_index()

    fig = px.bar(investors, y='investorName', x=col,
                 title=f'Top 10 Investors by {label}',
                 labels={col: label, 'investorName': 'Investor Name'},
                 orientation="h",
                 color_discrete_sequence=colors[1:],
                 text=col,
                 )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(xaxis={'categoryorder':'total ascending'},
                      yaxis_title="Investor",
                      xaxis_title=label)
    fig = update_hover_layout(fig)

    return fig


def investors_table(df, col, num):
    investors = df.groupby('investorName')[col].sum().sort_values(ascending=True).head(num)
    investors = investors.reset_index()

    fig = go.Figure(data=[go.Table(
        columnwidth=[1,1],
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
    fig.update_layout(margin=dict(l=0, r=10, b=10, t=30), height=400)

    return fig