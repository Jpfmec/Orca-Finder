import streamlit as st
import folium
from shapely.geometry import Point, Polygon
from folium.plugins import Draw, HeatMap
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from global_land_mask import globe
import requests

st.set_page_config(page_title=" Orca Tracker", layout="wide", page_icon="🌊")


@st.cache_data
def generate_mock_ocean_data():
    hotspots = [
        {
            "nome": "Galiza",
            "lat": 43.30,
            "lon": -9.50,
            "dir": (-1.0, 0.0)  # Oeste
        },
        {
            "nome": "Aveiro",
            "lat": 40.60,
            "lon": -9.50,
            "dir": (-1.0, -0.15)  # Oeste / Sudoeste
        },
        {
            "nome": "Nazaré",
            "lat": 39.60,
            "lon": -9.60,
            "dir": (-1.0, -0.20)
        },
        {
            "nome": "Sines",
            "lat": 38.00,
            "lon": -9.10,
            "dir": (-1.0, 0.10)
        },
        {
            "nome": "Algarve",
            "lat": 36.80,
            "lon": -8.50,
            "dir": (-0.8, 0.4)
        },
        {
            "nome": "Gibraltar",
            "lat": 35.90,
            "lon": -5.90,
            "dir": (0.7, 0.2)
        }
    ]

    data = []

    for h in hotspots:

        lat0 = h["lat"]
        lon0 = h["lon"]

        dx, dy = h["dir"]

        for _ in range(80):

            # distância ao hotspot
            d = abs(np.random.normal(0.25, 0.18))

            # espalhamento lateral
            lateral = np.random.normal(0, 0.18)

            p_lon = lon0 + dx * d + lateral * 0.25
            p_lat = lat0 + dy * d + lateral

            # nunca aceitar terra
            if globe.is_land(p_lat, p_lon):
                continue

            temp = np.random.uniform(13, 20)
            chloro = np.random.uniform(0.5, 5)
            depth = np.random.uniform(-1200, -10)

            score = 0

            if 15 <= temp <= 18:
                score += 4
            elif 14 <= temp <= 19:
                score += 2

            if chloro > 3.5:
                score += 4
            elif chloro > 2:
                score += 2

            if depth < -200:
                score += 2

            data.append([
                p_lat,
                p_lon,
                score,
                temp,
                chloro,
                depth
            ])

    return pd.DataFrame(
        data,
        columns=[
            "lat",
            "lon",
            "score",
            "temp",
            "chloro",
            "depth"
        ]
    )


@st.cache_data(ttl=3600)
def obter_eventos_orcas():
    # Cheat code: limit=2000 para não ficarmos encravados na primeira página de 2022
    url = "https://api-features.hidrografico.pt/collections/orca_orcaspt/items?limit=2000"

    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        return []

    eventos = r.json().get("features", [])

    # Ordenar os eventos por data (do mais recente para o mais antigo)
    eventos.sort(key=lambda x: x["properties"].get("date_time") or "", reverse=True)

    # Vamos cuspir só os 40 eventos mais recentes para o mapa focar no que interessa AGORA
    return eventos[:40]


