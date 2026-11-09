import streamlit as st

from src.publicacao import (
    SEMENTE,
    carregar_resumo_publico,
    como_ler_painel,
    formatar_numero,
    formatar_percentual,
    renderizar_comparacao,
    renderizar_descritiva,
)


st.title("Painel 2 — Amostra")
como_ler_painel(
    "Os mesmos indicadores do Painel 1, agora calculados só com os 384 "
    "nascimentos sorteados (n, x̄, S, P), seguidos da comparação lado a lado "
    "com a população. Diferenças pequenas são esperadas pela variabilidade "
    "amostral. O dimensionamento e o sorteio estão na seção 3.1 do relatório."
)
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
with st.expander("Cálculo do tamanho amostral"):
    st.markdown(
        "Parâmetros: confiança de **95%** (Z = 1,96), margem de erro de "
        "**5 p.p.** e **p = 0,5**, o valor que maximiza p(1 − p) e, portanto, "
        "garante a margem para qualquer proporção estimada."
    )
    st.latex(r"n_0 = \frac{Z^2\,p(1-p)}{d^2} = \frac{1{,}96^2 \times 0{,}25}{0{,}05^2} = 384{,}16")
    st.latex(
        r"n = \frac{n_0}{1 + \frac{n_0 - 1}{N}}"
        r" = \frac{384{,}16}{1 + \frac{383{,}16}{197.639}} \approx 383{,}4"
        r" \;\Rightarrow\; n = 384"
    )
    st.caption(
        "Como a fração amostral é de apenas 0,19%, a correção para população "
        "finita quase não altera o resultado. O valor n = 384 foi conferido na "
        "[calculadora de tamanho de amostra da SurveyMonkey]"
        "(https://pt.surveymonkey.com/learn/research-and-analysis/sample-size-calculator/) "
        "(população 197.639, confiança 95%, margem de erro 5%)."
    )
with st.expander("Procedimento de seleção"):
    st.code(
        "amostra = populacao.sort_values('indice_original').sample("
        "n=384, replace=False, random_state=2026)",
        language="python",
    )
    st.caption(
        "Sorteio único, sem reposição, com semente fixa: cada nascimento tem a "
        "mesma probabilidade de seleção (384/197.639 ≈ 0,19%)."
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
