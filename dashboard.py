import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# 🛠 Set konfigurasi halaman Streamlit
st.set_page_config(page_title="E-Commerce Data Analysis", page_icon="📊", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    all_data = pd.read_csv("all_data.csv")
    all_data['order_purchase_timestamp'] = pd.to_datetime(all_data['order_purchase_timestamp'], errors='coerce')
    return all_data

all_data = load_data()

# Menentukan tanggal analisis
max_date = all_data['order_purchase_timestamp'].max() + timedelta(days=1)

# Menghitung Recency, Frequency, dan Monetary (RFM)
rfm = all_data.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (max_date - x.max()).days,
    'order_id': 'count',
    'payment_value': 'sum'
}).rename(columns={
    'order_purchase_timestamp': 'recency',
    'order_id': 'frequency',
    'payment_value': 'monetary'
})

# Dashboard
st.title("📊 E-Commerce Data Analysis Dashboard")
st.markdown("---")

# Sidebar untuk filter
st.sidebar.header("🔍 Filter Data")
recency_range = st.sidebar.slider("Recency Range", int(rfm['recency'].min()), int(rfm['recency'].max()), (int(rfm['recency'].min()), int(rfm['recency'].max())))
frequency_range = st.sidebar.slider("Frequency Range", int(rfm['frequency'].min()), int(rfm['frequency'].max()), (int(rfm['frequency'].min()), int(rfm['frequency'].max())))
monetary_range = st.sidebar.slider("Monetary Range", float(rfm['monetary'].min()), float(rfm['monetary'].max()), (float(rfm['monetary'].min()), float(rfm['monetary'].max())))

# Filter data berdasarkan slider
filtered_rfm = rfm[(rfm['recency'].between(recency_range[0], recency_range[1])) &
                    (rfm['frequency'].between(frequency_range[0], frequency_range[1])) &
                    (rfm['monetary'].between(monetary_range[0], monetary_range[1]))]

st.subheader("📌 RFM Summary (Filtered)")
st.write(filtered_rfm.describe())

# Menampilkan metrik utama
total_customers = filtered_rfm.shape[0]
avg_recency = filtered_rfm['recency'].mean()
avg_frequency = filtered_rfm['frequency'].mean()
avg_monetary = filtered_rfm['monetary'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", total_customers)
col2.metric("Avg Recency", f"{avg_recency:.2f} days")
col3.metric("Avg Frequency", f"{avg_frequency:.2f} orders")
col4.metric("Avg Monetary", f"${avg_monetary:.2f}")

# Visualisasi Distribusi Recency
st.subheader("📈 Recency Distribution")
fig_recency = px.histogram(filtered_rfm, x='recency', nbins=50, title='Recency Distribution', color_discrete_sequence=['blue'])
st.plotly_chart(fig_recency, use_container_width=True)

# Visualisasi Distribusi Frequency
st.subheader("📉 Frequency Distribution")
fig_frequency = px.histogram(filtered_rfm, x='frequency', nbins=50, title='Frequency Distribution', color_discrete_sequence=['green'])
st.plotly_chart(fig_frequency, use_container_width=True)

# Visualisasi Distribusi Monetary
st.subheader("💰 Monetary Distribution")
fig_monetary = px.histogram(filtered_rfm, x='monetary', nbins=50, title='Monetary Distribution', color_discrete_sequence=['orange'])
st.plotly_chart(fig_monetary, use_container_width=True)

st.markdown("---")
st.caption("📌 Dashboard dibuat dengan Streamlit dan Plotly | Data: E-Commerce Public Dataset")
st.caption("👤 Nama: Muhammad Fery Syahputra")
st.caption("📧 Email: ferys2343@gmail.com")
st.caption("🆔 ID Dicoding: A009YBM322")
