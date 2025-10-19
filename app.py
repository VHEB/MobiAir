import streamlit as st
import requests
import pandas as pd

# ------------------------------------------------------------
# CONFIGURAÇÃO INICIAL
# ------------------------------------------------------------
st.set_page_config(page_title="MobiAir 🌍", page_icon="💨", layout="centered")
st.title("🌆 MobiAir – Qualidade do Ar e Mobilidade Urbana")

st.markdown("""
Aplicação para visualizar a **qualidade do ar** em tempo real 🌎  
e auxiliar na **mobilidade urbana saudável** 🚶‍♂️🚴‍♀️  
""")

# ------------------------------------------------------------
# ENTRADA DO USUÁRIO
# ------------------------------------------------------------
cidade = st.text_input("Digite uma cidade:", "São Paulo")

# Substitua pela sua chave
API_KEY = "f3e4172af1a3ce66f8cfdff1f1cf0af8"

if cidade:
    # ------------------------------------------------------------
    # BUSCA DE LOCALIZAÇÃO
    # ------------------------------------------------------------
    geo_url = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&lang=pt_br"
    geo_response = requests.get(geo_url)

    if geo_response.status_code == 200:
        geo_data = geo_response.json()
        lat = geo_data["coord"]["lat"]
        lon = geo_data["coord"]["lon"]
        nome = geo_data["name"]

        # ------------------------------------------------------------
        # BUSCA DE QUALIDADE DO AR
        # ------------------------------------------------------------
        aq_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aq_response = requests.get(aq_url)

        if aq_response.status_code == 200:
            aq_data = aq_response.json()
            aqi = aq_data["list"][0]["main"]["aqi"]
            componentes = aq_data["list"][0]["components"]

            # ------------------------------------------------------------
            # INTERPRETAÇÃO DO AQI
            # ------------------------------------------------------------
            descricao_aqi = {
                1: ("🟢 Boa", "#4CAF50"),
                2: ("🟡 Razoável", "#CDDC39"),
                3: ("🟠 Moderada", "#FFC107"),
                4: ("🔴 Ruim", "#F44336"),
                5: ("🟣 Muito Ruim", "#9C27B0"),
            }

            texto, cor = descricao_aqi.get(aqi, ("Desconhecido", "#9E9E9E"))

            st.subheader(f"🌍 Qualidade do ar em {nome}")
            st.markdown(f"""
            <div style="background-color:{cor}; padding:10px; border-radius:10px; text-align:center;">
                <h3 style="color:white;">Índice de Qualidade do Ar (AQI): {aqi} – {texto}</h3>
            </div>
            """, unsafe_allow_html=True)

            # ------------------------------------------------------------
            # EXIBE COMPONENTES
            # ------------------------------------------------------------
            st.write("🧪 **Componentes do ar (μg/m³):**")
            df = pd.DataFrame([componentes]).T
            df.columns = ["Concentração"]
            st.dataframe(df)

            # ------------------------------------------------------------
            # EXIBE LOCALIZAÇÃO NO MAPA
            # ------------------------------------------------------------
            st.write("📍 Localização aproximada:")
            st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))

        else:
            st.error("Não foi possível obter dados de qualidade do ar. 😞")
    else:
        st.error("Cidade não encontrada. Tente novamente.")
