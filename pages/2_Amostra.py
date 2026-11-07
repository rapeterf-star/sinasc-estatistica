import streamlit as st

from src.publicacao import (
    SEMENTE,
    carregar_resumo_publico,
    formatar_numero,
    formatar_percentual,
    renderizar_comparacao,
    renderizar_descritiva,
)


st.title("Painel 2 — Amostra")
resumo = carregar_resumo_publico()
amostra = resumo["amostra"]
populacao = resumo["populacao"]
anos = ["Todos"] + sorted(amostra["por_ano"], key=int)
ano = st.sidebar.selectbox("Ano de nascimento", anos, key="amostra_ano")
amostra_dados = amostra["total"] if ano == "Todos" else amostra["por_ano"][ano]
populacao_dados = (
    populacao["total"] if ano == "Todos" else populacao["por_ano"][ano]
)

st.caption(
    "Este painel publica apenas estatísticas agregadas; os 384 registros "
    "individuais da amostra não são disponibilizados."
)
st.markdown(
    f"**Amostragem aleatória simples, sem reposição:** n = {resumo['n_amostra']} · "
    f"semente = {SEMENTE} · fração amostral = "
    f"{formatar_percentual(resumo['n_amostra'] / resumo['n_populacao'], 2)} · "
    f"sorteio em {resumo['data_sorteio']}."
)
st.code(
    "amostra = populacao.sort_values('indice_original').sample("
    "n=384, replace=False, random_state=2026)",
    language="python",
)

indicadores = amostra["total"]["indicadores"]
metricas = [
    ("n", f"{resumo['n_amostra']:,}".replace(",", ".")),
    ("Peso médio (x̄)", f"{formatar_numero(indicadores['peso_medio'])} g"),
    ("DP peso (S)", f"{formatar_numero(indicadores['peso_dp'])} g"),
    ("Cesáreas (P)", formatar_percentual(indicadores["cesarea"])),
    ("Baixo peso", formatar_percentual(indicadores["baixo_peso"])),
    ("Prematuros", formatar_percentual(indicadores["prematuro"])),
    (
        "Idade média materna",
        f"{formatar_numero(indicadores['idade_media'])} anos",
    ),
]
for inicio in (0, 4):
    with st.container(horizontal=True):
        for label, valor in metricas[inicio : inicio + 4]:
            st.metric(label, valor, border=True)

if ano != "Todos":
    st.info(
        f"Os gráficos detalhados mostram a amostra de {ano}; os indicadores "
        "principais continuam resumindo a amostra completa."
    )
else:
    st.caption(
        "Os indicadores resumem a amostra oficial completa. Os gráficos abaixo "
        "podem ser filtrados por ano."
    )
renderizar_descritiva(amostra_dados, chave=f"amostra_{ano}")
renderizar_comparacao(
    populacao_dados,
    amostra_dados,
    chave=f"amostra_{ano}",
)
