import streamlit as st


st.set_page_config(
    page_title="SINASC Porto Alegre — Estatística",
    page_icon=":material/monitoring:",
    layout="wide",
)

paginas = [
    st.Page("app/inicio.py", title="Apresentação", icon=":material/home:", default=True),
    st.Page("pages/1_Populacao.py", title="População", icon=":material/analytics:"),
    st.Page("pages/2_Amostra.py", title="Amostra", icon=":material/bar_chart:"),
    st.Page("pages/3_Inferencia.py", title="Inferência", icon=":material/science:"),
]
pagina = st.navigation(paginas, position="top")
pagina.run()
