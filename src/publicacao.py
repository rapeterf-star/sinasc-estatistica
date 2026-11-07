import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
ARQUIVO_PUBLICO = ROOT / "data" / "resumo_publico.json"
N_ORIGINAL = 197_801
N_MINIMO_EXIBICAO = 10
SEMENTE = 2026
DATA_SORTEIO = "04/11/2026"
COR_POPULACAO = "#0072B2"
COR_AMOSTRA = "#D55E00"
CORES_CONJUNTOS = {
    "População": COR_POPULACAO,
    "Amostra": COR_AMOSTRA,
}

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

VARIAVEIS_QUANTITATIVAS = {
    "peso": {"label": "Peso ao nascer", "unit": "Peso (g)", "step": 100},
    "idade_mae": {"label": "Idade da mãe", "unit": "Idade (anos)", "step": 1},
}


def formatar_numero(valor: float, casas: int = 1) -> str:
    formatado = f"{valor:,.{casas}f}"
    return formatado.replace(",", "_").replace(".", ",").replace("_", ".")


def formatar_percentual(valor: float, casas: int = 1) -> str:
    return f"{formatar_numero(valor * 100, casas)}%"


def _carregar_json() -> dict[str, Any]:
    if not ARQUIVO_PUBLICO.exists():
        raise FileNotFoundError(
            f"Resumo agregado ausente: {ARQUIVO_PUBLICO}. "
            "Execute `python src/04_preparar_publicacao.py` localmente."
        )
    with ARQUIVO_PUBLICO.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


@st.cache_data
def carregar_resumo_publico() -> dict[str, Any]:
    return _carregar_json()


def _formatar_medida(resultado: dict[str, Any], valor: float) -> str:
    codigo = resultado["codigo"]
    if codigo == "H1":
        return formatar_percentual(valor)
    if codigo == "H2":
        return f"{formatar_numero(valor * 100)} p.p."
    return f"{formatar_numero(valor)} g"


def _formatar_ic(resultado: dict[str, Any]) -> str:
    inferior, superior = resultado["intervalo"]
    return (
        f"[{_formatar_medida(resultado, inferior)}, "
        f"{_formatar_medida(resultado, superior)}]"
    )


def _formatar_p(valor: float) -> str:
    return "< 0,001" if valor < 0.001 else formatar_numero(valor, 3)


def _escolher_ano(chave: str, dados: dict[str, Any]) -> str:
    opcoes = ["Todos"] + sorted(dados["por_ano"], key=int)
    return st.sidebar.selectbox("Ano de nascimento", opcoes, key=chave)


def _visao_ano(dados: dict[str, Any], ano: str) -> dict[str, Any]:
    if ano == "Todos":
        return dados["total"]
    return dados["por_ano"][ano]


def _mostrar_contexto(ano: str, nome_conjunto: str) -> None:
    st.caption(
        "Fonte: SINASC — Prefeitura de Porto Alegre · nascimentos de 2011 a 2021 · "
        "[dados abertos](https://dadosabertos.poa.br/dataset/sinasc). "
        "Este painel publica apenas estatísticas agregadas, sem linhas individuais."
    )
    if ano != "Todos":
        st.info(
            f"Os gráficos detalhados mostram {nome_conjunto} de {ano}. "
            "Os indicadores principais continuam resumindo o conjunto completo."
        )


