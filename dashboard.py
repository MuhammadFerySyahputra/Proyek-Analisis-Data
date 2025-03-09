import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import calendar
from plotly.subplots import make_subplots
import time

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

# RFM Segmentation
def rfm_segment(row):
    # Definisi untuk RFM segmentation
    if row['recency'] <= 30 and row['frequency'] >= 3 and row['monetary'] >= 1000:
        return 'Champions'
    elif row['recency'] <= 30 and row['frequency'] >= 2 and row['monetary'] >= 750:
        return 'Loyal Customers'
    elif row['recency'] <= 90 and row['frequency'] >= 2 and row['monetary'] >= 500:
        return 'Potential Loyalists'
    elif row['recency'] <= 30 and row['frequency'] <= 2 and row['monetary'] <= 250:
        return 'New Customers'
    elif row['recency'] <= 180 and row['frequency'] >= 3 and row['monetary'] >= 500:
        return 'Need Attention'
    elif row['recency'] > 180 and row['frequency'] >= 2 and row['monetary'] >= 250:
        return 'At Risk'
    elif row['recency'] > 365 and row['frequency'] <= 2 and row['monetary'] <= 250:
        return 'Lost'
    else:
        return 'Others'

rfm['segment'] = rfm.apply(rfm_segment, axis=1)

st.title("📊 E-Commerce Data Analysis Dashboard")

# # Tambahkan fitur tema dark/light
# theme_option = st.sidebar.selectbox("🎨 Theme", ["Light", "Dark"])
# if theme_option == "Dark":
#     st.markdown("""
#     <style>
#     .main {
#         background-color: #0E1117 !important;
#         color: white;
#     }
#     .css-1d391kg {
#         background-color: #262730 !important;
#         color: white;
#     }
#     </style>
#     """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar untuk filter
st.sidebar.header("🔍 Filter Data")
recency_range = st.sidebar.slider("Recency Range", int(rfm['recency'].min()), int(rfm['recency'].max()), (int(rfm['recency'].min()), int(rfm['recency'].max())))
frequency_range = st.sidebar.slider("Frequency Range", int(rfm['frequency'].min()), int(rfm['frequency'].max()), (int(rfm['frequency'].min()), int(rfm['frequency'].max())))
monetary_range = st.sidebar.slider("Monetary Range", float(rfm['monetary'].min()), float(rfm['monetary'].max()), (float(rfm['monetary'].min()), float(rfm['monetary'].max())))

product_categories = all_data['product_category_name'].dropna().unique().tolist()
selected_category = st.sidebar.selectbox("Pilih Kategori Produk", ['All'] + product_categories)

# Tambahkan filter untuk segmen pelanggan
customer_segments = rfm['segment'].unique().tolist()
selected_segment = st.sidebar.selectbox("Pilih Segmen Pelanggan", ['All'] + customer_segments)

# Tambahkan filter periode waktu
if 'order_purchase_timestamp' in all_data.columns:
    min_date = all_data['order_purchase_timestamp'].min().date()
    max_date_filter = all_data['order_purchase_timestamp'].max().date()
    date_range = st.sidebar.date_input(
        "Rentang Waktu",
        [min_date, max_date_filter],
        min_value=min_date,
        max_value=max_date_filter
    )
    if len(date_range) == 2:
        start_date, end_date = date_range
        all_data = all_data[(all_data['order_purchase_timestamp'].dt.date >= start_date) & 
                           (all_data['order_purchase_timestamp'].dt.date <= end_date)]

if selected_category != 'All':
    filtered_data = all_data[all_data['product_category_name'] == selected_category]
else:
    filtered_data = all_data

filtered_rfm = rfm[(rfm['recency'].between(recency_range[0], recency_range[1])) &
                    (rfm['frequency'].between(frequency_range[0], frequency_range[1])) &
                    (rfm['monetary'].between(monetary_range[0], monetary_range[1]))]

if selected_segment != 'All':
    filtered_rfm = filtered_rfm[filtered_rfm['segment'] == selected_segment]
    customer_ids = filtered_rfm.index.tolist()
    filtered_data = filtered_data[filtered_data['customer_id'].isin(customer_ids)]

# Tambahkan tab untuk memisahkan bagian analisis
tabs = st.tabs(["📌 Summary", "👥 Customer Segmentation", "📊 Sales Analysis", "🔍 Product Analysis", "💡 Insights"])

