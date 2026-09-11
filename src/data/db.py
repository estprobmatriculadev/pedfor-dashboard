import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env na raiz
load_dotenv()

def get_db_config():
    """
    Retorna o dicionário de configuração de conexão ao TiDB Cloud.
    Suporta leitura via Streamlit Secrets (share.streamlit.io) ou arquivo .env local.
    """
    host = ""
    port = 4000
    user = ""
    password = ""
    database = ""
    ssl_enable = True

    # 1. Tenta obter das Secrets do Streamlit (nuvem)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "TIDB_HOST" in st.secrets:
            host = st.secrets["TIDB_HOST"]
            port = int(st.secrets.get("TIDB_PORT", 4000))
            user = st.secrets.get("TIDB_USER", "")
            password = st.secrets.get("TIDB_PASSWORD", "")
            database = st.secrets.get("TIDB_DATABASE", "")
            ssl_enable = str(st.secrets.get("TIDB_SSL_ENABLE", "true")).lower() in ("true", "1", "t")
    except Exception:
        pass

    # 2. Fallback para variáveis de ambiente locais (.env)
    if not host:
        host = os.getenv("TIDB_HOST", "")
        port = int(os.getenv("TIDB_PORT", "4000"))
        user = os.getenv("TIDB_USER", "")
        password = os.getenv("TIDB_PASSWORD", "")
        database = os.getenv("TIDB_DATABASE", "")
        ssl_enable = os.getenv("TIDB_SSL_ENABLE", "true").lower() in ("true", "1", "t")

    ssl_config = {"rejectUnauthorized": True} if ssl_enable else None

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "cursorclass": DictCursor,
        "ssl": ssl_config,
        "connect_timeout": 10,
        "autocommit": True
    }

def get_connection():
    """Retorna uma nova conexão ativa com o banco TiDB."""
    config = get_db_config()
    if not config["host"] or not config["user"]:
        raise ValueError("Credenciais de banco de dados do TiDB não configuradas no arquivo .env ou Streamlit Secrets")
    return pymysql.connect(**config)

def execute_query(sql: str, params: tuple = ()):
    """Executa uma consulta SELECT no TiDB e retorna lista de dicionários."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            return result
    finally:
        conn.close()

def execute_statement(sql: str, params: tuple = ()):
    """Executa comandos INSERT/UPDATE/DELETE no TiDB e retorna contagem de linhas afetadas."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            affected = cursor.execute(sql, params)
            conn.commit()
            return affected
    finally:
        conn.close()
