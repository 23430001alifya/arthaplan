import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="ArthaPlan Dashboard", layout="wide")

# ======================
# LOAD DATA
# ======================
try:
    df = pd.read_csv("main_data.csv")
    st.success("Data berhasil dimuat")
except Exception as e:
    st.error(f"Gagal load data: {e}")
    st.stop()

# ======================
# SIDEBAR
# ======================
st.sidebar.title("🔧 Filter Data")

kategori_filter = st.sidebar.multiselect(
    "Pilih Kategori",
    options=df['kategori'].unique(),
    default=df['kategori'].unique()
)

df = df[df['kategori'].isin(kategori_filter)]

# ======================
# TITLE
# ======================
st.title("💰 ArthaPlan Financial Dashboard")

# ======================
# METRICS
# ======================
col1, col2, col3 = st.columns(3)

col1.metric("Total User", df['client_id'].nunique())
col2.metric("Total Limit (Rp)", f"{df['total_limit'].sum():,.0f}")
col3.metric("Rata-rata Limit (Rp)", f"{df['total_limit'].mean():,.0f}")

# ======================
# CHART 1 - SEGMENTASI
# ======================
st.subheader("📊 Segmentasi Pengguna")

fig1, ax1 = plt.subplots()
df['kategori'].value_counts().plot(kind='bar', ax=ax1)
st.pyplot(fig1)

# ======================
# CHART 2 - DISTRIBUSI LIMIT
# ======================
st.subheader("📈 Distribusi Credit Limit")

fig2, ax2 = plt.subplots()
ax2.hist(df['credit_limit_rupiah'], bins=50)
st.pyplot(fig2)

# ======================
# CHART 3 - SCATTER
# ======================
st.subheader("📉 Jumlah Kartu vs Total Limit")

fig3, ax3 = plt.subplots()
ax3.scatter(df['jumlah_kartu'], df['total_limit'])
ax3.set_xlabel("Jumlah Kartu")
ax3.set_ylabel("Total Limit")
st.pyplot(fig3)

# ======================
# OVERBUDGET
# ======================
st.subheader("🚨 Overbudget Analysis")

fig4, ax4 = plt.subplots()
df['overbudget'].value_counts().plot(kind='bar', ax=ax4)
st.pyplot(fig4)

# ======================
# TABLE
# ======================
st.subheader("📋 Data Preview")
st.dataframe(df.head(50))