def _mostrar_indicadores(
    resumo: dict[str, Any], quantidade: int, prefixo: str
) -> None:
    indicadores = resumo["indicadores"]
    metricas = [
        ("N" if prefixo == "pop" else "n", f"{quantidade:,}".replace(",", ".")),
        (
            "Peso médio (μ)" if prefixo == "pop" else "Peso médio (x̄)",
            f"{formatar_numero(indicadores['peso_medio'])} g",
        ),
        (
            "DP peso (σ)" if prefixo == "pop" else "DP peso (S)",
            f"{formatar_numero(indicadores['peso_dp'])} g",
        ),
        (
            "Cesáreas (π)" if prefixo == "pop" else "Cesáreas (P)",
            formatar_percentual(indicadores["cesarea"]),
        ),
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


def _tabela_medidas(
    estatisticas: dict[str, Any],
    nome_coluna: str,
) -> pd.DataFrame:
    registros = estatisticas[nome_coluna]
    linhas = [
        ("Observações válidas", str(registros["n"])),
        ("Média", formatar_numero(registros["media"], 2)),
        ("Mediana", formatar_numero(registros["mediana"], 2)),
        ("Moda", registros["moda"]),
        ("Desvio-padrão", formatar_numero(registros["desvio_padrao"], 2)),
        ("Variância", formatar_numero(registros["variancia"], 2)),
        (
            "Coeficiente de variação (%)",
            formatar_numero(registros["cv"], 2) if registros["cv"] is not None else "Não definido",
        ),
        ("Mínimo", formatar_numero(registros["minimo"], 2)),
        ("Q1", formatar_numero(registros["q1"], 2)),
        ("Q3", formatar_numero(registros["q3"], 2)),
        ("Máximo", formatar_numero(registros["maximo"], 2)),
        ("Amplitude", formatar_numero(registros["amplitude"], 2)),
        ("IQR", formatar_numero(registros["iqr"], 2)),
        ("Assimetria", formatar_numero(registros["assimetria"], 4)),
    ]
    return pd.DataFrame(linhas, columns=["Medida", "Valor"])


def _figura_histograma(
    hist: dict[str, Any],
    titulo: str,
    unidade: str,
    chave: str,
    grupo: str | None = None,
) -> None:
    fig = go.Figure()
    if grupo:
        for nome, item in hist.items():
            fig.add_bar(
                x=item["centros"],
                y=item["densidade"],
                width=item["larguras"],
                name=nome,
                marker_color=CORES_CONJUNTOS.get(nome),
                opacity=0.58,
                customdata=np.column_stack(
                    [item["contagens"], item["limites_inferiores"], item["limites_superiores"]]
                ),
                hovertemplate=(
                    "%{fullData.name}<br>Faixa: %{customdata[1]:.1f}–"
                    "%{customdata[2]:.1f}<br>Frequência: %{customdata[0]}"
                    "<br>Densidade: %{y:.5f}<extra></extra>"
                ),
            )
        fig.update_layout(barmode="overlay")
    else:
        fig.add_bar(
            x=hist["centros"],
            y=hist["contagens"],
            width=hist["larguras"],
            name="Frequência",
            marker_color=COR_POPULACAO,
            customdata=np.column_stack(
                [hist["limites_inferiores"], hist["limites_superiores"]]
            ),
            hovertemplate=(
                "Faixa: %{customdata[0]:.1f}–%{customdata[1]:.1f}"
                "<br>Frequência: %{y}<extra></extra>"
            ),
        )
        for valor, rotulo, cor, estilo in hist["linhas_referencia"]:
            fig.add_vline(
                x=valor,
                line_dash=estilo,
                line_color=cor,
                annotation_text=f"{rotulo}: {formatar_numero(valor)}",
            )
    fig.update_layout(
        title=titulo,
        xaxis_title=unidade,
        yaxis_title="Densidade" if grupo else "Frequência",
    )
    st.plotly_chart(fig, key=chave)


def _figura_boxplot(
    caixas: list[dict[str, Any]],
    titulo: str,
    chave: str,
    unidade: str,
    por_grupo: bool = False,
) -> None:
    fig = go.Figure()
    if por_grupo:
        for caixa in caixas:
            fig.add_trace(
                go.Box(
                    name=caixa["grupo"],
                    q1=[caixa["q1"]],
                    median=[caixa["mediana"]],
                    q3=[caixa["q3"]],
                    lowerfence=[caixa["limite_inferior"]],
                    upperfence=[caixa["limite_superior"]],
                    boxpoints=False,
                    fillcolor="rgba(0, 114, 178, 0.18)",
                    line_color=COR_POPULACAO,
                    hovertemplate=(
                        "%{x}<br>Q1: %{q1:.1f}<br>Mediana: %{median:.1f}"
                        "<br>Q3: %{q3:.1f}<extra></extra>"
                    ),
                )
            )
        fig.update_layout(xaxis_title="Grupo")
    else:
        caixa = caixas[0]
        fig.add_trace(
            go.Box(
                name="Distribuição agregada",
                q1=[caixa["q1"]],
                median=[caixa["mediana"]],
                q3=[caixa["q3"]],
                lowerfence=[caixa["limite_inferior"]],
                upperfence=[caixa["limite_superior"]],
                boxpoints=False,
                fillcolor="rgba(0, 114, 178, 0.18)",
                line_color=COR_POPULACAO,
                hovertemplate=(
                    "Q1: %{q1:.1f}<br>Mediana: %{median:.1f}"
                    "<br>Q3: %{q3:.1f}<extra></extra>"
                ),
            )
        )
    fig.update_layout(title=titulo, yaxis_title=unidade)
    st.plotly_chart(fig, key=chave)


def _figura_qq(
    pontos: list[dict[str, float]],
    inclinacao: float,
    intercepto: float,
    chave: str,
) -> None:
    teoricos = [ponto["teorico"] for ponto in pontos]
    observados = [ponto["observado"] for ponto in pontos]
    fig = go.Figure()
    fig.add_scatter(
        x=teoricos,
        y=observados,
        mode="markers",
        name="Quantis agrupados",
        marker_color=COR_POPULACAO,
        customdata=[ponto["n_aproximado"] for ponto in pontos],
        hovertemplate=(
            "Quantil teórico: %{x:.2f}<br>Quantil observado: %{y:.1f}"
            "<br>Observações representadas: ≈%{customdata}<extra></extra>"
        ),
    )
    fig.add_scatter(
        x=teoricos,
        y=[inclinacao * valor + intercepto for valor in teoricos],
        mode="lines",
        name="Referência normal",
        line={"color": "#555555", "dash": "dash"},
    )
    fig.update_layout(
        title="Gráfico Q-Q normal do peso (quantis agrupados)",
        xaxis_title="Quantis teóricos normais",
        yaxis_title="Quantis observados (g)",
    )
    st.plotly_chart(fig, key=chave)


def _mostrar_qualitativas(dados: dict[str, Any], chave: str) -> None:
    st.subheader("Variáveis qualitativas")
    st.caption(
        "As distribuições foram agrupadas. Categorias com menos de 10 registros "
        "foram reunidas e seus valores individuais não são divulgados."
    )
    for coluna, rotulo in VARIAVEIS_QUALITATIVAS.items():
        registros = dados["categorias"][coluna]
        frequencias = pd.DataFrame(registros)
        medida = st.selectbox(
            f"Escala do gráfico — {rotulo.lower()}",
            ["Proporção (%)", "Frequência"],
            key=f"{chave}_{coluna}_escala",
        )
        fig = go.Figure(
            go.Bar(
                x=frequencias["proporcao"] * 100
                if medida == "Proporção (%)"
                else frequencias["frequencia"],
                y=frequencias["categoria"],
                orientation="h",
                marker_color=COR_POPULACAO,
                customdata=frequencias[["frequencia", "proporcao"]],
                hovertemplate=(
                    "%{y}<br>Frequência: %{customdata[0]}"
                    "<br>Proporção: %{customdata[1]:.2%}<extra></extra>"
                ),
            )
        )
        fig.update_layout(
            title=rotulo,
            xaxis_title=medida,
            yaxis_title=rotulo,
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, key=f"{chave}_{coluna}_barras")
        tabela = frequencias.copy()
        tabela["Frequência"] = tabela["frequencia"].map(
            lambda valor: (
                "Suprimida"
                if pd.isna(valor)
                else f"{int(valor):,}".replace(",", ".")
            )
        )
        tabela["Proporção (%)"] = tabela["proporcao"].map(
            lambda valor: (
                "Suprimida"
                if pd.isna(valor)
                else formatar_percentual(valor, 2)
            )
        )
        st.dataframe(
            tabela[["categoria", "Frequência", "Proporção (%)"]].rename(
                columns={"categoria": "Categoria"}
            ),
            hide_index=True,
        )


def _mostrar_cruzamentos(dados: dict[str, Any], chave: str) -> None:
    st.subheader("Cruzamentos de interesse")

    escolaridade = pd.DataFrame(dados["cesarea_por_escolaridade"])
    if escolaridade.empty:
        st.info(
            "Cruzamento por escolaridade omitido neste recorte para evitar "
            "a divulgação de contagens pequenas."
        )
    else:
        fig_escolaridade = go.Figure(
            go.Bar(
                x=[valor * 100 for valor in escolaridade["proporcao_cesarea"]],
                y=escolaridade["grupo"],
                orientation="h",
                marker_color=COR_POPULACAO,
                customdata=escolaridade[["cesareas", "outros_partos", "n"]],
                hovertemplate=(
                    "%{y}<br>Cesáreas: %{customdata[0]}"
                    "<br>Outros partos: %{customdata[1]}"
                    "<br>Proporção: %{x:.1f}%<extra></extra>"
                ),
            )
        )
        fig_escolaridade.update_layout(
            title="Proporção de cesáreas por escolaridade materna",
            xaxis_title="Cesáreas (%)",
            yaxis_title="Grupo de escolaridade",
        )
        fig_escolaridade.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_escolaridade, key=f"{chave}_cesarea_escolaridade")
    st.caption(
        "O gráfico descreve associação entre escolaridade e proporção de cesáreas; "
        "não permite concluir que escolaridade cause o tipo de parto."
    )

    caixas = dados["peso_por_prenatal"]
    if caixas:
        _figura_boxplot(
            caixas,
            "Peso ao nascer por faixa de consultas pré-natais",
            f"{chave}_peso_prenatal",
            "Peso (g)",
            por_grupo=True,
        )
    else:
        st.info(
            "Boxplots por pré-natal omitidos neste recorte para evitar "
            "a divulgação de grupos pequenos."
        )
    st.caption(
        "O gráfico mostra quartis agregados por grupo, sem pontos ou observações "
        "individuais. As diferenças são associações, não prova de causalidade."
    )

    anual = pd.DataFrame(dados["tendencias_anuais"])
    col_esq, col_dir = st.columns(2)
    with col_esq:
        fig = go.Figure(
            go.Scatter(
                x=anual["ano"],
                y=[valor * 100 for valor in anual["cesarea"]],
                mode="lines+markers",
                line={"color": COR_POPULACAO},
                marker={"color": COR_POPULACAO},
                hovertemplate="%{x}<br>Cesáreas: %{y:.2f}%<extra></extra>",
            )
        )
        fig.update_layout(
            title="Cesáreas por ano",
            xaxis_title="Ano",
            yaxis_title="Cesáreas (%)",
        )
        st.plotly_chart(fig, key=f"{chave}_cesareas_ano")
    with col_dir:
        fig = go.Figure(
            go.Scatter(
                x=anual["ano"],
                y=anual["peso_medio"],
                mode="lines+markers",
                line={"color": COR_POPULACAO},
                marker={"color": COR_POPULACAO},
                hovertemplate="%{x}<br>Peso médio: %{y:.1f} g<extra></extra>",
            )
        )
        fig.update_layout(
            title="Peso médio por ano",
            xaxis_title="Ano",
            yaxis_title="Peso médio (g)",
        )
        st.plotly_chart(fig, key=f"{chave}_peso_ano")
    st.caption(
        "As tendências anuais mostram que os dados podem variar ao longo do tempo; "
        "os resultados gerais representam a mistura dos anos de 2011 a 2021."
    )


