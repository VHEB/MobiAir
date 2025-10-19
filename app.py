import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="MobiAir 🌤️", layout="wide")

st.title("🌍 MobiAir — Mobilidade e Qualidade do Ar")

city = st.text_input("Digite o nome da cidade:", "São Paulo")

if city:
    # 1️⃣ Buscar coordenadas da cidade
    geo_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json"
    geo_data = requests.get(geo_url).json()
    if geo_data:
        lat, lon = float(geo_data[0]['lat']), float(geo_data[0]['lon'])

        # 2️⃣ Buscar dados de qualidade do ar (OpenWeatherMap)
        API_KEY = "SUA_API_KEY_AQUI"
        aq_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aq_data = requests.get(aq_url).json()
        aqi = aq_data['list'][0]['main']['aqi']

        # 3️⃣ Mostrar mapa
        m = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], popup=f"Qualidade do Ar: {aqi}").add_to(m)
        st_folium(m, width=700, height=500)

        # 4️⃣ Exibir interpretação
        aqi_text = ["Boa", "Razoável", "Moderada", "Ruim", "Muito Ruim"][aqi - 1]
        st.subheader(f"Qualidade do ar em {city}: **{aqi_text}**")

        # Recomendação
        if aqi <= 2:
            st.success("✅ Ótimo momento para caminhar ou se exercitar!")
        else:
            st.warning("⚠️ Recomendado evitar atividades intensas ao ar livre.")
