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
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    for path in ["main_data.csv", "../main_data.csv", "dashboard/main_data.csv"]:
        if os.path.exists(path):
            return pd.read_csv(path)

    st.error("❌ File tidak ditemukan")
    st.write("📁 Files:", os.listdir())
    st.stop()

df = load_data()

# ======================
# FEATURE ENGINEERING
# ======================
if 'total_limit' not in df.columns or 'jumlah_kartu' not in df.columns:

    st.warning("⚠️ Kolom belum lengkap, membuat feature otomatis...")

    user_limit = df.groupby('client_id')['credit_limit_rupiah'].sum().reset_index()
    user_limit.columns = ['client_id', 'total_limit']

    user_cards = df.groupby('client_id').size().reset_index(name='jumlah_kartu')

    user_data = pd.merge(user_limit, user_cards, on='client_id')
    df = pd.merge(df, user_data, on='client_id', how='left')

# ======================
# KATEGORI
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
# SIDEBAR
# ======================
st.sidebar.header("🔧 Filter")

kategori_list = df['kategori'].unique()

kategori = st.sidebar.multiselect(
    "Pilih Kategori",
    kategori_list,
    default=kategori_list
)

df = df[df['kategori'].isin(kategori)]

# ======================
# METRICS
# ======================
col1, col2, col3 = st.columns(3)

col1.metric("Total User", df['client_id'].nunique())
col2.metric("Total Limit", f"Rp {df['total_limit'].sum():,.0f}")
col3.metric("Avg Limit", f"Rp {df['total_limit'].mean():,.0f}")

# ======================
# VISUAL
# ======================
st.subheader("📊 Segmentasi")
fig1 = px.pie(df, names='kategori')
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📈 Distribusi Limit")
fig2 = px.histogram(df, x='credit_limit_rupiah')
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📉 Scatter")
fig3 = px.scatter(df, x='jumlah_kartu', y='total_limit', color='kategori')
st.plotly_chart(fig3, use_container_width=True)

st.subheader("🚨 Overbudget")
over = df['overbudget'].value_counts().reset_index()
over.columns = ['status', 'jumlah']
fig4 = px.bar(over, x='status', y='jumlah', color='status')
st.plotly_chart(fig4, use_container_width=True)

# ======================
# TABLE
# ======================
st.subheader("📋 Data")
st.dataframe(df.head(50))
