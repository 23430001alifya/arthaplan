import streamlit as st
import pandas as pd
import os
import plotly.express as px

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="ArthaPlan Dashboard", layout="wide")
st.title("💰 ArthaPlan Interactive Dashboard")

# ======================
# LOAD DATA (ANTI ERROR PATH)
# ======================
@st.cache_data
def load_data():
    possible_paths = [
        "main_data.csv",
        "../main_data.csv",
        "dashboard/main_data.csv"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return pd.read_csv(path)
    
    st.error("❌ File main_data.csv tidak ditemukan!")
    st.write("📁 Files tersedia:", os.listdir())
    st.stop()

df = load_data()

# ======================
# VALIDASI KOLOM
# ======================
required_cols = ['client_id', 'kategori', 'total_limit', 'jumlah_kartu', 'credit_limit_rupiah', 'overbudget']

missing = [col for col in required_cols if col not in df.columns]

if missing:
    st.error(f"❌ Kolom tidak ditemukan: {missing}")
    st.stop()

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("🔧 Filter Data")

kategori = st.sidebar.multiselect(
    "Pilih Kategori",
    df['kategori'].unique(),
    default=df['kategori'].unique()
)

min_limit, max_limit = st.sidebar.slider(
    "Range Total Limit",
    int(df['total_limit'].min()),
    int(df['total_limit'].max()),
    (int(df['total_limit'].min()), int(df['total_limit'].max()))
)

df = df[
    (df['kategori'].isin(kategori)) &
    (df['total_limit'] >= min_limit) &
    (df['total_limit'] <= max_limit)
]

# ======================
# METRICS
# ======================
st.subheader("📊 Ringkasan")

col1, col2, col3 = st.columns(3)

col1.metric("Total User", df['client_id'].nunique())
col2.metric("Total Limit", f"Rp {df['total_limit'].sum():,.0f}")
col3.metric("Rata-rata Limit", f"Rp {df['total_limit'].mean():,.0f}")

# ======================
# CHART 1 - PIE
# ======================
st.subheader("📊 Segmentasi Pengguna")

fig1 = px.pie(df, names='kategori', title='Distribusi Kategori')
st.plotly_chart(fig1, use_container_width=True)

# ======================
# CHART 2 - HISTOGRAM
# ======================
st.subheader("📈 Distribusi Credit Limit")

fig2 = px.histogram(df, x='credit_limit_rupiah', nbins=50)
st.plotly_chart(fig2, use_container_width=True)

# ======================
# CHART 3 - SCATTER
# ======================
st.subheader("📉 Perilaku Pengguna")

fig3 = px.scatter(
    df,
    x='jumlah_kartu',
    y='total_limit',
    color='kategori',
    size='total_limit',
    hover_data=['client_id']
)

st.plotly_chart(fig3, use_container_width=True)

# ======================
# CHART 4 - OVERBUDGET
# ======================
st.subheader("🚨 Overbudget Analysis")

over = df['overbudget'].value_counts().reset_index()
over.columns = ['status', 'jumlah']

fig4 = px.bar(over, x='status', y='jumlah', color='status')
st.plotly_chart(fig4, use_container_width=True)

# ======================
# TOP USERS
# ======================
st.subheader("🏆 Top 10 User Limit Tertinggi")

top_users = df.sort_values(by='total_limit', ascending=False).head(10)
st.dataframe(top_users)

# ======================
# INSIGHT
# ======================
st.subheader("💡 Insight")

st.info("""
- User kategori **Boros** memiliki limit lebih tinggi  
- Semakin banyak kartu → potensi overbudget meningkat  
- ArthaPlan dapat memberikan notifikasi berbasis perilaku user  
""")

# ======================
# DATA TABLE
# ======================
st.subheader("📋 Data Preview")
st.dataframe(df.head(50))
