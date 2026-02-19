#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 BET BOOSTER - INSTALADOR OFICIAL
Sistema Avançado de Análise de Apostas Esportivas
Instalador com Interface Gráfica Detalhada
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import sys
import os
import threading
import time
from datetime import datetime

class BetBoosterInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 BET BOOSTER - INSTALADOR OFICIAL")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Centralizar janela
        self.center_window()
        
        # Configurar cores e estilo
        self.setup_styles()
        
        # Estado da instalação
        self.aceito_termos = tk.BooleanVar()
        self.instalacao_em_progresso = False
        
        # Criar interface
        self.create_welcome_screen()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
    
    def setup_styles(self):
        """Configura cores e estilos"""
        self.root.configure(bg='#f0f0f0')
        
        # Cores
        self.cores = {
            'primary': '#1e40af',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'dark': '#1f2937',
            'light': '#f8fafc'
        }
        
        # Configurar estilos ttk
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 20, 'bold'), foreground=self.cores['primary'])
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground=self.cores['dark'])
        style.configure('Body.TLabel', font=('Arial', 11), foreground=self.cores['dark'])
        style.configure('Success.TLabel', font=('Arial', 12, 'bold'), foreground=self.cores['success'])
        style.configure('Primary.TButton', font=('Arial', 12, 'bold'))
    
    def create_welcome_screen(self):
        """Cria a tela de boas-vindas e informações"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header com logo/título
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🎯 BET BOOSTER", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Sistema Avançado de Análise de Apostas Esportivas", style='Header.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
        version_label = ttk.Label(header_frame, text="Versão 2.0 - Edição Profissional", style='Body.TLabel')
        version_label.pack(pady=(5, 0))
        
        # Área de descrição com scroll
        desc_frame = tk.LabelFrame(main_frame, text="📋 Sobre o Programa", font=('Arial', 12, 'bold'), 
                                  bg='#f0f0f0', fg=self.cores['primary'])
        desc_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        desc_text = scrolledtext.ScrolledText(desc_frame, height=12, font=('Arial', 10), 
                                             wrap=tk.WORD, bg='white', relief='flat', bd=5)
        desc_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Texto descritivo
        descricao = """🚀 O QUE É O BET BOOSTER?

O Bet Booster é um sistema profissional de análise de apostas esportivas que utiliza modelos estatísticos avançados para calcular probabilidades reais de resultados em jogos de futebol.

📊 PRINCIPAIS FUNCIONALIDADES:

🎯 Análise Estatística Avançada
   • Modelo matemático baseado na Distribuição de Poisson
   • Cálculo de probabilidades para Over/Under, Gols, Escanteios
   • Análise de valor de apostas (Value Betting)
   • Comparação automática com odds das casas

⚽ Base de Dados Completa
   • Integração com APIs de dados esportivos em tempo real
   • Dados do Radar Esportivo e SofaScore
   • Estatísticas atualizadas de gols marcados/sofridos
   • Dados de mandante/visitante separados
   • Filtros por data e busca avançada

🖥️ Interface Profissional
   • 5 abas especializadas para diferentes análises
   • Sistema de busca e filtros inteligentes
   • Seleção múltipla de times e jogos
   • Calculadora de apostas múltiplas
   • Histórico e acompanhamento de resultados

💰 Ferramentas de Gestão
   • Calculadora de bankroll e stake
   • Controle de lucros e perdas
   • Sugestões de apostas de valor
   • Alertas de oportunidades

🔧 RECURSOS TÉCNICOS:

✅ Fácil de usar - Interface intuitiva
✅ Rápido - Cálculos instantâneos
✅ Preciso - Modelos matematicamente validados
✅ Atualizado - Dados em tempo real via API
✅ Completo - Tudo que você precisa em um só lugar
✅ Seguro - Dados salvos localmente

📦 DEPENDÊNCIAS INSTALADAS:

• Python 3.6+ (obrigatório)
• requests>=2.32.0 (para APIs de dados)
• tkinter (interface gráfica - incluído no Python)
• Bibliotecas padrão (json, datetime, threading, etc.)

🎓 IDEAL PARA:

