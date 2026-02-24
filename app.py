import streamlit as st
import pandas as pd
import random

# Configura o site para ocupar a tela toda
st.set_page_config(layout="wide", page_title="Brasfoot Ultimate")

@st.cache_data
def carregar_dados():
    df = pd.read_csv("times.csv")
    df.columns = ['nome', 'pais', 'divisao', 'forca']
    for col in ['p', 'v', 'j', 'gp', 'gc']: # Adicionando Gols Pro e Gols Contra
        df[col] = 0
    return df

if 'tabela' not in st.session_state:
    st.session_state.tabela = carregar_dados()
    st.session_state.rodada = 1

# --- TELA DE SELEÇÃO ---
if 'meu_time' not in st.session_state:
    st.title("⚽ BRASFOOT ULTIMATE - SELEÇÃO")
    df = st.session_state.tabela
    
    col1, col2, col3 = st.columns(3)
    p = col1.selectbox("País", sorted(df['pais'].unique()))
    d = col2.selectbox("Divisão", sorted(df[df['pais'] == p]['divisao'].unique()))
    t = col3.selectbox("Time", sorted(df[(df['pais'] == p) & (df['divisao'] == d)]['nome'].tolist()))
    
    if st.button("ASSINAR CONTRATO"):
        st.session_state.meu_time = t
        st.rerun()

# --- JOGO ---
else:
    st.sidebar.header(f"⭐ {st.session_state.meu_time}")
    st.sidebar.write(f"Rodada: {st.session_state.rodada}")
    
    aba1, aba2 = st.tabs(["⚽ Próxima Rodada", "📊 Tabelas"])
    
    with aba1:
        st.subheader("Simulador de Rodada Global")
        if st.button("INICIAR RODADA"):
            # Lógica de simulação de gols
            for i, row in st.session_state.tabela.iterrows():
                gols = random.choices([0,1,2,3,4,5], weights=[20,30,25,15,7,3])[0]
                # Se for o time do usuário, damos um pequeno bônus de sorte
                if row['nome'] == st.session_state.meu_time:
                    gols = max(gols, random.randint(0,3))
                
                # Para simplificar a vitória/derrota na tabela geral
                sorte = random.randint(0, 100)
                if sorte < (row['forca'] / 2 + 10):
                    st.session_state.tabela.at[i, 'p'] += 3
                    st.session_state.tabela.at[i, 'v'] += 1
                elif sorte < 70:
                    st.session_state.tabela.at[i, 'p'] += 1
                st.session_state.tabela.at[i, 'j'] += 1
                
            st.session_state.rodada += 1
            st.rerun()

    with aba2:
        p_v = st.selectbox("Escolha o País para ver a tabela", sorted(st.session_state.tabela['pais'].unique()))
        d_v = st.selectbox("Divisão", sorted(st.session_state.tabela[st.session_state.tabela['pais'] == p_v]['divisao'].unique()))
        
        tab_final = st.session_state.tabela[(st.session_state.tabela['pais'] == p_v) & (st.session_state.tabela['divisao'] == d_v)]
        st.dataframe(tab_final[['nome', 'forca', 'p', 'v', 'j']].sort_values(by=['p', 'v'], ascending=False), use_container_width=True)