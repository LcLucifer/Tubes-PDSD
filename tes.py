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

# CSS Font Biar Lebih Modern
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Judul Utama
st.title("🌊 WONDERFUL INDONESIA")
st.caption("Jelajahi keindahan nusantara lewat peta interaktif.")

# ==========================================
# 🧠 LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_wisata_final_banget.csv")
        df = df.dropna(subset=['latitude', 'longitude'])
        return df
    except:
        return pd.DataFrame()

df = load_data()

# ==========================================
# 🔍 SIDEBAR FILTER & KONTROL
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

# Opsi untuk menampilkan chart
tampil_chart = st.sidebar.checkbox("📊 Tampilkan Statistik")

st.sidebar.caption("Gunakan filter di atas untuk menyaring lokasi wisata.")

# ==========================================
# 🧮 LOGIC FILTER
# ==========================================
if not pilih_prov:
    df_filtered = df
else:
    df_filtered = df[df['provinsi'].isin(pilih_prov)]

if pilih_kat:
    df_filtered = df_filtered[df_filtered['kategori'].isin(pilih_kat)]

# ==========================================
# 🗺️ TAMPILAN MAP UTAMA
# ==========================================
st.divider()

st.subheader(f"📍 Menampilkan {len(df_filtered)} Lokasi Wisata")

if not df_filtered.empty:

    center_lat = df_filtered['latitude'].mean()
    center_lon = df_filtered['longitude'].mean()

    # Map menggunakan OpenStreetMap
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )

    marker_cluster = MarkerCluster().add_to(m)

    for index, row in df_filtered.iterrows():

        popup_html = f"""
        <div style="font-family: 'Poppins', sans-serif; width: 200px;">
            <img src="{row.get('Image_Path', '')}"
                 style="width: 100%; height: 120px;
                 object-fit: cover; border-radius: 8px;
                 margin-bottom: 8px;">

            <h4 style="margin: 0; color: #0078AA;">
                {row['nama_wisata']}
            </h4>

            <p style="margin: 5px 0 10px 0; font-size: 12px; color: gray;">
                📍 {row['kota_kabupaten']}, {row['provinsi']}
            </p>

            <span style="
                background-color: #0078AA;
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 10px;">
                {row['kategori']}
            </span>
        </div>
        """

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            tooltip=row['nama_wisata'],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(marker_cluster)

    st_folium(m, width="100%", height=600)

else:
    st.warning("Data kosong, coba atur filter lagi.")

# ==========================================
# 📊 CHARTS (HANYA MUNCUL JIKA DIPILIH)
# ==========================================
if tampil_chart:

    st.divider()
    st.subheader("📊 Statistik Ringkas")

    if not df_filtered.empty:

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # Bar Chart Provinsi
            chart_data = df_filtered['provinsi'].value_counts().reset_index()
            chart_data.columns = ['Provinsi', 'Jumlah']

            bar = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Provinsi', sort='-y'),
                y='Jumlah',
                color=alt.Color('Provinsi', legend=None),
                tooltip=['Provinsi', 'Jumlah']
            ).properties(title="Top Provinsi")

            st.altair_chart(bar, use_container_width=True)

        with chart_col2:
            # Donut Chart Kategori
            cat_data = df_filtered['kategori'].value_counts().reset_index()
            cat_data.columns = ['Kategori', 'Jumlah']

            donut = alt.Chart(cat_data).mark_arc(innerRadius=50).encode(
                theta='Jumlah',
                color='Kategori',
                tooltip=['Kategori', 'Jumlah']
            ).properties(title="Kategori Wisata")

            st.altair_chart(donut, use_container_width=True)

    else:
        st.info("Tidak ada data untuk ditampilkan pada statistik.")
