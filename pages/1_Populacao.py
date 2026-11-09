import streamlit as st

from src.publicacao import (
    N_ORIGINAL,
    carregar_resumo_publico,
    como_ler_painel,
    formatar_numero,
    formatar_percentual,
    renderizar_descritiva,
)


st.title("Painel 1 — População")
como_ler_painel(
    "Aqui estão os parâmetros verdadeiros (N, μ, σ, π) dos 197.639 nascimentos: "
    "o \"gabarito\" contra o qual a amostra é julgada no Painel 3. Use o filtro "
    "de ano na barra lateral para ver cada ano. A descrição completa está na "
    "seção 4.1 do relatório."
)
resumo = carregar_resumo_publico()
populacao = resumo["populacao"]
anos = ["Todos"] + sorted(populacao["por_ano"], key=int)
ano = st.sidebar.selectbox("Ano de nascimento", anos, key="populacao_ano")
dados = populacao["total"] if ano == "Todos" else populacao["por_ano"][ano]

st.caption(
    "Fonte: SINASC — Prefeitura de Porto Alegre · nascimentos de 2011 a 2021 · "
    "[dados abertos](https://dadosabertos.poa.br/dataset/sinasc). "
    "Este painel publica apenas estatísticas agregadas, sem linhas individuais."
)
st.markdown(
    f"**N antes do recorte:** {N_ORIGINAL:,}".replace(",", ".")
    + f" · **N após o recorte de peso ≥ 500 g:** {resumo['n_populacao']:,}"
    .replace(",", ".")
)
st.caption(
    "O limite de 500 g é um recorte metodológico, não uma afirmação de que "
    "todos os registros abaixo dele sejam inválidos. As conclusões referem-se "
    "à população analisada após esse recorte."
)

for inicio in (0, 4):
    indicadores = dados["indicadores"]
    metricas = [
        ("N", f"{dados['n']:,}".replace(",", ".")),
        ("Peso médio (μ)", f"{formatar_numero(indicadores['peso_medio'])} g"),
        ("DP peso (σ)", f"{formatar_numero(indicadores['peso_dp'])} g"),
        ("Cesáreas (π)", formatar_percentual(indicadores["cesarea"])),
        ("Baixo peso", formatar_percentual(indicadores["baixo_peso"])),
        ("Prematuros", formatar_percentual(indicadores["prematuro"])),
        (
            "Idade média materna",
            f"{formatar_numero(indicadores['idade_media'])} anos",
        ),
    ]
    with st.container(horizontal=True):
        for label, valor in metricas[inicio : inicio + 4]:
            st.metric(label, valor, border=True)

if ano != "Todos":
    st.info(
        f"Os gráficos detalhados mostram a população de {ano}; os indicadores "
        "resumem apenas esse recorte anual."
    )
else:
    st.caption(
        "Os indicadores acima são os parâmetros de referência calculados sobre "
        "a população completa; gráficos e tabelas detalhadas cobrem 2011–2021."
    )
renderizar_descritiva(dados, chave=f"populacao_{ano}")
