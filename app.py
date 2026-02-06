import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import altair as alt

# ==========================================
# 🔧 KONFIGURASI WEB
# ==========================================
st.set_page_config(
    page_title="Explore Indo",
    layout="wide",
    page_icon="🌊"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌊 WONDERFUL INDONESIA")
st.caption("Jelajahi keindahan nusantara lewat peta interaktif.")

# ==========================================
# 🧠 LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("https://huggingface.co/spaces/xReyhan/Wisata-Indonesia/resolve/main/src/data_wisata_final_banget.csv")

        df = df.dropna(subset=['latitude', 'longitude'])

        # Normalisasi teks
        df['provinsi'] = df['provinsi'].astype(str).str.strip().str.title()
        df['kategori'] = df['kategori'].astype(str).str.strip().str.title()

        return df
    except Exception as e:
        st.error(f"Gagal load data: {e}")
        return pd.DataFrame()

df = load_data()

# ==========================================
# 🔍 SIDEBAR
# ==========================================
st.sidebar.title("⚙️ Menu")

if df.empty:
    st.error("Data tidak ditemukan.")
    st.stop()

# Filter Provinsi
list_prov = sorted(df['provinsi'].unique())
pilih_prov = st.sidebar.multiselect("📍 Pilih Provinsi", list_prov)

# Filter Kategori
list_kat = sorted(df['kategori'].unique())
pilih_kat = st.sidebar.multiselect("🏷️ Kategori", list_kat)

# Opsi Statistik
tampil_chart = st.sidebar.checkbox("📊 Tampilkan Statistik")

# OPSI BARU UNTUK MENAMPILKAN DATA CSV
tampil_csv = st.sidebar.checkbox("📄 Tampilkan Data Scrapping (CSV)")

st.sidebar.caption("Gunakan filter di atas untuk menyaring lokasi wisata.")

# ==========================================
# 🧮 FILTER LOGIC
# ==========================================
df_filtered = df.copy()

if pilih_prov:
    df_filtered = df_filtered[df_filtered['provinsi'].isin(pilih_prov)]

if pilih_kat:
    df_filtered = df_filtered[df_filtered['kategori'].isin(pilih_kat)]

# ==========================================
# 📄 MENAMPILKAN DATA CSV JIKA DIPILIH
# ==========================================
if tampil_csv:

    st.divider()
    st.subheader("📄 Data Hasil Scrapping")

    # Tampilkan tabel interaktif
    st.dataframe(
        df_filtered,
        use_container_width=True,
        height=400
    )

    # Ringkasan singkat
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"Total Data: {len(df_filtered)}")

    with col2:
        st.info(f"Total Provinsi: {df_filtered['provinsi'].nunique()}")

    with col3:
        st.info(f"Total Kategori: {df_filtered['kategori'].nunique()}")

# ==========================================
# 🗺️ MAP
# ==========================================
st.divider()
st.subheader(f"📍 Menampilkan {len(df_filtered)} Lokasi Wisata")

if not df_filtered.empty:

    center_lat = df_filtered['latitude'].mean()
    center_lon = df_filtered['longitude'].mean()

    zoom_level = 6
    if pilih_prov and len(pilih_prov) == 1:
        zoom_level = 8

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles='OpenStreetMap'
    )

    sw = df_filtered[['latitude', 'longitude']].min().values.tolist()
    ne = df_filtered[['latitude', 'longitude']].max().values.tolist()
    m.fit_bounds([sw, ne])

    marker_cluster = MarkerCluster().add_to(m)

    for index, row in df_filtered.iterrows():

        popup_html = f"""
        <div style="font-family: 'Poppins', sans-serif; width: 200px;">
            <h4>{row['nama_wisata']}</h4>
            <p>📍 {row['kota_kabupaten']}, {row['provinsi']}</p>
            <small>{row['kategori']}</small>
        </div>
        """

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            tooltip=row['nama_wisata'],
            popup=popup_html
        ).add_to(marker_cluster)

    st_folium(m, width="100%", height=600)

else:
    st.warning("Tidak ada lokasi wisata sesuai filter.")

# ==========================================
# 📊 STATISTIK
# ==========================================
if tampil_chart:

    st.divider()
    st.subheader("📊 Statistik Ringkas")

    if not df_filtered.empty:

        c1, c2 = st.columns(2)

        with c1:
            chart_data = df_filtered['provinsi'].value_counts().reset_index()
            chart_data.columns = ['Provinsi', 'Jumlah']

            bar = alt.Chart(chart_data).mark_bar().encode(
                x='Provinsi',
                y='Jumlah',
                color='Provinsi'
            )

            st.altair_chart(bar, use_container_width=True)

        with c2:
            cat_data = df_filtered['kategori'].value_counts().reset_index()
            cat_data.columns = ['Kategori', 'Jumlah']

            donut = alt.Chart(cat_data).mark_arc(innerRadius=50).encode(
                theta='Jumlah',
                color='Kategori'
            )

            st.altair_chart(donut, use_container_width=True)