def renderizar_descritiva(dados: dict[str, Any], chave: str) -> None:
    st.subheader("Variáveis quantitativas")
    for coluna, configuracao in VARIAVEIS_QUANTITATIVAS.items():
        st.markdown(f"#### {configuracao['label']}")
        estatisticas = dados["estatisticas"]
        _figura_histograma(
            dados["histogramas"][coluna],
            f"Distribuição — {configuracao['label'].lower()}",
            configuracao["unit"],
            f"{chave}_{coluna}_hist",
        )
        _figura_boxplot(
            [dados["boxplots"][coluna]],
            f"Boxplot — {configuracao['label'].lower()}",
            f"{chave}_{coluna}_box",
            configuracao["unit"],
        )
        st.dataframe(_tabela_medidas(estatisticas, coluna), hide_index=True)
        st.caption(
            "O boxplot exibe quartis e limites de 1,5 × IQR, sem pontos individuais. "
            "A idade materna usa apenas registros com idade válida."
        )

    qq = dados["qq_peso"]
    _figura_qq(qq["pontos"], qq["inclinacao"], qq["intercepto"], f"{chave}_qq")
    st.caption(
        "O Q-Q plot mostra quantis agrupados para preservar a privacidade. "
        "Pontos próximos à reta indicam compatibilidade aproximada com normalidade."
    )
    _mostrar_qualitativas(dados, chave)
    _mostrar_cruzamentos(dados, chave)


