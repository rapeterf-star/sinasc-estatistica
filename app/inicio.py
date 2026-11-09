import streamlit as st

from src.publicacao import botao_relatorio


st.title("SINASC Porto Alegre")
st.write(
    "Análise descritiva da população e de uma amostra aleatória de nascimentos, "
    "seguida de inferência estatística."
)
st.markdown(
    "A base contém nascimentos registrados em Porto Alegre entre 2011 e 2021. "
    "Após aplicar o recorte analítico de peso igual ou superior a 500 g, "
    "a população analisada tem 197.639 registros; a amostra aleatória simples "
    "contém 384 nascimentos. O limite é uma decisão metodológica deste estudo; "
    "nascidos vivos podem apresentar peso extremamente baixo, então registros "
    "abaixo do limite não são automaticamente classificados como erros. "
    "O aplicativo disponibiliza apenas resumos estatísticos agregados, sem "
    "registros individuais."
)
with st.container(horizontal=True):
    st.link_button(
        "Fonte dos dados — SINASC Porto Alegre",
        "https://dadosabertos.poa.br/dataset/sinasc",
        icon=":material/open_in_new:",
    )
    botao_relatorio()
st.markdown(
    "**Como navegar:** o vídeo resume os principais resultados; o **relatório "
    "completo** traz todas as análises, incluindo a simulação de 1.000 amostras "
    "e um **estudo complementar** que replica o mesmo desenho amostral nos "
    "óbitos infantis do SIM, numa população cerca de 111 vezes menor."
)
st.info(
    "Use a navegação acima para explorar os painéis de população, amostra e "
    "inferência estatística. Microdados locais não são publicados nem oferecidos "
    "para download neste aplicativo."
)
