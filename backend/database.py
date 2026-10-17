import sqlite3
from pathlib import Path

# A base fica na pasta dados/, irmã de backend/, conforme o roteiro do Encontro 3.
RAIZ_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_BANCO = RAIZ_PROJETO / "dados" / "reservas.db"
DB_PATH = CAMINHO_BANCO  # Alias mantido para facilitar testes e compatibilidade.


def conectar() -> sqlite3.Connection:
    CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(CAMINHO_BANCO, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabela() -> None:
    with conectar() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS reservas (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          laboratorio TEXT NOT NULL,
          responsavel TEXT NOT NULL,
          data TEXT NOT NULL,
          turno TEXT NOT NULL,
          finalidade TEXT NOT NULL,
          quantidade_alunos INTEGER NOT NULL DEFAULT 1 CHECK(quantidade_alunos BETWEEN 1 AND 40),
          status TEXT NOT NULL CHECK(status IN ('confirmada', 'pendente', 'cancelada')),
          data_criacao TEXT NOT NULL
        )""")
        # Atualização idempotente para bases criadas por versões anteriores do exercício.
        colunas = {linha["name"] for linha in conn.execute("PRAGMA table_info(reservas)")}
        if "quantidade_alunos" not in colunas:
            conn.execute("ALTER TABLE reservas ADD COLUMN quantidade_alunos INTEGER NOT NULL DEFAULT 1 CHECK(quantidade_alunos BETWEEN 1 AND 40)")
