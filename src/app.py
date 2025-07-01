import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv
import altair as alt

# Load environment variables
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Create SQLAlchemy engine
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

st.set_page_config(page_title="Bitcoin Dashboard", page_icon=":robot_face:", layout="wide")
st.title("Bitcoin Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        Este é um dashboard simples para visualizar o preço do Bitcoin.
        Ele utiliza a API do Yahoo Finance para obter os dados.
        A cada 5 minutos, o preço do Bitcoin é atualizado e salvo em um banco de dados PostgreSQL.
        A orquestração do pipeline é feita com Kestra, que executa o scraper e armazena os dados no banco de dados.
        O dashboard é construído com Streamlit e utiliza Altair para visualização dos dados.
    """)

    st.markdown("""
        ### Visite o repositório do projeto no GitHub:
        [Projeto Kestra - Bitcoin Monitor](https://github.com/mvgentil/kestra-pipelines)
    """)

with col2:
    if st.button("🔄 Atualizar dados"):
        st.rerun()

    time_range = st.selectbox(
        "Selecione o período:",
        ("Últimas 24 horas", "Últimos 7 dias", "Todo o período"),
        index=0
    )

    # Query data from the database based on the selected time range
    if time_range == "Últimas 24 horas":
        query = text("""
            SELECT timestamp, price
            FROM bitcoin_price
            WHERE timestamp >= NOW() - INTERVAL '24 HOURS'
            ORDER BY timestamp ASC
        """)
        title = "Preço do Bitcoin nas últimas 24 horas"
    elif time_range == "Últimos 7 dias":
        query = text("""
            SELECT timestamp, price
            FROM bitcoin_price
            WHERE timestamp >= NOW() - INTERVAL '7 DAYS'
            ORDER BY timestamp ASC
        """)
        title = "Preço do Bitcoin nos últimos 7 dias"
    else:
        query = text("""
            SELECT timestamp, price
            FROM bitcoin_price
            ORDER BY timestamp ASC
        """)
        title = "Histórico de Preço do Bitcoin"


    try:
        df = pd.read_sql(query, engine)
        if not df.empty:
            st.markdown(f"### {title}")
            
            # The base chart
            line = (
                alt.Chart(df)
                .mark_line(color="#1f77b4")
                .encode(
                    x=alt.X("timestamp:T", title="Horário"),
                    y=alt.Y("price:Q", title="Preço (USD)", scale=alt.Scale(zero=False)),
                )
            )

            # Create a selection that chooses the nearest point to the cursor
            nearest = alt.selection_point(nearest=True, on='mouseover',
                                        fields=['timestamp'], empty='none')

            # A transparent selector that is used to trigger the tooltip
            selectors = alt.Chart(df).mark_point().encode(
                x='timestamp:T',
                opacity=alt.value(0),
                tooltip=[alt.Tooltip('timestamp:T', title='Horário'), alt.Tooltip('price:Q', title='Preço (USD)', format='.2f')]
            ).add_params(
                nearest
            )

            # Draw points on the line, and highlight based on selection
            points = line.mark_point().encode(
                opacity=alt.condition(nearest, alt.value(1), alt.value(0))
            )

            # Draw a rule at the location of the selection
            rule = alt.Chart(df).mark_rule(color='gray').encode(
                x='timestamp:T',
            ).transform_filter(
                nearest
            )

            # Layer the chart components
            chart = alt.layer(
                line, selectors, points, rule
            ).properties(
                width=800,
                height=400
            )

            st.altair_chart(chart, use_container_width=True)
            st.write("Última atualização:", df["timestamp"].max())
            st.write("Preço atual:", df["price"].iloc[-1])
        else:
            st.warning(f"Nenhum dado encontrado no banco de dados para o período selecionado.")
    except Exception as e:
        st.error(f"Erro ao consultar o banco de dados: {e}")
