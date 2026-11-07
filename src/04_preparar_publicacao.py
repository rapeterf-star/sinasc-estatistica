import json
from dataclasses import asdict
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.inferencia import N_SIMULACOES, executar_inferencia, simular_variabilidade
from src.publicacao import (
    ARQUIVO_PUBLICO,
    N_MINIMO_EXIBICAO,
    ORDEM_CATEGORIAS,
    VARIAVEIS_QUALITATIVAS,
    VARIAVEIS_QUANTITATIVAS,
)


ROOT = Path(__file__).resolve().parents[1]
POPULACAO_PATH = ROOT / "data" / "populacao.parquet"
AMOSTRA_PATH = ROOT / "data" / "amostra.csv"


def _ler_dados() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not POPULACAO_PATH.exists():
        raise FileNotFoundError(f"Arquivo de população não encontrado: {POPULACAO_PATH}")
    if not AMOSTRA_PATH.exists():
        raise FileNotFoundError(f"Arquivo de amostra não encontrado: {AMOSTRA_PATH}")
    populacao = pd.read_parquet(POPULACAO_PATH)
    amostra = pd.read_csv(AMOSTRA_PATH)
    if len(populacao) != 197_639 or len(amostra) != 384:
        raise ValueError(
            "Os dados não correspondem à população limpa e à amostra oficial "
            "documentadas no plano."
        )
    return populacao, amostra


def _normalizar_categorias(serie: pd.Series) -> pd.Series:
    categorias = serie.astype("string").str.strip()
    return categorias.fillna("").replace("", "(Não informado)")


def _distribuicao_categorica(
    serie: pd.Series, coluna: str
) -> list[dict[str, Any]]:
    dados = _normalizar_categorias(serie)
    contagens = dados.value_counts(dropna=False).to_dict()
    ordem = {
        valor: indice
        for indice, valor in enumerate(ORDEM_CATEGORIAS.get(coluna, []))
    }
    categorias = sorted(
        contagens,
        key=lambda categoria: (ordem.get(categoria, 999), categoria),
    )
    divulgaveis: list[dict[str, Any]] = []
    suprimidas = 0
    for categoria in categorias:
        frequencia = int(contagens[categoria])
        if frequencia < N_MINIMO_EXIBICAO:
            suprimidas += frequencia
            continue
        divulgaveis.append(
            {
                "categoria": categoria,
                "frequencia": frequencia,
                "proporcao": frequencia / len(dados),
            }
        )
    if suprimidas:
        divulgar_total = suprimidas >= N_MINIMO_EXIBICAO
        divulgaveis.append(
            {
                "categoria": "Categorias de baixa frequência agrupadas",
                "frequencia": suprimidas if divulgar_total else None,
                "proporcao": suprimidas / len(dados) if divulgar_total else None,
            }
        )
    return divulgaveis


def _histograma(
    serie: pd.Series, edges: np.ndarray
) -> dict[str, Any]:
    dados = pd.to_numeric(serie, errors="coerce").dropna().to_numpy(dtype=float)
    contagens, _ = np.histogram(dados, bins=edges)
    bins: list[tuple[float, float, int]] = []
    inicio = float(edges[0])
    acumulada = 0
    for indice, contagem in enumerate(contagens):
        acumulada += int(contagem)
        fim = float(edges[indice + 1])
        if acumulada >= N_MINIMO_EXIBICAO:
            bins.append((inicio, fim, acumulada))
            inicio = fim
            acumulada = 0
    if acumulada:
        if bins:
            inferior, _, frequencia = bins[-1]
            bins[-1] = (inferior, float(edges[-1]), frequencia + acumulada)
        else:
            bins.append((float(edges[0]), float(edges[-1]), acumulada))

    inferiores = [bin_[0] for bin_ in bins]
    superiores = [bin_[1] for bin_ in bins]
    frequencias = [bin_[2] for bin_ in bins]
    larguras = [superior - inferior for inferior, superior, _ in bins]
    centros = [
        (inferior + superior) / 2 for inferior, superior, _ in bins
    ]
    densidades = [
        frequencia / (len(dados) * largura)
        for frequencia, largura in zip(frequencias, larguras)
    ]
    media = float(np.mean(dados))
    mediana = float(np.median(dados))
    return {
        "limites_inferiores": inferiores,
        "limites_superiores": superiores,
        "centros": centros,
        "larguras": larguras,
        "contagens": frequencias,
        "densidade": densidades,
        "linhas_referencia": [
            (media, "Média", "#2457a7", "solid"),
            (mediana, "Mediana", "#d62728", "dash"),
        ],
    }


