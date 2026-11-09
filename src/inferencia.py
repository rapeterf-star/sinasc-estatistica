from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import (
    confint_proportions_2indep,
    proportion_confint,
    proportions_ztest,
)


ALPHA = 0.05
N_SIMULACOES = 1_000
SEMENTE_SIMULACAO = 2030
H0_H1 = 0.50
MU0_H3 = 3_200.0
PREMATURO_CATEGORIAS = {
    "MENOS DE 22 SEM",
    "DE 22 A 27 SEM",
    "DE 28 A 31 SEM",
    "DE 32 A 36 SEM",
}


@dataclass(frozen=True)
class Condicao:
    nome: str
    atendida: bool
    detalhe: str


@dataclass(frozen=True)
class ResultadoTeste:
    codigo: str
    pergunta: str
    variavel: str
    hipotese_nula: str
    hipotese_alternativa: str
    procedimento: str
    estimativa: float
    parametro_populacional: float
    intervalo: tuple[float, float]
    intervalo_unilateral_inferior: float | None
    estatistica: float
    distribuicao: str
    graus_liberdade: float | None
    valor_p: float
    rejeita_h0: bool
    h0_verdadeira_na_populacao: bool
    contem_parametro: bool
    classificacao: str
    conclusao: str
    condicoes: tuple[Condicao, ...]
    tamanho_grupos: tuple[int, ...]
    desvio_grupos: tuple[float, ...]


def _verificar_colunas(df: pd.DataFrame, colunas: set[str], nome: str) -> None:
    ausentes = sorted(colunas.difference(df.columns))
    if ausentes:
        raise ValueError(f"{nome} não contém as colunas necessárias: {ausentes}")


def _resumo_h0(
    *,
    codigo: str,
    estimativa: float,
    parametro_populacional: float,
    rejeita_h0: bool,
    diferenca: bool = False,
) -> tuple[bool, str]:
    if diferenca:
        h0_verdadeira = bool(np.isclose(parametro_populacional, 0, atol=1e-12))
    elif codigo == "H1":
        h0_verdadeira = parametro_populacional <= H0_H1
    else:
        h0_verdadeira = bool(
            np.isclose(parametro_populacional, MU0_H3, atol=1e-12)
        )
    if rejeita_h0 and h0_verdadeira:
        classificacao = "Erro tipo I"
    elif not rejeita_h0 and not h0_verdadeira:
        classificacao = "Erro tipo II"
    elif rejeita_h0:
        classificacao = "Rejeição correta de H₀"
    else:
        classificacao = "Não rejeição correta de H₀"
    return h0_verdadeira, classificacao


def _classificar_e_concluir(
    *,
    codigo: str,
    pergunta: str,
    estimativa: float,
    parametro_populacional: float,
    rejeita_h0: bool,
    diferenca: bool = False,
) -> tuple[bool, str, str]:
    h0_verdadeira, classificacao = _resumo_h0(
        codigo=codigo,
        estimativa=estimativa,
        parametro_populacional=parametro_populacional,
        rejeita_h0=rejeita_h0,
        diferenca=diferenca,
    )
    decisao = "Rejeitamos" if rejeita_h0 else "Não rejeitamos"
    if codigo == "H1":
        texto = (
            f"{decisao} H₀; a amostra "
            f"{'fornece' if rejeita_h0 else 'não fornece'} evidência, a 5%, "
            "de que a proporção de cesáreas supera 50%."
        )
    elif codigo == "H2":
        texto = (
            f"{decisao} H₀; a amostra "
            f"{'indica' if rejeita_h0 else 'não indica'} diferença na proporção "
            "de cesáreas entre os grupos de escolaridade."
        )
    elif codigo == "H3":
        texto = (
            f"{decisao} H₀; a amostra "
            f"{'indica' if rejeita_h0 else 'não indica'} que o peso médio difere "
            "de 3.200 g."
        )
    else:
        texto = (
            f"{decisao} H₀; a amostra "
            f"{'indica' if rejeita_h0 else 'não indica'} diferença no peso médio "
            "entre os grupos de consultas pré-natais."
        )
    return h0_verdadeira, classificacao, texto


