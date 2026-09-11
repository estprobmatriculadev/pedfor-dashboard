"""
Entrypoint oficial do PEDFOR Dashboard no Streamlit Community Cloud (share.streamlit.io).
"""
import os
import sys

# Garante que a raiz e o diretório src estejam no PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

# Executa a aplicação do dashboard
app_path = os.path.join(BASE_DIR, "src", "app.py")
with open(app_path, "r", encoding="utf-8") as f:
    code = compile(f.read(), app_path, 'exec')
    exec(code, globals())
