from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
POPULACAO_PATH = ROOT / "data" / "populacao.parquet"
AMOSTRA_PATH = ROOT / "data" / "amostra.csv"
N_ORIGINAL = 197_801
SEMENTE = 2026
DATA_SORTEIO = "04/11/2026"

VARIAVEIS_QUALITATIVAS = {
    "parto": "Tipo de parto",
    "escolaridade_mae": "Escolaridade da mãe",
    "nro_consultas_prenatal": "Consultas de pré-natal",
    "duracao_gestacao": "Duração da gestação",
    "sexo": "Sexo do bebê",
}

ORDEM_CATEGORIAS = {
    "parto": ["VAGINAL", "CESAREO", "IGNORADO", "(Não informado)"],
    "escolaridade_mae": [
        "NENHUMA",
        "DE 1 A 3 ANOS",
        "DE 4 A 7 ANOS",
        "DE 8 A 11 ANOS",
        "COM 12 ANOS OU MAIS",
        "IGNORADO",
        "(Não informado)",
    ],
    "nro_consultas_prenatal": [
        "NENHUMA",
        "DE 1 A 3 CONS",
        "DE 4 A 6 CONS",
        "7 OU MAIS CONS",
        "IGNORADO",
        "(Não informado)",
    ],
    "duracao_gestacao": [
        "MENOS DE 22 SEM",
        "DE 22 A 27 SEM",
        "DE 28 A 31 SEM",
        "DE 32 A 36 SEM",
        "DE 37 A 41 SEM",
        "COM 42 SEM OU MAIS",
        "(Não informado)",
    ],
    "sexo": ["MASCULINO", "FEMININO", "(Não informado)"],
}


def formatar_numero(valor: float, casas: int = 1) -> str:
    formatado = f"{valor:,.{casas}f}"
    return formatado.replace(",", "_").replace(".", ",").replace("_", ".")


def formatar_percentual(valor: float, casas: int = 1) -> str:
    return f"{formatar_numero(valor * 100, casas)}%"


@st.cache_data
def carregar_populacao() -> pd.DataFrame:
    if not POPULACAO_PATH.exists():
        raise FileNotFoundError(f"Arquivo de população não encontrado: {POPULACAO_PATH}")
    return pd.read_parquet(POPULACAO_PATH)


@st.cache_data
def carregar_amostra() -> pd.DataFrame:
    if not AMOSTRA_PATH.exists():
        raise FileNotFoundError(f"Arquivo de amostra não encontrado: {AMOSTRA_PATH}")
    return pd.read_csv(AMOSTRA_PATH)


def selecionar_ano(df: pd.DataFrame, chave: str) -> tuple[pd.DataFrame, int | None]:
    anos = sorted(df["ano"].dropna().astype(int).unique().tolist())
    opcoes = ["Todos"] + anos
    selecionado = st.sidebar.selectbox("Ano de nascimento", opcoes, key=chave)
    if selecionado == "Todos":
        return df, None
    return df.loc[df["ano"].eq(selecionado)].copy(), int(selecionado)


def mostrar_contexto(ano: int | None, nome_conjunto: str) -> None:
    st.caption(
        f"Fonte: SINASC — Prefeitura de Porto Alegre · nascimentos de 2011 a 2021 · "
        f"[dados abertos](https://dadosabertos.poa.br/dataset/sinasc)"
    )
    if ano is not None:
        st.info(
            f"Os gráficos abaixo mostram {nome_conjunto} de {ano}. "
            "Os indicadores e parâmetros de referência continuam calculados sobre "
            "a população/amostra completa."
        )