def _tabela_comparacao(
    populacao: dict[str, Any], amostra: dict[str, Any]
) -> pd.DataFrame:
    medidas = [
        ("Média do peso (g)", "peso_medio"),
        ("Mediana do peso (g)", "peso_mediano"),
        ("DP do peso (g)", "peso_dp"),
        ("Cesáreas (%)", "cesarea"),
        ("Baixo peso (%)", "baixo_peso"),
        ("Prematuros (%)", "prematuro"),
        ("Idade média materna (anos)", "idade_media"),
    ]
    linhas = []
    for nome, chave in medidas:
        valor_pop = populacao["indicadores"][chave]
        valor_amostra = amostra["indicadores"][chave]
        if chave in {"cesarea", "baixo_peso", "prematuro"}:
            valor_pop *= 100
            valor_amostra *= 100
        diferenca = valor_amostra - valor_pop
        linhas.append(
            {
                "Medida": nome,
                "População": formatar_numero(valor_pop, 2),
                "Amostra": formatar_numero(valor_amostra, 2),
                "Diferença absoluta": formatar_numero(abs(diferenca), 2),
                "Diferença relativa (%)": (
                    formatar_percentual(abs(diferenca / valor_pop), 2)
                    if valor_pop
                    else "Não definida"
                ),
            }
        )
    return pd.DataFrame(linhas)


