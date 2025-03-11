import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from datetime import datetime, timedelta

class LiteLLMKeyManager:
    def __init__(self, root):
        self.root = root
        self.root.title("LiteLLM Key Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variáveis
        self.server_url = tk.StringVar(value="http://localhost:8080")
        self.master_key = tk.StringVar()
        self.key_name = tk.StringVar()
        self.team_id = tk.StringVar()
        self.max_budget = tk.DoubleVar(value=50.0)
        self.expires_days = tk.StringVar(value="30d")
        
        # Modelos disponíveis
        self.available_models = [
            "gpt-3.5-turbo", 
            "gpt-4", 
            "claude-3-opus", 
            "claude-3-sonnet", 
            "gemini-pro", 
            "grok-1"
        ]
        
        # Checkbuttons para os modelos
        self.model_vars = {}
        for model in self.available_models:
            self.model_vars[model] = tk.BooleanVar(value=False)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal com notebook para abas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba de Conexão
        connection_frame = ttk.Frame(notebook)
        notebook.add(connection_frame, text="Conexão")
        
        # Aba de Gerenciamento de Chaves
        keys_frame = ttk.Frame(notebook)
        notebook.add(keys_frame, text="Gerenciar Chaves")
        
        # Aba de Listagem de Chaves
        list_keys_frame = ttk.Frame(notebook)
        notebook.add(list_keys_frame, text="Listar Chaves")
        
        # Configurar a aba de Conexão
        self.setup_connection_tab(connection_frame)
        
        # Configurar a aba de Gerenciamento de Chaves
        self.setup_keys_tab(keys_frame)
        
        # Configurar a aba de Listagem de Chaves
        self.setup_list_keys_tab(list_keys_frame)
        
        # Barra de status
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_connection_tab(self, parent):
        # Frame de configuração do servidor
        server_frame = ttk.LabelFrame(parent, text="Configuração do Servidor")
        server_frame.pack(fill=tk.X, expand=False, padx=10, pady=10)
        
        # URL do Servidor
        ttk.Label(server_frame, text="URL do Servidor:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(server_frame, textvariable=self.server_url, width=50).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Chave Mestra
        ttk.Label(server_frame, text="Chave Mestra:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(server_frame, textvariable=self.master_key, width=50, show="*").grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Botão para testar conexão
        ttk.Button(server_frame, text="Testar Conexão", command=self.test_connection).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Instruções de uso
        instructions_frame = ttk.LabelFrame(parent, text="Instruções")
        instructions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        instructions = scrolledtext.ScrolledText(instructions_frame, wrap=tk.WORD, width=70, height=15)
        instructions.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        instructions.insert(tk.END, """
1. Iniciando o LiteLLM Server:
   - Clone o repositório: git clone https://github.com/BerriAI/litellm.git
   - Navegue até o diretório: cd litellm
   - Crie o arquivo config.yaml na pasta raiz
   - Configure as variáveis de ambiente com suas chaves de API
   - Inicie o servidor com:
     python -m litellm.proxy.proxy_server --config /path/to/config.yaml --port 8000 --api_key sua_chave_mestra

2. Conectando ao servidor:
   - Configure a URL do servidor (padrão: http://localhost:8000)
   - Digite a chave mestra definida ao iniciar o servidor
   - Clique em "Testar Conexão" para verificar

3. Gerenciando chaves:
   - Crie novas chaves com parâmetros específicos na aba "Gerenciar Chaves"
   - Visualize chaves existentes na aba "Listar Chaves"
   - Delete chaves quando necessário
        """)
        instructions.config(state=tk.DISABLED)
    
    def setup_keys_tab(self, parent):
        # Frame para criar novas chaves
        create_frame = ttk.LabelFrame(parent, text="Criar Nova Chave")
        create_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Formulário em grid para criar chaves
        ttk.Label(create_frame, text="Nome da Chave:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(create_frame, textvariable=self.key_name, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(create_frame, text="ID da Equipe (opcional):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(create_frame, textvariable=self.team_id, width=40).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(create_frame, text="Orçamento Máximo ($):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(create_frame, from_=0, to=1000, textvariable=self.max_budget, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(create_frame, text="Expirar em (ex: 30d, 24h, 60m):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Função de validação para permitir números e sufixos de tempo (d, h, m, s)
        def validate_duration(input):
            if input == "":
                return True
            # Aceita dígitos seguidos opcionalmente por d, h, m ou s
            import re
            return bool(re.match(r'^[0-9]+[dhms]?$', input))
                
        vcmd = (self.root.register(validate_duration), '%P')
        ttk.Entry(create_frame, textvariable=self.expires_days, width=10, 
                 validate="key", validatecommand=vcmd).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Frame para os modelos
        models_frame = ttk.LabelFrame(create_frame, text="Modelos Permitidos")
        models_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=10)
        
        # Checkbuttons para modelos
        for i, model in enumerate(self.available_models):
            row, col = divmod(i, 3)
            ttk.Checkbutton(models_frame, text=model, variable=self.model_vars[model]).grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
        
        # Botão para criar chave
        ttk.Button(create_frame, text="Criar Chave", command=self.create_key).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Área para mostrar a chave criada
        ttk.Label(create_frame, text="Chave Gerada:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.key_result = scrolledtext.ScrolledText(create_frame, wrap=tk.WORD, width=70, height=10)
        self.key_result.grid(row=7, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
    def setup_list_keys_tab(self, parent):
        # Frame para listar chaves
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botão para atualizar lista
        ttk.Button(list_frame, text="Atualizar Lista de Chaves", command=self.list_keys).pack(pady=10)
        
        # Treeview para mostrar as chaves
        columns = ('key', 'name', 'team_id', 'models', 'budget', 'spend', 'expires')
        self.keys_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configurar cabeçalhos
        self.keys_tree.heading('key', text='Chave')
        self.keys_tree.heading('name', text='Nome')
        self.keys_tree.heading('team_id', text='Equipe')
        self.keys_tree.heading('models', text='Modelos')
        self.keys_tree.heading('budget', text='Orçamento')
        self.keys_tree.heading('spend', text='Gasto')
        self.keys_tree.heading('expires', text='Expira em')
        
        # Configurar colunas
        self.keys_tree.column('key', width=150, anchor='w')
        self.keys_tree.column('name', width=100, anchor='w')
        self.keys_tree.column('team_id', width=80, anchor='w')
        self.keys_tree.column('models', width=200, anchor='w')
        self.keys_tree.column('budget', width=80, anchor='e')
        self.keys_tree.column('spend', width=80, anchor='e')
        self.keys_tree.column('expires', width=100, anchor='w')
        
        # Adicionar scrollbar
        keys_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.keys_tree.yview)
        self.keys_tree.configure(yscroll=keys_scroll.set)
        
        # Empacotar elementos
        self.keys_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        keys_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botão para revogar chave selecionada
        ttk.Button(list_frame, text="Revogar Chave Selecionada", command=self.revoke_key).pack(pady=10)
        
    def test_connection(self):
        """Testa a conexão com o servidor LiteLLM"""
        try:
            url = f"{self.server_url.get()}/health"
            headers = {"Authorization": f"Bearer {self.master_key.get()}"}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                messagebox.showinfo("Conexão", "Conexão com o servidor bem-sucedida!")
                self.status_var.set("Conexão com o servidor estabelecida")
            else:
                messagebox.showerror("Erro", f"Erro ao conectar: Status {response.status_code}")
                self.status_var.set(f"Erro de conexão: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao servidor: {str(e)}")
            self.status_var.set(f"Erro de conexão: {str(e)}")