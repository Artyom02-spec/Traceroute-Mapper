# traceroute_mapper_app.py

import streamlit as st
import subprocess
import geoip2.database
import folium
from folium import Popup
from streamlit_folium import st_folium

GEOIP_DB = "GeoLite2-Country.mmdb"

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

def get_country(ip, reader):
    try:
        response = reader.country(ip)
        country = response.country.name
        return country
    except:
        return None

def plot_route_with_country(ip_list, reader):
    m = folium.Map(location=[20, 0], zoom_start=2)
    last_point = None

    for idx, ip in enumerate(ip_list):
        country = get_country(ip, reader)

        if country:

            coord = COUNTRY_COORDINATES.get(country)
            if coord:
                lat, lon = coord
                popup_text = f"Hop {idx+1}: {ip}<br>{country}"

                folium.Marker(
                    location=[lat, lon],
                    popup=Popup(popup_text, max_width=250),
                    icon=folium.Icon(color="blue")
                ).add_to(m)

                if last_point:
                    folium.PolyLine([last_point, (lat, lon)], color="blue", weight=2).add_to(m)

                last_point = (lat, lon)

    return m

# Ülkelere göre merkez koordinatlar
COUNTRY_COORDINATES = {
    "United States": (37.0902, -95.7129),
    "Germany": (51.1657, 10.4515),
    "France": (46.2276, 2.2137),
    "United Kingdom": (55.3781, -3.4360),
    "Netherlands": (52.1326, 5.2913),
    "Canada": (56.1304, -106.3468),
    "Turkey": (38.9637, 35.2433),
    "Russia": (61.5240, 105.3188),
    "Japan": (36.2048, 138.2529),
    "China": (35.8617, 104.1954),
    "India": (20.5937, 78.9629),
    "Brazil": (-14.2350, -51.9253),
    "Australia": (-25.2744, 133.7751),
    "Albania": (41.1533, 20.1683),
    "Andorra": (42.5078, 1.5211),
    "Armenia": (40.0691, 45.0382),
    "Austria": (47.5162, 14.5501),
    "Azerbaijan": (40.1431, 47.5769),
    "Belarus": (53.7098, 27.9534),
    "Belgium": (50.8503, 4.3517),
    "Bosnia and Herzegovina": (43.9159, 17.6791),
    "Bulgaria": (42.7339, 25.4858),
    "Croatia": (45.1, 15.2),
    "Cyprus": (35.1264, 33.4299),
    "Czech Republic": (49.8175, 15.473),
    "Denmark": (56.2639, 9.5018),
    "Estonia": (58.5953, 25.0136),
    "Finland": (61.9241, 25.7482),
    "Georgia": (42.3154, 43.3569),
    "Greece": (39.0742, 21.8243),
    "Hungary": (47.1625, 19.5033),
    "Iceland": (64.9631, -19.0208),
    "Ireland": (53.1424, -7.6921),
    "Italy": (41.8719, 12.5674),
    "Kazakhstan": (48.0196, 66.9237),  
    "Kosovo": (42.6026, 20.902),
    "Latvia": (56.8796, 24.6032),
    "Liechtenstein": (47.166, 9.5554),
    "Lithuania": (55.1694, 23.8813),
    "Luxembourg": (49.8153, 6.1296),
    "Malta": (35.9375, 14.3754),
    "Moldova": (47.4116, 28.3699),
    "Monaco": (43.7384, 7.4246),
    "Montenegro": (42.7087, 19.3744),
    "North Macedonia": (41.9981, 21.4254),
    "Norway": (60.472, 8.4689),
    "Poland": (51.9194, 19.1451),
    "Portugal": (39.3999, -8.2245),
    "Romania": (45.9432, 24.9668),
    "San Marino": (43.9333, 12.4500),
    "Serbia": (44.0165, 21.0059),
    "Slovakia": (48.669, 19.699),
    "Slovenia": (46.1512, 14.9955),
    "Spain": (40.4637, -3.7492),
    "Sweden": (60.1282, 18.6435),
    "Switzerland": (46.8182, 8.2275),
    "Ukraine": (48.3794, 31.1656),
    "Vatican City": (41.9029, 12.4534)
}


st.title("Traceroute Mapper")

target = st.text_input("Hedef IP veya Domain", value="google.com")

if 'result_ips' not in st.session_state:
    st.session_state.result_ips = None

if st.button("Traceroute Başlat"):
    with st.spinner("Traceroute çalışıyor..."):
        ips = run_traceroute(target)
        st.session_state.result_ips = ips
        st.success(f"{len(ips)} hop bulundu.")

if st.session_state.result_ips:
    st.write("Bulunan Hop IP'leri:", st.session_state.result_ips)

    reader = geoip2.database.Reader(GEOIP_DB)
    route_map = plot_route_with_country(st.session_state.result_ips, reader)
    st_folium(route_map, width=700, height=500)