def _condicao_aas(n: int, n_populacao: int) -> Condicao:
    fracao = n / n_populacao
    return Condicao(
        "Independência e regra dos 10%",
        fracao < 0.10,
        f"AAS sem reposição; n/N = {_decimal_br(fracao * 100, 3)}%, abaixo de 10%.",
    )


def _decimal_br(valor: float, casas: int) -> str:
    """Número com vírgula decimal e ponto de milhar, como no restante do app."""
    return f"{valor:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def teste_h1(
    amostra: pd.DataFrame, populacao: pd.DataFrame
) -> ResultadoTeste:
    _verificar_colunas(amostra, {"cesarea"}, "A amostra")
    _verificar_colunas(populacao, {"cesarea"}, "A população")
    sucesso = int(amostra["cesarea"].sum())
    n = len(amostra)
    if n == 0:
        raise ValueError("A amostra está vazia.")
    estimativa = sucesso / n
    parametro = float(populacao["cesarea"].mean())
    estatistica, valor_p = proportions_ztest(
        count=sucesso,
        nobs=n,
        value=H0_H1,
        alternative="larger",
        prop_var=H0_H1,
    )
    erro_ic = np.sqrt(estimativa * (1 - estimativa) / n)
    z_bilateral = stats.norm.ppf(1 - ALPHA / 2)
    z_unilateral = stats.norm.ppf(1 - ALPHA)
    intervalo = (
        float(estimativa - z_bilateral * erro_ic),
        float(estimativa + z_bilateral * erro_ic),
    )
    limite_inferior = float(estimativa - z_unilateral * erro_ic)
    rejeita = bool(valor_p < ALPHA)
    h0_verdadeira, classificacao, conclusao = _classificar_e_concluir(
        codigo="H1",
        pergunta="A proporção de cesáreas supera 50%?",
        estimativa=estimativa,
        parametro_populacional=parametro,
        rejeita_h0=rejeita,
    )
    esperados = [n * H0_H1, n * (1 - H0_H1)]
    condicoes = (
        _condicao_aas(n, len(populacao)),
        Condicao(
            "Sucessos e fracassos esperados ≥ 10",
            min(esperados) >= 10,
            f"Em H₀: {esperados[0]:.0f} sucessos e {esperados[1]:.0f} fracassos esperados.",
        ),
    )
    return ResultadoTeste(
        codigo="H1",
        pergunta="A cesárea já é maioria dos partos em Porto Alegre?",
        variavel="Proporção de cesáreas",
        hipotese_nula="π = 0,50",
        hipotese_alternativa="π > 0,50",
        procedimento="Teste Z unilateral de 1 proporção; IC de Wald",
        estimativa=float(estimativa),
        parametro_populacional=parametro,
        intervalo=intervalo,
        intervalo_unilateral_inferior=limite_inferior,
        estatistica=float(estatistica),
        distribuicao="normal",
        graus_liberdade=None,
        valor_p=float(valor_p),
        rejeita_h0=rejeita,
        h0_verdadeira_na_populacao=h0_verdadeira,
        contem_parametro=intervalo[0] <= parametro <= intervalo[1],
        classificacao=classificacao,
        conclusao=conclusao,
        condicoes=condicoes,
        tamanho_grupos=(n,),
        desvio_grupos=(),
    )


