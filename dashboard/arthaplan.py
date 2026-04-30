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
# LOAD DATA (AUTO PATH)
# ======================
@st.cache_data
def load_data():
    paths = ["main_data.csv", "../main_data.csv", "dashboard/main_data.csv"]
    for path in paths:
        if os.path.exists(path):
            return pd.read_csv(path)

    st.error("❌ File main_data.csv tidak ditemukan")
    st.write("📁 File tersedia:", os.listdir())
    st.stop()

df = load_data()


# ======================
# CLEAN DATA (RUPIAH)
# ======================
if 'credit_limit_rupiah' in df.columns:
    df['credit_limit_rupiah'] = (
        df['credit_limit_rupiah']
        .astype(str)
        .str.replace("Rp", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
    )

    df['credit_limit_rupiah'] = pd.to_numeric(df['credit_limit_rupiah'], errors='coerce')

# ======================
# VALIDASI KOLOM PENTING
# ======================
if 'client_id' not in df.columns:
    st.error("❌ Kolom client_id tidak ditemukan")
    st.stop()

if 'credit_limit_rupiah' not in df.columns:
    st.error("❌ Kolom credit_limit_rupiah tidak ditemukan")
    st.stop()

# ======================
# FEATURE ENGINEERING
# ======================
if 'total_limit' not in df.columns or 'jumlah_kartu' not in df.columns:

    user_limit = df.groupby('client_id')['credit_limit_rupiah'].sum().reset_index()
    user_limit.columns = ['client_id', 'total_limit']

    user_cards = df.groupby('client_id').size().reset_index(name='jumlah_kartu')

    user_data = pd.merge(user_limit, user_cards, on='client_id')
    df = pd.merge(df, user_data, on='client_id', how='left')

# ======================
# KATEGORI USER
# ======================
if 'kategori' not in df.columns:
    q1 = df['total_limit'].quantile(0.33)
    q2 = df['total_limit'].quantile(0.66)

    def kategori(x):
        if x < q1:
            return "Hemat"
        elif x < q2:
            return "Normal"
        else:
            return "Boros"

    df['kategori'] = df['total_limit'].apply(kategori)

# ======================
# OVERBUDGET
# ======================
if 'overbudget' not in df.columns:
    df['overbudget'] = df['total_limit'] > df['total_limit'].mean()

# ======================
# SIDEBAR UI ADVANCED
# ======================
st.sidebar.markdown("## ⚙️ Smart Filter Panel")

# ======================
# MODE FILTER
# ======================
mode = st.sidebar.radio(
    "Mode Filter",
    ["Basic", "Advanced"],
    horizontal=True
)

# ======================
# KATEGORI FILTER
# ======================
kategori_list = df['kategori'].dropna().unique()

kategori = st.sidebar.multiselect(
    "🏷️ Pilih Kategori",
    kategori_list,
    default=list(kategori_list)
)

# ======================
# RANGE LIMIT
# ======================
min_limit = int(df['total_limit'].min())
max_limit = int(df['total_limit'].max())

range_limit = st.sidebar.slider(
    "💰 Range Total Limit",
    min_limit,
    max_limit,
    (min_limit, max_limit),
    step=100000
)

st.sidebar.caption(
    f"📊 Rp {range_limit[0]:,} — Rp {range_limit[1]:,}"
)

# ======================
# ADVANCED FILTER
# ======================
if mode == "Advanced":

    st.sidebar.markdown("### 🔬 Advanced Options")

    show_overbudget = st.sidebar.checkbox("Tampilkan hanya Overbudget")

    min_kartu = st.sidebar.number_input(
        "Minimum Jumlah Kartu",
        min_value=0,
        max_value=int(df['jumlah_kartu'].max()),
        value=0
    )

else:
    show_overbudget = False
    min_kartu = 0

# ======================
# APPLY FILTER
# ======================
df_filtered = df[
    (df['kategori'].isin(kategori)) &
    (df['total_limit'] >= range_limit[0]) &
    (df['total_limit'] <= range_limit[1]) &
    (df['jumlah_kartu'] >= min_kartu)
]

if show_overbudget:
    df_filtered = df_filtered[df_filtered['overbudget'] == True]

# ======================
# RESET BUTTON
# ======================
if st.sidebar.button("🔄 Reset Semua Filter"):
    st.experimental_rerun()

# ======================
# MINI INSIGHT SIDEBAR
# ======================
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Insight")

st.sidebar.metric("👥 User", df_filtered['client_id'].nunique())
st.sidebar.metric("💰 Avg Limit", f"Rp {df_filtered['total_limit'].mean():,.0f}")
st.sidebar.metric("🚨 Overbudget", df_filtered['overbudget'].sum())

# ======================
# PROGRESS BAR (INTERAKTIF)
# ======================
over_pct = df_filtered['overbudget'].mean() if len(df_filtered) > 0 else 0

st.sidebar.markdown("### 🚨 Risk Level")
st.sidebar.progress(float(over_pct))

# ======================
# GUNAKAN DATA INI
# ======================
df = df_filtered

# ======================
# METRICS
# ======================
st.subheader("📊 Ringkasan")

col1, col2, col3 = st.columns(3)

col1.metric("Total User", df['client_id'].nunique())
col2.metric("Total Limit", f"Rp {df['total_limit'].sum():,.0f}")
col3.metric("Rata-rata Limit", f"Rp {df['total_limit'].mean():,.0f}")

# ======================
# VISUALISASI
# ======================

# PIE
st.subheader("📊 Segmentasi Pengguna")
fig1 = px.pie(df, names='kategori')
st.plotly_chart(fig1, use_container_width=True)

# HISTOGRAM
st.subheader("📈 Distribusi Credit Limit")
fig2 = px.histogram(df, x='credit_limit_rupiah', nbins=50)
st.plotly_chart(fig2, use_container_width=True)

# SCATTER
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

# OVERBUDGET
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
- Sistem dapat memberikan notifikasi keuangan berbasis perilaku  
""")

# ======================
# DATA TABLE
# ======================
st.subheader("📋 Data Preview")
st.dataframe(df.head(50))