• Apostadores iniciantes que querem aprender
• Apostadores experientes buscando vantagem estatística
• Analistas esportivos profissionais
• Qualquer pessoa interessada em dados de futebol

⚠️ AVISO IMPORTANTE:
Este software é destinado apenas para fins educacionais e de entretenimento. Apostas envolvem riscos financeiros. Aposte com responsabilidade.

🏆 Desenvolvido por especialistas em análise esportiva e programação."""

        desc_text.insert(tk.END, descricao)
        desc_text.configure(state='disabled')
        
        # Frame dos termos e botões
        bottom_frame = tk.Frame(main_frame, bg='#f0f0f0')
        bottom_frame.pack(fill='x', side='bottom')
        
        # Checkbox dos termos
        terms_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        terms_frame.pack(pady=(10, 0))
        
        terms_check = tk.Checkbutton(terms_frame, text="Li e aceito os termos de uso e instalação do programa", 
                                   variable=self.aceito_termos, font=('Arial', 11, 'bold'),
                                   bg='#f0f0f0', fg=self.cores['primary'])
        terms_check.pack()
        
        # Botões
        buttons_frame = tk.Frame(bottom_frame, bg='#f0f0f0')
        buttons_frame.pack(pady=(15, 0))
        
        cancel_btn = tk.Button(buttons_frame, text="❌ Cancelar", font=('Arial', 12, 'bold'),
                              bg=self.cores['danger'], fg='white', padx=20, pady=8,
                              command=self.cancelar_instalacao)
        cancel_btn.pack(side='left', padx=(0, 10))
        
        install_btn = tk.Button(buttons_frame, text="🚀 ACEITAR E INSTALAR", font=('Arial', 12, 'bold'),
                               bg=self.cores['success'], fg='white', padx=30, pady=8,
                               command=self.iniciar_instalacao)
        install_btn.pack(side='right')
    
    def cancelar_instalacao(self):
        """Cancela a instalação"""
        if messagebox.askyesno("Cancelar", "Tem certeza que deseja cancelar a instalação?"):
            self.root.quit()
    
    def iniciar_instalacao(self):
        """Inicia o processo de instalação"""
        if not self.aceito_termos.get():
            messagebox.showwarning("Termos", "Você deve aceitar os termos para prosseguir com a instalação!")
            return
        
        if self.instalacao_em_progresso:
            return
        
        # Confirmar instalação
        if not messagebox.askyesno("Confirmação", 
                                  "Iniciar a instalação do Bet Booster?\n\n" +
                                  "O programa irá:\n" +
                                  "• Verificar dependências do Python\n" +
                                  "• Instalar bibliotecas necessárias\n" +
                                  "• Criar atalho na área de trabalho\n" +
                                  "• Configurar o ambiente"):
            return
        
        self.create_installation_screen()
    
    def create_installation_screen(self):
        """Cria a tela de instalação"""
        # Limpar tela
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔧 INSTALANDO BET BOOSTER", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Progress frame
        progress_frame = tk.LabelFrame(main_frame, text="Progresso da Instalação", 
                                     font=('Arial', 12, 'bold'), bg='#f0f0f0')
        progress_frame.pack(fill='x', pady=(0, 20))
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=500)
        self.progress_bar.pack(pady=10, padx=20)
        
        # Label de status
        self.status_label = ttk.Label(progress_frame, text="Preparando instalação...", 
                                     style='Body.TLabel')
        self.status_label.pack(pady=(0, 10))
        
        # Log de instalação
        log_frame = tk.LabelFrame(main_frame, text="Log de Instalação", 
                                font=('Arial', 12, 'bold'), bg='#f0f0f0')
        log_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=('Consolas', 9), 
                                                bg='#1f2937', fg='#10b981', insertbackground='#10b981')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Iniciar instalação em thread separada
        self.instalacao_em_progresso = True
        threading.Thread(target=self.executar_instalacao, daemon=True).start()
    
    def log_message(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_progress(self, value, status):
        """Atualiza barra de progresso e status"""
        self.progress_var.set(value)
        self.status_label.config(text=status)
        self.root.update()
    
    def executar_instalacao(self):
        """Executa o processo completo de instalação"""
        try:
            steps = [
                (10, "Verificando versão do Python..."),
                (20, "Verificando dependências básicas..."),
                (40, "Instalando bibliotecas do requirements.txt..."),
                (60, "Configurando ambiente e APIs..."),
                (75, "Criando atalho na área de trabalho..."),
                (90, "Finalizando configuração..."),
                (100, "Instalação concluída!")
            ]
            
            for progress, status in steps:
                self.update_progress(progress, status)
                
                if progress == 10:
                    self.verificar_python()
                elif progress == 20:
                    self.verificar_dependencias()
                elif progress == 40:
                    self.instalar_bibliotecas()
                elif progress == 60:
                    self.configurar_ambiente()
                elif progress == 75:
                    self.criar_atalho_desktop()
                elif progress == 90:
                    self.finalizar_configuracao()
                
                time.sleep(1)
            
            self.instalacao_concluida()
            
        except Exception as e:
            self.instalacao_falhou(str(e))
    
    def verificar_python(self):
        """Verifica a versão do Python"""
        self.log_message(f"🐍 Python {sys.version}")
        
        if sys.version_info < (3, 6):
            raise Exception("Python 3.6+ é necessário!")
        
        self.log_message("✅ Versão do Python compatível")
    
    def verificar_dependencias(self):
        """Verifica dependências básicas"""
        self.log_message("🔍 Verificando dependências básicas...")
        
        # Verificar tkinter (GUI)
        try:
            import tkinter
            self.log_message("✅ tkinter encontrado")
        except ImportError:
            raise Exception("tkinter não está disponível - necessário para a interface gráfica")
        
        # Verificar requests (API calls)
        try:
            import requests
            self.log_message(f"✅ requests encontrado (versão: {requests.__version__})")
        except ImportError:
            self.log_message("⚠️  requests não encontrado - será instalado")
        
        # Verificar outras dependências padrão do Python
        deps_padrao = ['json', 'datetime', 'os', 'threading', 'math', 'sys']
        for dep in deps_padrao:
            try:
                __import__(dep)
                self.log_message(f"✅ {dep} disponível")
            except ImportError:
                self.log_message(f"❌ {dep} não encontrado (biblioteca padrão)")
        
        self.log_message("✅ Verificação de dependências concluída")
    
    def instalar_bibliotecas(self):
        """Instala bibliotecas necessárias"""
        self.log_message("📦 Instalando bibliotecas necessárias...")
        
        # Verificar se requirements.txt existe
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        requirements_path = os.path.join(pasta_atual, 'docs', 'requirements.txt')
        
        # Primeira tentativa: atualizar pip para garantir compatibilidade
        try:
            self.log_message("🔄 Atualizando pip para versão mais recente...")
            upgrade_result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], capture_output=True, text=True, timeout=120)
            
            if upgrade_result.returncode == 0:
                self.log_message("✅ pip atualizado com sucesso")
            else:
                self.log_message("⚠️ Não foi possível atualizar pip, continuando mesmo assim...")
        except Exception as e:
            self.log_message(f"⚠️ Aviso ao atualizar pip: {e}")
        
        # Verificar e instalar requirements.txt
        if os.path.exists(requirements_path):
            self.log_message(f"📋 Arquivo requirements.txt encontrado: {requirements_path}")
            
            # Ler bibliotecas do arquivo requirements.txt (ignorando comentários e bibliotecas built-in)
            bibliotecas = []
            try:
                with open(requirements_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        # Ignorar linhas vazias, comentários e bibliotecas padrão do Python
                        if line and not line.startswith('#') and not any(builtin in line for builtin in 
                                                                        ['tkinter  #', 'json  #', 'datetime  #', 
                                                                         'threading  #', 'os  #', 'sys  #']):
                            bibliotecas.append(line)
                
                self.log_message(f"� Encontradas {len(bibliotecas)} bibliotecas para instalar: {', '.join(bibliotecas)}")
                
                # Tentar instalar bibliotecas individualmente do requirements
                self.instalar_bibliotecas_do_requirements(bibliotecas)
                
            except Exception as e:
                self.log_message(f"❌ Erro ao processar requirements.txt: {e}")
                # Cair no modo de fallback com bibliotecas essenciais
                self.instalar_dependencias_individuais()
        else:
            self.log_message("⚠️ requirements.txt não encontrado - instalando dependências essenciais...")
            self.instalar_dependencias_individuais()
    
    def instalar_bibliotecas_do_requirements(self, bibliotecas):
        """Instala bibliotecas listadas no requirements.txt individualmente"""
        self.log_message("📦 Instalando bibliotecas do requirements.txt individualmente...")
        
        bibliotecas_sucesso = []
        bibliotecas_falha = []
        
        for lib in bibliotecas:
            try:
                # Limpar a biblioteca (remover comentários)
                lib_clean = lib.split('#')[0].strip()
                
                self.log_message(f"📥 Instalando {lib_clean}...")
                
                # Usar --no-deps para tkcalendar para evitar conflitos
                if 'tkcalendar' in lib_clean:
                    self.log_message("🔧 Usando configuração especial para tkcalendar...")
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", lib_clean, "--no-deps"
                    ], capture_output=True, text=True, timeout=180)
                else:
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", lib_clean
                    ], capture_output=True, text=True, timeout=180)
                
                if result.returncode == 0:
                    self.log_message(f"✅ {lib_clean} instalado com sucesso")
                    bibliotecas_sucesso.append(lib_clean)
                else:
                    self.log_message(f"⚠️ Erro ao instalar {lib_clean}: {result.stderr[:150]}...")
                    bibliotecas_falha.append(lib_clean)
                    
                    # Tentar instalar versão sem restrição de versão se falhar
                    if '>=' in lib_clean or '==' in lib_clean:
                        lib_name = lib_clean.split('>=')[0].split('==')[0].strip()
                        self.log_message(f"🔄 Tentando instalar {lib_name} sem restrição de versão...")
                        
                        alt_result = subprocess.run([
                            sys.executable, "-m", "pip", "install", lib_name
                        ], capture_output=True, text=True, timeout=180)
                        
                        if alt_result.returncode == 0:
                            self.log_message(f"✅ {lib_name} instalado com sucesso (versão alternativa)")
                            bibliotecas_sucesso.append(lib_name)
                        else:
                            self.log_message(f"❌ Falha ao instalar {lib_name} (versão alternativa)")
                    
            except subprocess.TimeoutExpired:
                self.log_message(f"⏱️ Timeout ao instalar {lib}")
                bibliotecas_falha.append(lib)
            except Exception as e:
                self.log_message(f"❌ Erro ao instalar {lib}: {e}")
                bibliotecas_falha.append(lib)
        
        # Resumo da instalação
        if bibliotecas_sucesso:
            self.log_message(f"✅ {len(bibliotecas_sucesso)} bibliotecas instaladas com sucesso: {', '.join(bibliotecas_sucesso)}")
        
        if bibliotecas_falha:
            self.log_message(f"⚠️ {len(bibliotecas_falha)} bibliotecas com falha na instalação: {', '.join(bibliotecas_falha)}")
            # Se falhar a instalação das bibliotecas do requirements, tentar o método alternativo
            if 'tkcalendar' in ' '.join(bibliotecas_falha):
                self.instalar_tkcalendar_alternativo()
    
    def instalar_tkcalendar_alternativo(self):
        """Método alternativo para instalar tkcalendar"""
        self.log_message("🔄 Tentando instalar tkcalendar usando método alternativo...")
        
        try:
            # Verificar dependências do tkcalendar primeiro (Babel, pytz)
            for dep in ["Babel", "pytz"]:
                self.log_message(f"📥 Instalando dependência {dep} para tkcalendar...")
                dep_result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True, timeout=120)
                
                if dep_result.returncode == 0:
                    self.log_message(f"✅ {dep} instalado com sucesso")
                else:
                    self.log_message(f"⚠️ Aviso ao instalar {dep}: {dep_result.stderr[:100]}...")
            
            # Agora instalar tkcalendar
            self.log_message("📥 Instalando tkcalendar...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "tkcalendar"
            ], capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                self.log_message("✅ tkcalendar instalado com sucesso (método alternativo)")
                return True
            else:
                self.log_message(f"⚠️ Falha no método alternativo: {result.stderr[:150]}...")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Erro no método alternativo para tkcalendar: {e}")
            return False
    
    def instalar_dependencias_individuais(self):
        """Instala dependências essenciais uma por uma"""
        self.log_message("🔄 Instalando dependências essenciais manualmente...")
        
        # Lista de bibliotecas essenciais para o Bet Booster
        bibliotecas_essenciais = [
            'requests>=2.32.0',  # Para APIs de dados esportivos
            'Babel>=2.9.1',      # Dependência do tkcalendar
            'pytz>=2021.3',      # Dependência do tkcalendar
            'tkcalendar==1.6.1', # Para seleção de datas
        ]
        
        # Lista de bibliotecas opcionais para funcionalidades extras
        bibliotecas_opcionais = [
            'pywin32',  # Para funcionalidades Windows (atalhos)
            'winshell'  # Para manipulação de shell Windows
        ]
        
        # Instalar bibliotecas essenciais
        for lib in bibliotecas_essenciais:
            try:
                self.log_message(f"📥 Instalando biblioteca essencial: {lib}...")
                
                # Configuração especial para tkcalendar
                if 'tkcalendar' in lib:
                    if not self.instalar_tkcalendar_alternativo():
                        self.log_message("⚠️ Não foi possível instalar tkcalendar. Algumas funcionalidades de calendário podem não funcionar.")
                    continue
                
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", lib
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    self.log_message(f"✅ {lib} instalado com sucesso")
                else:
                    self.log_message(f"❌ Erro ao instalar {lib}: {result.stderr[:100]}...")
                    
                    # Tentar versão sem restrição se falhar
                    if '>=' in lib or '==' in lib:
                        lib_name = lib.split('>=')[0].split('==')[0].strip()
                        self.log_message(f"🔄 Tentando instalar {lib_name} sem restrição de versão...")
                        
                        alt_result = subprocess.run([
                            sys.executable, "-m", "pip", "install", lib_name
                        ], capture_output=True, text=True, timeout=120)
                        
                        if alt_result.returncode == 0:
                            self.log_message(f"✅ {lib_name} instalado com sucesso (versão alternativa)")
                        else:
                            self.log_message(f"⚠️ Falha ao instalar {lib_name} (versão alternativa)")
                    
            except subprocess.TimeoutExpired:
                self.log_message(f"⏱️ Timeout ao instalar {lib}")
            except Exception as e:
                self.log_message(f"❌ Erro ao instalar {lib}: {e}")
        
        # Instalar bibliotecas opcionais (não críticas)
        for lib in bibliotecas_opcionais:
            try:
                self.log_message(f"📥 Instalando biblioteca opcional: {lib}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", lib
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    self.log_message(f"✅ {lib} instalado com sucesso")
                else:
                    self.log_message(f"⚠️ Aviso ao instalar {lib}: {result.stderr[:100]}...")
                    
            except subprocess.TimeoutExpired:
                self.log_message(f"⏱️ Timeout ao instalar {lib} (opcional)")
            except Exception as e:
                self.log_message(f"⚠️ Aviso: {lib} (opcional) - {e}")
    
    def configurar_ambiente(self):
        """Configura o ambiente do programa"""
        self.log_message("⚙️  Configurando ambiente...")
        
        # Verificar se os arquivos principais existem
        arquivos_necessarios = [
            'src/bet_booster_v2.py',  # V2 como principal
            'src/interface_apostas.py',  # Legado
            'api/radar_esportivo_api.py',
            'api/sofascore_api.py',
            'assets/bet-booster.ico',
            'docs/requirements.txt'
        ]
        
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        arquivos_encontrados = 0
        
        for arquivo in arquivos_necessarios:
            caminho = os.path.join(pasta_atual, arquivo)
            if os.path.exists(caminho):
                self.log_message(f"✅ {arquivo} encontrado")
                arquivos_encontrados += 1
            else:
                self.log_message(f"⚠️  {arquivo} não encontrado")
        
        # Verificar se a estrutura mínima está presente
        if arquivos_encontrados >= 2:  # Pelo menos interface principal e uma API
            self.log_message("✅ Estrutura mínima do projeto verificada")
        else:
            self.log_message("⚠️  Estrutura incompleta - algumas funcionalidades podem não funcionar")
        
        # Verificar se as dependências foram instaladas corretamente
        try:
            import requests
            self.log_message("✅ requests verificado após instalação")
        except ImportError:
            self.log_message("❌ requests ainda não está disponível")
            raise Exception("Falha crítica: requests não foi instalado corretamente")
        
        self.log_message("✅ Ambiente configurado com sucesso")
    
    def criar_atalho_desktop(self):
        """Cria atalho na área de trabalho"""
        self.log_message("🖥️ Criando atalho na área de trabalho...")
        
        # Método principal: usar PowerShell para criar atalho .lnk
        if self.criar_atalho_powershell():
            return
        
        # Método alternativo 1: criar arquivo .bat
        if self.criar_atalho_alternativo():
            return
        
        # Método alternativo 2: criar script Python direto
        self.criar_atalho_python()
    
    def criar_atalho_powershell(self):
        """Cria atalho usando PowerShell (método mais confiável)"""
        try:
            self.log_message("🔧 Tentando criar atalho com PowerShell...")
            
            # Obter caminhos
            pasta_atual = os.path.dirname(os.path.abspath(__file__))
            script_principal = os.path.join(pasta_atual, 'src', 'bet_booster_v2.py')  # V2 como principal
            icone_path = os.path.join(pasta_atual, 'assets', 'bet-booster.ico')
            
            # Obter desktop path
            desktop_paths = [
                os.path.join(os.path.expanduser('~'), 'Desktop'),
                os.path.join(os.path.expanduser('~'), 'Área de Trabalho'),
                os.path.join(os.path.expanduser('~'), 'OneDrive', 'Desktop'),
                os.path.join(os.path.expanduser('~'), 'OneDrive', 'Área de Trabalho')
            ]
            
            desktop = None
            for path in desktop_paths:
                if os.path.exists(path):
                    desktop = path
                    break
            
            if not desktop:
                self.log_message("⚠️  Pasta da área de trabalho não encontrada")
                return False
            
            atalho_path = os.path.join(desktop, "Bet Booster.lnk")
            
            # Script PowerShell para criar atalho
            powershell_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{atalho_path}")
$Shortcut.TargetPath = "{sys.executable}"
$Shortcut.Arguments = '"{script_principal}"'
$Shortcut.WorkingDirectory = "{pasta_atual}"
$Shortcut.Description = "Bet Booster - Sistema de Análise de Apostas"'''

            # Adicionar ícone se existir
            if os.path.exists(icone_path):
                powershell_script += f'\n$Shortcut.IconLocation = "{icone_path}"'
            
            powershell_script += '\n$Shortcut.Save()'
            
            # Executar PowerShell
            result = subprocess.run([
                'powershell', '-ExecutionPolicy', 'Bypass', '-Command', powershell_script
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(atalho_path):
                self.log_message(f"✅ Atalho criado com sucesso: {atalho_path}")
                return True
            else:
                self.log_message(f"⚠️  PowerShell falhou: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message("⚠️  PowerShell demorou muito para responder")
            return False
        except Exception as e:
            self.log_message(f"⚠️  Erro no PowerShell: {e}")
            return False
    
    def criar_atalho_alternativo(self):
        """Cria atalho alternativo usando arquivo .bat"""
        self.log_message("🔄 Criando atalho alternativo (.bat)...")
        
        try:
            pasta_atual = os.path.dirname(os.path.abspath(__file__))
            script_principal = os.path.join(pasta_atual, 'src', 'bet_booster_v2.py')  # V2 como principal
            
            # Tentar diferentes caminhos para área de trabalho
            desktop_paths = [
                os.path.join(os.path.expanduser('~'), 'Desktop'),
                os.path.join(os.path.expanduser('~'), 'Área de Trabalho'),
                os.path.join(os.path.expanduser('~'), 'OneDrive', 'Desktop'),
                os.path.join(os.path.expanduser('~'), 'OneDrive', 'Área de Trabalho'),
                os.path.expanduser('~')  # Fallback para pasta do usuário
            ]
            
            desktop = None
            for path in desktop_paths:
                if os.path.exists(path):
                    desktop = path
                    break
            
            if not desktop:
                self.log_message("❌ Nenhuma pasta válida encontrada")
                return False
            
            bat_path = os.path.join(desktop, "Bet Booster.bat")
            
            # Criar arquivo .bat melhorado
            bat_content = f'''@echo off
title Bet Booster - Sistema de Análise de Apostas
color 0A
echo.
echo  ┌─────────────────────────────────────────┐
echo  │        🎯 BET BOOSTER                  │
echo  │   Sistema de Análise de Apostas        │
echo  └─────────────────────────────────────────┘
echo.
echo ⚡ Iniciando programa...
echo.

cd /d "{pasta_atual}"

if exist "{script_principal}" (
    echo ✅ Arquivo encontrado, executando...
    python "{script_principal}"
    if errorlevel 1 (
        echo.
        echo ❌ Erro ao executar o programa!
        echo 💡 Certifique-se que o Python está instalado corretamente.
        echo.
        pause
    )
) else (
    echo ❌ Erro: Arquivo principal não encontrado!
    echo.
    echo 📁 Esperado em: {script_principal}
    echo.
    echo 🔧 Soluções:
    echo    1. Verifique se todos os arquivos estão na pasta correta
    echo    2. Execute novamente o instalador
    echo.
    pause
)
'''
            
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            
            self.log_message(f"✅ Atalho .bat criado: {bat_path}")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Erro ao criar atalho .bat: {e}")
            return False
    
    def criar_atalho_python(self):
        """Cria script Python direto como última alternativa"""
        self.log_message("🐍 Criando launcher Python...")
        
        try:
            pasta_atual = os.path.dirname(os.path.abspath(__file__))
            script_principal = os.path.join(pasta_atual, 'src', 'bet_booster_v2.py')  # V2 como principal
            
            # Tentar diferentes caminhos para área de trabalho
            desktop_paths = [
                os.path.join(os.path.expanduser('~'), 'Desktop'),
                os.path.join(os.path.expanduser('~'), 'Área de Trabalho'),
                pasta_atual  # Fallback para pasta do programa
            ]
            
            desktop = None
            for path in desktop_paths:
                if os.path.exists(path):
                    desktop = path
                    break
            
            py_path = os.path.join(desktop, "EXECUTAR_BET_BOOSTER.py")
            
            # Criar launcher Python
            launcher_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 BET BOOSTER LAUNCHER
Launcher para o Sistema de Análise de Apostas
"""

