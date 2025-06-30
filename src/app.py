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

    # Query data from the database
    query = text("""
        SELECT timestamp, price
        FROM bitcoin_price
        WHERE timestamp >= NOW() - INTERVAL '24 HOURS'
        ORDER BY timestamp ASC
    """)
    try:
        df = pd.read_sql(query, engine)
        if not df.empty:
            st.markdown("### Preço do Bitcoin nas últimas 24 horas")
            chart = (
                alt.Chart(df)
                .mark_line(color="#1f77b4")
                .encode(
                    x=alt.X("timestamp:T", title="Horário"),
                    y=alt.Y("price:Q", title="Preço (BRL)", scale=alt.Scale(zero=False)),
                    tooltip=["timestamp:T", "price:Q"]
                )
                .properties(
                    width=800,
                    height=400
                )
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)
            st.write("Última atualização:", df["timestamp"].max())
            st.write("Preço atual:", df["price"].iloc[-1])
        else:
            st.warning("Nenhum dado encontrado no banco de dados nas últimas 24 horas.")
    except Exception as e:
        st.error(f"Erro ao consultar o banco de dados: {e}")