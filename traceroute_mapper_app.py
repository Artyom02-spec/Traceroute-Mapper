# traceroute_mapper_app.py

import streamlit as st
import subprocess
import geoip2.database
import folium
from folium import Popup
from streamlit_folium import st_folium

# GeoIP veri tabanı yolu
GEOIP_DB = "GeoLite2-City.mmdb"

def run_traceroute(host):
    result = subprocess.run(['tracert', '-d', host], capture_output=True, text=True, shell=True)
    lines = result.stdout.splitlines()
    ips = []
    for line in lines:
        if line.strip() and ('ms' in line or '*' in line):
            parts = line.split()
            for part in parts:
                if part.count('.') == 3:
                    ips.append(part)
                    break
    return ips

def get_location(ip, reader):
    try:
        response = reader.city(ip)
        return response.location.latitude, response.location.longitude, response.city.name, response.country.name
    except:
        return None, None, None, None

def plot_route(ip_list, reader):
    m = folium.Map(location=[0, 0], zoom_start=2)
    last_point = None
    for idx, ip in enumerate(ip_list):
        lat, lon, city, country = get_location(ip, reader)
        if lat is not None:
            folium.Marker(
                location=[lat, lon],
                popup=Popup(f"Hop {idx+1}: {ip}\n{city}, {country}", max_width=200),
                icon=folium.Icon(color="blue")
            ).add_to(m)

            if last_point:
                folium.PolyLine([last_point, (lat, lon)], color="blue", weight=2).add_to(m)

            last_point = (lat, lon)
    return m

# Streamlit arayüz
st.title("Traceroute Mapper")
target = st.text_input("Hedef IP veya Domain", value="google.com")

if 'result_ips' not in st.session_state:
    st.session_state.result_ips = None

if st.button("Traceroute Başlat"):
    with st.spinner("Traceroute yapiliyor..."):
        ips = run_traceroute(target)
        st.session_state.result_ips = ips
        st.success(f"{len(ips)} hop bulundu.")

# Eğer IP'ler session_state içinde varsa, devam et
if st.session_state.result_ips:
    st.write("Hop IP'leri:", st.session_state.result_ips)

    reader = geoip2.database.Reader(GEOIP_DB)
    route_map = plot_route(st.session_state.result_ips, reader)
    st_folium(route_map, width=700, height=500)

