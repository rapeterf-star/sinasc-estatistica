from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "sinasc_nascimentos.csv"
OUTPUT_PATH = ROOT / "data" / "populacao.parquet"

PREMATURO_CATEGORIAS = {
    "MENOS DE 22 SEM",
    "DE 22 A 27 SEM",
    "DE 28 A 31 SEM",
    "DE 32 A 36 SEM",
}


def main() -> None:
    dados = pd.read_csv(CSV_PATH, sep=";", encoding="utf-8-sig", low_memory=False)
    dados.insert(0, "indice_original", range(len(dados)))

    peso = pd.to_numeric(dados["peso"].astype("string").str.strip(), errors="coerce")
    if peso.isna().any():
        raise ValueError(f"{peso.isna().sum()} registro(s) têm peso ausente ou inválido.")

    total_original = len(dados)
    dados["peso"] = peso
    dados = dados.loc[dados["peso"] >= 500].copy()

    data_nascimento = pd.to_datetime(
        dados["data_nascimento"].astype("string").str.strip(),
        format="%m/%Y",
        errors="coerce",
    )
    if data_nascimento.isna().any():
        raise ValueError(
            f"{data_nascimento.isna().sum()} registro(s) têm data_nascimento inválida."
        )

    nascimento_mae = pd.to_datetime(
        dados["nascimento_mae"].astype("string").str.strip().replace("", pd.NA),
        format="%m/%Y",
        errors="coerce",
    )
    dados["idade_mae"] = (data_nascimento - nascimento_mae).dt.days / 365.25
    dados["cesarea"] = dados["parto"].eq("CESAREO").astype("int8")
    dados["baixo_peso"] = dados["peso"].lt(2500).astype("int8")
    dados["prematuro"] = (
        dados["duracao_gestacao"].isin(PREMATURO_CATEGORIAS).astype("int8")
    )
    dados["escol_12mais"] = (
        dados["escolaridade_mae"].eq("COM 12 ANOS OU MAIS").astype("int8")
    )
    dados["prenatal_7mais"] = (
        dados["nro_consultas_prenatal"].eq("7 OU MAIS CONS").astype("int8")
    )
    dados["ano"] = data_nascimento.dt.year.astype("int16")

    dados.sort_values("indice_original", inplace=True)
    dados.to_parquet(OUTPUT_PATH, index=False)

    print(f"Registros antes da limpeza: {total_original:,}")
    print(f"Registros removidos (peso < 500 g): {total_original - len(dados):,}")
    print(f"População salva: {len(dados):,} registros em {OUTPUT_PATH}")
    print(f"Idade da mãe ausente: {dados['idade_mae'].isna().sum():,} registro(s)")


if __name__ == "__main__":
    main()
