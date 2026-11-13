import streamlit as st
import pandas as pd
import os

# ============================================================
# 1. KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Bedah Kasus 1 - Data",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# 2. FUNGSI LOAD DATA (PENCARI OTOMATIS)
# ============================================================
@st.cache_data
def load_data():
    # Mencari file CSV di berbagai kemungkinan lokasi
    kandidat_path = [
        "data.csv",                           # Coba tebak nama umum
        "dataset.csv",
        "data_kasus_1.csv",
        "bedah_kasus_1/data.csv",             # Jika di dalam folder
        "bedah_kasus_1/dataset.csv",
        "bedah_kasus_1/data_kasus_1.csv",
        "bedah_kasus_1/data_sintesis.csv",    # Kemungkinan nama dari kasus sebelumnya
    ]
    
    # Looping untuk mencari file yang benar-benar ada
    for path in kandidat_path:
        if os.path.exists(path):
            # st.success(f"✅ Data berhasil dimuat dari: {path}")
            return pd.read_csv(path)

    # --- JIKA FILE TIDAK DITEMUKAN, TAMPILKAN DIAGNOSA ---
    st.error("❌ File data CSV tidak ditemukan.")
    st.write("Pastikan Anda sudah meng-upload file CSV ke repository `bedah_kasus_1`.")
    
    st.write("**Isi folder saat ini:**")
    try:
        st.code("\n".join(os.listdir(".")))
    except:
        pass
        
    st.write("**Isi folder bedah_kasus_1 (jika ada):**")
    try:
        if os.path.exists("bedah_kasus_1"):
            st.code("\n".join(os.listdir("bedah_kasus_1")))
    except:
        pass
        
    st.stop()

# Panggil fungsi load data
df = load_data()

# ============================================================
# 3. SIDEBAR - FILTER DATA
# ============================================================
st.sidebar.header("🔎 Filter Data")
filtered_df = df.copy()

# Filter otomatis untuk kolom teks/kategori
for col in df.select_dtypes(include=["object", "category"]).columns:
    unique_vals = df[col].dropna().unique().tolist()
    if 1 < len(unique_vals) <= 30: 
        pilihan = st.sidebar.multiselect(f"Pilih {col}:", options=unique_vals, default=unique_vals)
        filtered_df = filtered_df[filtered_df[col].isin(pilihan)]

# Filter untuk kolom angka (seperti Harga, Jumlah, dll)
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
st.title("📊 Dashboard Bedah Kasus 1")
st.markdown("Aplikasi ini menampilkan data untuk Bedah Kasus 1. Gunakan sidebar untuk memfilter.")

# Menampilkan Metrik Ringkasan
col1, col2 = st.columns(2)
col1.metric("📄 Total Baris Data", f"{len(filtered_df):,}")
col2.metric("📊 Total Kolom", f"{df.shape[1]}")

st.divider()

# Tampilkan Tabel Data
st.subheader("📋 Tabel Data")
st.dataframe(filtered_df, use_container_width=True)

# ============================================================
# 5. STATISTIK & VISUALISASI
# ============================================================
with st.expander("📈 Lihat Statistik Deskriptif"):
    st.write(filtered_df.describe(include="all"))

# Visualisasi sederhana
num_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
if num_cols:
    st.subheader("📊 Visualisasi Data")
    kolom_grafik = st.selectbox("Pilih kolom untuk melihat grafik:", num_cols)
    st.bar_chart(filtered_df[kolom_grafik].value_counts().sort_index())

# ============================================================
# 6. FITUR DOWNLOAD DATA
# ============================================================
st.subheader("⬇️ Unduh Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Data Terfilter (CSV)",
    data=csv,
    file_name="data_terfilter_kasus_1.csv",
    mime="text/csv",
)
