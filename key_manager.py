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