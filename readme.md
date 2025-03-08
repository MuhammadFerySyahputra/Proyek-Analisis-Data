# E-Commerce Data Analysis Dashboard

## 📌 Deskripsi Proyek
Proyek ini bertujuan untuk menganalisis dataset transaksi e-commerce menggunakan berbagai teknik analisis data. Analisis ini dilakukan untuk memahami perilaku pelanggan, tren transaksi, dan metrik bisnis utama yang dapat membantu dalam pengambilan keputusan.

## 🎯 Tujuan Analisis

### 1. **RFM Analysis (Recency, Frequency, Monetary)**
   - **Recency (R):** Mengukur berapa lama sejak pelanggan terakhir melakukan transaksi. Semakin kecil nilai recency, semakin aktif pelanggan.
   - **Frequency (F):** Mengukur seberapa sering pelanggan melakukan transaksi dalam periode tertentu.
   - **Monetary (M):** Mengukur total nilai transaksi yang dilakukan oleh pelanggan.
   - **Tujuan:** Menentukan segmentasi pelanggan berdasarkan aktivitas belanja mereka dan mengidentifikasi pelanggan yang bernilai tinggi.

### 2. **Distribusi Recency, Frequency, dan Monetary**
   - **Histogram Recency:** Memvisualisasikan distribusi waktu sejak transaksi terakhir pelanggan.
   - **Histogram Frequency:** Menampilkan pola seberapa sering pelanggan bertransaksi.
   - **Histogram Monetary:** Memvisualisasikan distribusi nilai transaksi pelanggan.
   - **Tujuan:** Memahami pola transaksi pelanggan untuk pengambilan keputusan strategis.

### 3. **Dashboard Interaktif dengan Streamlit**
   - Menampilkan metrik utama seperti jumlah pelanggan, rata-rata recency, frequency, dan monetary.
   - Filter interaktif untuk menyaring pelanggan berdasarkan nilai RFM.
   - Visualisasi interaktif menggunakan Plotly untuk memahami pola transaksi lebih dalam.
   - **Tujuan:** Menyediakan alat eksplorasi data yang mudah digunakan dan memberikan wawasan bisnis secara real-time.

## 🛠 Teknologi yang Digunakan
- **Python** (pandas, numpy, datetime, plotly, streamlit)
- **Streamlit** untuk membangun dashboard interaktif
- **Plotly** untuk visualisasi data
- **Jupyter Notebook** untuk eksplorasi awal data

## 📊 Cara Menjalankan Dashboard
1. Pastikan Python dan pustaka yang diperlukan telah diinstal:
   ```sh
   pip install streamlit pandas plotly
   ```
2. Jalankan dashboard dengan perintah berikut:
   ```sh
   streamlit run dashboard.py
   ```

## 👤 Informasi Pembuat
- **Nama:** Muhammad Fery Syahputra  
- **Email:** ferys2343@gmail.com  
- **ID Dicoding:** A009YBM322  

---
📌 *Dashboard ini dibuat sebagai bagian dari proyek analisis data e-commerce untuk memberikan wawasan yang lebih dalam terhadap perilaku pelanggan dan tren transaksi.*