def teste_h2(
    amostra: pd.DataFrame, populacao: pd.DataFrame
) -> ResultadoTeste:
    colunas = {"cesarea", "escol_12mais"}
    _verificar_colunas(amostra, colunas, "A amostra")
    _verificar_colunas(populacao, colunas, "A população")
    grupos = [
        amostra.loc[amostra["escol_12mais"].eq(1), "cesarea"],
        amostra.loc[amostra["escol_12mais"].eq(0), "cesarea"],
    ]
    n1, n2 = (len(grupo) for grupo in grupos)
    if n1 == 0 or n2 == 0:
        raise ValueError("A amostra precisa ter observações nos dois grupos da H2.")
    sucessos = [int(grupo.sum()) for grupo in grupos]
    proporcoes = [sucesso / n for sucesso, n in zip(sucessos, (n1, n2))]
    estimativa = proporcoes[0] - proporcoes[1]
    populacao_grupos = [
        populacao.loc[populacao["escol_12mais"].eq(1), "cesarea"],
        populacao.loc[populacao["escol_12mais"].eq(0), "cesarea"],
    ]
    parametro = float(populacao_grupos[0].mean() - populacao_grupos[1].mean())
    estatistica, valor_p = proportions_ztest(
        count=sucessos,
        nobs=[n1, n2],
        value=0,
        alternative="two-sided",
    )
    erro_ic = np.sqrt(
        proporcoes[0] * (1 - proporcoes[0]) / n1
        + proporcoes[1] * (1 - proporcoes[1]) / n2
    )
    z_critico = stats.norm.ppf(1 - ALPHA / 2)
    intervalo = (
        float(estimativa - z_critico * erro_ic),
        float(estimativa + z_critico * erro_ic),
    )
    rejeita = bool(valor_p < ALPHA)
    h0_verdadeira, classificacao, conclusao = _classificar_e_concluir(
        codigo="H2",
        pergunta="A taxa de cesárea difere conforme a escolaridade da mãe?",
        estimativa=estimativa,
        parametro_populacional=parametro,
        rejeita_h0=rejeita,
        diferenca=True,
    )
    celulas = [
        sucessos[0],
        n1 - sucessos[0],
        sucessos[1],
        n2 - sucessos[1],
    ]
    condicoes = (
        _condicao_aas(len(amostra), len(populacao)),
        Condicao(
            "Sucessos e fracassos ≥ 10 em cada grupo",
            min(celulas) >= 10,
            f"12 anos ou mais: {celulas[0]} cesáreas e {celulas[1]} outros partos; "
            f"demais escolaridades: {celulas[2]} cesáreas e {celulas[3]} outros partos.",
        ),
    )
    return ResultadoTeste(
        codigo="H2",
        pergunta="A taxa de cesárea difere conforme a escolaridade da mãe?",
        variavel="Diferença de proporções de cesárea (12 anos ou mais − demais)",
        hipotese_nula="π₁ − π₂ = 0",
        hipotese_alternativa="π₁ − π₂ ≠ 0",
        procedimento="Teste Z bilateral de 2 proporções (P agrupada); IC não agrupado",
        estimativa=float(estimativa),
        parametro_populacional=parametro,
        intervalo=intervalo,
        intervalo_unilateral_inferior=None,
        estatistica=float(estatistica),
        distribuicao="normal",
        graus_liberdade=None,
        valor_p=float(valor_p),
        rejeita_h0=rejeita,
        h0_verdadeira_na_populacao=h0_verdadeira,
        contem_parametro=intervalo[0] <= parametro <= intervalo[1],
        classificacao=classificacao,
        conclusao=conclusao,
        condicoes=condicoes,
        tamanho_grupos=(n1, n2),
        desvio_grupos=(),
    )