def mostrar_indicadores(df: pd.DataFrame, n: int, ddof: int, prefixo: str) -> None:
    desvios = df["peso"].std(ddof=ddof)
    idade = df["idade_mae"].mean()
    valores = [
        ("N" if prefixo == "pop" else "n", f"{n:,}".replace(",", ".")),
        (
            "Peso médio (μ)" if prefixo == "pop" else "Peso médio (x̄)",
            f"{formatar_numero(df['peso'].mean())} g",
        ),
        (
            "DP peso (σ)" if prefixo == "pop" else "DP peso (S)",
            f"{formatar_numero(desvios)} g",
        ),
        (
            "Cesáreas (π)" if prefixo == "pop" else "Cesáreas (P)",
            formatar_percentual(df["cesarea"].mean()),
        ),
        ("Baixo peso", formatar_percentual(df["baixo_peso"].mean())),
        ("Prematuros", formatar_percentual(df["prematuro"].mean())),
        ("Idade média materna", f"{formatar_numero(idade)} anos"),
    ]
    for inicio in (0, 4):
        with st.container(horizontal=True):
            for label, valor in valores[inicio : inicio + 4]:
                st.metric(label, valor, border=True)


def _medidas_resumo(serie: pd.Series, ddof: int) -> pd.DataFrame:
    dados = pd.to_numeric(serie, errors="coerce").dropna()
    if dados.empty:
        return pd.DataFrame(
            {"Medida": ["Observações válidas"], "Valor": [0]}
        )

    moda = dados.mode()
    desvio = dados.std(ddof=ddof)
    media = dados.mean()
    medidas = [
        ("Observações válidas", str(len(dados))),
        ("Média", formatar_numero(media, 2)),
        ("Mediana", formatar_numero(dados.median(), 2)),
        ("Moda", ", ".join(formatar_numero(float(valor), 2) for valor in moda)),
        ("Desvio-padrão", formatar_numero(desvio, 2)),
        ("Variância", formatar_numero(dados.var(ddof=ddof), 2)),
        (
            "Coeficiente de variação (%)",
            formatar_numero(desvio / media * 100, 2) if media else "Não definido",
        ),
        ("Mínimo", formatar_numero(dados.min(), 2)),
        ("Q1", formatar_numero(dados.quantile(0.25), 2)),
        ("Q3", formatar_numero(dados.quantile(0.75), 2)),
        ("Máximo", formatar_numero(dados.max(), 2)),
        ("Amplitude", formatar_numero(dados.max() - dados.min(), 2)),
        ("IQR", formatar_numero(dados.quantile(0.75) - dados.quantile(0.25), 2)),
        ("Assimetria", formatar_numero(dados.skew(), 4)),
    ]
    return pd.DataFrame(medidas, columns=["Medida", "Valor"])


def _histograma(serie: pd.Series, titulo: str, chave: str, unidade: str) -> None:
    dados = pd.to_numeric(serie, errors="coerce").dropna()
    if dados.empty:
        st.warning("Não há observações válidas para exibir.")
        return
    media = dados.mean()
    mediana = dados.median()
    fig = px.histogram(
        x=dados,
        nbins=35,
        labels={"x": unidade, "count": "Frequência"},
        title=titulo,
    )
    fig.add_vline(
        x=media,
        line_dash="dash",
        line_color="#d62728",
        annotation_text=f"Média: {formatar_numero(media)}",
    )
    fig.add_vline(
        x=mediana,
        line_dash="dot",
        line_color="#2ca02c",
        annotation_text=f"Mediana: {formatar_numero(mediana)}",
    )
    st.plotly_chart(fig, key=f"{chave}_hist")


def _boxplot(serie: pd.Series, titulo: str, chave: str, unidade: str) -> None:
    dados = pd.to_numeric(serie, errors="coerce").dropna()
    fig = px.box(
        x=dados,
        points="outliers",
        labels={"x": unidade},
        title=titulo,
    )
    st.plotly_chart(fig, key=f"{chave}_box")


def _qqplot_peso(df: pd.DataFrame, chave: str) -> None:
    pesos = df["peso"].dropna()
    if len(pesos) < 2:
        st.warning("São necessárias ao menos duas observações para o gráfico Q-Q.")
        return
    (teoricos, ordenados), (inclinacao, intercepto, _) = stats.probplot(
        pesos, dist="norm"
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=teoricos,
            y=ordenados,
            mode="markers",
            name="Pesos observados",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=teoricos,
            y=inclinacao * teoricos + intercepto,
            mode="lines",
            name="Referência normal",
        )
    )
    fig.update_layout(
        title="Gráfico Q-Q normal do peso",
        xaxis_title="Quantis teóricos normais",
        yaxis_title="Quantis observados (g)",
    )
    st.plotly_chart(fig, key=f"{chave}_qq")


