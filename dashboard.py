import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 🛠 Set konfigurasi halaman Streamlit
st.set_page_config(page_title="E-Commerce Data Analysis", page_icon="📊", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    all_data = pd.read_csv("all_data.csv")
    all_data['order_purchase_timestamp'] = pd.to_datetime(all_data['order_purchase_timestamp'], errors='coerce')
    return all_data

all_data = load_data()

# Sidebar untuk filter interaktif
st.sidebar.header("🔍 Filter Data")

# Filter tanggal
min_date = all_data['order_purchase_timestamp'].min()
max_date = all_data['order_purchase_timestamp'].max()
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)
filtered_data = all_data[(all_data['order_purchase_timestamp'] >= pd.to_datetime(date_range[0])) & (all_data['order_purchase_timestamp'] <= pd.to_datetime(date_range[1]))]

# Filter kategori produk
categories = all_data['product_category_name'].dropna().unique()
selected_category = st.sidebar.selectbox("Pilih Kategori Produk", ['Semua'] + list(categories))
if selected_category != 'Semua':
    filtered_data = filtered_data[filtered_data['product_category_name'] == selected_category]

# Filter jumlah transaksi pelanggan
min_trans, max_trans = int(filtered_data['order_id'].nunique()), int(all_data['order_id'].nunique())
trans_range = st.sidebar.slider("Filter Jumlah Transaksi", min_trans, max_trans, (min_trans, max_trans))
filtered_data = filtered_data.groupby('customer_unique_id').filter(lambda x: min_trans <= len(x) <= trans_range[1])

# Dashboard
st.title("📊 E-Commerce Data Analysis Dashboard")
st.markdown("---")

# Visualisasi 1: Kategori Produk dengan Penjualan Tertinggi
st.subheader("🏆 Kategori Produk dengan Penjualan Tertinggi")
top_categories = filtered_data['product_category_name'].value_counts().head(10).reset_index()
top_categories.columns = ['Kategori Produk', 'Jumlah Penjualan']
fig1 = px.bar(top_categories, x='Jumlah Penjualan', y='Kategori Produk', orientation='h', color='Jumlah Penjualan', title='Top 10 Kategori Produk', color_continuous_scale='Blues')
st.plotly_chart(fig1, use_container_width=True)

# Visualisasi 2: Tren Penjualan Berdasarkan Waktu
st.subheader("📅 Tren Penjualan Berdasarkan Waktu")
filtered_data['order_date'] = filtered_data['order_purchase_timestamp'].dt.date
sales_trend = filtered_data.groupby('order_date').size().reset_index(name='Jumlah Order')
fig2 = px.line(sales_trend, x='order_date', y='Jumlah Order', title='Tren Penjualan dari Waktu ke Waktu', markers=True)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("📌 Dashboard dibuat dengan Streamlit dan Plotly | Data: E-Commerce Public Dataset")
st.caption("👤 Nama: Muhammad Fery Syahputra")
st.caption("📧 Email: ferys2343@gmail.com")
st.caption("🆔 ID Dicoding: A009YBM322")
