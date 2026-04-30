import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="ArthaPlan Dashboard", layout="wide")

st.title("💰 ArthaPlan Dashboard")

# ======================
# DEBUG FILE
# ======================
st.write("📁 Files di directory:")
st.write(os.listdir())

# ======================
# LOAD DATA (AMAN)
# ======================
try:
    df = pd.read_csv("main_data.csv")
    st.success("✅ Data berhasil dimuat")
except Exception as e:
    st.error("❌ Gagal load data")
    st.write(e)
    st.stop()

# ======================
# DEBUG DATA
# ======================
st.write("📊 Kolom dataset:")
st.write(df.columns)

st.write("📄 Preview data:")
st.dataframe(df.head())

# ======================
# VALIDASI KOLOM WAJIB
# ======================
required_cols = ['kategori', 'credit_limit_rupiah', 'jumlah_kartu', 'total_limit', 'overbudget']

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"❌ Kolom tidak ditemukan: {missing_cols}")
    st.stop()

# ======================
# SIDEBAR
# ======================
kategori_filter = st.sidebar.multiselect(
    "Filter Kategori",
    df['kategori'].unique(),
    default=df['kategori'].unique()
)

df = df[df['kategori'].isin(kategori_filter)]

# ======================
# METRICS
# ======================
st.subheader("📊 Ringkasan")

col1, col2, col3 = st.columns(3)
col1.metric("Total User", df['client_id'].nunique())
col2.metric("Total Limit", f"{df['total_limit'].sum():,.0f}")
col3.metric("Rata-rata Limit", f"{df['total_limit'].mean():,.0f}")

# ======================
# VISUALISASI
# ======================
import matplotlib.pyplot as plt

st.subheader("Segmentasi Pengguna")
fig1, ax1 = plt.subplots()
df['kategori'].value_counts().plot(kind='bar', ax=ax1)
st.pyplot(fig1)

st.subheader("Distribusi Credit Limit")
fig2, ax2 = plt.subplots()
ax2.hist(df['credit_limit_rupiah'], bins=50)
st.pyplot(fig2)

st.subheader("Jumlah Kartu vs Total Limit")
fig3, ax3 = plt.subplots()
ax3.scatter(df['jumlah_kartu'], df['total_limit'])
st.pyplot(fig3)

st.subheader("Overbudget")
fig4, ax4 = plt.subplots()
df['overbudget'].value_counts().plot(kind='bar', ax=ax4)
st.pyplot(fig4)
