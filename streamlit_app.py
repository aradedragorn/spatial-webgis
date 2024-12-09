import streamlit as st
import folium
from streamlit_folium import st_folium
from geographiclib.geodesic import Geodesic
from geopy.geocoders import Nominatim
import math

# Fungsi untuk menghitung lintasan besar
@st.cache_data
def calculate_great_circle_path(lat1, lon1, lat2, lon2):
    path = []
    geod = Geodesic.WGS84
    g = geod.InverseLine(lat1, lon1, lat2, lon2)
    ds = 1000e3
    n = int(g.s13 / ds) + 1
    for i in range(n + 1):
        s = min(ds * i, g.s13)
        point = g.Position(s)
        path.append((point['lat2'], point['lon2']))
    return path

# Fungsi untuk menghitung jarak
@st.cache_data
def calculate_great_circle_distance(lat1, lon1, lat2, lon2):
    geod = Geodesic.WGS84
    g = geod.Inverse(lat1, lon1, lat2, lon2)
    return g['s12'] / 1000

# Fungsi untuk menghitung azimuth
@st.cache_data
def calculate_azimuth(lat1, lon1, lat2, lon2):
    geod = Geodesic.WGS84
    g = geod.Inverse(lat1, lon1, lat2, lon2)
    return g['azi1']

# Tampilan aplikasi Streamlit
st.title("WebGIS Interaktif: Great Circle Distance (GCD)")
st.markdown("Masukkan koordinat dalam format desimal untuk melihat lintasan besar dan jarak di peta.")

# Input pencarian lokasi
st.sidebar.header("Cari Lokasi")
location = st.sidebar.text_input("Masukkan lokasi:", value="")

# Inisialisasi geolocator
geolocator = Nominatim(user_agent="webgis_app")

if location:
    try:
        # Menggunakan geopy untuk mencari lokasi
        loc = geolocator.geocode(location)
        if loc:
            st.sidebar.write(f"Koordinat untuk '{location}':")
            lat_decimal = loc.latitude
            lon_decimal = loc.longitude
            st.sidebar.write(f"Lintang: {lat_decimal:.4f}°")
            st.sidebar.write(f"Bujur: {lon_decimal:.4f}°")
        else:
            st.sidebar.error("Lokasi tidak ditemukan.")
    except Exception as e:
        st.sidebar.error(f"Kesalahan saat mencari lokasi: {e}")

# Input koordinat dalam format desimal
st.sidebar.header("Masukkan Koordinat dalam Desimal")

# Koordinat Titik Awal
st.sidebar.subheader("Koordinat Titik Awal")
start_lat = st.sidebar.number_input("Latitude (°)", min_value=-90.0, max_value=90.0, value=6.20889)
start_lon = st.sidebar.number_input("Longitude (°)", min_value=-180.0, max_value=180.0, value=106.82750)

# Koordinat Titik Akhir
st.sidebar.subheader("Koordinat Titik Akhir")
end_lat = st.sidebar.number_input("Latitude (°)", min_value=-90.0, max_value=90.0, value=35.50000)
end_lon = st.sidebar.number_input("Longitude (°)", min_value=-180.0, max_value=180.0, value=100.00000)

# Menggunakan session state untuk menjaga status kalkulasi
if "calculate" not in st.session_state:
    st.session_state.calculate = False

# Button untuk menghitung
if st.sidebar.button("Hitung"):
    st.session_state.calculate = True

# Menampilkan hasil perhitungan dan peta hanya jika tombol "Hitung" ditekan
if st.session_state.calculate:
    # Menghitung lintasan besar, jarak, dan azimuth
    path = calculate_great_circle_path(start_lat, start_lon, end_lat, end_lon)
    distance = calculate_great_circle_distance(start_lat, start_lon, end_lat, end_lon)

    # Menghitung azimuth berangkat dan azimuth pulang
    lat1, lon1 = start_lat, start_lon
    lat2, lon2 = end_lat, end_lon

    d_lon = math.radians(lon2 - lon1)

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat 2, lon2])

    x = math.cos(lat2) * math.sin(d_lon)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(d_lon))
    azimuth = math.atan2(x, y)
    azimuth = math.degrees(azimuth)
    azimuth = (azimuth + 360) % 360  # Normalize to 0-360 degrees

    # Menampilkan hasil
    st.write(f"**Jarak antara titik:** {distance:.2f} km")
    st.write(f"**Azimuth dari titik awal ke titik akhir:** {azimuth:.2f}°")

    # Membuat peta dengan Folium
    m = folium.Map(location=[(start_lat + end_lat) / 2, (start_lon + end_lon) / 2], zoom_start=5)

    # Menambahkan marker untuk titik awal dan akhir
    folium.Marker([start_lat, start_lon], tooltip='Titik Awal', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([end_lat, end_lon], tooltip='Titik Akhir', icon=folium.Icon(color='red')).add_to(m)

    # Menambahkan lintasan besar ke peta
    folium.PolyLine(path, color='blue', weight=2.5, opacity=1).add_to(m)

    # Menampilkan peta di Streamlit
    st_folium(m, width=700, height=500)
