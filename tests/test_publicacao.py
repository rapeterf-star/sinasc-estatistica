import importlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd


publicacao = importlib.import_module("src.04_preparar_publicacao")
renderizacao = importlib.import_module("src.publicacao")


class TestPreparacaoPublicacao(unittest.TestCase):
    def test_categorias_com_poucas_ocorrencias_sao_agrupadas(self) -> None:
        dados = pd.Series(["A"] * 12 + ["B"] * 4 + ["C"] * 2)

        resultado = publicacao._distribuicao_categorica(dados, "variavel")

        self.assertEqual(resultado[0]["categoria"], "A")
        self.assertEqual(resultado[0]["frequencia"], 12)
        self.assertEqual(
            resultado[1]["categoria"],
            "Categorias de baixa frequência agrupadas",
        )
        self.assertIsNone(resultado[1]["frequencia"])
        self.assertIsNone(resultado[1]["proporcao"])

    def test_histograma_agrupa_bins_ate_o_limiar_minimo(self) -> None:
        dados = pd.Series([1] * 4 + [2] * 4 + [3] * 12)

        resultado = publicacao._histograma(dados, np.array([0, 1.5, 2.5, 3.5]))

        self.assertTrue(
            all(
                frequencia >= publicacao.N_MINIMO_EXIBICAO
                for frequencia in resultado["contagens"]
            )
        )
        self.assertEqual(sum(resultado["contagens"]), len(dados))

    def test_quantis_qq_representam_grupos_de_ao_menos_dez(self) -> None:
        resultado = publicacao._qq_peso(pd.Series(np.arange(35, dtype=float)))

        self.assertEqual(len(resultado["pontos"]), 3)
        self.assertTrue(
            all(
                ponto["n_aproximado"] >= publicacao.N_MINIMO_EXIBICAO
                for ponto in resultado["pontos"]
            )
        )

    def test_artefato_publico_contem_apenas_resumos_agregados(self) -> None:
        caminho = Path("data/resumo_publico.json")
        self.assertTrue(caminho.exists(), "Execute o script de preparação pública.")
        resumo = json.loads(caminho.read_text(encoding="utf-8"))
        serializado = json.dumps(resumo, ensure_ascii=False)
        self.assertNotIn("indice_original", serializado)
        self.assertNotIn("nascimento_mae", serializado)
        self.assertEqual(resumo["n_populacao"], 197_639)
        self.assertEqual(resumo["n_amostra"], 384)

        for conjunto in ("populacao", "amostra"):
            resumos = [
                resumo[conjunto]["total"],
                *resumo[conjunto]["por_ano"].values(),
            ]
            for dados in resumos:
                for histograma in dados["histogramas"].values():
                    self.assertTrue(
                        all(
                            frequencia >= publicacao.N_MINIMO_EXIBICAO
                            for frequencia in histograma["contagens"]
                        )
                    )
                for categorias in dados["categorias"].values():
                    self.assertTrue(
                        all(
                            item["frequencia"] is None
                            or item["frequencia"] >= publicacao.N_MINIMO_EXIBICAO
                            for item in categorias
                        )
                    )
                self.assertTrue(
                    all(
                        ponto["n_aproximado"] >= publicacao.N_MINIMO_EXIBICAO
                        for ponto in dados["qq_peso"]["pontos"]
                    )
                )

    def test_graficos_categoricos_usam_barras_horizontais(self) -> None:
        dados = {
            "categorias": {
                coluna: [
                    {"categoria": "A", "frequencia": 12, "proporcao": 0.6},
                    {"categoria": "B", "frequencia": 8, "proporcao": 0.4},
                ]
                for coluna in renderizacao.VARIAVEIS_QUALITATIVAS
            }
        }
        with (
            patch.object(renderizacao.st, "subheader"),
            patch.object(renderizacao.st, "caption"),
            patch.object(renderizacao.st, "selectbox", return_value="Proporção (%)"),
            patch.object(renderizacao.st, "dataframe"),
            patch.object(renderizacao.st, "plotly_chart") as plotly_chart,
        ):
            renderizacao._mostrar_qualitativas(dados, "teste")

        figuras = [chamada.args[0] for chamada in plotly_chart.call_args_list]
        self.assertEqual(len(figuras), len(renderizacao.VARIAVEIS_QUALITATIVAS))
        self.assertTrue(all(figura.data[0].orientation == "h" for figura in figuras))
        self.assertTrue(
            all(figura.layout.yaxis.autorange == "reversed" for figura in figuras)
        )

    def test_comparacao_usa_cores_fixas_e_barras_horizontais(self) -> None:
        dados = pd.DataFrame(
            [
                {
                    "Variável": "Tipo de parto",
                    "Categoria": categoria,
                    "Conjunto": conjunto,
                    "Proporção (%)": proporcao,
                }
                for categoria, proporcao in (("Vaginal", 50.0), ("Cesáreo", 50.0))
                for conjunto in ("População", "Amostra")
            ]
        )

        figura = renderizacao._figura_barras_comparacao(dados)

        self.assertTrue(all(trace.orientation == "h" for trace in figura.data))
        self.assertEqual(
            [trace.marker.color for trace in figura.data],
            [
                renderizacao.COR_POPULACAO,
                renderizacao.COR_AMOSTRA,
            ],
        )
        self.assertEqual(list(figura.layout.xaxis.range), [0, 100])
        self.assertEqual(figura.layout.yaxis.autorange, "reversed")

    def test_histograma_comparativo_usa_cores_fixas(self) -> None:
        histograma = {
            conjunto: {
                "centros": [1.0],
                "densidade": [1.0],
                "larguras": [1.0],
                "contagens": [12],
                "limites_inferiores": [0.5],
                "limites_superiores": [1.5],
            }
            for conjunto in ("População", "Amostra")
        }

        with patch.object(renderizacao.st, "plotly_chart") as plotly_chart:
            renderizacao._figura_histograma(
                histograma,
                "Distribuição",
                "Peso (g)",
                "teste",
                grupo="Conjunto",
            )

        figura = plotly_chart.call_args.args[0]
        self.assertEqual(
            [trace.marker.color for trace in figura.data],
            [renderizacao.COR_POPULACAO, renderizacao.COR_AMOSTRA],
        )


if __name__ == "__main__":
    unittest.main()
