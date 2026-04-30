import streamlit as st
import pandas as pd
import os

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="ArthaPlan Dashboard", layout="wide")

st.title("💰 ArthaPlan Financial Dashboard")

# ======================
# LOAD DATA (ANTI ERROR PATH)
# ======================
base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, "..", "dashboard/main_data.csv")

@st.cache_data
def load_data():
    return pd.read_csv(file_path)

try:
    df = load_data()
    st.success("✅ Data berhasil dimuat")
except Exception as e:
    st.error(f"❌ Gagal load data: {e}")
    st.stop()

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("🔧 Filter")

kategori = st.sidebar.multiselect(
    "Pilih Kategori",
    df['kategori'].unique(),
    default=df['kategori'].unique()
)

df = df[df['kategori'].isin(kategori)]

# ======================
# METRICS
# ======================
st.subheader("📊 Ringkasan")

col1, col2, col3 = st.columns(3)

col1.metric("Total User", df['client_id'].nunique())
col2.metric("Total Limit", f"Rp {df['total_limit'].sum():,.0f}")
col3.metric("Rata-rata Limit", f"Rp {df['total_limit'].mean():,.0f}")

# ======================
# CHART 1 (BUILT-IN)
# ======================
st.subheader("📊 Segmentasi Pengguna")
st.bar_chart(df['kategori'].value_counts())

# ======================
# CHART 2
# ======================
st.subheader("📈 Distribusi Credit Limit")
st.bar_chart(df['credit_limit_rupiah'])

# ======================
# CHART 3
# ======================
st.subheader("📉 Jumlah Kartu vs Total Limit")
st.line_chart(df[['jumlah_kartu', 'total_limit']])

# ======================
# OVERBUDGET
# ======================
st.subheader("🚨 Overbudget")
st.bar_chart(df['overbudget'].value_counts())

# ======================
# INSIGHT
# ======================
st.subheader("💡 Insight")

st.write("""
- Pengguna kategori **Boros** memiliki limit lebih tinggi
- Semakin banyak kartu → potensi overbudget meningkat
- ArthaPlan dapat memberikan notifikasi finansial berbasis kategori
""")

# ======================
# DATA TABLE
# ======================
st.subheader("📋 Data Preview")
st.dataframe(df.head(50))
