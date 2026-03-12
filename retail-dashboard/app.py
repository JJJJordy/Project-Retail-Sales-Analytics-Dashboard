import pandas as pd
import sqlite3
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)


# ---- BUILD DATABASE IF IT DOESN'T EXIST ----
def build_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'Superstore_clean.csv')
    db_path = os.path.join(base_dir, 'superstore.db')
    conn = sqlite3.connect(db_path)
    df = pd.read_csv(csv_path)
    df.to_sql('orders', conn, if_exists='replace', index=False)
    conn.close()

build_database()

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'superstore.db')
    conn = sqlite3.connect(db_path)

    orders = pd.read_sql_query("SELECT * FROM orders", conn)
    
    sales_by_year = pd.read_sql_query("""
        SELECT
            "Order Year",
            COUNT(DISTINCT "Order ID") AS total_orders,
            ROUND(SUM(Sales), 2) AS total_sales,
            ROUND(SUM(Profit), 2) AS total_profit,
            ROUND(AVG("Profit Margin %"), 2) AS avg_margin
        FROM orders
        GROUP BY "Order Year"
        ORDER BY "Order Year"
    """, conn)

    sales_by_category = pd.read_sql_query("""
        SELECT
            Category,
            ROUND(SUM(Sales), 2) AS total_sales,
            ROUND(SUM(Profit), 2) AS total_profit,
            ROUND(AVG("Profit Margin %"), 2) AS avg_margin,
            COUNT(*) AS total_orders
        FROM orders
        GROUP BY Category
        ORDER BY total_sales DESC
    """, conn)

    sales_by_region = pd.read_sql_query("""
        SELECT
            "Product Name",
            Category,
            ROUND(SUM(Sales), 2) AS total_sales,
            ROUND(SUM(Profit), 2) AS total_profit
        FROM orders
        GROUP BY "Product Name", Category
        ORDER BY total_profit DESC
        LIMIT 10
    """, conn)

    top_products = pd.read_sql_query("""
        SELECT
            "Product Name",
            Category,
            ROUND(SUM(Sales), 2) AS total_sales,
            ROUND(SUM(Profit), 2) AS total_profit
        FROM orders
        GROUP BY "Product Name", Category
        ORDER BY total_profit DESC
        LIMIT 10
    """, conn)

    loss_products = pd.read_sql_query("""
        SELECT 
            "Product Name",
            Category,
            ROUND(SUM(Sales), 2) AS total_sales,
            ROUND(SUM(Profit), 2) AS total_profit
        FROM orders
        GROUP BY "Product Name", Category
        ORDER BY total_profit ASC
        LIMIT 10
    """, conn)

    monthly_trend = pd.read_sql_query("""
        SELECT
            "Order Year",
            "Order Month",
            "Order Month Name",
            ROUND(SUM(Sales), 2) AS total_sales,
            ROUND(SUM(Profit), 2) AS total_profit
        FROM orders
        GROUP BY "Order Year", "Order Month", "Order Month Name"
        ORDER BY "Order Year", "Order Month"
    """, conn)

    segments = pd.read_sql_query("""
        SELECT 
            Segment,
            COUNT(DISTINCT "Customer ID") AS unique_customers,
            ROUND(SUM(Sales), 2) AS total_sales,
            ROUND(SUM(Profit), 2) AS total_profit,
            ROUND(AVG(Sales), 2) AS avg_order_value
        FROM orders
        GROUP BY Segment
        ORDER BY total_sales DESC
    """, conn)

    conn.close()
    return orders, sales_by_year, sales_by_category, sales_by_region, top_products, loss_products, monthly_trend, segments

orders, sales_by_year, sales_by_category, sales_by_region, top_products, loss_products, monthly_trend, segments = load_data()


# --- SIDEBAR FILTERS ---
st.sidebar.image("https://img.icons8.com/fluency/96/shopping-cart/png", width=60)
st.sidebar.title("Filters")

selected_years = st.sidebar.multiselect(
    "Select Year(s)",
    options=sorted(orders["Order Year"].unique()),
    default=sorted(orders["Order Year"].unique())
)

selected_regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=orders["Region"].unique(),
    default=orders["Region"].unique()
)

selected_categories = st.sidebar.multiselect(
    "Select Category",
    options=orders["Category"].unique(),
    default=orders["Category"].unique()
)

# Filter the main roders dataframe
filtered_df = orders[
    (orders["Order Year"].isin(selected_years)) &
    (orders["Region"].isin(selected_regions)) &
    (orders["Category"].isin(selected_categories))
]

# --- HEADER ---
st.title("🛒 Retail Sales Analytics Dashboard")
st.markdown("An interactive analysis of sales performance, profitability, and customer trends.")
st.markdown("---")