def teste_h3(
    amostra: pd.DataFrame, populacao: pd.DataFrame
) -> ResultadoTeste:
    _verificar_colunas(amostra, {"peso"}, "A amostra")
    _verificar_colunas(populacao, {"peso"}, "A população")
    pesos = amostra["peso"].dropna().astype(float)
    n = len(pesos)
    if n < 2:
        raise ValueError("São necessárias ao menos duas observações válidas na H3.")
    estimativa = float(pesos.mean())
    desvio = float(pesos.std(ddof=1))
    erro = desvio / np.sqrt(n)
    gl = float(n - 1)
    critico = stats.t.ppf(1 - ALPHA / 2, gl)
    intervalo = (
        float(estimativa - critico * erro),
        float(estimativa + critico * erro),
    )
    teste = stats.ttest_1samp(pesos, popmean=MU0_H3, alternative="two-sided")
    parametro = float(populacao["peso"].mean())
    rejeita = bool(teste.pvalue < ALPHA)
    h0_verdadeira, classificacao, conclusao = _classificar_e_concluir(
        codigo="H3",
        pergunta="O peso médio ao nascer difere de 3.200 g?",
        estimativa=estimativa,
        parametro_populacional=parametro,
        rejeita_h0=rejeita,
    )
    condicoes = (
        _condicao_aas(n, len(populacao)),
        Condicao(
            "Tamanho amostral para o TCL",
            n > 30,
            f"n = {n}; n > 30 permite a aproximação da distribuição da média amostral.",
        ),
    )
    return ResultadoTeste(
        codigo="H3",
        pergunta="O peso médio ao nascer difere de 3.200 g?",
        variavel="Peso ao nascer (g)",
        hipotese_nula="μ = 3.200 g",
        hipotese_alternativa="μ ≠ 3.200 g",
        procedimento="Teste t bilateral de 1 amostra; IC t",
        estimativa=estimativa,
        parametro_populacional=parametro,
        intervalo=intervalo,
        intervalo_unilateral_inferior=None,
        estatistica=float(teste.statistic),
        distribuicao="t",
        graus_liberdade=gl,
        valor_p=float(teste.pvalue),
        rejeita_h0=rejeita,
        h0_verdadeira_na_populacao=h0_verdadeira,
        contem_parametro=intervalo[0] <= parametro <= intervalo[1],
        classificacao=classificacao,
        conclusao=conclusao,
        condicoes=condicoes,
        tamanho_grupos=(n,),
        desvio_grupos=(desvio,),
    )


