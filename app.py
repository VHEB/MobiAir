import streamlit as st
import requests

# ==============================
# CONFIGURAÇÕES INICIAIS
# ==============================
st.set_page_config(page_title="QualiAr", page_icon="🌍")
st.title("🌿 QualiAr - Monitoramento da Qualidade do Ar")

API_KEY = "f3e4172af1a3ce66f8cfdff1f1cf0af8"
BASE_URL = "https://api.openweathermap.org/data/2.5/"

# ==============================
# FUNÇÕES AUXILIARES
# ==============================
def get_coordinates(city):
    """Obtém latitude e longitude de uma cidade."""
    geo_url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&lang=pt_br"
    response = requests.get(geo_url)

    # Logs de debug
    st.write("📡 [GEO] Status:", response.status_code)
    st.write("📦 [GEO] Resposta:", response.text)

    if response.status_code == 200:
        data = response.json()
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]
        return lat, lon
    else:
        return None, None


def get_air_quality(lat, lon):
    """Obtém dados de qualidade do ar."""
    aq_url = f"{BASE_URL}air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(aq_url)

    # Logs de debug
    st.write("📡 [AIR] Status:", response.status_code)
    st.write("📦 [AIR] Resposta:", response.text)

    if response.status_code == 200:
        return response.json()
    else:
        return None

# ==============================
# INTERFACE
# ==============================
city = st.text_input("Digite o nome da cidade:", "São Paulo")

if st.button("Consultar"):
    lat, lon = get_coordinates(city)

    if lat is None or lon is None:
        st.error("❌ Cidade não encontrada ou chave ainda não ativada.")
    else:
        data = get_air_quality(lat, lon)

        if data and "list" in data and data["list"]:
            aqi = data["list"][0]["main"]["aqi"]
            components = data["list"][0]["components"]

            st.subheader(f"🌆 Qualidade do ar em {city.title()}")
            st.write(f"**Índice de Qualidade do Ar (AQI):** {aqi}")

            st.write("### 🧪 Componentes:")
            st.json(components)

            legenda = {
                1: "Boa 😊",
                2: "Razoável 🙂",
                3: "Moderada 😐",
                4: "Ruim 😷",
                5: "Muito Ruim ☠️"
            }

            st.success(f"Nível de qualidade: **{legenda.get(aqi, 'Desconhecido')}**")

        else:
            st.warning("⚠️ Nenhum dado de qualidade do ar disponível no momento. "
                       "Verifique se a chave já foi ativada (pode levar até 2 horas).")
