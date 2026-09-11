import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env na raiz
load_dotenv()

def get_db_config():
    """Retorna o dicionário de configuração de conexão ao TiDB Cloud."""
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
        raise ValueError("Credenciais de banco de dados do TiDB não configuradas no arquivo .env")
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
