from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
POPULACAO_PATH = ROOT / "data" / "populacao.parquet"
OUTPUT_PATH = ROOT / "data" / "amostra.csv"
TAMANHO_AMOSTRA = 384
SEMENTE = 2026


def main() -> None:
    populacao = pd.read_parquet(POPULACAO_PATH)
    if "indice_original" not in populacao.columns:
        raise ValueError("A população precisa conter a coluna indice_original.")
    if populacao["indice_original"].duplicated().any():
        raise ValueError("A coluna indice_original contém valores duplicados.")
    if len(populacao) < TAMANHO_AMOSTRA:
        raise ValueError(
            f"A população tem {len(populacao)} registros; "
            f"são necessários pelo menos {TAMANHO_AMOSTRA}."
        )

    populacao = populacao.sort_values("indice_original")
    amostra = populacao.sample(
        n=TAMANHO_AMOSTRA,
        replace=False,
        random_state=SEMENTE,
    )
    amostra.sort_values("indice_original", inplace=True)
    amostra.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    fracao = TAMANHO_AMOSTRA / len(populacao)
    print(f"Amostra salva: {len(amostra)} registros em {OUTPUT_PATH}")
    print(f"Semente: {SEMENTE}; fração amostral: {fracao:.2%}")
    print("O arquivo inclui indice_original para auditoria do sorteio.")


if __name__ == "__main__":
    main()