def _estatisticas(serie: pd.Series, ddof: int) -> dict[str, Any]:
    dados = pd.to_numeric(serie, errors="coerce").dropna()
    if dados.empty:
        raise ValueError("Não há observações para calcular estatísticas.")
    moda = dados.mode()
    media = float(dados.mean())
    desvio = float(dados.std(ddof=ddof))
    q1 = float(dados.quantile(0.25))
    q3 = float(dados.quantile(0.75))
    iqr = q3 - q1
    modas = ", ".join(f"{valor:g}" for valor in moda)
    return {
        "n": int(len(dados)),
        "media": media,
        "mediana": float(dados.median()),
        "moda": modas,
        "desvio_padrao": desvio,
        "variancia": float(dados.var(ddof=ddof)),
        "cv": float(desvio / media * 100) if media else None,
        "minimo": float(dados.min()),
        "q1": q1,
        "q3": q3,
        "maximo": float(dados.max()),
        "amplitude": float(dados.max() - dados.min()),
        "iqr": iqr,
        "assimetria": float(dados.skew()),
    }


def _caixa(serie: pd.Series) -> dict[str, float | int]:
    dados = pd.to_numeric(serie, errors="coerce").dropna()
    q1 = float(dados.quantile(0.25))
    mediana = float(dados.median())
    q3 = float(dados.quantile(0.75))
    iqr = q3 - q1
    dentro = dados.loc[dados.ge(q1 - 1.5 * iqr) & dados.le(q3 + 1.5 * iqr)]
    return {
        "n": int(len(dados)),
        "q1": q1,
        "mediana": mediana,
        "q3": q3,
        "limite_inferior": float(dentro.min()),
        "limite_superior": float(dentro.max()),
    }


def _qq_peso(serie: pd.Series) -> dict[str, Any]:
    dados = serie.dropna().to_numpy(dtype=float)
    n_grupos = len(dados) // N_MINIMO_EXIBICAO
    if n_grupos == 0:
        raise ValueError("São necessárias ao menos 10 observações para o Q-Q plot.")
    probabilidades = (
        np.array([0.5])
        if n_grupos == 1
        else (np.arange(n_grupos) + 0.5) / n_grupos
    )
    quantis = np.quantile(dados, probabilidades)
    teoricos = stats.norm.ppf(probabilidades)
    if len(teoricos) > 1:
        inclinacao, intercepto = np.polyfit(teoricos, quantis, 1)
    else:
        inclinacao, intercepto = 0.0, float(quantis[0])
    tamanho_grupo = len(dados) // len(probabilidades)
    return {
        "inclinacao": float(inclinacao),
        "intercepto": float(intercepto),
        "pontos": [
            {
                "teorico": float(teorico),
                "observado": float(observado),
                "n_aproximado": tamanho_grupo,
            }
            for teorico, observado in zip(teoricos, quantis)
        ],
    }


def _indicadores(df: pd.DataFrame, ddof: int) -> dict[str, float]:
    return {
        "peso_medio": float(df["peso"].mean()),
        "peso_mediano": float(df["peso"].median()),
        "peso_dp": float(df["peso"].std(ddof=ddof)),
        "cesarea": float(df["cesarea"].mean()),
        "baixo_peso": float(df["baixo_peso"].mean()),
        "prematuro": float(df["prematuro"].mean()),
        "idade_media": float(df["idade_mae"].mean()),
    }


def _resumo_por_ano(
    df: pd.DataFrame,
    edges: dict[str, np.ndarray],
    ddof: int,
) -> dict[str, Any]:
    total = _resumir_conjunto(df, edges, ddof)
    por_ano = {
        str(int(ano)): _resumir_conjunto(grupo, edges, ddof)
        for ano, grupo in df.groupby("ano", sort=True)
    }
    return {"total": total, "por_ano": por_ano}


def _resumir_conjunto(
    df: pd.DataFrame, edges: dict[str, np.ndarray], ddof: int
) -> dict[str, Any]:
    histogramas = {}
    boxplots = {}
    estatisticas = {}
    for coluna in VARIAVEIS_QUANTITATIVAS:
        serie = df[coluna]
        histogramas[coluna] = _histograma(serie, edges[coluna])
        boxplots[coluna] = _caixa(serie)
        estatisticas[coluna] = _estatisticas(serie, ddof)

    categorias = {
        coluna: _distribuicao_categorica(df[coluna], coluna)
        for coluna in VARIAVEIS_QUALITATIVAS
    }

    escolaridade = []
    grupos_escolaridade = (
        ("12 anos ou mais", df["escol_12mais"].eq(1)),
        ("Demais escolaridades", df["escol_12mais"].eq(0)),
    )
    for grupo, mascara in grupos_escolaridade:
        dados = df.loc[mascara, "cesarea"]
        sucessos = int(dados.sum())
        total = len(dados)
        escolaridade.append((grupo, total, sucessos))
    if any(
        min(sucessos, total - sucessos) < N_MINIMO_EXIBICAO
        for _, total, sucessos in escolaridade
    ):
        escolaridade = []
    else:
        escolaridade = [
            {
                "grupo": grupo,
                "n": total,
                "cesareas": sucessos,
                "outros_partos": total - sucessos,
                "proporcao_cesarea": sucessos / total if total else 0,
            }
            for grupo, total, sucessos in escolaridade
        ]

    prenatal = []
    for grupo, dados in df.groupby("nro_consultas_prenatal", dropna=False, sort=False):
        peso = dados["peso"].dropna()
        if len(peso) < N_MINIMO_EXIBICAO:
            continue
        prenatal.append(
            {
                "grupo": str(grupo) if pd.notna(grupo) and str(grupo).strip() else "(Não informado)",
                **_caixa(peso),
            }
        )

    tendencia = (
        df.groupby("ano")
        .agg(cesarea=("cesarea", "mean"), peso_medio=("peso", "mean"))
        .reset_index()
    )
    return {
        "n": int(len(df)),
        "indicadores": _indicadores(df, ddof),
        "estatisticas": estatisticas,
        "histogramas": histogramas,
        "boxplots": boxplots,
        "qq_peso": _qq_peso(df["peso"]),
        "categorias": categorias,
        "cesarea_por_escolaridade": escolaridade,
        "peso_por_prenatal": prenatal,
        "tendencias_anuais": [
            {
                "ano": int(row.ano),
                "cesarea": float(row.cesarea),
                "peso_medio": float(row.peso_medio),
            }
            for row in tendencia.itertuples(index=False)
        ],
    }


