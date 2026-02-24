import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Brasfoot Global", layout="wide")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("times.csv")
        # Força as 4 primeiras colunas a terem esses nomes exatos
        novas_colunas = ['nome', 'pais', 'divisao', 'forca']
        # Se o seu CSV tiver mais colunas que 4, a gente pega só as 4 primeiras
        df = df.iloc[:, :4] 
        df.columns = novas_colunas
        
        df['p'] = 0
        df['v'] = 0
        df['j'] = 0
        return df
    except Exception as e:
        st.error(f"Erro: {e}. Verifique se o times.csv tem 4 colunas.")
        return pd.DataFrame()

# --- LÓGICA DE VIRADA ---
def virar_temporada():
    df = st.session_state.tabela_global.copy()
    for pais in df['pais'].unique():
        paises_df = df[df['pais'] == pais]
        for d in sorted(paises_df['divisao'].unique()):
            times_div = paises_df[paises_df['divisao'] == d].sort_values(by=['p', 'v'], ascending=False)
            if d > 1:
                df.loc[times_div.iloc[:2].index, 'divisao'] -= 1
            if d < 4: # Considerando até 4 divisões
                df.loc[times_div.iloc[-2:].index, 'divisao'] += 1
    df['p'], df['v'], df['j'] = 0, 0, 0
    st.session_state.tabela_global = df
    st.session_state.rodada_atual = 1

# --- INICIALIZAÇÃO ---
if 'tabela_global' not in st.session_state:
    st.session_state.tabela_global = carregar_dados()
    st.session_state.rodada_atual = 1

if 'meu_time' not in st.session_state:
    st.title("⚽ Brasfoot Global - Início")
    df = st.session_state.tabela_global
    if not df.empty:
        p = st.selectbox("País", sorted(df['pais'].unique()))
        d = st.selectbox("Divisão", sorted(df[df['pais'] == p]['divisao'].unique()))
        t = st.selectbox("Time", df[(df['pais'] == p) & (df['divisao'] == d)]['nome'].tolist())
        if st.button("Iniciar"):
            st.session_state.meu_time = t
            st.rerun()
else:
    # --- JOGO ---
    st.sidebar.title(f"🚩 {st.session_state.meu_time}")
    st.sidebar.write(f"Rodada: {st.session_state.rodada_atual}")
    
    aba1, aba2 = st.tabs(["Jogar", "Classificação"])
    
    with aba1:
        if st.session_state.rodada_atual <= 10:
            if st.button("Simular Rodada"):
                df = st.session_state.tabela_global
                for i, row in df.iterrows():
                    res = random.randint(0, 100)
                    # Força agora é garantida como 'forca'
                    if res < (int(row['forca']) / 2 + 15):
                        df.at[i, 'p'] += 3
                        df.at[i, 'v'] += 1
                    elif res < 70:
                        df.at[i, 'p'] += 1
                    df.at[i, 'j'] += 1
                st.session_state.rodada_atual += 1
                st.rerun()
        else:
            if st.button("Virar Temporada"):
                virar_temporada()
                st.rerun()

    with aba2:
        # Exibe a tabela filtrada
        df_exibir = st.session_state.tabela_global
        p_sel = st.selectbox("País", sorted(df_exibir['pais'].unique()), key="view_p")
        d_sel = st.selectbox("Divisão", sorted(df_exibir[df_exibir['pais'] == p_sel]['divisao'].unique()), key="view_d")
        
        resultado_tab = df_exibir[(df_exibir['pais'] == p_sel) & (df_exibir['divisao'] == d_sel)]
        st.table(resultado_tab[['nome', 'forca', 'p', 'v', 'j']].sort_values(by=['p', 'v'], ascending=False))