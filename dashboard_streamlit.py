import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard de Ventas", layout="wide")

# Cargar datos desde la base de datos
@st.cache_data
def load_data():
    # Cargar los datos desde los archivos CSV en /data
    orders = pd.read_csv("data/orders.csv")
    order_items = pd.read_csv("data/order_items.csv")
    stores = pd.read_csv("data/stores.csv")
    products = pd.read_csv("data/products.csv")

    # Convertir fechas
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    
    # Total de ventas
    order_items["total_price"] = order_items["quantity"] * order_items["list_price"] * (1 - order_items["discount"])
    total_ventas = order_items["total_price"].sum()
    
    # Crecimiento de ventas por año
    ventas_por_año = orders.merge(order_items, on="order_id").merge(stores, on="store_id", how="left")
    ventas_por_año["year"] = ventas_por_año["order_date"].dt.year
    crecimiento_anual = ventas_por_año.groupby(["year", "state", "product_id"])["total_price"].sum().reset_index()
    
    # Ventas por región
    ventas_por_region = ventas_por_año.groupby(["state", "product_id"])["total_price"].sum().reset_index()
    
    # Productos más vendidos
    productos_mas_vendidos = order_items.merge(products, on="product_id").groupby("product_name")["quantity"].sum().reset_index()
    productos_mas_vendidos = productos_mas_vendidos.sort_values(by="quantity", ascending=False).head(10)
    
    return total_ventas, crecimiento_anual, ventas_por_region, productos_mas_vendidos, ventas_por_año

total_ventas, crecimiento_anual, ventas_por_region, productos_mas_vendidos, ventas_por_año = load_data()

# Título
st.title("📊 Dashboard de Ventas")

# Filtros interactivos
st.sidebar.header("Filtros")
selected_region = st.sidebar.selectbox("Selecciona una región", ["Todas"] + list(ventas_por_region["state"].dropna().unique()))
selected_product = st.sidebar.selectbox("Selecciona un producto", ["Todos"] + list(productos_mas_vendidos["product_name"]))

# Aplicar filtros a los datos
filtered_data = ventas_por_año.copy()
filtered_growth = crecimiento_anual.copy()
filtered_region_sales = ventas_por_region.copy()
filtered_products = productos_mas_vendidos.copy()

if selected_region != "Todas":
    filtered_data = filtered_data[filtered_data["state"] == selected_region]
    filtered_growth = filtered_growth[filtered_growth["state"] == selected_region]
    filtered_region_sales = filtered_region_sales[filtered_region_sales["state"] == selected_region]

if selected_product != "Todos":
    product_id = products[products["product_name"] == selected_product]["product_id"].values
    if len(product_id) > 0:
        product_id = product_id[0]
        filtered_data = filtered_data[filtered_data["product_id"] == product_id]
        filtered_growth = filtered_growth[filtered_growth["product_id"] == product_id]
        filtered_region_sales = filtered_region_sales[filtered_region_sales["product_id"] == product_id]
        filtered_products = filtered_products[filtered_products["product_name"] == selected_product]

# KPI Cards
col1, col2, col3 = st.columns(3)
col1.metric("Total de Ventas", f"${filtered_data['total_price'].sum():,.2f}")
col2.metric("Crecimiento 2017", f"{filtered_growth[filtered_growth['year'] == 2017]['total_price'].sum() if not filtered_growth[filtered_growth['year'] == 2017].empty else 0:.2f}%")
col3.metric("Crecimiento 2018", f"{filtered_growth[filtered_growth['year'] == 2018]['total_price'].sum() if not filtered_growth[filtered_growth['year'] == 2018].empty else 0:.2f}%")

# Gráfico de barras: Ventas por región
st.subheader("📍 Ventas por Región")
fig_barras = px.bar(
    filtered_region_sales, 
    x="state", 
    y="total_price", 
    title="Ventas por Región",
    labels={"state": "Región", "total_price": "Total de Ventas"},
    color="state"
)
st.plotly_chart(fig_barras, use_container_width=True)

# Gráfico de líneas: Crecimiento Anual
st.subheader("📈 Crecimiento Anual de Ventas")
fig_lineas = px.line(
    filtered_growth.groupby("year")["total_price"].sum().reset_index(),
    x="year", 
    y="total_price", 
    title="Crecimiento de Ventas por Año",
    labels={"year": "Año", "total_price": "Crecimiento (%)"},
    markers=True
)
st.plotly_chart(fig_lineas, use_container_width=True)

# Gráfico de barras: Productos más vendidos
st.subheader("🏆 Productos Más Vendidos")
fig_productos = px.bar(
    filtered_products, 
    x="product_name", 
    y="quantity", 
    title="Top 10 Productos Más Vendidos",
    labels={"product_name": "Producto", "quantity": "Cantidad Vendida"},
    color="product_name"
)
st.plotly_chart(fig_productos, use_container_width=True)