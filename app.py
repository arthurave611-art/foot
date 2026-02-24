import streamlit as st
import pandas as pd
import random

# Configuração da Página
st.set_page_config(page_title="Brasfoot Global Edition", layout="wide")

# --- 1. FUNÇÃO DE CARREGAMENTO E LIMPEZA ---
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("times.csv")
        # Limpeza: remove espaços e coloca tudo em minúsculo
        df.columns = df.columns.str.strip().str.lower()
        # Padroniza o nome da coluna de força para 'forca' independente de como escreveu
        df = df.rename(columns={'força': 'forca', 'power': 'forca', 'fca': 'forca'})
        
        # Garante que as colunas de estatísticas existam
        if 'p' not in df.columns: df['p'] = 0
        if 'v' not in df.columns: df['v'] = 0
        if 'j' not in df.columns: df['j'] = 0
        
        return df
    except Exception as e:
        st.error(f"Erro ao ler times.csv: {e}")
        return pd.DataFrame(columns=['nome', 'pais', 'divisao', 'forca', 'p', 'v', 'j'])

# --- 2. LOGICA DE VIRADA DE TEMPORADA ---
def virar_temporada():
    df = st.session_state.tabela_global.copy()
    
    # Processa cada país e suas divisões
    for pais in df['pais'].unique():
        paises_df = df[df['pais'] == pais]
        divisoes = sorted(paises_df['divisao'].unique())
        
        for d in divisoes:
            # Pega times da divisão atual ordenados por Pontos e Vitórias
            times_div = paises_df[paises_df['divisao'] == d].sort_values(by=['p', 'v'], ascending=False)
            
            # SUBIDA: Os 2 primeiros sobem (se houver divisão acima)
            if d > 1:
                subindo = times_div.iloc[:2].index
                df.loc[subindo, 'divisao'] -= 1
                
            # DESCIDA: Os 2 últimos descem (se houver divisão abaixo)
            if d < max(divisoes):
                descendo = times_div.iloc[-2:].index
                df.loc[descendo, 'divisao'] += 1
                
    # Reset de estatísticas para o novo ano
    df['p'] = 0
    df['v'] = 0
    df['j'] = 0
    st.session_state.tabela_global = df
    st.session_state.rodada_atual = 1
    st.success("🎉 Temporada finalizada! Subidas e descidas processadas.")

# --- 3. INICIALIZAÇÃO DO JOGO ---
if 'tabela_global' not in st.session_state:
    st.session_state.tabela_global = carregar_dados()
    st.session_state.rodada_atual = 1

# --- TELA DE SELEÇÃO INICIAL ---
if 'meu_time' not in st.session_state:
    st.title("⚽ Seleção de Time - Temporada 1")
    df = st.session_state.tabela_global
    
    col1, col2 = st.columns(2)
    with col1:
        pais_sel = st.selectbox("Escolha o País", sorted(df['pais'].unique()))
    with col2:
        div_sel = st.selectbox("Divisão", sorted(df[df['pais'] == pais_sel]['divisao'].unique()))
    
    times_disp = df[(df['pais'] == pais_sel) & (df['divisao'] == div_sel)]
    time_escolhido = st.selectbox("Clube", times_disp['nome'].tolist())
    
    if st.button("Começar Carreira"):
        st.session_state.meu_time = time_escolhido
        st.rerun()

# --- PAINEL PRINCIPAL ---
else:
    st.sidebar.title(f"🎮 {st.session_state.meu_time}")
    st.sidebar.write(f"Rodada: {st.session_state.rodada_atual} / 10") # Exemplo de 10 rodadas
    
    if st.sidebar.button("Reiniciar Tudo"):
        del st.session_state.meu_time
        del st.session_state.tabela_global
        st.rerun()

    aba1, aba2 = st.tabs(["Próxima Rodada", "Classificação Geral"])

    with aba1:
        if st.session_state.rodada_atual <= 10:
            st.subheader(f"Simular Rodada {st.session_state.rodada_atual}")
            if st.button("⚽ Jogar Rodada Completa"):
                # Simulação simples baseada em força
                df = st.session_state.tabela_global
                for i, row in df.iterrows():
                    # Sorteio: chance de ganhar aumenta com a força
                    resultado = random.randint(0, 100)
                    if resultado < (row['forca'] / 2 + 20): # Lógica de vitória
                        df.at[i, 'p'] += 3
                        df.at[i, 'v'] += 1
                    elif resultado < 70: # Empate
                        df.at[i, 'p'] += 1
                    df.at[i, 'j'] += 1
                
                st.session_state.rodada_atual += 1
                st.rerun()
        else:
            st.warning("Fim da temporada!")
            if st.button("🏆 Processar Virada de Temporada"):
                virar_temporada()
                st.rerun()

    with aba2:
        pais_v = st.selectbox("Ver País", sorted(st.session_state.tabela_global['pais'].unique()))
        div_v = st.selectbox("Ver Divisão", sorted(st.session_state.tabela_global[st.session_state.tabela_global['pais'] == pais_v]['divisao'].unique()))
        
        tab_view = st.session_state.tabela_global[
            (st.session_state.tabela_global['pais'] == pais_v) & 
            (st.session_state.tabela_global['divisao'] == div_v)
        ]
        st.table(tab_view[['nome', 'forca', 'p', 'v', 'j']].sort_values(by=['p', 'v'], ascending=False))