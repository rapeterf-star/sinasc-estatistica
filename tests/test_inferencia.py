import unittest

import pandas as pd

from src.inferencia import (
    conferir_com_statsmodels,
    executar_inferencia,
    simular_variabilidade,
)


class TestInferenciaSINASC(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.populacao = pd.read_parquet("data/populacao.parquet")
        cls.amostra = pd.read_csv("data/amostra.csv")
        cls.resultados = executar_inferencia(cls.amostra, cls.populacao)

    def test_quatro_hipoteses_e_decisoes_reprodutiveis(self) -> None:
        self.assertEqual([r.codigo for r in self.resultados], ["H1", "H2", "H3", "H4"])
        self.assertEqual(
            [r.rejeita_h0 for r in self.resultados],
            [False, True, False, True],
        )
        self.assertEqual(
            [r.classificacao for r in self.resultados],
            [
                "Erro tipo II",
                "Rejeição correta de H₀",
                "Erro tipo II",
                "Rejeição correta de H₀",
            ],
        )
        self.assertTrue(all(r.contem_parametro for r in self.resultados))

    def test_intervalos_e_gl_sao_validos(self) -> None:
        for resultado in self.resultados:
            inferior, superior = resultado.intervalo
            self.assertLess(inferior, superior, resultado.codigo)
            self.assertGreaterEqual(resultado.valor_p, 0)
            self.assertLessEqual(resultado.valor_p, 1)
            self.assertTrue(resultado.condicoes[0].atendida)
        self.assertEqual(self.resultados[2].graus_liberdade, 383)
        self.assertGreater(self.resultados[3].graus_liberdade, 30)

    def test_estatisticas_e_intervalos_conferem_com_statsmodels(self) -> None:
        comparacoes = conferir_com_statsmodels(self.amostra, self.populacao)
        for codigo, valores in comparacoes.items():
            for nome, diferenca in valores.items():
                self.assertAlmostEqual(
                    diferenca,
                    0.0,
                    delta=1e-10,
                    msg=f"{codigo} {nome}",
                )

    def test_simulacao_reprodutivel_e_limitada(self) -> None:
        primeira = simular_variabilidade(self.populacao, n_simulacoes=50, semente=2030)
        segunda = simular_variabilidade(self.populacao, n_simulacoes=50, semente=2030)
        self.assertEqual(primeira, segunda)
        self.assertEqual(set(primeira), {"H1", "H2", "H3", "H4"})
        for resultado in primeira.values():
            self.assertGreaterEqual(resultado["cobertura_ic"], 0)
            self.assertLessEqual(resultado["cobertura_ic"], 1)
            self.assertGreaterEqual(resultado["taxa_rejeicao"], 0)
            self.assertLessEqual(resultado["taxa_rejeicao"], 1)


if __name__ == "__main__":
    unittest.main()