with tabs[0]:
    st.subheader("📌 RFM Summary (Filtered)")
    st.write(filtered_rfm.describe())

    total_customers = filtered_rfm.shape[0]
    avg_recency = filtered_rfm['recency'].mean()
    avg_frequency = filtered_rfm['frequency'].mean()
    avg_monetary = filtered_rfm['monetary'].mean()

    # Tambahkan animasi loading untuk metrik
    with st.spinner("Loading metrics..."):
        time.sleep(0.5)  # Simulasi loading
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", total_customers)
        col2.metric("Avg Recency", f"{avg_recency:.2f} days")
        col3.metric("Avg Frequency", f"{avg_frequency:.2f} orders")
        col4.metric("Avg Monetary", f"${avg_monetary:.2f}")

    # Tambahkan baris metrik ringkasan tambahan
    total_orders = filtered_data['order_id'].nunique()
    total_revenue = filtered_data['payment_value'].sum()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    total_products = filtered_data['product_id'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", total_orders)
    col2.metric("Total Revenue", f"${total_revenue:.2f}")
    col3.metric("Avg Order Value", f"${avg_order_value:.2f}")
    col4.metric("Total Products", total_products)

    # Use only numeric columns for correlation
    st.subheader("📊 Heatmap Hubungan antara RFM Metrics")
    fig, ax = plt.subplots()
    # Only include numeric columns (recency, frequency, monetary)
    rfm_numeric = rfm[['recency', 'frequency', 'monetary']]
    sns.heatmap(rfm_numeric.corr(), annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

    

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

with tabs[1]:
    st.subheader("👥 Segmentasi Pelanggan")
    
    # Visualisasi segmen pelanggan
    segment_counts = filtered_rfm['segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_segments = px.pie(segment_counts, values='Count', names='Segment', title='Distribusi Segmen Pelanggan', 
                             color_discrete_sequence=px.colors.qualitative.Bold)
        fig_segments.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_segments, use_container_width=True)
    
    with col2:
        fig_segments_bar = px.bar(segment_counts, x='Segment', y='Count', 
                                 title='Jumlah Pelanggan per Segmen',
                                 color='Segment', color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_segments_bar, use_container_width=True)
    
    # 3D Scatter plot untuk segmentasi RFM
    st.subheader("🔍 3D Visualisasi RFM Segments")
    sample_size = min(1000, len(filtered_rfm))  # Batasi sampel untuk performa
    sampled_rfm = filtered_rfm.sample(sample_size) if len(filtered_rfm) > sample_size else filtered_rfm
    
    fig_3d = px.scatter_3d(sampled_rfm, x='recency', y='frequency', z='monetary',
                          color='segment', size='monetary', opacity=0.7,
                          title="3D Visualisasi Segmentasi RFM",
                          color_discrete_sequence=px.colors.qualitative.Bold)
    
    fig_3d.update_layout(scene=dict(
        xaxis_title='Recency (days)',
        yaxis_title='Frequency (orders)',
        zaxis_title='Monetary (value)'
    ))
    
    st.plotly_chart(fig_3d, use_container_width=True)
    
    # Karakteristik segmen
    st.subheader("📊 Karakteristik Segmen Pelanggan")
    segment_characteristics = filtered_rfm.groupby('segment').agg({
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean'
    }).reset_index()
    
    segment_characteristics = segment_characteristics.round(2)
    
    fig_char = px.bar(segment_characteristics, x='segment', y=['recency', 'frequency', 'monetary'],
                     title="Rata-rata Metrik RFM per Segmen", barmode='group',
                     color_discrete_sequence=px.colors.qualitative.Safe)
    
    st.plotly_chart(fig_char, use_container_width=True)

with tabs[2]:
    st.subheader("📅 Analisis Penjualan")
    
    # Tren penjualan dari waktu ke waktu
    st.subheader("📈 Tren Penjualan Bulanan")
    # Gunakan format tanggal yang JSON serializable
    all_data['order_purchase_month'] = all_data['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly_sales = all_data.groupby('order_purchase_month').size().reset_index(name='count')
    monthly_revenue = all_data.groupby('order_purchase_month')['payment_value'].sum().reset_index()
    monthly_revenue.columns = ['order_purchase_month', 'revenue']
    
    monthly_data = pd.merge(monthly_sales, monthly_revenue, on='order_purchase_month')
    
    # Tambahkan pilihan metrik untuk visualisasi
    sales_metric = st.radio("Pilih Metrik Penjualan", ["Jumlah Pesanan", "Pendapatan"], horizontal=True)
    
    y_column = 'count' if sales_metric == "Jumlah Pesanan" else 'revenue'
    y_title = 'Jumlah Pesanan' if sales_metric == "Jumlah Pesanan" else 'Pendapatan (USD)'
    
    fig_trend = px.line(monthly_data, x='order_purchase_month', y=y_column, 
                       title=f'Tren {sales_metric} Bulanan', markers=True,
                       labels={'order_purchase_month': 'Bulan', y_column: y_title})
    
    fig_trend.update_xaxes(categoryorder='category ascending')  # Mengurutkan bulan secara kronologis
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Heatmap Penjualan Mingguan
    if 'order_purchase_timestamp' in all_data.columns:
        st.subheader("🔥 Heatmap Penjualan Harian")
        all_data['day_of_week'] = all_data['order_purchase_timestamp'].dt.day_name()
        all_data['hour_of_day'] = all_data['order_purchase_timestamp'].dt.hour
        
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        hourly_sales = all_data.groupby(['day_of_week', 'hour_of_day']).size().reset_index(name='count')
        hourly_sales_pivot = hourly_sales.pivot_table(index='day_of_week', columns='hour_of_day', values='count', fill_value=0)
        
        # Reindex to ensure correct order of days
        hourly_sales_pivot = hourly_sales_pivot.reindex(day_order)
        
        fig = px.imshow(hourly_sales_pivot, 
                       labels=dict(x="Jam", y="Hari", color="Jumlah Pesanan"),
                       x=hourly_sales_pivot.columns, 
                       y=hourly_sales_pivot.index,
                       color_continuous_scale='Viridis')
        
        fig.update_layout(
            title="Heatmap Waktu Pemesanan (Hari vs Jam)",
            xaxis_title="Jam",
            yaxis_title="Hari"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Analisis Metode Pembayaran
    st.subheader("💳 Analisis Metode Pembayaran")
    if 'payment_type' in filtered_data.columns:
        payment_counts = filtered_data['payment_type'].value_counts()
        payment_revenue = filtered_data.groupby('payment_type')['payment_value'].sum().reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_payment = px.pie(
                values=payment_counts.values,
                names=payment_counts.index,
                title="Distribusi Metode Pembayaran",
                hole=0.4
            )
            st.plotly_chart(fig_payment, use_container_width=True)
        
        with col2:
            fig_payment_rev = px.bar(
                payment_revenue,
                x='payment_type',
                y='payment_value',
                title="Pendapatan per Metode Pembayaran",
                color='payment_type',
                labels={'payment_type': 'Metode Pembayaran', 'payment_value': 'Pendapatan (USD)'}
            )
            st.plotly_chart(fig_payment_rev, use_container_width=True)
    else:
        st.warning("Kolom 'payment_type' tidak ditemukan dalam dataset.")

with tabs[3]:
    st.subheader("🔍 Analisis Produk")
    
    # Top 10 Kategori Produk
    st.subheader("🏆 Top 10 Kategori Produk")
    top_categories = filtered_data['product_category_name'].value_counts().nlargest(10)
    fig_top = px.bar(
        x=top_categories.index, 
        y=top_categories.values, 
        title="Top 10 Kategori Produk",
        labels={'x': 'Kategori', 'y': 'Jumlah Penjualan'},
        color_discrete_sequence=['#1f77b4']
    )
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Word Cloud Produk Terlaris
    st.subheader("🌟 Word Cloud Produk Terlaris")
    # Menghindari error jika tidak ada kategori produk yang dipilih
    if filtered_data['product_category_name'].dropna().shape[0] > 0:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(filtered_data['product_category_name'].dropna()))
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.warning("Tidak ada data kategori produk untuk ditampilkan.")
    
    # Analisis Penjualan vs Review
    if 'review_score' in filtered_data.columns and 'product_category_name' in filtered_data.columns:
        st.subheader("⭐ Analisis Rating Produk")
        
        avg_reviews = filtered_data.groupby('product_category_name')['review_score'].mean().reset_index()
        avg_reviews = avg_reviews.sort_values('review_score', ascending=False).head(10)
        
        fig_reviews = px.bar(
            avg_reviews,
            x='product_category_name',
            y='review_score',
            title="Kategori Produk dengan Rating Tertinggi",
            color='review_score',
            color_continuous_scale=px.colors.sequential.Viridis,
            labels={'product_category_name': 'Kategori Produk', 'review_score': 'Rating Rata-rata'}
        )
        st.plotly_chart(fig_reviews, use_container_width=True)
        
        # Distribusi review score
        st.subheader("📊 Distribusi Rating")
        fig_rating_dist = px.histogram(
            filtered_data,
            x='review_score',
            nbins=5,
            title="Distribusi Rating Produk",
            color_discrete_sequence=['goldenrod']
        )
        fig_rating_dist.update_layout(bargap=0.1)
        st.plotly_chart(fig_rating_dist, use_container_width=True)
    
    # Peta Interaktif
    st.subheader("🗺️ Peta Distribusi Penjualan di Brazil")
    if 'customer_lat' in all_data.columns and 'customer_lng' in all_data.columns:
        map_data = all_data.dropna(subset=['customer_lat', 'customer_lng'])
        fig_map = px.scatter_mapbox(map_data, lat='customer_lat', lon='customer_lng', zoom=3, mapbox_style="carto-positron",
                                    title="Distribusi Pelanggan di Brazil")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Kolom 'customer_lat' dan 'customer_lng' tidak ditemukan dalam dataset.")

with tabs[4]:
    st.subheader("💡 Insights dan Rekomendasi")
    
    # Ekspor Data
    st.subheader("📤 Ekspor Data Analisis")
    
    # Fungsi helper untuk ekspor data
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Download RFM Data",
            data=convert_df_to_csv(filtered_rfm.reset_index()),
            file_name='rfm_data.csv',
            mime='text/csv',
        )
    
    with col2:
        st.download_button(
            label="📥 Download Filtered Sales Data",
            data=convert_df_to_csv(filtered_data),
            file_name='filtered_sales_data.csv',
            mime='text/csv',
        )
    
    # Tampilkan insights berdasarkan analisis data
    st.subheader("🔍 Key Insights")
    
    # Calculating insights
    top_segment = filtered_rfm['segment'].value_counts().index[0] if len(filtered_rfm) > 0 else "N/A"
    top_category = filtered_data['product_category_name'].value_counts().index[0] if 'product_category_name' in filtered_data.columns and len(filtered_data) > 0 else "N/A"
    
    if 'order_purchase_timestamp' in filtered_data.columns and len(filtered_data) > 0:
        filtered_data['month'] = filtered_data['order_purchase_timestamp'].dt.month
        filtered_data['day_of_week'] = filtered_data['order_purchase_timestamp'].dt.dayofweek
        peak_month = filtered_data['month'].value_counts().index[0]
        peak_month_name = calendar.month_name[peak_month]
        peak_day = filtered_data['day_of_week'].value_counts().index[0]
        peak_day_name = calendar.day_name[peak_day]
    else:
        peak_month_name = "N/A"
        peak_day_name = "N/A"
    
    insights = [
        f"Segmen pelanggan terbesar adalah '{top_segment}', yang memerlukan strategi khusus untuk mempertahankan loyalitas mereka.",
        f"Kategori produk terlaris adalah '{top_category}', yang menunjukkan permintaan pasar yang tinggi.",
        f"Bulan dengan penjualan tertinggi adalah {peak_month_name}, yang menunjukkan pola musiman dalam penjualan.",
        f"Hari dengan penjualan tertinggi adalah {peak_day_name}, yang dapat dimanfaatkan untuk strategi promosi.",
    ]
    
    for i, insight in enumerate(insights):
        st.write(f"{i+1}. {insight}")
    
    # Rekomendasi berdasarkan segmen pelanggan
    st.subheader("📋 Rekomendasi Strategi")
    
    rekomendasi = {
        "Champions": "Tawarkan program loyalitas eksklusif dan akses ke produk terbaru.",
        "Loyal Customers": "Berikan diskon khusus dan penawaran bundle untuk meningkatkan nilai transaksi.",
        "Potential Loyalists": "Promosikan program membership dan manfaatnya untuk mendorong pembelian berulang.",
        "New Customers": "Tawarkan pengalaman onboarding yang menarik dan insentif untuk pembelian kedua.",
        "Need Attention": "Kirimkan email personalisasi dengan penawaran untuk kembali berbelanja.",
        "At Risk": "Berikan diskon besar dan penawaran istimewa untuk mengembalikan minat mereka.",
        "Lost": "Jalankan kampanye reaktivasi dengan penawaran yang tidak dapat ditolak."
    }
    
    for segment, reco in rekomendasi.items():
        expander = st.expander(f"Strategi untuk Segmen '{segment}'")
        with expander:
            st.write(reco)
    
    # Prediksi Sederhana
    st.subheader("🔮 Prediksi Churn Risk")
    
    if len(filtered_rfm) > 0:
        # Menghitung risiko churn sederhana berdasarkan recency
        filtered_rfm['churn_risk'] = np.where(filtered_rfm['recency'] > 180, 'High',
                                             np.where(filtered_rfm['recency'] > 90, 'Medium', 'Low'))
        
        churn_counts = filtered_rfm['churn_risk'].value_counts().reset_index()
        churn_counts.columns = ['Risk Level', 'Count']
        
        fig_churn = px.pie(
            churn_counts,
            values='Count',
            names='Risk Level',
            title="Distribusi Risiko Churn Pelanggan",
            color='Risk Level',
            color_discrete_map={'High': 'red', 'Medium': 'orange', 'Low': 'green'}
        )
        
        st.plotly_chart(fig_churn, use_container_width=True)
        
        # Highlight high risk customers
        if 'High' in filtered_rfm['churn_risk'].values:
            high_risk = filtered_rfm[filtered_rfm['churn_risk'] == 'High'].shape[0]
            st.warning(f"⚠️ Terdapat {high_risk} pelanggan dengan risiko churn tinggi. Perlu tindakan segera untuk kampanye retensi.")

st.markdown("---")
st.caption("📌 Dashboard dibuat dengan Streamlit dan Plotly | Data: E-Commerce Public Dataset")
st.caption("👤 Nama: Muhammad Fery Syahputra")
st.caption("📧 Email: ferys2343@gmail.com")
st.caption("🆔 ID Dicoding: A009YBM322")

# Tambahkan feedback form
with st.expander("📝 Berikan Feedback"):
    # Use a form to collect inputs without rerunning until submission
    with st.form(key="feedback_form"):
        nama = st.text_input("Nama Anda")
        feedback = st.text_area("Bagaimana pendapat Anda tentang dashboard ini?")
        rating = st.slider("Rating (1-5)", 1, 5, 5)
        submit_button = st.form_submit_button("Submit Feedback")
    
    if submit_button:
        if feedback and nama:
            # Buat dictionary untuk data feedback
            feedback_data = {
                "nama": nama,
                "pesan": feedback,
                "rating": rating,
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Path file untuk menyimpan feedback
            feedback_file = "feedback.csv"
            
            # Buat DataFrame untuk data baru
            new_feedback_df = pd.DataFrame([feedback_data])
            
            try:
                # Coba baca file yang sudah ada
                if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
                    feedback_df = pd.read_csv(feedback_file)
                    feedback_df = pd.concat([feedback_df, new_feedback_df], ignore_index=True)
                else:
                    # Jika file tidak ada atau kosong, gunakan data baru saja
                    feedback_df = new_feedback_df
                
                # Simpan ke file CSV
                feedback_df.to_csv(feedback_file, index=False)
                st.success("Terima kasih atas feedback Anda!")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat menyimpan feedback: {str(e)}")
        else:
            st.error("Mohon isi nama dan feedback Anda.")

# Tampilkan semua feedback yang sudah masuk
st.header("💬 Feedback Pengunjung")

feedback_file = "feedback.csv"
try:
    if os.path.exists(feedback_file) and os.path.getsize(feedback_file) > 0:
        feedback_df = pd.read_csv(feedback_file)
        
        if not feedback_df.empty:
            # Tambahkan statistik ringkasan di bagian atas
            total_feedback = len(feedback_df)
            avg_rating = feedback_df['rating'].mean()
            
            # Tampilkan ringkasan dengan metrik
            col_stats1, col_stats2 = st.columns(2)
            with col_stats1:
                st.metric(label="Total Feedback", value=total_feedback)
            with col_stats2:
                st.metric(label="Rating Rata-rata", value=f"{avg_rating:.1f} ⭐")
            
            # Tambahkan filter dan sorting
            col_filter, col_sort = st.columns(2)
            with col_filter:
                min_rating = st.slider("Filter berdasarkan rating minimum:", 1, 5, 1)
                filtered_df = feedback_df[feedback_df['rating'] >= min_rating]
            with col_sort:
                sort_option = st.selectbox("Urutkan berdasarkan:", 
                                          ["Terbaru", "Terlama", "Rating Tertinggi", "Rating Terendah"])
            
            # Terapkan pengurutan yang dipilih
            if sort_option == "Terbaru":
                filtered_df = filtered_df.sort_values(by="timestamp", ascending=False)
            elif sort_option == "Terlama":
                filtered_df = filtered_df.sort_values(by="timestamp", ascending=True)
            elif sort_option == "Rating Tertinggi":
                filtered_df = filtered_df.sort_values(by="rating", ascending=False)
            else:  # Rating Terendah
                filtered_df = filtered_df.sort_values(by="rating", ascending=True)
            
            # Tambahkan baris pencarian sederhana
            search_query = st.text_input("Cari berdasarkan nama atau kata kunci:")
            if search_query:
                filtered_df = filtered_df[
                    filtered_df['nama'].str.contains(search_query, case=False) | 
                    filtered_df['pesan'].str.contains(search_query, case=False)
                ]
            
            st.markdown("---")
            
            # Tampilkan jumlah feedback yang ditampilkan setelah filter
            st.write(f"Menampilkan {len(filtered_df)} dari {total_feedback} feedback")
            
            # Gunakan layout dengan card untuk menampilkan feedback
            if not filtered_df.empty:
                # Tentukan jumlah kolom untuk grid card
                cols_per_row = 2
                
                # Buat baris untuk setiap n card
                for i in range(0, len(filtered_df), cols_per_row):
                    cols = st.columns(cols_per_row)
                    
                    # Isi setiap kolom dengan card
                    for j in range(cols_per_row):
                        if i + j < len(filtered_df):
                            row = filtered_df.iloc[i + j]
                            
                            # Konversi timestamp ke format yang lebih mudah dibaca
                            try:
                                timestamp = pd.to_datetime(row['timestamp'])
                                formatted_date = timestamp.strftime("%d %b %Y, %H:%M")
                            except:
                                formatted_date = row['timestamp']
                            
                            # Tentukan warna berdasarkan rating
                            if row['rating'] >= 4:
                                card_color = "#4CAF50"  # Hijau
                                bg_color = "#e8f5e9"
                                text_bg = "#c8e6c9"  # Latar belakang pesan yang lebih gelap
                            elif row['rating'] >= 3:
                                card_color = "#FF9800"  # Oranye
                                bg_color = "#fff3e0"
                                text_bg = "#ffe0b2"  # Latar belakang pesan yang lebih gelap
                            else:
                                card_color = "#F44336"  # Merah
                                bg_color = "#ffebee"
                                text_bg = "#ffcdd2"  # Latar belakang pesan yang lebih gelap
                            
                            # Buat card dengan HTML dan CSS
                            with cols[j]:
                                st.markdown(f"""
                                <div style="
                                    border-radius: 10px;
                                    border-left: 5px solid {card_color};
                                    background-color: {bg_color};
                                    padding: 15px;
                                    margin-bottom: 15px;
                                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                                ">
                                    <h3 style="margin-top: 0; color: #333;">{row['nama']}</h3>
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                        <span style="color: #666; font-size: 0.8em;">📅 {formatted_date}</span>
                                        <span style="font-size: 1.2em;">{"⭐" * int(row['rating'])}</span>
                                    </div>
                                    <div style="
                                        background-color: {text_bg};
                                        padding: 12px;
                                        border-radius: 5px;
                                        margin-bottom: 0;
                                        color: #333;
                                        font-weight: 400;
                                        border: 1px solid rgba(0,0,0,0.1);
                                    ">
                                        {row['pesan']}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("Tidak ada feedback yang sesuai dengan filter atau pencarian Anda.")
        else:
            st.info("Belum ada feedback yang diberikan.")
    else:
        st.info("Belum ada feedback yang diberikan.")

except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca feedback: {str(e)}")
    # Jika terjadi error, hapus file yang mungkin rusak
    if os.path.exists(feedback_file) and os.path.getsize(feedback_file) == 0:
        os.remove(feedback_file)
        st.info("File feedback telah direset. Silakan coba lagi.")