def _histogram_edges(
    populacao: pd.DataFrame, amostra: pd.DataFrame
) -> dict[str, np.ndarray]:
    edges = {}
    for coluna, configuracao in VARIAVEIS_QUANTITATIVAS.items():
        serie = populacao[coluna].dropna()
        serie_amostra = amostra[coluna].dropna()
        step = float(configuracao["step"])
        inicio = np.floor(float(serie.min()) / step) * step
        fim = np.ceil(float(serie.max()) / step) * step + step
        limites = np.arange(inicio, fim + step, step)
        contagens, _ = np.histogram(serie_amostra, bins=limites)
        agrupados = [float(limites[0])]
        acumulada = 0
        for indice, frequencia in enumerate(contagens):
            acumulada += int(frequencia)
            if acumulada >= N_MINIMO_EXIBICAO:
                agrupados.append(float(limites[indice + 1]))
                acumulada = 0
        if acumulada:
            if len(agrupados) > 1:
                agrupados[-1] = float(limites[-1])
            else:
                agrupados.append(float(limites[-1]))
        edges[coluna] = np.array(agrupados)
    return edges


def _inferencia(
    amostra: pd.DataFrame, populacao: pd.DataFrame
) -> dict[str, Any]:
    resultados = [asdict(resultado) for resultado in executar_inferencia(amostra, populacao)]
    for resultado in resultados:
        for condicao in resultado["condicoes"]:
            if (
                resultado["codigo"] == "H2"
                and condicao["nome"] == "Sucessos e fracassos ≥ 10 em cada grupo"
            ):
                condicao["detalhe"] = (
                    "As contagens por célula não são divulgadas individualmente."
                )
    simulacao = simular_variabilidade(populacao)
    return {"resultados": resultados, "simulacao": simulacao}


def gerar_resumo_publico() -> dict[str, Any]:
    populacao, amostra = _ler_dados()
    edges = _histogram_edges(populacao, amostra)
    populacao_resumida = _resumo_por_ano(populacao, edges, ddof=0)
    amostra_resumida = _resumo_por_ano(amostra, edges, ddof=1)
    return {
        "versao_schema": 1,
        "aviso_privacidade": (
            "Este arquivo contém apenas estatísticas agregadas. "
            "Nenhuma linha individual ou identificador é publicado."
        ),
        "limiar_suprimir": N_MINIMO_EXIBICAO,
        "n_original": 197_801,
        "n_populacao": int(len(populacao)),
        "n_amostra": int(len(amostra)),
        "semente_amostra": 2026,
        "data_sorteio": "04/11/2026",
        "populacao": populacao_resumida,
        "amostra": amostra_resumida,
        "inferencia": _inferencia(amostra, populacao),
    }


def main() -> None:
    resumo = gerar_resumo_publico()
    ARQUIVO_PUBLICO.parent.mkdir(parents=True, exist_ok=True)
    with ARQUIVO_PUBLICO.open("w", encoding="utf-8") as arquivo:
        json.dump(resumo, arquivo, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        arquivo.write("\n")
    print(
        f"Resumo agregado salvo em {ARQUIVO_PUBLICO}; "
        f"população={resumo['n_populacao']}, amostra={resumo['n_amostra']}, "
        f"simulações={N_SIMULACOES}."
    )
    print(
        f"Arquivo de publicação: {ARQUIVO_PUBLICO.stat().st_size:,} bytes. "
        "Verifique `git status` antes de publicar para confirmar que microdados "
        "não foram adicionados."
    )


if __name__ == "__main__":
    main()
