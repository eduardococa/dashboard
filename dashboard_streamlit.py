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
    ventas_por_año = orders.merge(order_items, on="order_id")
    ventas_por_año["year"] = ventas_por_año["order_date"].dt.year
    crecimiento_anual = ventas_por_año.groupby("year")["total_price"].sum().pct_change() * 100
    
    # Ventas por región
    ventas_por_region = ventas_por_año.merge(stores, on="store_id").groupby("state")["total_price"].sum().reset_index()
    
    # Productos más vendidos
    productos_mas_vendidos = order_items.merge(products, on="product_id").groupby("product_name")["quantity"].sum().reset_index()
    productos_mas_vendidos = productos_mas_vendidos.sort_values(by="quantity", ascending=False).head(10)
    
    return total_ventas, crecimiento_anual, ventas_por_region, productos_mas_vendidos

total_ventas, crecimiento_anual, ventas_por_region, productos_mas_vendidos = load_data()

# Título
st.title("📊 Dashboard de Ventas")

# KPI Cards
col1, col2, col3 = st.columns(3)
col1.metric("Total de Ventas", f"${total_ventas:,.2f}")
col2.metric("Crecimiento 2017", f"{crecimiento_anual.get(2017, 0):.2f}%")
col3.metric("Crecimiento 2018", f"{crecimiento_anual.get(2018, 0):.2f}%")

# Gráfico de barras: Ventas por región
st.subheader("📍 Ventas por Región")
fig_barras = px.bar(
    ventas_por_region, 
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
    x=crecimiento_anual.index, 
    y=crecimiento_anual.values, 
    title="Crecimiento de Ventas por Año",
    labels={"x": "Año", "y": "Crecimiento (%)"},
    markers=True
)
st.plotly_chart(fig_lineas, use_container_width=True)

# Gráfico de barras: Productos más vendidos
st.subheader("🏆 Productos Más Vendidos")
fig_productos = px.bar(
    productos_mas_vendidos, 
    x="product_name", 
    y="quantity", 
    title="Top 10 Productos Más Vendidos",
    labels={"product_name": "Producto", "quantity": "Cantidad Vendida"},
    color="product_name"
)
st.plotly_chart(fig_productos, use_container_width=True)

# Filtros interactivos
st.sidebar.header("Filtros")
selected_region = st.sidebar.selectbox("Selecciona una región", ["Todas"] + list(ventas_por_region["state"]))
if selected_region != "Todas":
    ventas_filtradas = ventas_por_region[ventas_por_region['state'] == selected_region]
    st.write(f"### Ventas en {selected_region}: ${ventas_filtradas['total_price'].values[0]:,.2f}")
else:
    st.write("### Mostrando todas las regiones")

selected_product = st.sidebar.selectbox("Selecciona un producto", ["Todos"] + list(productos_mas_vendidos["product_name"]))
if selected_product != "Todos":
    producto_filtrado = productos_mas_vendidos[productos_mas_vendidos['product_name'] == selected_product]
    st.write(f"### Ventas del producto {selected_product}: {producto_filtrado['quantity'].values[0]} unidades vendidas")
else:
    st.write("### Mostrando todos los productos")