import streamlit as st
import pandas as pd
import os

# ============================================================
# 1. KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Bedah Kasus 1 - Penjualan",
    page_icon="🛒",
    layout="wide"
)

# ============================================================
# 2. FUNGSI LOAD DATA (KHUSUS BEDAH KASUS 1)
# ============================================================
@st.cache_data
def load_data():
    # Nama file yang benar sesuai gambar Anda
    nama_file = "data_penjualan_sintesis.csv"
    
    # Pencarian otomatis lokasi file
    kandidat_path = [
        nama_file,                        # Di folder yang sama (app.py)
        f"bedah_kasus_1/{nama_file}",     # Di dalam sub-folder
        f"../{nama_file}",                # Di luar folder
    ]
    
    for path in kandidat_path:
        if os.path.exists(path):
            return pd.read_csv(path)

    st.error(f"❌ File '{nama_file}' tidak ditemukan.")
    st.stop()

# Panggil fungsi load data
df = load_data()

# --- OTOMATISASI TANGGAL ---
# Jika ada kolom yang berbau 'tanggal' atau 'date', ubah ke format datetime
kolom_tanggal = [col for col in df.columns if 'tanggal' in col.lower() or 'date' in col.lower()]
if kolom_tanggal:
    df[kolom_tanggal[0]] = pd.to_datetime(df[kolom_tanggal[0]], errors='coerce')

# ============================================================
# 3. SIDEBAR - FILTER DATA
# ============================================================
st.sidebar.header("🔎 Filter Data Penjualan")
filtered_df = df.copy()

# Filter otomatis untuk kolom teks/kategori (Produk, Wilayah, dll)
for col in df.select_dtypes(include=["object", "category"]).columns:
    unique_vals = df[col].dropna().unique().tolist()
    if 1 < len(unique_vals) <= 30: 
        pilihan = st.sidebar.multiselect(f"Pilih {col}:", options=unique_vals, default=unique_vals)
        filtered_df = filtered_df[filtered_df[col].isin(pilihan)]

# Filter untuk kolom angka (Harga, Kuantitas, Total, dll)
for col in df.select_dtypes(include=["number"]).columns:
    min_val = float(df[col].min())
    max_val = float(df[col].max())
    if min_val < max_val:
        rentang = st.sidebar.slider(
            f"Rentang {col}:",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        )
        filtered_df = filtered_df[
            (filtered_df[col] >= rentang[0]) & (filtered_df[col] <= rentang[1])
        ]

# ============================================================
# 4. HALAMAN UTAMA - METRIK & TABEL
# ============================================================
st.title("🛒 Dashboard Analisis Penjualan")
st.markdown("Aplikasi ini menampilkan data dan analisis dari `data_penjualan_sintesis.csv`. Gunakan sidebar kiri untuk memfilter.")

# Menampilkan Metrik Ringkasan
col1, col2, col3 = st.columns(3)
col1.metric("📄 Total Transaksi", f"{len(filtered_df):,}")
col2.metric("📊 Jumlah Kolom", f"{df.shape[1]}")

# Coba cari kolom total harga / pendapatan untuk dijumlahkan
kolom_pendapatan = [col for col in df.columns if 'total' in col.lower() or 'pendapatan' in col.lower() or 'revenue' in col.lower()]
if kolom_pendapatan:
    total_pendapatan = filtered_df[kolom_pendapatan[0]].sum()
    col3.metric(f"💰 Total {kolom_pendapatan[0]}", f"Rp {total_pendapatan:,.0f}")

st.divider()

# Tampilkan Tabel Data
st.subheader("📋 Tabel Data Transaksi")
st.dataframe(filtered_df, use_container_width=True)

# ============================================================
# 5. STATISTIK & VISUALISASI
# ============================================================
st.subheader("📊 Visualisasi Data")

# Jika ada kolom tanggal, buat grafik tren (Time Series)
if kolom_tanggal:
    st.markdown("**Tren Penjualan Berdasarkan Waktu**")
    kolom_waktu = kolom_tanggal[0]
    
    # Mengelompokkan berdasarkan bulan/tanggal
    tren = filtered_df.groupby(filtered_df[kolom_waktu].dt.date).size().reset_index(name='Jumlah Transaksi')
    tren.set_index(kolom_waktu, inplace=True)
    st.line_chart(tren)
    
    # Grafik pendapatan per waktu (jika ada kolom pendapatan)
    if kolom_pendapatan:
        st.markdown(f"**Tren Total {kolom_pendapatan[0]}**")
        tren_pendapatan = filtered_df.groupby(filtered_df[kolom_waktu].dt.date)[kolom_pendapatan[0]].sum()
        st.bar_chart(tren_pendapatan)

# Grafik batang untuk kolom kategori terbanyak
for col in df.select_dtypes(include=["object", "category"]).columns:
    if 1 < df[col].nunique() <= 15:
        st.markdown(f"**Distribusi Berdasarkan {col}**")
        st.bar_chart(filtered_df[col].value_counts())

with st.expander("📈 Lihat Statistik Deskriptif Lengkap"):
    st.write(filtered_df.describe(include="all"))

# ============================================================
# 6. FITUR DOWNLOAD DATA
# ============================================================
st.subheader("⬇️ Unduh Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Data Penjualan Terfilter (CSV)",
    data=csv,
    file_name="data_penjualan_terfilter.csv",
    mime="text/csv",
)
