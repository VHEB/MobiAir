import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from dotenv import load_dotenv

# ==============================
# CONFIGURAÇÃO INICIAL
# ==============================
st.set_page_config(page_title="MobiAir 🌍", page_icon="💨", layout="centered")
st.title("🌆 MobiAir – Qualidade do Ar e Rotas de Caminhada")
st.markdown("""
Aplicativo para visualizar a **qualidade do ar** e gerar **rotas de caminhada saudáveis** 🚶‍♂️🌿
""")

# ==============================
# CARREGAR CHAVES DO .env
# ==============================
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
ORS_API_KEY = os.getenv("ORS_API_KEY")

if not API_KEY or not ORS_API_KEY:
    st.error("⚠️ Verifique se as chaves API estão configuradas no arquivo `.env`.")
    st.stop()

# ==============================
# FUNÇÕES AUXILIARES
# ==============================
def get_coordinates(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&lang=pt_br"
    r = requests.get(url)
    if r.status_code == 200:
        d = r.json()
        return d["coord"]["lat"], d["coord"]["lon"], d["name"]
    return None, None, None

def get_air_quality(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

def interpretar_aqi(aqi):
    descricao = {
        1: ("🟢 Boa", "#4CAF50"),
        2: ("🟡 Razoável", "#CDDC39"),
        3: ("🟠 Moderada", "#FFC107"),
        4: ("🔴 Ruim", "#F44336"),
        5: ("🟣 Muito Ruim", "#9C27B0")
    }
    return descricao.get(aqi, ("Desconhecido", "#9E9E9E"))

def obter_rota(origem, destino):
    url = "https://api.openrouteservice.org/v2/directions/foot-walking"
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body = {"coordinates": [[origem[1], origem[0]], [destino[1], destino[0]]]}  # [lon, lat]
    r = requests.post(url, json=body, headers=headers)

    try:
        data = r.json()
    except ValueError:
        st.error("Erro: resposta inválida da API ORS.")
        return None

    if r.status_code == 200 and "features" in data:
        return data
    else:
        st.error(f"Erro ao gerar rota ORS: {data.get('error', r.status_code)}")
        return None

# ==============================
# QUALIDADE DO AR
# ==============================
st.header("🌫️ Qualidade do Ar")
cidade = st.text_input("Digite a cidade:", "São Paulo")

if cidade:
    lat, lon, nome = get_coordinates(cidade)
    if lat and lon:
        aq_data = get_air_quality(lat, lon)
        if aq_data and "list" in aq_data and aq_data["list"]:
            aqi = aq_data["list"][0]["main"]["aqi"]
            componentes = aq_data["list"][0]["components"]

            texto, cor = interpretar_aqi(aqi)
            st.markdown(f"""
            <div style="background-color:{cor}; padding:10px; border-radius:10px; text-align:center;">
                <h3 style="color:white;">Índice AQI: {aqi} – {texto}</h3>
            </div>
            """, unsafe_allow_html=True)

            st.write("🧪 **Componentes do ar (μg/m³):**")
            df = pd.DataFrame([componentes]).T
            df.columns = ["Concentração"]
            st.dataframe(df)

            st.write("📍 Localização aproximada:")
            st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
        else:
            st.warning("⚠️ Nenhum dado de qualidade do ar disponível no momento.")
    else:
        st.error("Cidade não encontrada. Tente novamente.")

# ==============================
# ROTAS DE CAMINHADA
# ==============================
st.header("🚶‍♂️ Rotas de Caminhada Saudáveis")
origem_cidade = st.text_input("Origem:", "São Paulo")
destino_cidade = st.text_input("Destino:", "Parque Ibirapuera")

if st.button("Gerar rota"):
    origem_coords = get_coordinates(origem_cidade)[:2]
    destino_coords = get_coordinates(destino_cidade)[:2]

    if None in origem_coords or None in destino_coords:
        st.error("Não foi possível localizar origem ou destino.")
    else:
        rota = obter_rota(origem_coords, destino_coords)
        if rota and "features" in rota:
            geometry = rota["features"][0]["geometry"]["coordinates"]
            pontos = [[lat, lon] for lon, lat in geometry]

            mapa = folium.Map(location=pontos[0], zoom_start=13)
            folium.PolyLine(pontos, color="blue", weight=5, opacity=0.7).add_to(mapa)
            folium.Marker(pontos[0], tooltip="Origem").add_to(mapa)
            folium.Marker(pontos[-1], tooltip="Destino").add_to(mapa)
            st_folium(mapa, width=700, height=500)