def renderizar_comparacao(
    populacao: dict[str, Any], amostra: dict[str, Any], chave: str
) -> None:
    st.subheader("Comparação com a população")
    st.dataframe(_tabela_comparacao(populacao, amostra), hide_index=True)
    _figura_histograma(
        {
            "População": populacao["histogramas"]["peso"],
            "Amostra": amostra["histogramas"]["peso"],
        },
        "Distribuição do peso: população e amostra",
        "Peso (g)",
        f"{chave}_peso_sobreposto",
        grupo="Conjunto",
    )

    comparacao = []
    for coluna, rotulo in VARIAVEIS_QUALITATIVAS.items():
        tabelas = {
            "População": {
                registro["categoria"]: registro
                for registro in populacao["categorias"][coluna]
            },
            "Amostra": {
                registro["categoria"]: registro
                for registro in amostra["categorias"][coluna]
            },
        }
        categorias = list(
            dict.fromkeys(
                list(tabelas["População"].keys()) + list(tabelas["Amostra"].keys())
            )
        )
        for categoria in categorias:
            for conjunto, tabela in tabelas.items():
                registro = tabela.get(categoria)
                if registro is None:
                    proporcao = None
                    frequencia: int | None = None
                else:
                    proporcao = registro["proporcao"]
                    frequencia = registro["frequencia"]
                comparacao.append(
                    {
                        "Variável": rotulo,
                        "Categoria": categoria,
                        "Conjunto": conjunto,
                        "Proporção (%)": (
                            proporcao * 100
                            if frequencia is not None and proporcao is not None
                            else None
                        ),
                    }
                )
    agrupado = pd.DataFrame(comparacao)
    fig = _figura_barras_comparacao(agrupado)
    st.plotly_chart(fig, key=f"{chave}_categorias_comparadas")

    media_pop = populacao["indicadores"]["peso_medio"]
    media_amostra = amostra["indicadores"]["peso_medio"]
    prop_pop = populacao["indicadores"]["cesarea"]
    prop_amostra = amostra["indicadores"]["cesarea"]
    st.markdown(
        f"Na amostra, o peso médio foi **{formatar_numero(media_amostra)} g** "
        f"(população: {formatar_numero(media_pop)} g), e a proporção de cesáreas foi "
        f"**{formatar_percentual(prop_amostra)}** "
        f"(população: {formatar_percentual(prop_pop)}). "
        "Diferenças são esperadas pela variabilidade amostral; caudas e eventos "
        "raros variam mais que as medidas de centro."
    )
    st.caption(
        "O aplicativo publica resumos agregados; o arquivo CSV com os 384 registros "
        "individuais não é disponibilizado no deploy público."
    )


