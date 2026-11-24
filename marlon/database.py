import sqlite3
from .config import DATABASE_PATH


def connect():
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    conn = connect()
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON")

    c.execute("""CREATE TABLE IF NOT EXISTS emblemas
                 (nome TEXT PRIMARY KEY, url_imagem TEXT, emoji TEXT, 
                  descricao TEXT, data_criacao TEXT,
                  preco INTEGER DEFAULT 0, na_loja BOOLEAN DEFAULT 0)""")

    c.execute("""CREATE TABLE IF NOT EXISTS codigos
                 (codigo TEXT PRIMARY KEY, emblema_nome TEXT, 
                  limite INTEGER DEFAULT -1, usos INTEGER DEFAULT 0,
                  validade TEXT, ativo BOOLEAN DEFAULT 1)""")

    c.execute("""CREATE TABLE IF NOT EXISTS inventario
                 (user_id INTEGER, emblema_nome TEXT, 
                 data_resgate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY(emblema_nome) REFERENCES emblemas(nome))""")

    c.execute("""CREATE TABLE IF NOT EXISTS usuarios
                 (user_id INTEGER PRIMARY KEY, saldo INTEGER DEFAULT 0, 
                  destaques TEXT DEFAULT '', last_daily TEXT, bio TEXT, last_work TEXT)""")

    # --- MIGRAÇÕES ---
    try:
        c.execute("ALTER TABLE emblemas ADD COLUMN preco INTEGER DEFAULT 0")
    except:
        pass

    try:
        c.execute("ALTER TABLE emblemas ADD COLUMN na_loja BOOLEAN DEFAULT 0")
    except:
        pass

    try:
        c.execute(
            "ALTER TABLE usuarios ADD COLUMN bio TEXT DEFAULT 'Sem bio definida.'"
        )
    except:
        pass

    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN last_work TEXT")
    except:
        pass

    c.execute("PRAGMA table_info(codigos)")
    cols = [info[1] for info in c.fetchall()]
    if "limite" not in cols:
        c.execute("ALTER TABLE codigos ADD COLUMN limite INTEGER DEFAULT -1")
    if "usos" not in cols:
        c.execute("ALTER TABLE codigos ADD COLUMN usos INTEGER DEFAULT 0")
    if "validade" not in cols:
        c.execute("ALTER TABLE codigos ADD COLUMN validade TEXT")
    if "ativo" not in cols:
        c.execute("ALTER TABLE codigos ADD COLUMN ativo BOOLEAN DEFAULT 1")

    conn.commit()
    conn.close()


def check_user_exists(user_id):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO usuarios (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
