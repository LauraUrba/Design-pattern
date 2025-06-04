from Cantina import BancoDados


try:
    bd = BancoDados()
    bd.executar_query("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        senha TEXT
    )
    """)
    bd.executar_query("""
    CREATE TABLE IF NOT EXISTS alimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        quantidade INTEGER,
        preco REAL
    )
    """)
    bd.executar_query("""
    CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        item TEXT,
        valor REAL,
        tipo TEXT
    )
    """)
    print("Banco de dados configurado!")
except Exception as e:
    print(f"Erro ao configurar banco de dados: {e}")