# --- KPI CARDS ---
k1, k2, k3, k4 = st.columns(4)

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order ID"].nunique()
avg_margin = filtered_df["Profit Margin %"].mean()

k1.metric("💰 Total Sales", f"${total_sales:,.0f}")
k2.metric("📈 Total Profit", f"${total_profit:,.0f}")
k3.metric("🧾 Total Orders", f"{total_orders:,}")
k4.metric("📊 Avg Profit Margin", f"{avg_margin:.1f}%")

st.markdown("---")

# --- ROW 1: YEARLY TREND + CATEGORY BREAKDOWN ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales & Profit by Year")
    filtered_yearly = filtered_df.groupby("Order Year").agg(
        total_sales=("Sales", "sum"),
        total_profit=("Profit", "sum")
    ).reset_index()

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=filtered_yearly["Order Year"],
        y=filtered_yearly["total_sales"],
        name="Sales",
        marker_color="#4C78A8"
    ))
    fig1.add_trace(go.Bar(
        x=filtered_yearly["Order Year"],
        y=filtered_yearly["total_profit"],
        name="Profit",
        marker_color="#72B7B2"
    ))
    fig1.update_layout(barmode="group", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Sales by Category")
    filtered_category = filtered_df.groupby("Category").agg(
        total_sales=("Sales", "sum"),
        total_profit=("Profit", "sum")
    ).reset_index()

    fig2 = px.pie(
        filtered_category,
        values="total_sales",
        names="Category",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

# --- ROW 2: MONTHLY TREND ---
st.subheader("Monthly Sales Trend")

filtered_monthly = filtered_df.groupby(["Order Year", "Order Month", "Order Month Name"]).agg(
    total_sales=("Sales", "sum"),
    total_profit=("Profit", "sum")
).reset_index().sort_values(["Order Year", "Order Month"])

filtered_monthly["Year-Month"] = (
    filtered_monthly["Order Year"].astype(str) + "-" +
    filtered_monthly["Order Month"].astype(str).str.zfill(2)
)

fig3 = px.line(
    filtered_monthly,
    x="Year-Month",
    y="total_sales",
    color="Order Year",
    markers=True,
    color_discrete_sequence=px.colors.qualitative.Set1
)

fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-45)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# --- ROW 3: REGION + SEGMENT ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("Profit by Region")
    filtered_region = filtered_df.groupby("Region").agg(
        total_sales=("Sales", "sum"),
        total_profit=("Profit", "sum")
    ).reset_index()

    fig4 = px.bar(
        filtered_region,
        x="Region",
        y="total_profit",
        color="total_profit",
        color_continuous_scale=["#FF6B6B", "#FFE66D", "#4ECDC4"],
        text_auto=".2s"
    )
    fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig4, use_container_width=True)

with col4:
    st.subheader("Sales by Customer Segment")
    filtered_segment = filtered_df.groupby("Segment").agg(
        total_sales=("Sales", "sum"),
        total_profit=("Profit", "sum"),
        unique_customers=("Customer ID", "nunique"),
        avg_order_value=("Sales", "mean")
    ).reset_index()

    fig5 = px.bar(
        filtered_segment,
        x="Segment",
        y="total_sales",
        color="Segment",
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig5.update_layout(plot_bgcolor=("rgba(0,0,0,0)"))
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# --- ROW 4: TOP & WORST PRODUCTS ---
col5, col6 = st.columns(2)

with col5:
    st.subheader("Top 10 Most Profitable Products")
    filtered_top = filtered_df.groupby(["Product Name", "Category"]).agg(
        total_profit=("Profit", "sum")
    ).reset_index().nlargest(10, "total_profit")

    fig6 = px.bar(
        filtered_top,
        x="total_profit",
        y="Product Name",
        color="Category",
        orientation="h",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig6.update_layout(plot_bgcolor="rgba(0,0,0,0)", yaxis={"categoryorder" : "total ascending"})
    st.plotly_chart(fig6, use_container_width=True)

with col6:
    st.subheader("Top 10 Loss-Making Products")
    filtered_loss = filtered_df.groupby(["Product Name", "Category"]).agg(
        total_profit=("Profit", "sum")
    ).reset_index().nsmallest(10, "total_profit")

    fig7 = px.bar(
        filtered_loss,
        x="total_profit",
        y="Product Name",
        color="Category",
        orientation="h",
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig7.update_layout(plot_bgcolor="rgba(0,0,0,0)", yaxis={"categoryorder": "total descending"})
    st.plotly_chart(fig7, use_conttainer_width=True)

st.markdown("---")

# --- RAW DATA TABLE ---
with st.expander("View Raw Data"):
    st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

st.caption("Built with Python, SQLite & Streamlit | Superstore Sales Dataset")