def _dados_categoricos(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    categorias = df[coluna].astype("string").str.strip().fillna("")
    categorias = categorias.mask(categorias.eq(""), "(Não informado)")
    frequencias = categorias.value_counts(dropna=False).rename_axis("Categoria").reset_index(name="Frequência")
    frequencias["Proporção (%)"] = frequencias["Frequência"] / len(df) * 100
    ordem = {valor: indice for indice, valor in enumerate(ORDEM_CATEGORIAS[coluna])}
    frequencias["_ordem"] = frequencias["Categoria"].map(ordem).fillna(999)
    return frequencias.sort_values(["_ordem", "Categoria"]).drop(columns="_ordem")


def _secao_qualitativa(df: pd.DataFrame, chave: str) -> None:
    st.subheader("Variáveis qualitativas")
    st.caption(
        "As barras mostram contagens ou proporções; passe o cursor para consultar "
        "a frequência e o percentual. Categorias vazias aparecem como “Não informado”."
    )
    for coluna, rotulo in VARIAVEIS_QUALITATIVAS.items():
        frequencias = _dados_categoricos(df, coluna)
        medida = st.selectbox(
            f"Escala do gráfico — {rotulo.lower()}",
            ["Proporção (%)", "Frequência"],
            key=f"{chave}_{coluna}_escala",
        )
        fig = px.bar(
            frequencias,
            x="Categoria",
            y=medida,
            title=rotulo,
            custom_data=["Frequência", "Proporção (%)"],
            category_orders={"Categoria": ORDEM_CATEGORIAS[coluna]},
            labels={"Categoria": rotulo, medida: medida},
        )
        fig.update_traces(
            hovertemplate=(
                "%{x}<br>Frequência: %{customdata[0]}"
                "<br>Proporção: %{customdata[1]:.2f}%<extra></extra>"
            )
        )
        st.plotly_chart(fig, key=f"{chave}_{coluna}_barras")
        st.dataframe(
            frequencias.assign(
                **{
                    "Proporção (%)": frequencias["Proporção (%)"].map(
                        lambda valor: f"{formatar_numero(valor, 2)}%"
                    )
                }
            )[["Categoria", "Frequência", "Proporção (%)"]],
            hide_index=True,
        )
        st.caption(
            f"Na variável {rotulo.lower()}, cada barra representa a distribuição das "
            "categorias neste conjunto de dados; categorias ignoradas ou ausentes "
            "permanecem visíveis para contextualizar os percentuais."
        )


def renderizar_descritiva(df: pd.DataFrame, chave: str, ddof: int) -> None:
    st.subheader("Variáveis quantitativas")
    for coluna, rotulo, unidade in [
        ("peso", "Peso ao nascer", "Peso (g)"),
        ("idade_mae", "Idade da mãe", "Idade (anos)"),
    ]:
        dados_validos = df[coluna].dropna()
        st.markdown(f"#### {rotulo}")
        _histograma(dados_validos, f"Distribuição — {rotulo.lower()}", f"{chave}_{coluna}", unidade)
        _boxplot(dados_validos, f"Boxplot — {rotulo.lower()}", f"{chave}_{coluna}", unidade)
        resumo = _medidas_resumo(dados_validos, ddof)
        st.dataframe(resumo, hide_index=True)
        st.caption(
            "O boxplot destaca como valores atípicos os pontos além de 1,5 × IQR. "
            "A idade materna usa apenas registros com idade válida."
        )

    _qqplot_peso(df, chave)
    st.caption(
        "No Q-Q plot, pontos próximos à reta indicam compatibilidade aproximada "
        "com a distribuição normal; desvios nas caudas mostram diferenças."
    )

    _secao_qualitativa(df, chave)
    _secoes_cruzamentos(df, chave)


def _secoes_cruzamentos(df: pd.DataFrame, chave: str) -> None:
    st.subheader("Cruzamentos de interesse")

    cesareas_escolaridade = df.groupby("escolaridade_mae", dropna=False).agg(
        cesareas=("cesarea", "sum"),
        nascimentos=("cesarea", "size"),
    )
    cesareas_escolaridade["Proporção de cesáreas (%)"] = (
        cesareas_escolaridade["cesareas"] / cesareas_escolaridade["nascimentos"] * 100
    )
    cesareas_escolaridade = cesareas_escolaridade.reset_index()
    cesareas_escolaridade["escolaridade_mae"] = (
        cesareas_escolaridade["escolaridade_mae"]
        .astype("string")
        .str.strip()
        .replace("", "(Não informado)")
        .fillna("(Não informado)")
    )
    fig_escolaridade = px.bar(
        cesareas_escolaridade,
        x="escolaridade_mae",
        y="Proporção de cesáreas (%)",
        custom_data=["cesareas", "nascimentos"],
        title="Proporção de cesáreas por escolaridade materna",
        labels={
            "escolaridade_mae": "Escolaridade da mãe",
            "Proporção de cesáreas (%)": "Cesáreas (%)",
        },
    )
    fig_escolaridade.update_traces(
        hovertemplate="%{x}<br>Cesáreas: %{customdata[0]} de %{customdata[1]}"
        "<br>Proporção: %{y:.1f}%<extra></extra>"
    )
    st.plotly_chart(fig_escolaridade, key=f"{chave}_cesarea_escolaridade")
    st.caption(
        "O gráfico descreve associação entre escolaridade e proporção de cesáreas; "
        "não permite concluir que escolaridade cause o tipo de parto."
    )

    prenatal = df["nro_consultas_prenatal"].astype("string").str.strip().fillna("")
    prenatal = prenatal.mask(prenatal.eq(""), "(Não informado)")
    dados_peso = df.assign(faixa_prenatal=prenatal)
    ordem = ORDEM_CATEGORIAS["nro_consultas_prenatal"]
    fig_prenatal = px.box(
        dados_peso,
        x="faixa_prenatal",
        y="peso",
        points="outliers",
        category_orders={"faixa_prenatal": ordem},
        title="Peso ao nascer por faixa de consultas pré-natais",
        labels={
            "faixa_prenatal": "Consultas de pré-natal",
            "peso": "Peso (g)",
        },
    )
    st.plotly_chart(fig_prenatal, key=f"{chave}_peso_prenatal")
    st.caption(
        "As caixas comparam a distribuição do peso entre faixas de consultas. "
        "Diferenças observadas são associações e não demonstram causalidade."
    )

    por_ano = df.groupby("ano").agg(
        cesareas=("cesarea", "mean"),
        peso_medio=("peso", "mean"),
    ).reset_index()
    por_ano["cesareas"] *= 100
    col_esq, col_dir = st.columns(2)
    with col_esq:
        fig_cesareas = px.line(
            por_ano,
            x="ano",
            y="cesareas",
            markers=True,
            title="Cesáreas por ano",
            labels={"ano": "Ano", "cesareas": "Cesáreas (%)"},
        )
        st.plotly_chart(fig_cesareas, key=f"{chave}_cesareas_ano")
    with col_dir:
        fig_peso = px.line(
            por_ano,
            x="ano",
            y="peso_medio",
            markers=True,
            title="Peso médio por ano",
            labels={"ano": "Ano", "peso_medio": "Peso médio (g)"},
        )
        st.plotly_chart(fig_peso, key=f"{chave}_peso_ano")
    st.caption(
        "As tendências anuais mostram que os dados podem variar ao longo do tempo; "
        "por isso, os resultados gerais representam a mistura dos anos de 2011 a 2021."
    )


def _medidas_comparaveis(df: pd.DataFrame) -> dict[str, float]:
    return {
        "Média do peso (g)": df["peso"].mean(),
        "Mediana do peso (g)": df["peso"].median(),
        "DP do peso (g)": df["peso"].std(ddof=1),
        "Cesáreas (%)": df["cesarea"].mean() * 100,
        "Baixo peso (%)": df["baixo_peso"].mean() * 100,
        "Prematuros (%)": df["prematuro"].mean() * 100,
        "Idade média materna (anos)": df["idade_mae"].mean(),
    }


def _tabela_comparacao(populacao: pd.DataFrame, amostra: pd.DataFrame) -> pd.DataFrame:
    pop_medidas = _medidas_comparaveis(populacao)
    amostra_medidas = _medidas_comparaveis(amostra)
    linhas = []
    for medida, valor_pop in pop_medidas.items():
        valor_amostra = amostra_medidas[medida]
        diferenca = valor_amostra - valor_pop
        relativa = abs(diferenca) / abs(valor_pop) * 100 if valor_pop else float("nan")
        linhas.append(
            {
                "Medida": medida,
                "População": valor_pop,
                "Amostra": valor_amostra,
                "Diferença absoluta": abs(diferenca),
                "Diferença relativa (%)": relativa,
            }
        )
    return pd.DataFrame(linhas)


def renderizar_comparacao(populacao: pd.DataFrame, amostra: pd.DataFrame, chave: str) -> None:
    st.subheader("Comparação com a população")
    tabela = _tabela_comparacao(populacao, amostra)
    tabela_exibicao = tabela.copy()
    for coluna in ["População", "Amostra", "Diferença absoluta"]:
        tabela_exibicao[coluna] = tabela_exibicao[coluna].map(
            lambda valor: formatar_numero(valor, 2)
        )
    tabela_exibicao["Diferença relativa (%)"] = tabela_exibicao[
        "Diferença relativa (%)"
    ].map(lambda valor: f"{formatar_numero(valor, 2)}%")
    st.dataframe(
        tabela_exibicao,
        hide_index=True,
    )

    dados_peso = pd.concat(
        [
            populacao[["peso"]].assign(Conjunto="População"),
            amostra[["peso"]].assign(Conjunto="Amostra"),
        ],
        ignore_index=True,
    )
    fig_peso = px.histogram(
        dados_peso,
        x="peso",
        color="Conjunto",
        histnorm="probability density",
        barmode="overlay",
        opacity=0.55,
        nbins=40,
        title="Distribuição do peso: população e amostra",
        labels={"peso": "Peso (g)", "density": "Densidade"},
    )
    st.plotly_chart(fig_peso, key=f"{chave}_peso_sobreposto")

    linhas = []
    for coluna, rotulo in VARIAVEIS_QUALITATIVAS.items():
        for conjunto, dados in [("População", populacao), ("Amostra", amostra)]:
            frequencias = _dados_categoricos(dados, coluna)
            for _, linha in frequencias.iterrows():
                linhas.append(
                    {
                        "Variável": rotulo,
                        "Categoria": linha["Categoria"],
                        "Conjunto": conjunto,
                        "Proporção (%)": linha["Proporção (%)"],
                    }
                )
    comparacao_qualitativa = pd.DataFrame(linhas)
    fig_categorias = px.bar(
        comparacao_qualitativa,
        x="Categoria",
        y="Proporção (%)",
        color="Conjunto",
        barmode="group",
        facet_col="Variável",
        facet_col_wrap=2,
        title="Proporções por categoria: população e amostra",
    )
    fig_categorias.update_xaxes(matches=None, tickangle=30)
    fig_categorias.for_each_annotation(
        lambda anotacao: anotacao.update(text=anotacao.text.split("=")[-1])
    )
    st.plotly_chart(fig_categorias, key=f"{chave}_categorias_comparadas")

    media_pop = populacao["peso"].mean()
    media_amostra = amostra["peso"].mean()
    cesarea_pop = populacao["cesarea"].mean()
    cesarea_amostra = amostra["cesarea"].mean()
    st.markdown(
        f"Na amostra, o peso médio foi **{formatar_numero(media_amostra)} g** "
        f"(população: {formatar_numero(media_pop)} g), e a proporção de cesáreas foi "
        f"**{formatar_percentual(cesarea_amostra)}** "
        f"(população: {formatar_percentual(cesarea_pop)}). "
        "Diferenças são esperadas pela variabilidade amostral; caudas e eventos "
        "raros tendem a variar mais do que as medidas de centro."
    )
