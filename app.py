import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_folium import st_folium
import folium

# ==============================
# Configurações iniciais
# ==============================
st.set_page_config(page_title="MobiAir 🌤️", layout="wide")

st.title("🌍 MobiAir — Mobilidade e Qualidade do Ar")
st.write("Descubra a qualidade do ar na sua cidade e encontre o melhor momento para se exercitar ao ar livre!")

# ==============================
# Carregar variáveis de ambiente
# ==============================
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    st.error("⚠️ API Key do OpenWeatherMap não encontrada. Verifique o arquivo `.env`.")
    st.stop()

# ==============================
# Funções auxiliares
# ==============================

@st.cache_data(ttl=600)  # cache por 10 minutos
def get_coordinates(city_name):
    """Busca latitude e longitude pelo nome da cidade."""
    headers = {"User-Agent": "MobiAirApp/1.0 (contato@example.com)"}
    geo_url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json"
    response = requests.get(geo_url, headers=headers, timeout=10)

    if response.status_code == 200 and response.text.strip():
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    return None, None


@st.cache_data(ttl=600)
def get_air_quality(lat, lon):
    """Busca dados de qualidade do ar na API do OpenWeatherMap."""
    aq_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(aq_url, timeout=10)

    if response.status_code == 200:
        return response.json()
    return None


def get_aqi_text(aqi_value):
    """Traduz o índice AQI para texto descritivo."""
    levels = ["Boa", "Razoável", "Moderada", "Ruim", "Muito Ruim"]
    return levels[aqi_value - 1] if 1 <= aqi_value <= 5 else "Desconhecida"


# ==============================
# Interface principal
# ==============================
city = st.text_input("🏙️ Digite o nome da cidade:", "São Paulo")

if city:
    with st.spinner("Buscando dados..."):
        lat, lon = get_coordinates(city)

        if lat and lon:
            aq_data = get_air_quality(lat, lon)

            if aq_data:
                aqi = aq_data["list"][0]["main"]["aqi"]
                aqi_text = get_aqi_text(aqi)

                # ==============================
                # Exibição dos dados
                # ==============================
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader(f"🌫️ Qualidade do ar em **{city}**:")
                    st.metric("Índice AQI", value=aqi, delta=None)
                    st.write(f"**Nível:** {aqi_text}")

                    if aqi <= 2:
                        st.success("✅ Ótimo momento para caminhar ou se exercitar!")
                    elif aqi == 3:
                        st.warning("⚠️ Qualidade moderada — prefira atividades leves.")
                    else:
                        st.error("🚫 Evite atividades intensas ao ar livre hoje.")

                with col2:
                    # Mapa interativo com marcador
                    m = folium.Map(location=[lat, lon], zoom_start=11)
                    folium.Marker(
                        [lat, lon],
                        popup=f"{city}: Qualidade do ar {aqi_text} (AQI {aqi})",
                        icon=folium.Icon(color="green" if aqi <= 2 else "orange" if aqi == 3 else "red"),
                    ).add_to(m)

                    st_folium(m, width=700, height=500)

            else:
                st.error("❌ Não foi possível obter dados de qualidade do ar.")
        else:
            st.error("❌ Cidade não encontrada. Verifique o nome digitado.")
