import os
import streamlit as st
import pandas as pd
import plotly.express as px

# ... (kode lainnya tetap sama)

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    # Mengambil path folder tempat app.py berada
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data_penjualan_sintesis.csv")
    
    df = pd.read_csv(file_path, parse_dates=["Tanggal"])
    df["Total_Penjualan"] = df["Harga"] * df["Jumlah_Terjual"]
    return df
