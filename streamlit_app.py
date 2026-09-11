"""
Entrypoint principal do PEDFOR Dashboard para publicação no Streamlit Community Cloud (share.streamlit.io).
"""
import os
import sys

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa e executa a aplicação principal
import src.app
