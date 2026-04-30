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
base_path = os.path.dirname(__file__)
file_path = os.path.join(base_path, "..", "main_data.csv")

@st.cache_data
def load_data():
    return pd.read_csv(file_path)

df = load_data()

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("🔧 Filter")

kategori = st.sidebar.multiselect(
    "Pilih Kategori",
    df['kategori'].unique(),
    default=data['kategori'].unique()
)

min_limit, max_limit = st.sidebar.slider(
    "Filter Total Limit",
    int(data['total_limit'].min()),
    int(data['total_limit'].max()),
    (int(data['total_limit'].min()), int(data['total_limit'].max()))
)

data = data[
    (data['kategori'].isin(kategori)) &
    (data['total_limit'] >= min_limit) &
    (data['total_limit'] <= max_limit)
]

# ======================
# METRICS
# ======================
col1, col2, col3 = st.columns(3)

col1.metric("Total User", data['client_id'].nunique())
col2.metric("Total Limit", f"Rp {data['total_limit'].sum():,.0f}")
col3.metric("Avg Limit", f"Rp {data['total_limit'].mean():,.0f}")

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

fig4 = px.bar(df['overbudget'].value_counts().reset_index(),
              x='index', y='overbudget')

fig4.update_layout(xaxis_title="Status", yaxis_title="Jumlah")
st.plotly_chart(fig4, use_container_width=True)

# ======================
# TOP USERS
# ======================
st.subheader("🏆 Top 10 User dengan Limit Tertinggi")

top_users = df.sort_values(by='total_limit', ascending=False).head(10)
st.dataframe(top_users)

# ======================
# INSIGHT
# ======================
st.subheader("💡 Insight")

st.info("""
- User kategori **Boros** mendominasi limit tinggi  
- Jumlah kartu berbanding lurus dengan total limit  
- Risiko overbudget meningkat pada user dengan banyak kartu  
""")
