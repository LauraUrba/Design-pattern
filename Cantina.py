import sqlite3
import tkinter as tk
from tkinter import messagebox, Toplevel

# Banco de Dados Singleton (design pattern) - (Padrões Criacionais)
# Garante que apenas uma instância do banco de dados seja criada
class BancoDados:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.conn = sqlite3.connect("cantina.db")
            cls._instance.cursor = cls._instance.conn.cursor()
            cls._instance.criar_tabelas()
        return cls._instance

    def executar_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def criar_tabelas(self):
        self.executar_query("""CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            senha TEXT)""")

        self.executar_query("""CREATE TABLE IF NOT EXISTS alimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            quantidade INTEGER,
            preco REAL)""")

        self.executar_query("""CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            item TEXT,
            valor REAL,
            tipo TEXT)""") 

# Classe que encapsula as operações do banco de dados, sendo uma interface simples - Facade (Padrões estruturais)
# Usuário
class Usuario:
    @staticmethod
    def criar_usuario(nome, senha):
        bd = BancoDados()
        try:
            bd.executar_query("INSERT INTO usuarios (nome, senha) VALUES (?, ?)", (nome, senha))
            messagebox.showinfo("Sucesso", f"Usuário {nome} cadastrado!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Nome de usuário já existe!")

    @staticmethod
    def login(nome, senha):
        bd = BancoDados()
        bd.cursor.execute("SELECT * FROM usuarios WHERE nome = ? AND senha = ?", (nome, senha))
        return bd.cursor.fetchone() is not None

# Compra
class Compra:
    @staticmethod
    def verificar_dividas():
        bd = BancoDados()
        bd.cursor.execute("SELECT usuario, item, SUM(valor) FROM compras WHERE tipo = 'Dívida' GROUP BY usuario, item")
        dividas = bd.cursor.fetchall()

        if dividas:
            texto = "\n".join([f"{usuario} deve R${total:.2f} pelo item {item}" for usuario, item, total in dividas])
        else:
            texto = "Nenhuma dívida encontrada."

        messagebox.showinfo("Dívidas", texto)

    @staticmethod
    def registrar_compra(usuario, item, valor, tipo):
        bd = BancoDados()
        bd.executar_query(
            "INSERT INTO compras (usuario, item, valor, tipo) VALUES (?, ?, ?, ?)",
            (usuario, item, valor, tipo)
        )
        messagebox.showinfo("Compra", f"{tipo} registrada para {usuario}: {item} por R${valor:.2f}.")

# Alimento
class Alimento:
    @staticmethod
    def adicionar_alimento(nome, quantidade, preco):
        bd = BancoDados()
        try:
            preco = float(str(preco).replace(',', '.'))
            bd.executar_query("INSERT INTO alimentos (nome, quantidade, preco) VALUES (?, ?, ?)", (nome, quantidade, preco))
        except sqlite3.IntegrityError:
            preco = float(str(preco).replace(',', '.'))
            bd.executar_query("UPDATE alimentos SET quantidade = quantidade + ?, preco = ? WHERE nome = ?", (quantidade, preco, nome))
        messagebox.showinfo("Estoque", f"{nome} adicionado com {quantidade} unidades por R${preco:.2f}.")


# Interface Gráfica
class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema da Cantina")
        self.root.geometry("300x250")
        self.usuario_logado = None
        self.tela_login()

    def limpar_tela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def tela_login(self):
        self.limpar_tela()
        tk.Label(self.root, text="Nome:").pack()
        self.nome_entry = tk.Entry(self.root)
        self.nome_entry.pack()

        tk.Label(self.root, text="Senha:").pack()
        self.senha_entry = tk.Entry(self.root, show="*")
        self.senha_entry.pack()

        tk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.root, text="Cadastrar", command=self.tela_cadastro).pack()

    def tela_cadastro(self):
        self.limpar_tela()
        tk.Label(self.root, text="Novo Usuário:").pack()
        self.nome_entry = tk.Entry(self.root)
        self.nome_entry.pack()

        tk.Label(self.root, text="Senha:").pack()
        self.senha_entry = tk.Entry(self.root, show="*")
        self.senha_entry.pack()

        tk.Button(self.root, text="Cadastrar", command=self.cadastrar).pack(pady=5)
        tk.Button(self.root, text="Voltar", command=self.tela_login).pack()

    def login(self):
        nome = self.nome_entry.get()
        senha = self.senha_entry.get()
        if Usuario.login(nome, senha):
            self.usuario_logado = nome
            self.tela_principal()
        else:
            messagebox.showerror("Erro", "Login inválido.")

    def cadastrar(self):
        nome = self.nome_entry.get()
        senha = self.senha_entry.get()
        Usuario.criar_usuario(nome, senha)
        self.tela_login()

    def tela_principal(self):
        self.limpar_tela()
        tk.Label(self.root, text=f"Bem-vindo à Cantina da Lydia, {self.usuario_logado}").pack(pady=10)
        tk.Button(self.root, text="Estoque", command=self.tela_estoque).pack(fill="x", padx=20, pady=5)
        tk.Button(self.root, text="Compra", command=self.tela_compra).pack(fill="x", padx=20, pady=5)
        tk.Button(self.root, text="Ver Dívidas", command=lambda: Compra.verificar_dividas()).pack(fill="x", padx=20, pady=5)
        tk.Button(self.root, text="Sair", command=self.tela_login).pack(fill="x", padx=20, pady=10)

    def tela_estoque(self):
        win = Toplevel(self.root)
        win.title("Estoque")
        win.geometry("300x250")

        tk.Label(win, text="Alimento:").pack()
        nome = tk.Entry(win)
        nome.pack()

        tk.Label(win, text="Quantidade:").pack()
        quantidade = tk.Entry(win)
        quantidade.pack()

        tk.Label(win, text="Preço R$:").pack()
        preco = tk.Entry(win)
        preco.pack()

        def adicionar():
            try:
                qtd = int(quantidade.get())
                prc = float(preco.get().replace(',', '.'))
                Alimento.adicionar_alimento(nome.get(), qtd, prc)
                win.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Quantidade ou preço inválido.")

        tk.Button(win, text="Adicionar", command=adicionar).pack(pady=10)

    def tela_compra(self):
        win = Toplevel(self.root)
        win.title("Compra")
        win.geometry("300x250")

        tk.Label(win, text="Comprador:").pack()
        comprador_entry = tk.Entry(win) 
        comprador_entry.pack()

        tk.Label(win, text="Item:").pack()
        item_entry = tk.Entry(win)
        item_entry.pack()

        tk.Label(win, text="Valor R$:").pack()
        valor_entry = tk.Entry(win)
        valor_entry.pack()

        def realizar_compra(tipo):
            try:
                comprador = comprador_entry.get().strip() 
                item = item_entry.get().strip()  
                val = float(valor_entry.get().replace(',', '.'))  
                
                if not comprador or not item:  
                    messagebox.showerror("Erro", "Preencha todos os campos!")
                    return
                
                Compra.registrar_compra(comprador, item, val, tipo)  # Passa o comprador manualmente
                win.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido.")

        tk.Button(win, text="Comprar", command=lambda: realizar_compra("Compra")).pack(pady=5)
        tk.Button(win, text="Marcar (como dívida)", command=lambda: realizar_compra("Dívida")).pack(pady=5)

# Rodando o sistema
if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()