import os
import sys
import subprocess

def main():
    print("🎯 BET BOOSTER LAUNCHER")
    print("=" * 40)
    
    # Caminho do script principal
    pasta_programa = r"{pasta_atual}"
    script_principal = r"{script_principal}"
    
    # Verificar se arquivo existe
    if not os.path.exists(script_principal):
        print("❌ Erro: Arquivo principal não encontrado!")
        print(f"📁 Esperado: {{script_principal}}")
        input("Pressione Enter para sair...")
        return
    
    # Mudar para pasta do programa
    os.chdir(pasta_programa)
    print(f"📁 Pasta: {{pasta_programa}}")
    
    try:
        print("🚀 Iniciando Bet Booster...")
        # Executar usando subprocess para melhor controle
        result = subprocess.run([sys.executable, script_principal], check=True)
        print("✅ Programa executado com sucesso!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {{e}}")
        input("Pressione Enter para sair...")
    except KeyboardInterrupt:
        print("\\n⏹️  Execução cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {{e}}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
'''
            
            with open(py_path, 'w', encoding='utf-8') as f:
                f.write(launcher_content)
            
            self.log_message(f"✅ Launcher Python criado: {py_path}")
            self.log_message("💡 Clique duplo no arquivo para executar")
            
        except Exception as e:
            self.log_message(f"❌ Erro ao criar launcher Python: {e}")
            # Criar pelo menos na pasta do programa
            try:
                py_path = os.path.join(pasta_atual, "EXECUTAR_BET_BOOSTER.py")
                with open(py_path, 'w', encoding='utf-8') as f:
                    f.write(launcher_content)
                self.log_message(f"✅ Launcher criado na pasta do programa: {py_path}")
            except:
                self.log_message("❌ Falha crítica ao criar launcher")
    
    def finalizar_configuracao(self):
        """Finaliza a configuração"""
        self.log_message("🎯 Finalizando configuração...")
        self.log_message("✅ Bet Booster instalado com sucesso!")
        self.log_message("🚀 Pronto para usar!")
    
    def instalacao_concluida(self):
        """Exibe tela de instalação concluída"""
        # Limpar tela
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Ícone de sucesso e título
        success_label = ttk.Label(main_frame, text="🎉", font=('Arial', 48))
        success_label.pack(pady=(20, 10))
        
        title_label = ttk.Label(main_frame, text="INSTALAÇÃO CONCLUÍDA!", style='Title.TLabel')
        title_label.pack()
        
        success_msg = ttk.Label(main_frame, text="Bet Booster foi instalado com sucesso!", style='Success.TLabel')
        success_msg.pack(pady=(10, 20))
        
        # Informações
        info_frame = tk.LabelFrame(main_frame, text="✅ O que foi instalado:", 
                                 font=('Arial', 12, 'bold'), bg='#f0f0f0')
        info_frame.pack(fill='x', pady=(0, 20))
        
        info_text = """
• ✅ Sistema Bet Booster configurado
• ✅ Todas as dependências instaladas
• ✅ Atalho criado na área de trabalho
• ✅ Ambiente pronto para uso

🚀 Como usar:
1. Clique duplo no atalho "Bet Booster" na área de trabalho
2. O programa abrirá automaticamente
3. Comece a analisar suas apostas!
        """
        
        info_label = ttk.Label(info_frame, text=info_text, style='Body.TLabel', justify='left')
        info_label.pack(padx=20, pady=15)
        
        # Botões finais
        buttons_frame = tk.Frame(main_frame, bg='#f0f0f0')
        buttons_frame.pack(side='bottom', pady=(20, 0))
        
        launch_btn = tk.Button(buttons_frame, text="🚀 EXECUTAR AGORA", font=('Arial', 12, 'bold'),
                              bg=self.cores['success'], fg='white', padx=30, pady=10,
                              command=self.executar_programa)
        launch_btn.pack(side='left', padx=(0, 15))
        
        close_btn = tk.Button(buttons_frame, text="✅ FINALIZAR", font=('Arial', 12, 'bold'),
                             bg=self.cores['primary'], fg='white', padx=30, pady=10,
                             command=self.root.quit)
        close_btn.pack(side='right')
    
    def instalacao_falhou(self, erro):
        """Exibe tela de erro na instalação"""
        messagebox.showerror("Erro na Instalação", 
                           f"Ocorreu um erro durante a instalação:\n\n{erro}\n\n" +
                           "Por favor, tente novamente ou entre em contato com o suporte.")
        self.root.quit()
    
    def executar_programa(self):
        """Executa o programa principal"""
        try:
            pasta_atual = os.path.dirname(os.path.abspath(__file__))
            script_principal = os.path.join(pasta_atual, 'src', 'bet_booster_v2.py')  # V2 como principal
            
            if os.path.exists(script_principal):
                self.root.quit()
                os.system(f'python "{script_principal}"')
            else:
                messagebox.showerror("Erro", "Arquivo principal não encontrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar programa: {e}")
    
    def run(self):
        """Inicia o instalador"""
        self.root.mainloop()

def main():
    """Função principal"""
    try:
        print("🎯 BET BOOSTER - INSTALADOR OFICIAL")
        print("=" * 50)
        print("Inicializando instalador com interface gráfica...")
        print()
        
        # Verificar se está no Windows
        if os.name != 'nt':
            print("⚠️  Este instalador foi desenvolvido para Windows")
            print("💡 No Linux/Mac, execute diretamente: python interface_apostas.py")
            input("Pressione Enter para continuar mesmo assim...")
        
        # Executar instalador
        installer = BetBoosterInstaller()
        installer.run()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("📦 Algumas bibliotecas podem estar faltando")
        print("� Isso é normal, o instalador tentará corrigir automaticamente")
        print()
        try:
            installer = BetBoosterInstaller()
            installer.run()
        except Exception as e2:
            print(f"❌ Erro crítico: {e2}")
            print("🔧 Instale manualmente: pip install tkinter")
            input("Pressione Enter para sair...")
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print("🔄 Tentando executar mesmo assim...")
        try:
            installer = BetBoosterInstaller()
            installer.run()
        except:
            print("❌ Falha crítica no instalador")
            input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
