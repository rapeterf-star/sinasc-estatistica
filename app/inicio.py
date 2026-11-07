import streamlit as st


st.title("SINASC Porto Alegre")
st.write(
    "Análise descritiva da população e de uma amostra aleatória de nascimentos, "
    "seguida de inferência estatística."
)
st.markdown(
    "A base contém nascimentos registrados em Porto Alegre entre 2011 e 2021. "
    "Após remover pesos abaixo de 500 g, a população analisada tem 197.639 "
    "registros; a amostra aleatória simples contém 384 nascimentos. "
    "O aplicativo disponibiliza apenas resumos estatísticos agregados, sem "
    "registros individuais."
)
st.link_button(
    "Fonte dos dados — SINASC Porto Alegre",
    "https://dadosabertos.poa.br/dataset/sinasc",
    icon=":material/open_in_new:",
)
st.info(
    "Use a navegação acima para explorar os painéis de população, amostra e "
    "inferência estatística. Microdados locais não são publicados nem oferecidos "
    "para download neste aplicativo."
)
