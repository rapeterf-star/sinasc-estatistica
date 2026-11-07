import streamlit as st

from src.publicacao import carregar_resumo_publico, renderizar_inferencia


resumo = carregar_resumo_publico()
renderizar_inferencia(resumo)