def _welch(
    grupo1: pd.Series, grupo2: pd.Series
) -> tuple[float, float, float, float, float, float]:
    x1 = grupo1.dropna().astype(float).to_numpy()
    x2 = grupo2.dropna().astype(float).to_numpy()
    n1, n2 = len(x1), len(x2)
    if n1 < 2 or n2 < 2:
        raise ValueError("São necessárias ao menos duas observações em cada grupo da H4.")
    var1, var2 = float(np.var(x1, ddof=1)), float(np.var(x2, ddof=1))
    erro = np.sqrt(var1 / n1 + var2 / n2)
    if erro == 0:
        raise ValueError("Não é possível calcular o teste de Welch com erro-padrão zero.")
    gl = (var1 / n1 + var2 / n2) ** 2 / (
        (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
    )
    diferenca = float(np.mean(x1) - np.mean(x2))
    estatistica = diferenca / erro
    return diferenca, erro, float(gl), float(estatistica), float(var1**0.5), float(var2**0.5)


def teste_h4(
    amostra: pd.DataFrame, populacao: pd.DataFrame
) -> ResultadoTeste:
    colunas = {"peso", "prenatal_7mais"}
    _verificar_colunas(amostra, colunas, "A amostra")
    _verificar_colunas(populacao, colunas, "A população")
    grupos = [
        amostra.loc[amostra["prenatal_7mais"].eq(1), "peso"],
        amostra.loc[amostra["prenatal_7mais"].eq(0), "peso"],
    ]
    diferenca, erro, gl, estatistica, desvio1, desvio2 = _welch(*grupos)
    teste = stats.ttest_ind(
        grupos[0].dropna(),
        grupos[1].dropna(),
        equal_var=False,
        alternative="two-sided",
    )
    critico = stats.t.ppf(1 - ALPHA / 2, gl)
    intervalo = (
        float(diferenca - critico * erro),
        float(diferenca + critico * erro),
    )
    pop_grupos = [
        populacao.loc[populacao["prenatal_7mais"].eq(1), "peso"],
        populacao.loc[populacao["prenatal_7mais"].eq(0), "peso"],
    ]
    parametro = float(pop_grupos[0].mean() - pop_grupos[1].mean())
    n1 = int(grupos[0].notna().sum())
    n2 = int(grupos[1].notna().sum())
    rejeita = bool(teste.pvalue < ALPHA)
    h0_verdadeira, classificacao, conclusao = _classificar_e_concluir(
        codigo="H4",
        pergunta=(
            "O peso médio difere entre mães com 7 ou mais consultas pré-natais "
            "e as demais?"
        ),
        estimativa=diferenca,
        parametro_populacional=parametro,
        rejeita_h0=rejeita,
        diferenca=True,
    )
    condicoes = (
        _condicao_aas(len(amostra), len(populacao)),
        Condicao(
            "Tamanho de cada grupo para o TCL",
            n1 > 30 and n2 > 30,
            f"7 ou mais consultas: n = {n1}; demais: n = {n2}. Ambos devem ser > 30.",
        ),
        Condicao(
            "Variâncias iguais",
            True,
            f"Não é exigida: foi usado Welch. Desvios-padrão amostrais: "
            f"{_decimal_br(desvio1, 1)} g e {_decimal_br(desvio2, 1)} g.",
        ),
    )
    return ResultadoTeste(
        codigo="H4",
        pergunta=(
            "O peso médio difere entre mães com 7 ou mais consultas pré-natais "
            "e as demais?"
        ),
        variavel="Diferença de médias do peso (7 ou mais − demais consultas)",
        hipotese_nula="μ₁ − μ₂ = 0",
        hipotese_alternativa="μ₁ − μ₂ ≠ 0",
        procedimento="Teste t bilateral de Welch; IC t com graus de liberdade de Welch",
        estimativa=diferenca,
        parametro_populacional=parametro,
        intervalo=intervalo,
        intervalo_unilateral_inferior=None,
        estatistica=float(teste.statistic),
        distribuicao="t",
        graus_liberdade=gl,
        valor_p=float(teste.pvalue),
        rejeita_h0=rejeita,
        h0_verdadeira_na_populacao=h0_verdadeira,
        contem_parametro=intervalo[0] <= parametro <= intervalo[1],
        classificacao=classificacao,
        conclusao=conclusao,
        condicoes=condicoes,
        tamanho_grupos=(n1, n2),
        desvio_grupos=(desvio1, desvio2),
    )


def executar_inferencia(
    amostra: pd.DataFrame, populacao: pd.DataFrame
) -> list[ResultadoTeste]:
    return [
        teste_h1(amostra, populacao),
        teste_h2(amostra, populacao),
        teste_h3(amostra, populacao),
        teste_h4(amostra, populacao),
    ]


def simular_variabilidade(
    populacao: pd.DataFrame,
    n_simulacoes: int = N_SIMULACOES,
    semente: int = SEMENTE_SIMULACAO,
) -> dict[str, dict[str, float]]:
    colunas = {"peso", "cesarea", "escol_12mais", "prenatal_7mais"}
    _verificar_colunas(populacao, colunas, "A população")
    if n_simulacoes < 1:
        raise ValueError("O número de simulações deve ser maior que zero.")

    pesos = populacao["peso"].to_numpy(dtype=float)
    cesareas = populacao["cesarea"].to_numpy(dtype=np.int8)
    escolaridade = populacao["escol_12mais"].to_numpy(dtype=np.int8)
    prenatal = populacao["prenatal_7mais"].to_numpy(dtype=np.int8)
    n_pop = len(populacao)
    if n_pop < 384:
        raise ValueError(
            f"A população tem {n_pop} registros; são necessários ao menos 384 "
            "para simular o tamanho amostral planejado."
        )
    n = 384
    verdade_h1 = float(cesareas.mean())
    grupos_h2 = [escolaridade == 1, escolaridade == 0]
    verdade_h2 = float(
        cesareas[grupos_h2[0]].mean() - cesareas[grupos_h2[1]].mean()
    )
    verdade_h3 = float(pesos.mean())
    grupos_h4 = [prenatal == 1, prenatal == 0]
    verdade_h4 = float(
        pesos[grupos_h4[0]].mean() - pesos[grupos_h4[1]].mean()
    )

    coberturas = {codigo: 0 for codigo in ("H1", "H2", "H3", "H4")}
    rejeicoes = {codigo: 0 for codigo in ("H1", "H2", "H3", "H4")}
    rng = np.random.default_rng(semente)
    z_bilateral = stats.norm.ppf(1 - ALPHA / 2)
    z_unilateral = stats.norm.ppf(1 - ALPHA)
    z_h1_critico = stats.norm.ppf(1 - ALPHA)
    z_h2_critico = stats.norm.ppf(1 - ALPHA / 2)

    for indices in (
        rng.choice(n_pop, size=n, replace=False) for _ in range(n_simulacoes)
    ):
        ces_sample = cesareas[indices]
        escol_sample = escolaridade[indices]
        prenatal_sample = prenatal[indices]
        peso_sample = pesos[indices]

        phat = float(ces_sample.mean())
        erro_ci1 = np.sqrt(phat * (1 - phat) / n)
        ic_h1 = (phat - z_bilateral * erro_ci1, phat + z_bilateral * erro_ci1)
        coberturas["H1"] += int(ic_h1[0] <= verdade_h1 <= ic_h1[1])
        erro_teste1 = np.sqrt(H0_H1 * (1 - H0_H1) / n)
        z_h1 = (phat - H0_H1) / erro_teste1
        rejeicoes["H1"] += int(z_h1 > z_h1_critico)

        mascara1, mascara2 = escol_sample == 1, escol_sample == 0
        n1, n2 = int(mascara1.sum()), int(mascara2.sum())
        s1, s2 = int(ces_sample[mascara1].sum()), int(ces_sample[mascara2].sum())
        if n1 and n2:
            p1, p2 = s1 / n1, s2 / n2
            dif_h2 = p1 - p2
            erro_ci2 = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
            ic_h2 = (
                dif_h2 - z_bilateral * erro_ci2,
                dif_h2 + z_bilateral * erro_ci2,
            )
            coberturas["H2"] += int(ic_h2[0] <= verdade_h2 <= ic_h2[1])
            p_pool = (s1 + s2) / (n1 + n2)
            erro_teste2 = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
            z_h2 = (p1 - p2) / erro_teste2
            rejeicoes["H2"] += int(abs(z_h2) > z_h2_critico)

        media3 = float(peso_sample.mean())
        sd3 = float(peso_sample.std(ddof=1))
        gl3 = n - 1
        erro3 = sd3 / np.sqrt(n)
        tcrit3 = stats.t.ppf(1 - ALPHA / 2, gl3)
        ic_h3 = (media3 - tcrit3 * erro3, media3 + tcrit3 * erro3)
        coberturas["H3"] += int(ic_h3[0] <= verdade_h3 <= ic_h3[1])
        t_h3 = (media3 - MU0_H3) / erro3
        rejeicoes["H3"] += int(abs(t_h3) > tcrit3)

        g1 = peso_sample[prenatal_sample == 1]
        g2 = peso_sample[prenatal_sample == 0]
        if len(g1) > 1 and len(g2) > 1:
            n1h, n2h = len(g1), len(g2)
            var1, var2 = float(g1.var(ddof=1)), float(g2.var(ddof=1))
            erro4 = np.sqrt(var1 / n1h + var2 / n2h)
            gl4 = (var1 / n1h + var2 / n2h) ** 2 / (
                (var1 / n1h) ** 2 / (n1h - 1)
                + (var2 / n2h) ** 2 / (n2h - 1)
            )
            dif_h4 = float(g1.mean() - g2.mean())
            tcrit4 = stats.t.ppf(1 - ALPHA / 2, gl4)
            ic_h4 = (
                dif_h4 - tcrit4 * erro4,
                dif_h4 + tcrit4 * erro4,
            )
            coberturas["H4"] += int(ic_h4[0] <= verdade_h4 <= ic_h4[1])
            t_h4 = dif_h4 / erro4
            rejeicoes["H4"] += int(abs(t_h4) > tcrit4)

    return {
        codigo: {
            "cobertura_ic": coberturas[codigo] / n_simulacoes,
            "taxa_rejeicao": rejeicoes[codigo] / n_simulacoes,
            "n_simulacoes": float(n_simulacoes),
        }
        for codigo in ("H1", "H2", "H3", "H4")
    }


def conferir_com_statsmodels(
    amostra: pd.DataFrame, populacao: pd.DataFrame
) -> dict[str, dict[str, float]]:
    from statsmodels.stats.weightstats import CompareMeans, DescrStatsW

    resultados = executar_inferencia(amostra, populacao)
    por_codigo = {resultado.codigo: resultado for resultado in resultados}

    h1 = por_codigo["H1"]
    h1_z, h1_p = proportions_ztest(
        int(amostra["cesarea"].sum()),
        len(amostra),
        value=H0_H1,
        alternative="larger",
        prop_var=H0_H1,
    )
    h1_ci = proportion_confint(
        int(amostra["cesarea"].sum()),
        len(amostra),
        alpha=ALPHA,
        method="normal",
    )

    h2 = por_codigo["H2"]
    h2_grupos = [
        amostra.loc[amostra["escol_12mais"].eq(valor), "cesarea"]
        for valor in (1, 0)
    ]
    h2_counts = [int(grupo.sum()) for grupo in h2_grupos]
    h2_ns = [len(grupo) for grupo in h2_grupos]
    h2_z, h2_p = proportions_ztest(
        h2_counts, h2_ns, value=0, alternative="two-sided"
    )
    h2_ci = confint_proportions_2indep(
        h2_counts[0],
        h2_ns[0],
        h2_counts[1],
        h2_ns[1],
        compare="diff",
        alpha=ALPHA,
        method="wald",
    )

    h3 = por_codigo["H3"]
    h3_stats = DescrStatsW(amostra["peso"].dropna())
    h3_ci = h3_stats.tconfint_mean(alpha=ALPHA)
    h3_test, h3_p, _ = h3_stats.ttest_mean(
        value=MU0_H3,
        alternative="two-sided",
    )

    h4 = por_codigo["H4"]
    h4_grupos = [
        amostra.loc[amostra["prenatal_7mais"].eq(valor), "peso"].dropna()
        for valor in (1, 0)
    ]
    h4_stats = CompareMeans(
        DescrStatsW(h4_grupos[0]), DescrStatsW(h4_grupos[1])
    )
    h4_ci = h4_stats.tconfint_diff(alpha=ALPHA, usevar="unequal")
    h4_test, h4_p, _ = h4_stats.ttest_ind(
        alternative="two-sided", usevar="unequal"
    )

    comparacoes = {
        "H1": {
            "z_diferenca": float(h1.estatistica - h1_z),
            "p_diferenca": float(h1.valor_p - h1_p),
            "ic_inferior_diferenca": float(h1.intervalo[0] - h1_ci[0]),
            "ic_superior_diferenca": float(h1.intervalo[1] - h1_ci[1]),
        },
        "H2": {
            "z_diferenca": float(h2.estatistica - h2_z),
            "p_diferenca": float(h2.valor_p - h2_p),
            "ic_inferior_diferenca": float(h2.intervalo[0] - h2_ci[0]),
            "ic_superior_diferenca": float(h2.intervalo[1] - h2_ci[1]),
        },
        "H3": {
            "t_diferenca": float(h3.estatistica - h3_test),
            "p_diferenca": float(h3.valor_p - h3_p),
            "ic_inferior_diferenca": float(h3.intervalo[0] - h3_ci[0]),
            "ic_superior_diferenca": float(h3.intervalo[1] - h3_ci[1]),
        },
        "H4": {
            "t_diferenca": float(h4.estatistica - h4_test),
            "p_diferenca": float(h4.valor_p - h4_p),
            "ic_inferior_diferenca": float(h4.intervalo[0] - h4_ci[0]),
            "ic_superior_diferenca": float(h4.intervalo[1] - h4_ci[1]),
        },
    }
    return comparacoes
