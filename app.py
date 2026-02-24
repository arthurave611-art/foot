import streamlit as st
import pandas as pd
import random

# Configuração da Página
st.set_page_config(page_title="Brasfoot Global", layout="wide")

# 1. CARREGAR OS TIMES
@st.cache_data
def carregar_dados():
    # Aqui carregamos a lista de times reais que você criou
    return pd.read_csv("times.csv")

df_times = carregar_dados()

# 2. INICIALIZAR O CAMPEONATO
if 'tabela_global' not in st.session_state:
    # Criamos uma tabela de classificação para todos os times
    df_times['P'] = 0  # Pontos
    df_times['J'] = 0  # Jogos
    df_times['V'] = 0  # Vitórias
    st.session_state.tabela_global = df_times
    st.session_state.rodada_atual = 1

# --- INTERFACE ---
st.title("🏆 Brasfoot Global Edition")

# Filtros para ver as ligas
col1, col2 = st.columns(2)
with col1:
    pais_sel = st.selectbox("Escolha o País", ["Brasil", "Inglaterra", "Espanha", "Itália", "Alemanha", "França", "Argentina", "Portugal", "Holanda", "EUA"])
with col2:
    # Filtra as divisões disponíveis para aquele país
    divs_disponiveis = st.session_state.tabela_global[st.session_state.tabela_global['pais'] == pais_sel]['divisao'].unique()
    div_sel = st.selectbox("Divisão", sorted(divs_disponiveis))

# Exibir a Tabela da Liga Selecionada
st.subheader(f"Classificação: {pais_sel} - {div_sel}ª Divisão")

tabela_exibicao = st.session_state.tabela_global[
    (st.session_state.tabela_global['pais'] == pais_sel) & 
    (st.session_state.tabela_global['divisao'] == div_sel)
]

st.table(tabela_exibicao.sort_values(by=['P', 'V'], ascending=False))

# --- BOTÃO DE SIMULAR RODADA ---
if st.button("⏩ Simular Próxima Rodada"):
    # Lógica de simulação simplificada para todos os times do mundo
    for index, time in st.session_state.tabela_global.iterrows():
        resultado = random.choice([3, 1, 0]) # 3 pontos, 1 ponto ou 0
        st.session_state.tabela_global.at[index, 'P'] += resultado
        st.session_state.tabela_global.at[index, 'J'] += 1
        if resultado == 3:
            st.session_state.tabela_global.at[index, 'V'] += 1
    
    st.session_state.rodada_atual += 1
    st.rerun()