def _figura_barras_comparacao(agrupado: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for conjunto in ("População", "Amostra"):
        parte = agrupado.loc[agrupado["Conjunto"].eq(conjunto)]
        rotulos = [
            f"{variavel} — {categoria}"
            for variavel, categoria in zip(parte["Variável"], parte["Categoria"])
        ]
        fig.add_bar(
            x=parte["Proporção (%)"],
            y=rotulos,
            orientation="h",
            name=conjunto,
            marker_color=CORES_CONJUNTOS[conjunto],
            customdata=parte[["Variável", "Categoria"]],
            hovertemplate="%{customdata[0]}<br>%{customdata[1]}<br>%{x:.2f}%<extra></extra>",
        )
    fig.update_layout(
        title="Proporções por categoria: população e amostra",
        barmode="group",
        xaxis_title="Proporção (%)",
        yaxis_title="Variável e categoria",
        legend={"orientation": "h"},
        height=max(480, 30 * agrupado[["Variável", "Categoria"]].drop_duplicates().shape[0]),
        margin={"l": 300, "t": 70},
    )
    fig.update_xaxes(range=[0, 100])
    fig.update_yaxes(autorange="reversed")
    return fig


def renderizar_inferencia(resumo: dict[str, Any]) -> None:
    resultados = resumo["inferencia"]["resultados"]
    simulacao = resumo["inferencia"]["simulacao"]

    def medida(resultado: dict[str, Any], valor: float) -> str:
        return _formatar_medida(resultado, valor)

    def resumo_tabela(resultado: dict[str, Any]) -> dict[str, str]:
        return {
            "Hipótese": resultado["codigo"],
            "Parâmetro populacional": medida(
                resultado, resultado["parametro_populacional"]
            ),
            "Estimativa amostral": medida(resultado, resultado["estimativa"]),
            "IC de 95%": _formatar_ic(resultado),
            "IC contém o parâmetro?": "Sim" if resultado["contem_parametro"] else "Não",
            "Valor-p": _formatar_p(resultado["valor_p"]),
            "Decisão": "Rejeita H₀" if resultado["rejeita_h0"] else "Não rejeita H₀",
            "H₀ verdadeira na população?": (
                "Sim" if resultado["h0_verdadeira_na_populacao"] else "Não"
            ),
            "Classificação": resultado["classificacao"],
        }

    st.title("Painel 3 — Inferência")
    st.markdown(
        "Os quatro testes usam a amostra aleatória oficial de 384 nascimentos. "
        "O nível de significância é **α = 5%**. Depois das decisões, comparamos "
        "estimativas e intervalos com os parâmetros calculados na população completa."
    )
    st.subheader("Resumo dos resultados")
    st.dataframe([resumo_tabela(resultado) for resultado in resultados], hide_index=True)
    st.caption(
        "A classificação compara a decisão do teste com a verdade conhecida na "
        "população. Não rejeitar H₀ não significa provar que H₀ é verdadeira."
    )

    for resultado in resultados:
        st.divider()
        st.header(f"{resultado['codigo']} — {resultado['pergunta']}")
        st.markdown(
            f"**Variável:** {resultado['variavel']}  \n"
            f"**Hipóteses:** H₀: {resultado['hipotese_nula']} · "
            f"H₁: {resultado['hipotese_alternativa']} · **α = 5%**  \n"
            f"**Procedimento:** {resultado['procedimento']}"
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Estimativa amostral", medida(resultado, resultado["estimativa"]))
            st.metric(
                "Parâmetro na população",
                medida(resultado, resultado["parametro_populacional"]),
            )
        with col2:
            st.metric("Intervalo de confiança de 95%", _formatar_ic(resultado))
            st.metric(
                "IC contém o parâmetro?",
                "Sim" if resultado["contem_parametro"] else "Não",
            )
        with col3:
            st.metric(
                "Estatística de teste",
                formatar_numero(resultado["estatistica"], 3),
            )
            st.metric("Valor-p", _formatar_p(resultado["valor_p"]))
        if resultado["intervalo_unilateral_inferior"] is not None:
            st.info(
                "Para a H1 unilateral, o limite inferior de confiança de 95% é "
                f"**{formatar_percentual(resultado['intervalo_unilateral_inferior'])}**. "
                "O intervalo bilateral também é apresentado para comparação."
            )
        if resultado["graus_liberdade"] is not None:
            st.caption(
                f"Graus de liberdade: "
                f"{formatar_numero(resultado['graus_liberdade'], 2)}."
            )
        decisao = "Rejeitamos H₀" if resultado["rejeita_h0"] else "Não rejeitamos H₀"
        verdade = (
            "é verdadeira"
            if resultado["h0_verdadeira_na_populacao"]
            else "é falsa"
        )
        st.markdown(
            f"**Decisão:** {decisao} (valor-p "
            f"{'<' if resultado['valor_p'] < 0.05 else '≥'} 0,05). "
            f"**Comparação:** H₀ {verdade} na população; classificação: "
            f"**{resultado['classificacao']}**."
        )
        st.write(resultado["conclusao"])
        st.plotly_chart(
            _figura_distribuicao(resultado),
            key=f"{resultado['codigo']}_distribuicao",
        )
        st.markdown("**Condições de aplicação**")
        for condicao in resultado["condicoes"]:
            estado = "Atendida" if condicao["atendida"] else "Não atendida"
            st.markdown(
                f"- **{estado} — {condicao['nome']}:** {condicao['detalhe']}"
            )

    st.divider()
    st.subheader("Variabilidade entre amostras")
    st.write(
        "A simulação considera 1.000 amostras aleatórias simples de 384 nascimentos, "
        "sem reposição. Ela não altera a amostra oficial, sorteada uma única vez."
    )
    linhas = []
    for resultado in resultados:
        dados = simulacao[resultado["codigo"]]
        linhas.append(
            {
                "Hipótese": resultado["codigo"],
                "ICs que contêm o parâmetro real": formatar_percentual(
                    dados["cobertura_ic"], 1
                ),
                "Amostras que rejeitam H₀": formatar_percentual(
                    dados["taxa_rejeicao"], 1
                ),
            }
        )
    st.dataframe(linhas, hide_index=True)
    st.caption(
        "A cobertura observada aproxima o nível nominal de 95%. A proporção de "
        "rejeições estima o poder empírico para os parâmetros desta população."
    )
    with st.expander("Limitações e interpretação"):
        st.markdown(
            "- Os testes descrevem associações e diferenças; não demonstram causalidade.\n"
            "- A população agrega 11 anos e pode esconder tendências temporais.\n"
            "- Os dados administrativos podem conter erros e informações ausentes.\n"
            "- A simulação ilustra a variabilidade neste contexto específico."
        )


def _figura_distribuicao(resultado: dict[str, Any]) -> go.Figure:
    graus = resultado["graus_liberdade"]
    distribuicao = (
        stats.norm
        if resultado["distribuicao"] == "normal"
        else stats.t(float(graus))
    )
    alpha = 0.05
    valor_critico = (
        stats.norm.ppf(1 - alpha)
        if resultado["codigo"] == "H1"
        else distribuicao.ppf(1 - alpha / 2)
    )
    limite = max(
        4.0,
        abs(resultado["estatistica"]) + 1,
        float(valor_critico) + 0.5,
    )
    x = np.linspace(-limite, limite, 500)
    y = distribuicao.pdf(x)
    fig = go.Figure()
    fig.add_scatter(
        x=x,
        y=y,
        mode="lines",
        name="Distribuição de referência",
        line={"color": COR_POPULACAO, "width": 2},
    )
    rejeicoes = [(float(valor_critico), x >= valor_critico)]
    if resultado["codigo"] != "H1":
        rejeicoes.insert(0, (-float(valor_critico), x <= -valor_critico))
    for indice, (critico, mascara) in enumerate(rejeicoes):
        fig.add_scatter(
            x=x[mascara],
            y=y[mascara],
            mode="lines",
            fill="tozeroy",
            name="Região de rejeição (α = 5%)" if indice == 0 else None,
            showlegend=indice == 0,
            line={"color": COR_AMOSTRA},
            fillcolor="rgba(213, 94, 0, 0.25)",
        )
        fig.add_vline(
            x=critico,
            line_dash="dash",
            line_color=COR_AMOSTRA,
            annotation_text=f"Crítico = {formatar_numero(critico, 3)}",
        )
    fig.add_vline(
        x=resultado["estatistica"],
        line_color="#111111",
        line_width=2,
        annotation_text=(
            f"Estatística = {formatar_numero(resultado['estatistica'], 3)}"
        ),
        annotation_position="top",
    )
    fig.update_layout(
        title="Distribuição de referência e região de rejeição",
        xaxis_title="Estatística de teste",
        yaxis_title="Densidade",
        legend={"orientation": "h"},
        height=360,
    )
    return fig