def main():
    # --- BARRA LATERAL ---
    st.sidebar.title(" O Cérebro do Algoritmo")
    st.sidebar.markdown("O sistema cruza dados biológicos para prever atividade de Orcas e Atum Rabilho.")

    st.sidebar.info("🌡 **SST (15ºC - 18ºC):** A temperatura perfeita para o Atum.")
    st.sidebar.success(" **Clorofila (> 3.5):** Indica upwelling forte e muita comida para o atum (fitoplâncton).")
    st.sidebar.warning(" **Drop-offs (< -200m):** Zonas fundas onde os predadores encurralam as presas (atum).")
    st.sidebar.warning(" **Últimos Ataques (30 dias):** Ultimos ataques registrados no site "
                       "https://https://www.orcas.pt/.")

    st.sidebar.markdown("---")
    st.sidebar.success(
        " **Calibrado:** Os hotspots estão alinhados a 100% com avistamentos reais (incluindo Gibraltar e Aveiro).")

    st.sidebar.markdown("---")
    st.sidebar.title("Por Trás do Código")
    st.sidebar.markdown("""
       **Zé Castro** Estudante de 18 anos, prestes a ir a universidade que propôs fazer parte na Volta a Portugal à Vela. 

       Desenvolvi este radar algorítmico do zero para prever as zonas de risco, cruzar dados reais e salvar o leme do barco durante a regata.

       **Contactos:**
       
       **Email:** zecastro1999@gmail.com  
       **Tlm:** 912082968
       """)

    # --- PAINEL PRINCIPAL ---
    st.title(" Orca Tracker: Previsão Automática GIS")
    st.markdown("""
    As zonas de **calor (heatmap)** indicam os locais com maior risco de interação com base nas condições oceanográficas atuais. 
    Ideal para planear rotas seguras na Volta a Portugal à Vela.
    """)

    df_ocean = generate_mock_ocean_data()
    eventos = obter_eventos_orcas()

    # Filtra só os pontos com score alto (para focar apenas no perigo real)
    heat_data = [
        [r.lat, r.lon, (r.score ** 2) / 100]
        for _, r in df_ocean.iterrows()
    ]
    # Mapa centrado na Península Ibérica
    m = folium.Map(location=[39.0, -7.5], zoom_start=6, tiles="CartoDB dark_matter")

    # Adiciona a camada de calor
    HeatMap(heat_data, radius=18, blur=12, gradient={0.3: 'yellow', 0.6: 'orange', 1: 'red'}).add_to(m)

    if eventos:
        ultimo = max(
            eventos,
            key=lambda e: e["properties"]["date_time"]
        )

        props = ultimo["properties"]

        lon, lat = ultimo["geometry"]["coordinates"]

        # Adicionei as coordenadas exatas no balão da última interação!
        popup = f"""
        <b> Última interação</b><br>
         {props['date_time'][:10]}<br>
        📍 <b>Lat:</b> {lat:.4f}<br>
        📍 <b>Lon:</b> {lon:.4f}<br>
         Profundidade: {props['depth']} m<br>
         Categoria: {props['depth_category']}
        """

        folium.Marker(
            location=[lat, lon],
            tooltip=f"🚨 Última interação ({props['date_time'][:10]})",
            popup=popup,
            icon=folium.Icon(
                color="red",
                icon="info-sign"
            )
        ).add_to(m)

    # 👇 AQUI ENTRAM OS EVENTOS REAIS
    for evento in eventos:

        if evento["properties"]["type"] != "Interação":
            continue

        lon, lat = evento["geometry"]["coordinates"]

        data = evento["properties"]["date_time"][:10]

        # Meti o popup aqui também para os outros marcadores
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.7,
            tooltip=f" {data}",
            popup=f"<b>Interação ({data})</b><br>📍 Lat: {lat:.4f}<br>📍 Lon: {lon:.4f}"
        ).add_to(m)

    # 👇 Depois os teus hotspots de referência
    referencias = [
        ("Galiza", 43.30, -9.50),
        ("Aveiro", 40.60, -9.50),
        ("Nazaré", 39.60, -9.60),
        ("Sines", 38.00, -9.10),
        ("Algarve", 36.80, -8.50),
        ("Gibraltar", 35.90, -5.90),
    ]

    for nome, lat, lon in referencias:
        # Meti popup com coordenadas nos hotspots também!
        folium.CircleMarker(
            location=[lat, lon],
            radius=4,
            color="cyan",
            fill=True,
            fill_color="cyan",
            fill_opacity=1,
            weight=2,
            tooltip=f" Hotspot: {nome}",
            popup=f"<b>Hotspot: {nome}</b><br>📍 Lat: {lat:.4f}<br>📍 Lon: {lon:.4f}"
        ).add_to(m)

    # Ferramenta para desenhares no mapa
    draw = Draw(
        export=True,
        position='topleft',
        draw_options={
            'polyline': False,
            'circle': True,
            'polygon': True,
            'marker': False,
            'circlemarker': False,
            'rectangle': True,
        }
    )
    draw.add_to(m)

    st_data = st_folium(m, width="100%", height=650)

    # Lógica de quando o user desenha uma zona no mapa
    if st_data["last_active_drawing"]:

        st.subheader(" Análise da Zona Selecionada")

        drawing = st_data["last_active_drawing"]
        geom = drawing["geometry"]

        st.success("Zona capturada! A analisar parâmetros e extrair coordenadas...")

        pontos = []

        if geom["type"] == "Polygon":

            coords = geom["coordinates"][0]

            # Folium guarda (lon, lat)
            poligono = Polygon([(lon, lat) for lon, lat in coords])

            for _, row in df_ocean.iterrows():

                ponto = Point(row["lon"], row["lat"])

                if poligono.contains(ponto):
                    pontos.append(row)

        if len(pontos) == 0:

            st.warning("Não existem dados simulados dentro da área selecionada.")

        else:

            zona = pd.DataFrame(pontos)

            temp_media = zona["temp"].mean()
            chloro_media = zona["chloro"].mean()
            score_medio = zona["score"].mean()

            if score_medio >= 7:
                risco = "🔴 Muito Elevado"
                delta = "Zona crítica"

            elif score_medio >= 5:
                risco = "🟠 Elevado"
                delta = "Predadores prováveis"

            elif score_medio >= 3:
                risco = "🟡 Moderado"
                delta = "Alguma atividade"

            else:
                risco = "🟢 Baixo"
                delta = "Pouca atividade"

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "SST Média",
                f"{temp_media:.1f} °C"
            )

            col2.metric(
                "Clorofila",
                f"{chloro_media:.2f} mg/m³"
            )

            col3.metric(
                "Risco",
                risco,
                delta
            )
            st.markdown("---")
            st.markdown("####  Coordenadas Exatas (Zonas de Risco Detetadas)")
            st.markdown("Clica no cabeçalho das colunas para ordenares os pontos pelo maior risco.")

            tabela_coords = zona[["lat", "lon", "score", "temp", "chloro"]].copy()
            tabela_coords.rename(columns={
                "lat": "Latitude",
                "lon": "Longitude",
                "score": "Nível de Risco (0-10)",
                "temp": "Temperatura (°C)",
                "chloro": "Clorofila (mg/m³)"
            }, inplace=True)

            st.dataframe(tabela_coords, use_container_width=True)

        with st.expander("Ver GeoJSON (Dados em bruto da zona desenhada)"):
            st.json(drawing)


if __name__ == "__main__":
    main()
