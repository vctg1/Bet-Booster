#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BET BOOSTER V2 - Sistema Completo de Análise de Apostas
Reestruturação completa com novas funcionalidades
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkcalendar import DateEntry
import json
import math
from datetime import datetime, timedelta
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Importar API Radar Esportivo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.radar_esportivo_api import RadarEsportivoAPI

class BetBoosterV2:
    def __init__(self, root):
        self.root = root
        self.root.title("BET BOOSTER V2 - Sistema Avançado de Análise de Apostas")
        self.root.geometry("1200x800")
        
        # Dados do sistema
        self.times_database = {}
        self.jogos_do_dia = []
        self.apostas_multipla = []
        self.apostas_hot = []
        
        # Variáveis de controle
        self.modo_analise = tk.StringVar(value="detalhado")  # Modo padrão
        
        # Modo Escuro - detectar hora do dia para ativar automaticamente
        hora_atual = datetime.now().hour
        # Ativar modo escuro entre 18h e 6h
        self.modo_escuro = tk.BooleanVar(value=(hora_atual >= 18 or hora_atual < 6))
        
        # Definir cores do tema
        self.atualizar_cores_tema()
        
        # Configurar estilos ttk
        self.configurar_estilos_ttk()
        
        # API Integration
        self.api = RadarEsportivoAPI()
        
        # Sistema de Banca Simulada
        self.banca_data = {}
        self.apostas_ativas = []
        self.historico_apostas = []
        self.carregar_dados_banca()
        
        # Mostrar tela de carregamento
        self.mostrar_tela_carregamento()
        
        # Configurar interface (será feito após carregamento)
        self.main_widgets_created = False
    
    def atualizar_cores_tema(self):
        """Define as cores baseado no modo escuro ou claro"""
        if self.modo_escuro.get():
            # Modo Escuro
            self.cores = {
                'bg_principal': '#2b2b2b',        # Cinza escuro principal
                'bg_secundario': '#3a3a3a',       # Cinza escuro secundário
                'bg_terciario': '#4a4a4a',        # Cinza médio
                'bg_frame': '#353535',            # Cinza para frames
                'bg_card': '#404040',             # Cinza para cards
                'fg_titulo': '#ffffff',           # Texto títulos
                'fg_normal': '#e0e0e0',           # Texto normal
                'fg_secundario': '#b0b0b0',       # Texto secundário
                'bg_input': '#505050',            # Fundo inputs
                'fg_input': '#ffffff',            # Texto inputs
                'bg_button': '#505050',           # Fundo botões
                'border': '#5a5a5a'               # Bordas
            }
        else:
            # Modo Claro
            self.cores = {
                'bg_principal': '#f0f0f0',
                'bg_secundario': '#ffffff',
                'bg_terciario': '#f8f9fa',
                'bg_frame': '#ffffff',
                'bg_card': '#ffffff',
                'fg_titulo': '#1e40af',
                'fg_normal': '#374151',
                'fg_secundario': '#6b7280',
                'bg_input': '#ffffff',
                'fg_input': '#000000',
                'bg_button': '#ffffff',
                'border': '#e5e7eb'
            }
    
    def toggle_modo_escuro(self):
        """Alterna entre modo escuro e claro"""
        self.modo_escuro.set(not self.modo_escuro.get())
        self.atualizar_cores_tema()
        self.configurar_estilos_ttk()
        self.aplicar_tema_interface()
    
    def configurar_estilos_ttk(self):
        """Configura os estilos dos widgets ttk baseado no tema"""
        style = ttk.Style()
        
        if self.modo_escuro.get():
            # Configurar tema escuro para ttk
            style.theme_use('clam')  # Base theme que permite customização
            
            # Cores do modo escuro
            style.configure('.',
                          background=self.cores['bg_principal'],
                          foreground=self.cores['fg_normal'],
                          fieldbackground=self.cores['bg_input'],
                          bordercolor=self.cores['border'],
                          darkcolor=self.cores['bg_secundario'],
                          lightcolor=self.cores['bg_terciario'])
            
            # LabelFrame
            style.configure('TLabelframe',
                          background=self.cores['bg_frame'],
                          foreground=self.cores['fg_titulo'],
                          bordercolor=self.cores['border'])
            style.configure('TLabelframe.Label',
                          background=self.cores['bg_frame'],
                          foreground=self.cores['fg_titulo'])
            
            # Notebook (abas)
            style.configure('TNotebook',
                          background=self.cores['bg_principal'],
                          bordercolor=self.cores['border'])
            style.configure('TNotebook.Tab',
                          background=self.cores['bg_secundario'],
                          foreground=self.cores['fg_normal'],
                          padding=[10, 5])
            style.map('TNotebook.Tab',
                    background=[('selected', self.cores['bg_terciario'])],
                    foreground=[('selected', self.cores['fg_titulo'])])
            
            # Button
            style.configure('TButton',
                          background=self.cores['bg_button'],
                          foreground=self.cores['fg_normal'],
                          bordercolor=self.cores['border'],
                          padding=5)
            style.map('TButton',
                    background=[('active', self.cores['bg_terciario'])])
            
            # Entry
            style.configure('TEntry',
                          fieldbackground=self.cores['bg_input'],
                          foreground=self.cores['fg_input'],
                          bordercolor=self.cores['border'])
            
            # Combobox
            style.configure('TCombobox',
                          fieldbackground=self.cores['bg_input'],
                          foreground=self.cores['fg_input'],
                          background=self.cores['bg_button'],
                          bordercolor=self.cores['border'])
            
            # Label
            style.configure('TLabel',
                          background=self.cores['bg_principal'],
                          foreground=self.cores['fg_normal'])
            
            # Frame
            style.configure('TFrame',
                          background=self.cores['bg_principal'])
            
            # Treeview
            style.configure('Treeview',
                          background=self.cores['bg_input'],
                          foreground=self.cores['fg_input'],
                          fieldbackground=self.cores['bg_input'],
                          bordercolor=self.cores['border'])
            style.configure('Treeview.Heading',
                          background=self.cores['bg_secundario'],
                          foreground=self.cores['fg_titulo'],
                          bordercolor=self.cores['border'])
            style.map('Treeview',
                    background=[('selected', self.cores['bg_terciario'])],
                    foreground=[('selected', self.cores['fg_titulo'])])
            
        else:
            # Voltar ao tema padrão claro
            style.theme_use('vista')  # ou 'winnative' no Windows
    
    def aplicar_tema_interface(self):
        """Aplica o tema atual em toda a interface"""
        if not hasattr(self, 'notebook'):
            return
        
        # Atualizar cor de fundo da janela principal
        self.root.configure(bg=self.cores['bg_principal'])
        
        # Atualizar todas as abas
        for widget in self.root.winfo_children():
            self.atualizar_widget_cores(widget)
    
    def atualizar_widget_cores(self, widget):
        """Atualiza recursivamente as cores de um widget e seus filhos"""
        try:
            # Atualizar Frame
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.cores['bg_principal'])
            
            # Atualizar Label
            elif isinstance(widget, tk.Label):
                widget.configure(bg=self.cores['bg_principal'], fg=self.cores['fg_normal'])
            
            # Atualizar LabelFrame
            elif isinstance(widget, tk.LabelFrame):
                widget.configure(bg=self.cores['bg_frame'])
            
            # Recursivamente atualizar widgets filhos
            for child in widget.winfo_children():
                self.atualizar_widget_cores(child)
        except:
            pass
    
    def mostrar_tela_carregamento(self):
        """Mostra tela de carregamento inicial"""
        # Frame de carregamento
        self.loading_frame = tk.Frame(self.root, bg=self.cores['bg_principal'])
        self.loading_frame.pack(fill='both', expand=True)
        
        # Logo/Título
        title_label = tk.Label(self.loading_frame, text="🎯 BET BOOSTER V2", 
                              font=('Arial', 24, 'bold'), fg='#1e40af', bg=self.cores['bg_principal'])
        title_label.pack(pady=(100, 20))
        
        subtitle_label = tk.Label(self.loading_frame, text="Sistema Avançado de Análise de Apostas", 
                                 font=('Arial', 14), fg=self.cores['fg_normal'], bg=self.cores['bg_principal'])
        subtitle_label.pack(pady=(0, 50))
        
        # Frame para o progresso
        progress_frame = tk.Frame(self.loading_frame, bg=self.cores['bg_principal'])
        progress_frame.pack(pady=20)
        
        # Etapa atual de processamento (em destaque)
        self.loading_etapa = tk.Label(progress_frame, text="Inicializando...", 
                                    font=('Arial', 12, 'bold'), fg='#1e40af', bg=self.cores['bg_principal'])
        self.loading_etapa.pack(pady=(0, 15))
        
        # Frame para a barra e porcentagem
        bar_frame = tk.Frame(progress_frame, bg=self.cores['bg_principal'])
        bar_frame.pack(fill='x')
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(bar_frame, 
                                          variable=self.progress_var, 
                                          maximum=100, 
                                          length=400, 
                                          mode='determinate',
                                          style='Blue.Horizontal.TProgressbar')
        self.progress_bar.pack(side='left', padx=(0, 10))
        
        # Label para porcentagem
        self.progress_percent = tk.Label(bar_frame, text="0%", 
                                       font=('Arial', 10, 'bold'), fg='#1e40af', bg=self.cores['bg_principal'])
        self.progress_percent.pack(side='left')
        
        # Configurar estilo da barra de progresso
        style = ttk.Style()
        style.configure('Blue.Horizontal.TProgressbar', 
                       background='#3b82f6',
                       troughcolor='#e5e7eb',
                       borderwidth=0,
                       thickness=20)
        
        # Iniciar carregamento
        self.root.after(500, self.iniciar_carregamento)
    
    def iniciar_carregamento(self):
        """Inicia o processo de carregamento"""
        threading.Thread(target=self.executar_carregamento, daemon=True).start()
    
    # ==========================================
    # FUNÇÕES DE CACHE PARA JOGOS
    # ==========================================
    
    def get_cache_file_path(self, data):
        """Retorna o caminho do arquivo de cache para uma data específica"""
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        return os.path.join(cache_dir, f'jogos_{data}.json')
    
    def limpar_cache_antigo(self):
        """Limpa arquivos de cache com mais de 7 dias de idade"""
        try:
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
            if not os.path.exists(cache_dir):
                return
            
            data_hoje = datetime.now()
            arquivos_removidos = 0
            
            # Verificar todos os arquivos de cache
            for arquivo in os.listdir(cache_dir):
                if arquivo.startswith('jogos_') and arquivo.endswith('.json'):
                    # Extrair data do nome do arquivo
                    try:
                        data_str = arquivo.replace('jogos_', '').replace('.json', '')
                        data_arquivo = datetime.strptime(data_str, '%Y-%m-%d')
                        
                        # Calcular diferença de dias
                        diferenca_dias = (data_hoje - data_arquivo).days
                        
                        # Remover arquivos com mais de 7 dias
                        if diferenca_dias > 7:
                            arquivo_path = os.path.join(cache_dir, arquivo)
                            os.remove(arquivo_path)
                            arquivos_removidos += 1
                            print(f"🗑️ Cache antigo removido (mais de 7 dias): {arquivo}")
                    except ValueError:
                        # Nome de arquivo inválido, ignorar
                        continue
            
            if arquivos_removidos > 0:
                print(f"✅ {arquivos_removidos} arquivos de cache com mais de 7 dias removidos")
            else:
                print("✅ Nenhum cache antigo para remover")
                
        except Exception as e:
            print(f"⚠️ Erro ao limpar cache antigo: {e}")
    
    def verificar_cache_diario(self):
        """Verifica se precisa atualizar cache diário - só atualiza se não houver dados de hoje ou amanhã"""
        try:
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # PRIMEIRO: Atualizar períodos das apostas hot no cache
            self.atualizar_cache_periodo_apostas_hot()
            
            cache_hoje = self.carregar_jogos_cache(data_hoje)
            cache_amanha = self.carregar_jogos_cache(data_amanha)
            
            # Cache é válido se existir - não há expiração por tempo
            cache_hoje_valido = cache_hoje is not None
            cache_amanha_valido = cache_amanha is not None
            
            if cache_hoje_valido:
                print(f"📁 Cache de hoje encontrado: {len(cache_hoje['jogos'])} jogos")
            else:
                print("🔄 Cache de hoje não encontrado - será carregado da API")
                
            if cache_amanha_valido:
                print(f"📁 Cache de amanhã encontrado: {len(cache_amanha['jogos'])} jogos")
            else:
                print("🔄 Cache de amanhã não encontrado - será carregado da API")
            
            return cache_hoje_valido, cache_amanha_valido
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar cache diário: {e}")
            return False, False
            
        except Exception as e:
            print(f"⚠️ Erro ao verificar cache diário: {e}")
            return False, False
    
    def salvar_jogos_cache(self, data, jogos_dados):
        """Salva jogos e apostas hot no cache JSON"""
        try:
            cache_file = self.get_cache_file_path(data)
            
            cache_data = {
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'jogos': jogos_dados.get('jogos', []),
                'apostas_hot': jogos_dados.get('apostas_hot', []),
                'total_jogos': len(jogos_dados.get('jogos', [])),
                'total_apostas_hot': len(jogos_dados.get('apostas_hot', []))
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Cache salvo: {cache_data['total_jogos']} jogos, {cache_data['total_apostas_hot']} apostas hot")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar cache: {e}")
            return False
    
    def carregar_jogos_cache(self, data):
        """Carrega jogos do cache se disponível"""
        try:
            cache_file = self.get_cache_file_path(data)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Cache sem expiração por tempo - sempre válido se existir
            timestamp = datetime.fromisoformat(cache_data['timestamp'])
            
            print(f"✅ Cache válido carregado: {cache_data['total_jogos']} jogos, {cache_data['total_apostas_hot']} apostas hot")
            print(f"   Última atualização: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
            
            return {
                'jogos': cache_data.get('jogos', []),
                'apostas_hot': cache_data.get('apostas_hot', []),
                'timestamp': timestamp
            }
            
        except Exception as e:
            print(f"❌ Erro ao carregar cache: {e}")
            return None
            
        except Exception as e:
            print(f"❌ Erro ao carregar cache: {e}")
            return None
    
    def atualizar_jogos_do_dia_com_cache(self, data):
        """Atualiza jogos do dia usando cache quando possível"""
        try:
            # Tentar carregar do cache primeiro
            cache_data = self.carregar_jogos_cache(data)
            
            if cache_data:
                # Usar dados do cache APENAS PARA JOGOS DO DIA, NÃO PARA APOSTAS HOT
                self.jogos_do_dia = cache_data['jogos']
                # NÃO ALTERAR self.apostas_hot aqui para não afetar a aba de apostas hot
                
                # Só atualizar lista se a interface já foi criada
                if hasattr(self, 'tree_jogos'):
                    self.atualizar_lista_jogos()
                
                timestamp = cache_data['timestamp']
                tempo_cache = timestamp.strftime('%H:%M:%S')
                
                # Só atualizar status se o widget já foi criado
                if hasattr(self, 'status_jogos'):
                    self.status_jogos.config(
                        text=f"✅ {len(self.jogos_do_dia)} jogos carregados (cache {tempo_cache})", 
                        style='Success.TLabel'
                    )
                return True
            
            # Se não há cache válido, carregar normalmente
            return False
            
        except Exception as e:
            print(f"❌ Erro ao atualizar com cache: {e}")
            return False
    
    def executar_carregamento(self):
        """Executa o carregamento completo"""
        try:
            # Etapa 1: Carregar database
            self.atualizar_loading(5, "Inicializando sistema...")
            time.sleep(0.5)
            
            self.atualizar_loading(10, "Carregando database de times...")
            self.carregar_dados()
            time.sleep(0.3)
            
            # Etapa 2: Configurar estilos
            self.atualizar_loading(15, "Configurando interface do usuário...")
            self.setup_styles()
            time.sleep(0.3)
            
            # Etapa 3: Limpar cache antigo
            self.atualizar_loading(20, "Verificando e limpando cache antigo...")
            self.limpar_cache_antigo()
            time.sleep(0.2)
            
            # Etapa 4: Buscar jogos de hoje (com cache)
            self.atualizar_loading(25, "Verificando jogos de hoje na API...")
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            data_formatada = datetime.now().strftime('%d/%m/%Y')
            
            # Tentar carregar do cache primeiro
            cache_hoje = self.carregar_jogos_cache(data_hoje)
            if cache_hoje:
                self.atualizar_loading(30, "Carregando jogos de hoje do cache local...")
                print(f"📁 Usando cache para hoje: {len(cache_hoje['jogos'])} jogos")
                jogos_hoje = cache_hoje['jogos']
                apostas_hot_hoje = cache_hoje['apostas_hot']
                
                # Adicionar data_jogo a cada aposta para filtro correto
                for aposta in apostas_hot_hoje:
                    aposta['data_jogo'] = data_hoje
                    # Definir período para a data formatada para exibição no card
                    aposta['periodo'] = data_formatada
            else:
                self.atualizar_loading(30, "Buscando jogos de hoje na API...")
                jogos_hoje = self.api.buscar_jogos_do_dia(data_hoje)
                print(f"🌐 {len(jogos_hoje) if jogos_hoje else 0} jogos encontrados hoje")
                apostas_hot_hoje = []
            
            time.sleep(0.3)
            
            # Etapa 5: Buscar jogos de amanhã (com cache)
            self.atualizar_loading(35, "Verificando jogos de amanhã na API...")
            data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            data_formatada_amanha = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
            
            # Tentar carregar do cache primeiro
            cache_amanha = self.carregar_jogos_cache(data_amanha)
            if cache_amanha:
                self.atualizar_loading(40, "Carregando jogos de amanhã do cache local...")
                print(f"📁 Usando cache para amanhã: {len(cache_amanha['jogos'])} jogos")
                jogos_amanha = cache_amanha['jogos']
                apostas_hot_amanha = cache_amanha['apostas_hot']
                
                # Adicionar data_jogo a cada aposta para filtro correto
                for aposta in apostas_hot_amanha:
                    aposta['data_jogo'] = data_amanha
                    # Definir período para a data formatada para exibição no card
                    aposta['periodo'] = data_formatada_amanha
            else:
                self.atualizar_loading(40, "Buscando jogos de amanhã na API...")
                jogos_amanha = self.api.buscar_jogos_do_dia(data_amanha)
                print(f"🌐 {len(jogos_amanha) if jogos_amanha else 0} jogos encontrados amanhã")
                apostas_hot_amanha = []
            
            time.sleep(0.3)
            
            # Etapa 6: Preparar jogos para análise
            self.atualizar_loading(45, "Processando e filtrando jogos de hoje...")
            
            # Se não há cache, processar todos os jogos
            if not cache_hoje and jogos_hoje:
                jogos_validos_hoje = self.processar_todos_jogos(jogos_hoje)
                print(f"📊 {len(jogos_validos_hoje)} jogos de hoje preparados para análise")
            else:
                jogos_validos_hoje = []
                
            self.atualizar_loading(50, "Processando e filtrando jogos de amanhã...")
            if not cache_amanha and jogos_amanha:
                jogos_validos_amanha = self.processar_todos_jogos(jogos_amanha)
                print(f"📊 {len(jogos_validos_amanha)} jogos de amanhã preparados para análise")
            else:
                jogos_validos_amanha = []
            
            total_para_analisar = len(jogos_validos_hoje) + len(jogos_validos_amanha)
            if total_para_analisar > 0:
                print(f"🔥 {total_para_analisar} jogos SELECIONADOS para análise completa")
            time.sleep(0.5)
            
            # Etapa 7: CARREGAR E ANALISAR APOSTAS HOT COMPLETAMENTE
            apostas_todas = []
            
            # Se não há cache, analisar do zero
            if not cache_hoje and jogos_validos_hoje:
                self.atualizar_loading(60, "Analisando apostas hot de hoje detalhadamente...")
                apostas_hot_hoje, jogos_hoje_com_odds = self.analisar_jogos_completo_com_progresso(
                    jogos_validos_hoje, data_formatada, prog_inicial=60, prog_final=65
                )
                
                # Adicionar data_jogo a cada aposta para filtro correto
                for aposta in apostas_hot_hoje:
                    aposta['data_jogo'] = data_hoje
                
                self.atualizar_loading(65, "Salvando cache de jogos e apostas de hoje...")
                # Salvar no cache com jogos enriquecidos com odds
                dados_cache_hoje = {
                    'jogos': jogos_hoje_com_odds,
                    'apostas_hot': apostas_hot_hoje
                }
                self.salvar_jogos_cache(data_hoje, dados_cache_hoje)
            
            # Se não há cache, analisar do zero
            if not cache_amanha and jogos_validos_amanha:
                self.atualizar_loading(70, "Analisando apostas hot de amanhã detalhadamente...")
                apostas_hot_amanha, jogos_amanha_com_odds = self.analisar_jogos_completo_com_progresso(
                    jogos_validos_amanha, data_formatada_amanha, prog_inicial=70, prog_final=80
                )
                
                # Adicionar data_jogo a cada aposta para filtro correto
                for aposta in apostas_hot_amanha:
                    aposta['data_jogo'] = data_amanha
                
                self.atualizar_loading(80, "Salvando cache de jogos e apostas de amanhã...")
                # Salvar no cache com jogos enriquecidos com odds
                dados_cache_amanha = {
                    'jogos': jogos_amanha_com_odds,
                    'apostas_hot': apostas_hot_amanha
                }
                self.salvar_jogos_cache(data_amanha, dados_cache_amanha)
            
            # Para a interface, mostrar apenas os jogos de hoje por padrão
            self.atualizar_loading(85, "Organizando apostas para exibição...")
            apostas_todas.extend(apostas_hot_hoje)
            
            # Combinar e ordenar apostas por prob. bet booster
            self.apostas_hot_carregadas = apostas_todas
            self.apostas_hot_carregadas.sort(key=lambda x: -x.get('nossa_prob', 0))
            
            print(f"✅ {len(self.apostas_hot_carregadas)} apostas hot analisadas e prontas")
            
            # Etapa 8: Finalizar
            self.atualizar_loading(90, "Inicializando interface principal...")
            time.sleep(0.5)
            
            self.atualizar_loading(95, "Preparando cards de apostas...")
            time.sleep(0.3)
            
            self.atualizar_loading(100, "Finalização concluída! Iniciando aplicação...")
            time.sleep(0.8)
            
            # Criar interface principal
            self.root.after(100, self.finalizar_carregamento)
            
        except Exception as e:
            print(f"Erro no carregamento: {e}")
            self.apostas_hot_carregadas = []
            
            # Mostrar erro na interface de carregamento
            self.atualizar_loading(100, f"Erro ao carregar: {str(e)}")
            time.sleep(1)
            
            self.root.after(100, self.finalizar_carregamento)
    
    def processar_todos_jogos(self, jogos):
        """Processa jogos independente de validade - apenas adiciona ID se necessário"""
        jogos_processados = []
        
        for jogo in jogos:
            try:
                # Verificar se jogo é uma string (ID) ao invés de dicionário
                if isinstance(jogo, str):
                    # Se for apenas ID, criar dicionário básico
                    jogos_processados.append({'id': jogo})
                    continue
                
                # Se é dicionário, adicionar diretamente
                if isinstance(jogo, dict):
                    jogos_processados.append(jogo)
                else:
                    # Qualquer outro tipo, tentar converter para dict com ID
                    jogos_processados.append({'id': str(jogo)})
                    
            except Exception as e:
                print(f"⚠️ Erro ao processar jogo: {e}")
                # Mesmo com erro, tentar adicionar algo
                try:
                    jogos_processados.append({'id': str(jogo) if jogo else 'unknown'})
                except:
                    jogos_processados.append({'id': 'error_' + str(len(jogos_processados))})
        
        print(f"✅ {len(jogos_processados)} jogos processados")
        return jogos_processados
    
    def filtrar_jogos_validos(self, jogos):
        """MANTIDA PARA COMPATIBILIDADE - Mas agora aceita TODOS os jogos"""
        return self.processar_todos_jogos(jogos)
    
    def analisar_jogos_completo_com_progresso(self, jogos, periodo, progress_callback=None, prog_inicial=60, prog_final=70):
        """Analisa completamente os primeiros jogos de uma lista - VERSÃO PARALELA COM PROGRESSO"""
        apostas_analisadas = []
        jogos_com_odds = []  # Lista para jogos enriquecidos com odds

        print(f"🔥 Iniciando análise completa PARALELA de {len(jogos)} jogos ({periodo})")

        # Usar ThreadPoolExecutor para processamento paralelo
        max_workers = 10  # Máximo 10 threads simultâneas para não sobrecarregar API
        
        # Definir a etapa de processamento atual
        etapa_texto = f"Analisando apostas de {periodo.lower()}"
        
        # Atualizar barra com progresso inicial
        if hasattr(self, 'atualizar_loading'):
            self.atualizar_loading(prog_inicial, etapa_texto)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submeter todas as tarefas
            futures = []
            for i, jogo in enumerate(jogos):
                future = executor.submit(self.processar_jogo_para_hot_paralelo, jogo, periodo)
                futures.append(future)
            
            # Coletar resultados conforme completam
            for i, future in enumerate(as_completed(futures)):
                try:
                    # Atualizar barra de progresso a cada 10 jogos (ou menos se tiver menos de 100 jogos)
                    incremento_por_jogo = (prog_final - prog_inicial) / len(jogos)
                    novo_progresso = prog_inicial + (i + 1) * incremento_por_jogo
                    
                    # Atualizar a cada 10 jogos ou na primeira/última jogada
                    if i % 10 == 0 or i == len(jogos) - 1 or i == 0:
                        if hasattr(self, 'atualizar_loading'):
                            status_texto = f"{etapa_texto} - Jogo {i+1} de {len(jogos)}"
                            self.atualizar_loading(novo_progresso, status_texto)
                    
                    # Chamar o callback de progresso se fornecido
                    if progress_callback:
                        progresso_atual = (i + 1) / len(jogos) * 100
                        status_texto = f"Processando jogo {i+1}/{len(jogos)} ({progresso_atual:.0f}%)"
                        progress_callback(progresso_atual, status_texto)
                    
                    # Obter resultado
                    jogo_completo, recomendacoes = future.result(timeout=5)  # Timeout de 5 segundos por jogo
                    
                    # Adicionar resultados
                    jogos_com_odds.append(jogo_completo)
                    apostas_analisadas.extend(recomendacoes)
                    
                except Exception as e:
                    print(f"❌ ERRO ao processar jogo {i+1}: {e}")
                    # Adicionar jogo básico em caso de erro
                    jogo_erro = {
                        'id': f'erro_{i}',
                        'home_team': 'Erro',
                        'away_team': 'Erro',
                        'periodo': periodo,
                        'odds': None
                    }
                    jogos_com_odds.append(jogo_erro)
        
        # Garantir que chegue ao progresso final
        if hasattr(self, 'atualizar_loading'):
            self.atualizar_loading(prog_final, f"Análise de apostas de {periodo.lower()} concluída")
            
        print(f"🎯 CONCLUÍDO PARALELO: {len(jogos_com_odds)} jogos processados, {len(apostas_analisadas)} apostas hot geradas ({periodo})")
        return apostas_analisadas, jogos_com_odds

    def analisar_jogos_completo(self, jogos, periodo):
        """Analisa completamente os primeiros jogos de uma lista - redireciona para a versão com progresso"""
        # Esta função é mantida para compatibilidade com código existente
        # Apenas redireciona para a versão com progresso
        return self.analisar_jogos_completo_com_progresso(jogos, periodo)
    
    def atualizar_loading(self, progresso, status):
        """Atualiza barra de progresso e status"""
        def update():
            # Atualizar porcentagem
            self.progress_var.set(progresso)
            self.progress_percent.config(text=f"{int(progresso)}%")
            
            # Atualizar texto da etapa
            self.loading_etapa.config(text=status)
            
            # Atualizar cores baseado no progresso
            if progresso < 30:
                cor_etapa = '#1e40af'  # azul escuro
            elif progresso < 70:
                cor_etapa = '#2563eb'  # azul médio
            elif progresso < 100:
                cor_etapa = '#3b82f6'  # azul claro
            else:
                cor_etapa = '#047857'  # verde
                
            self.loading_etapa.config(fg=cor_etapa)
            
        self.root.after(0, update)
        self.root.update_idletasks()  # Forçar atualização da interface
        time.sleep(0.1)  # Pequena pausa para visualizar
    
    def finalizar_carregamento(self):
        """Remove tela de carregamento e mostra interface principal"""
        # Remover frame de carregamento
        self.loading_frame.destroy()
        
        # Criar interface principal
        self.create_widgets()
        self.main_widgets_created = True
        
        # Exibir apostas hot já carregadas
        if hasattr(self, 'apostas_hot_carregadas') and self.apostas_hot_carregadas:
            self.root.after(500, self.exibir_apostas_hot_prontas)
    
    def exibir_apostas_hot_prontas(self):
        """Exibe as apostas hot que já foram carregadas durante a inicialização"""
        try:
            if hasattr(self, 'status_hot') and hasattr(self, 'apostas_hot_carregadas'):
                # Exibir apostas hot
                self.exibir_apostas_hot(self.apostas_hot_carregadas)
                
                # Atualizar status
                total_apostas = len(self.apostas_hot_carregadas)
                data_formatada = datetime.now().strftime('%d/%m/%Y')
                
                self.status_hot.config(
                    text=f"✅ {total_apostas} apostas hot carregadas ({data_formatada})", 
                    style='Success.TLabel'
                )
                
                print(f"🔥 Interface atualizada com {total_apostas} apostas hot")
        except Exception as e:
            print(f"Erro ao exibir apostas prontas: {e}")
            if hasattr(self, 'status_hot'):
                self.status_hot.config(text="⚠️ Apostas carregadas com problemas", style='Warning.TLabel')
    
    def setup_styles(self):
        """Configura estilos da interface"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green', font=('Arial', 10, 'bold'))
        style.configure('Warning.TLabel', foreground='red', font=('Arial', 10, 'bold'))
        style.configure('Moderate.TLabel', foreground='#4A90E2', font=('Arial', 10, 'bold'))  # Azul claro para moderadas
        style.configure('Hot.TLabel', foreground='orange', font=('Arial', 10, 'bold'))
        style.configure('Danger.TLabel', foreground='red', font=('Arial', 10, 'bold'))  # Vermelho para muito arriscada
        style.configure('Live.TLabel', foreground='red', font=('Arial', 9, 'bold'))
    
    def create_widgets(self):
        """Cria todas as abas da interface"""
        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba 1: Apostas Hot (Nova funcionalidade)
        self.create_apostas_hot_tab()
        
        # Aba 2: Jogos do Dia (Atualizada)
        self.create_jogos_do_dia_tab()
        
        # Aba 3: Cadastro Manual
        self.create_cadastro_tab()
        
        # Aba 4: Análise de Confrontos
        self.create_analise_tab()
        
        # Aba 5: Múltiplas
        self.create_multiplas_tab()
        
        # Auto-carregar só se não foram carregadas na inicialização
        if not hasattr(self, 'apostas_hot_carregadas') or not self.apostas_hot_carregadas:
            self.root.after(1000, self.auto_carregar_apostas_hot)
    
    def create_apostas_hot_tab(self):
        """Nova aba: Apostas Hot - Recomendações automáticas"""
        self.tab_apostas_hot = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_apostas_hot, text="🔥 Apostas Hot")
        
        # Título
        title_frame = ttk.Frame(self.tab_apostas_hot)
        title_frame.pack(fill='x', pady=10)
        
        ttk.Label(title_frame, text="🔥 APOSTAS HOT - Recomendações Automáticas", 
                 style='Title.TLabel').pack()
        ttk.Label(title_frame, text="Análise automática das melhores apostas do dia", 
                 style='Subtitle.TLabel').pack(pady=5)
        
        # Frame de controles
        controles_frame = ttk.LabelFrame(self.tab_apostas_hot, text="Filtros e Configurações", padding=10)
        controles_frame.pack(fill='x', padx=20, pady=10)
        
        # Linha 1: Filtros
        filtros_frame = ttk.Frame(controles_frame)
        filtros_frame.pack(fill='x', pady=5)
        
        # Filtro de Data - Substituir ComboBox por DateEntry
        ttk.Label(filtros_frame, text="📅 Data:").pack(side='left', padx=(0, 5))
        
        # Inicializar com a data atual
        data_atual = datetime.now()
        self.filtro_data_entry = DateEntry(filtros_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, year=data_atual.year,
                                        month=data_atual.month, day=data_atual.day,
                                        date_pattern='dd/mm/yyyy')
        self.filtro_data_entry.pack(side='left', padx=(0, 15))
        # Armazenar a data selecionada em formato API
        self.data_selecionada = data_atual.strftime('%Y-%m-%d')
        # Armazenar a data formatada
        self.filtro_data_personalizada = data_atual.strftime('%d/%m/%Y')
        # Vincular evento de mudança de data
        self.filtro_data_entry.bind("<<DateEntrySelected>>", self.selecionar_data_apostas_hot)
        
        # Filtro de Recomendação
        ttk.Label(filtros_frame, text="🎯 Recomendações:").pack(side='left', padx=(0, 5))
        self.filtro_recomendacao = ttk.Combobox(filtros_frame, values=["Todos", "Fortes", "Moderadas", "Arriscadas", "Muito Arriscadas"], 
                                        state="readonly", width=15)
        self.filtro_recomendacao.pack(side='left', padx=(0, 15))
        self.filtro_recomendacao.set("Todos")
        self.filtro_recomendacao.bind('<<ComboboxSelected>>', self.aplicar_filtros_hot)
        
        # Filtro de Tipo de Aposta
        ttk.Label(filtros_frame, text="⚽ Tipo:").pack(side='left', padx=(0, 5))
        self.filtro_tipo = ttk.Combobox(filtros_frame, values=["Todos", "Resultado", "Outros"], 
                                       state="readonly", width=10)
        self.filtro_tipo.pack(side='left', padx=(0, 15))
        self.filtro_tipo.set("Todos")
        self.filtro_tipo.bind('<<ComboboxSelected>>', self.aplicar_filtros_hot)
        
        # Filtro de Ordenação
        ttk.Label(filtros_frame, text="🔄 Ordenar por:").pack(side='left', padx=(0, 5))
        self.filtro_ordenacao = ttk.Combobox(filtros_frame, values=["Prob. Média", "Value", "Horário", "Odd"], 
                                           state="readonly", width=12)
        self.filtro_ordenacao.pack(side='left', padx=(0, 15))
        self.filtro_ordenacao.set("Prob. Média")
        self.filtro_ordenacao.bind('<<ComboboxSelected>>', self.aplicar_filtros_hot)
        
        # Botão de limpeza de filtros
        ttk.Button(filtros_frame, text="🔄 Limpar Filtros", 
                  command=self.limpar_filtros_hot).pack(side='left', padx=15)
        
        # Linha 2: Botões de configuração
        buttons_frame = ttk.Frame(controles_frame)
        buttons_frame.pack(fill='x', pady=5)
        
        # Botão para atualizar apostas (limpar cache do dia)
        ttk.Button(buttons_frame, text="🔄 Atualizar apostas", 
                  command=self.atualizar_apostas_hot).pack(side='left', padx=5)
        
        # Botão de dicas
        ttk.Button(buttons_frame, text="💡 Dicas de Apostas", 
                  command=self.mostrar_dicas_apostas).pack(side='left', padx=5)
        
        # Botão de modo escuro
        ttk.Button(buttons_frame, text="🌙 Modo Escuro" if not self.modo_escuro.get() else "☀️ Modo Claro/Escuro", 
                  command=self.toggle_modo_escuro).pack(side='left', padx=5)
        
        # Separador visual
        ttk.Separator(buttons_frame, orient='vertical').pack(side='left', fill='y', padx=10)
        
        # Botão de bilhetes automáticos
        ttk.Button(buttons_frame, text="🎫 Bilhetes", 
                  command=self.mostrar_menu_bilhetes).pack(side='left', padx=5)
        
        # Status
        self.status_hot = ttk.Label(controles_frame, text="Pronto para análise", style='Success.TLabel')
        self.status_hot.pack(pady=5)
        
        # Frame principal com scrollbar
        main_frame = ttk.Frame(self.tab_apostas_hot)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Canvas para scroll - configuração melhorada
        canvas = tk.Canvas(main_frame, bg=self.cores['bg_principal'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.apostas_hot_frame = ttk.Frame(canvas)
        
        # Configurar o frame para ajustar a região de rolagem quando o tamanho mudar
        self.apostas_hot_frame.bind("<Configure>", 
                                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Criar janela no canvas para o frame de apostas
        canvas.create_window((0, 0), window=self.apostas_hot_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Melhorar a rolagem com eventos de mouse - bind específico para este canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Função para ativar scroll quando mouse entra na área
        def _bind_mouse_scroll(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Função para desativar scroll quando mouse sai da área
        def _unbind_mouse_scroll(event):
            canvas.unbind_all("<MouseWheel>")
        
        # Bind de entrada e saída do mouse
        canvas.bind("<Enter>", _bind_mouse_scroll)
        canvas.bind("<Leave>", _unbind_mouse_scroll)
        self.apostas_hot_frame.bind("<Enter>", _bind_mouse_scroll)
        self.apostas_hot_frame.bind("<Leave>", _unbind_mouse_scroll)
        
        # Configurar o canvas para expandir corretamente
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Garantir que o canvas tenha largura adequada
        self.tab_apostas_hot.update_idletasks()
        canvas.config(width=main_frame.winfo_width() - scrollbar.winfo_width())
    
    def selecionar_data_apostas_hot(self, event=None):
        """Gerencia a seleção de data para as apostas hot usando o DateEntry"""
        # Obter a data selecionada do DateEntry
        data_selecionada = self.filtro_data_entry.get_date()
        data_api = data_selecionada.strftime('%Y-%m-%d')
        data_formatada = data_selecionada.strftime('%d/%m/%Y')
        
        # Verificar se a data selecionada é hoje
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        # Armazenar as datas para uso posterior
        self.data_selecionada = data_api
        self.filtro_data_personalizada = data_formatada
        
        # Verificar se existe cache para esta data
        cache_path = self.get_cache_file_path(data_api)
        
        if os.path.exists(cache_path):
            # Se existe cache, carregar diretamente
            threading.Thread(
                target=self.carregar_apostas_data_especifica_thread,
                args=(data_api, data_formatada),
                daemon=True
            ).start()
        else:
            # Se não existe cache, perguntar se quer buscar da API
            resposta = messagebox.askyesno("Cache não encontrado", 
                                         "Não existe cache para esta data. Deseja buscar os dados da API?")
            if resposta:
                # Analisar jogos para a data selecionada
                self.analisar_jogos_data_especifica(data_api, data_formatada)
            else:
                # Se não quiser buscar, voltar para a data atual
                hoje = datetime.now()
                self.filtro_data_entry.set_date(hoje)
                # Tentar carregar do cache da data atual
                self.carregar_apostas_data_atual()
            # Aplicar filtros normais
            self.aplicar_filtros_hot()
    
    def analisar_jogos_data_especifica(self, data_api, data_formatada):
        """Analisa jogos de uma data específica e exibe apostas hot"""
        try:
            self.status_hot.config(text=f"🔄 Analisando jogos da data {data_formatada}...", style='Warning.TLabel')
            self.root.update()
            
            # Tentar carregar do cache
            cache_path = self.get_cache_file_path(data_api)
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                        
                    # Verificar se contém apostas_hot
                    if 'apostas_hot' in cache_data and cache_data['apostas_hot']:
                        # Adicionar data_jogo a cada aposta para filtro correto
                        for aposta in cache_data['apostas_hot']:
                            aposta['data_jogo'] = data_api
                        
                        self.exibir_apostas_hot(cache_data['apostas_hot'])
                        self.status_hot.config(text=f"✅ {len(cache_data['apostas_hot'])} apostas carregadas do cache ({data_formatada})", 
                                             style='Success.TLabel')
                        return True
                    else:
                        print(f"Cache existe mas não contém apostas_hot para {data_formatada}")
                except Exception as e:
                    print(f"Erro ao carregar cache de apostas hot: {e}")
            else:
                print(f"Cache não encontrado para {data_formatada}")
            
            # Se não tem cache válido, criar uma thread para buscar da API e processar
            self.status_hot.config(text=f"🔄 Buscando jogos da API para {data_formatada}...", 
                                 style='Warning.TLabel')
            
            # Iniciar em thread separada para não travar a interface
            threading.Thread(
                target=self.analisar_jogos_data_especifica_thread,
                args=(data_api, data_formatada),
                daemon=True
            ).start()
            
            return True
            
        except Exception as e:
            self.status_hot.config(text=f"❌ Erro: {str(e)}", style='Warning.TLabel')
            print(f"Erro ao analisar jogos da data {data_formatada}: {e}")
            return False
            
    def analisar_jogos_data_especifica_thread(self, data_api, data_formatada):
        """Versão em thread da análise de jogos para data específica"""
        try:
            # Buscar jogos da API
            jogos = self.api.buscar_jogos_do_dia(data_api)
            
            if not jogos:
                def atualizar_status_sem_jogos():
                    self.status_hot.config(text=f"❌ Nenhum jogo encontrado para {data_formatada}", 
                                         style='Warning.TLabel')
                self.root.after(0, atualizar_status_sem_jogos)
                return
            
            # Atualizar status na thread principal
            def atualizar_status_processando():
                self.status_hot.config(text=f"📊 Processando {len(jogos)} jogos para {data_formatada}...", 
                                     style='Warning.TLabel')
            self.root.after(0, atualizar_status_processando)
            
            # Usar a mesma abordagem de analisar_jogos_completo
            jogos_validos = self.processar_todos_jogos(jogos)  # Limitar a 100 jogos
            
            # Criar e exibir barra de progresso
            def criar_barra_progresso():
                # Frame para barra de progresso
                self.progresso_frame = ttk.Frame(self.tab_apostas_hot)
                self.progresso_frame.pack(fill='x', padx=20, pady=5)
                
                self.progresso_var = tk.DoubleVar()
                self.progresso_barra = ttk.Progressbar(
                    self.progresso_frame, 
                    variable=self.progresso_var,
                    maximum=100,
                    length=400
                )
                self.progresso_barra.pack(fill='x')
                
                self.progresso_texto = ttk.Label(self.progresso_frame, text="0%")
                self.progresso_texto.pack()
            
            self.root.after(0, criar_barra_progresso)
            
            # Função para atualizar o progresso
            def atualizar_progresso(valor, texto):
                def _atualizar():
                    self.progresso_var.set(valor)
                    self.progresso_texto.config(text=texto)
                self.root.after(0, _atualizar)
            
            apostas_recomendadas, jogos_com_odds = self.analisar_jogos_completo_com_progresso(
                jogos_validos, data_formatada, atualizar_progresso
            )
            
            # Verificar se retornou apostas
            if not apostas_recomendadas:
                def mostrar_sem_apostas():
                    # Remover barra de progresso
                    if hasattr(self, 'progresso_frame'):
                        self.progresso_frame.destroy()
                    
                    self.status_hot.config(text=f"❌ Nenhuma aposta recomendada para {data_formatada}", 
                                         style='Warning.TLabel')
                self.root.after(0, mostrar_sem_apostas)
                return
            
            # Adicionar data_jogo a cada aposta para filtro correto
            for aposta in apostas_recomendadas:
                aposta['data_jogo'] = data_api
                # Definir período para a data formatada para exibição no card
                aposta['periodo'] = data_formatada
            
            # Exibir apostas na thread principal
            def exibir_apostas():
                # Remover barra de progresso
                if hasattr(self, 'progresso_frame'):
                    self.progresso_frame.destroy()
                
                self.exibir_apostas_hot(apostas_recomendadas)
                self.status_hot.config(text=f"✅ {len(apostas_recomendadas)} apostas analisadas para {data_formatada}", 
                                     style='Success.TLabel')
            
            self.root.after(0, exibir_apostas)
            
            # Salvar apostas no cache
            try:
                cache_path = self.get_cache_file_path(data_api)
                cache_data = {}
                
                if os.path.exists(cache_path):
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                
                cache_data['apostas_hot'] = apostas_recomendadas
                
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=4)
                
                print(f"✅ {len(apostas_recomendadas)} apostas salvas no cache para {data_formatada}")
                
            except Exception as e:
                print(f"Erro ao salvar cache de apostas hot: {e}")
                
        except Exception as e:
            def mostrar_erro():
                # Remover barra de progresso
                if hasattr(self, 'progresso_frame'):
                    self.progresso_frame.destroy()
                    
                self.status_hot.config(text=f"❌ Erro: {str(e)}", style='Warning.TLabel')
            self.root.after(0, mostrar_erro)
            print(f"Erro ao analisar jogos da data {data_formatada}: {e}")
            
    def aplicar_filtros_hot(self, event=None):
        """Aplica filtros nas apostas hot"""
        try:
            if not hasattr(self, 'apostas_hot') or not self.apostas_hot:
                return
            
            # Obter a data selecionada do DateEntry
            data_selecionada_obj = self.filtro_data_entry.get_date()
            data_selecionada_api = data_selecionada_obj.strftime('%Y-%m-%d')
            data_selecionada_formatada = data_selecionada_obj.strftime('%d/%m/%Y')
            
            # Atualizar as variáveis de data
            self.data_selecionada = data_selecionada_api
            self.filtro_data_personalizada = data_selecionada_formatada
            
            filtro_recomendacao = self.filtro_recomendacao.get()
            filtro_tipo = self.filtro_tipo.get()
            filtro_ordenacao = self.filtro_ordenacao.get()
            
            # Filtrar apostas
            apostas_filtradas = []
            
            for aposta in self.apostas_hot:
                # Filtro de data - verificar se a data da aposta coincide com a data selecionada
                incluir_data = False
                data_aposta = aposta.get('data_jogo', aposta.get('periodo', ''))
                if data_aposta == data_selecionada_api:
                    incluir_data = True
                
                # Filtro de Recomendação - usar o campo 'tipo' da aposta
                incluir_recomendacao = True
                if filtro_recomendacao == "Fortes":
                    incluir_recomendacao = aposta.get('tipo') == 'FORTE'
                elif filtro_recomendacao == "Moderadas":
                    incluir_recomendacao = aposta.get('tipo') == 'MODERADA'
                elif filtro_recomendacao == "Arriscadas":
                    incluir_recomendacao = aposta.get('tipo') == 'ARRISCADA'
                elif filtro_recomendacao == "Muito Arriscadas":
                    incluir_recomendacao = aposta.get('tipo') == 'MUITO_ARRISCADA'

                # Filtro de tipo de aposta - verificar se é resultado ou outros
                incluir_tipo = True
                if filtro_tipo == "Resultado":
                    # Apostas de resultado: vitória casa, empate, vitória visitante
                    tipo_aposta = aposta.get('aposta', '').lower()
                    incluir_tipo = any(palavra in tipo_aposta for palavra in ['vitória', 'empate', 'casa', 'visitante'])
                elif filtro_tipo == "Outros":
                    # Apostas over/under e outras
                    tipo_aposta = aposta.get('aposta', '').lower()
                    incluir_tipo = any(palavra in tipo_aposta for palavra in ['over', 'under', 'btts', 'gols']) and not any(palavra in tipo_aposta for palavra in ['vitória', 'empate'])

                if incluir_data and incluir_recomendacao and incluir_tipo:
                    apostas_filtradas.append(aposta)
            
            # Ordenar apostas conforme filtro selecionado
            if filtro_ordenacao == "Horário":
                apostas_filtradas.sort(key=lambda x: x.get('horario', '00:00'))
            elif filtro_ordenacao == "Odd":
                apostas_filtradas.sort(key=lambda x: float(x.get('odd', 0)))
            elif filtro_ordenacao == "Value":
                apostas_filtradas.sort(key=lambda x: float(x.get('value', 0)), reverse=True)
                # Ordenar pela média das probabilidades (maior para menor)
            else:  # Prob. média
                for aposta in apostas_filtradas:
                    prob_calc = float(aposta.get('prob_calculada', 0))
                    prob_impl = float(aposta.get('prob_implicita', 0))
                    aposta['prob_media'] = (prob_calc + prob_impl) / 2
                apostas_filtradas.sort(key=lambda x: float(x.get('prob_media', 0)), reverse=True)
            
            # Atualizar interface com apostas filtradas
            self.atualizar_apostas_hot_interface(apostas_filtradas)
            
            # Atualizar status
            total_filtradas = len(apostas_filtradas)
            total_original = len(self.apostas_hot)
            
            status_text = f"✅ {total_filtradas} de {total_original} apostas ({self.filtro_data_personalizada})"
            if filtro_recomendacao != "Todos":
                status_text += f" ({filtro_recomendacao})"
            if filtro_tipo != "Todos":
                status_text += f" ({filtro_tipo})"
            if filtro_ordenacao != "Prob. Média":
                status_text += f" [Ord: {filtro_ordenacao}]"
            
            self.status_hot.config(text=status_text, style='Success.TLabel')
            
        except Exception as e:
            self.status_hot.config(text=f"❌ Erro ao aplicar filtros: {str(e)}", style='Warning.TLabel')
            print(f"Erro ao aplicar filtros: {e}")
    
    def carregar_apostas_amanha(self):
        """Carrega as apostas de amanhã do cache"""
        data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        data_formatada_amanha = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
        threading.Thread(
            target=self.carregar_apostas_data_especifica_thread,
            args=(data_amanha, data_formatada_amanha),
            daemon=True
        ).start()
    
    def carregar_apostas_data_atual(self):
        """Carrega as apostas da data atual do cache"""
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        data_formatada = datetime.now().strftime('%d/%m/%Y')
        threading.Thread(
            target=self.carregar_apostas_data_especifica_thread,
            args=(data_hoje, data_formatada),
            daemon=True
        ).start()
    
    def carregar_apostas_data_especifica_thread(self, data_api, data_formatada):
        """Thread para carregar apostas de uma data específica do cache sem travar a interface"""
        try:
            def atualizar_status(texto):
                self.status_hot.config(text=texto, style='Warning.TLabel')
                
            self.root.after(0, lambda: atualizar_status(f"🔄 Verificando cache de apostas para {data_formatada}..."))
            
            # Verificar e carregar do cache
            cache_path = self.get_cache_file_path(data_api)
            
            apostas_filtradas = []
            cache_encontrado = False
            
            # Verificar cache da data específica
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Verificar se contém apostas_hot
                    if 'apostas_hot' in cache_data and cache_data['apostas_hot']:
                        # Adicionar data_jogo a cada aposta para filtro correto
                        for aposta in cache_data['apostas_hot']:
                            aposta['data_jogo'] = data_api
                            # Definir período para a data formatada para exibição no card
                            aposta['periodo'] = data_formatada
                        
                        apostas_filtradas.extend(cache_data['apostas_hot'])
                        cache_encontrado = True
                        print(f"✅ Carregadas {len(cache_data['apostas_hot'])} apostas do cache para {data_formatada}")
                except Exception as e:
                    print(f"Erro ao carregar cache para {data_formatada}: {e}")
            
            # Exibir apostas se encontradas no cache
            if cache_encontrado and apostas_filtradas:
                def exibir_apostas_cache():
                    self.exibir_apostas_hot(apostas_filtradas)
                    self.status_hot.config(text=f"✅ {len(apostas_filtradas)} apostas carregadas do cache ({data_formatada})", 
                                         style='Success.TLabel')
                self.root.after(0, exibir_apostas_cache)
            else:
                # Se não encontrou no cache, informar ao usuário
                self.root.after(0, lambda: atualizar_status(f"❌ Nenhuma aposta encontrada para {data_formatada}"))
                
        except Exception as e:
            def mostrar_erro():
                self.status_hot.config(text=f"❌ Erro ao carregar apostas: {str(e)}", 
                                     style='Warning.TLabel')
            self.root.after(0, mostrar_erro)
            print(f"Erro ao carregar apostas para {data_formatada} em thread: {e}")
        
    def limpar_filtros_hot(self):
        """Limpa todos os filtros das apostas hot e carrega as apostas de hoje"""
        # Resetar filtros de recomendação e tipo
        self.filtro_recomendacao.set("Todos")
        self.filtro_tipo.set("Todos")
        self.filtro_ordenacao.set("Prob. Média")
        
        # Resetar o calendário para a data atual
        data_atual = datetime.now()
        self.filtro_data_entry.set_date(data_atual)
        
        # Atualizar as variáveis de data
        self.data_selecionada = data_atual.strftime('%Y-%m-%d')
        self.filtro_data_personalizada = data_atual.strftime('%d/%m/%Y')
        
        # Carregar apostas do cache para hoje
        self.carregar_apostas_data_atual()
    
    def filtrar_jogos(self, event=None):
        """Filtra jogos na lista baseado no texto da pesquisa"""
        try:
            texto_pesquisa = self.entry_pesquisa_jogos.get().lower().strip()
            
            # Armazenar dados originais se ainda não foi feito
            if not hasattr(self, 'jogos_originais'):
                self.jogos_originais = []
                for child in self.tree_jogos.get_children():
                    values = self.tree_jogos.item(child)['values']
                    self.jogos_originais.append(values)
            
            # Limpar tree
            for item in self.tree_jogos.get_children():
                self.tree_jogos.delete(item)
            
            # Filtrar e repovoar
            jogos_filtrados = 0
            for jogo_data in self.jogos_originais:
                if len(jogo_data) >= 5:  # Verificar se tem dados suficientes
                    casa = str(jogo_data[2]).lower()
                    visitante = str(jogo_data[3]).lower()
                    liga = str(jogo_data[4]).lower()
                    
                    # Verificar se o texto de pesquisa está em algum campo
                    if (not texto_pesquisa or 
                        texto_pesquisa in casa or 
                        texto_pesquisa in visitante or 
                        texto_pesquisa in liga):
                        
                        self.tree_jogos.insert('', 'end', values=jogo_data)
                        jogos_filtrados += 1
            
        except Exception as e:
            print(f"Erro ao filtrar jogos: {e}")
    
    def limpar_filtro_jogos(self):
        """Limpa o filtro de pesquisa de jogos"""
        self.entry_pesquisa_jogos.delete(0, tk.END)
        self.filtrar_jogos()
    
    def atualizar_apostas_hot(self):
        """Limpa o cache do dia atual ou selecionado e gera novas apostas hot"""
        try:
            # Determinar qual é a data atual selecionada do DateEntry
            data_selecionada_obj = self.filtro_data_entry.get_date()
            data_api = data_selecionada_obj.strftime('%Y-%m-%d')
            data_formatada = data_selecionada_obj.strftime('%d/%m/%Y')
            
            # Verificar se a data selecionada é hoje
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            
            if data_api == data_hoje:
                # Data de hoje selecionada - atualizar ambos os caches (hoje e amanhã)
                self.status_hot.config(text=f"🔄 Atualizando apostas para {data_formatada}...", 
                                     style='Warning.TLabel')
                self.root.update()
                
                # Iniciar uma thread para limpar o cache e recarregar as apostas
                threading.Thread(
                    target=self.atualizar_apostas_data_especifica_thread,
                    args=(data_api, data_formatada),
                    daemon=True
                ).start()
                
                # Também atualizar cache de amanhã em background
                data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                data_formatada_amanha = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
                
                # Após 5 segundos, iniciar a atualização dos dados de amanhã em background
                self.root.after(5000, lambda: threading.Thread(
                    target=self.atualizar_apostas_data_especifica_thread_silent,
                    args=(data_amanha, data_formatada_amanha),
                    daemon=True
                ).start())
            else:
                # Data personalizada selecionada
                self.status_hot.config(text=f"🔄 Atualizando apostas para {data_formatada}...", 
                                     style='Warning.TLabel')
                self.root.update()
                
                # Iniciar uma thread para limpar o cache e recarregar as apostas
                threading.Thread(
                    target=self.atualizar_apostas_data_especifica_thread,
                    args=(data_api, data_formatada),
                    daemon=True
                ).start()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar apostas: {str(e)}")
            self.status_hot.config(text="❌ Erro ao atualizar apostas", style='Warning.TLabel')
            
    def atualizar_apostas_hoje_amanha_thread(self, data_hoje, data_amanha):
        """Thread para atualizar apostas de hoje e amanhã sem travar a interface"""
        try:
            # Remover cache de hoje
            cache_hoje = self.get_cache_file_path(data_hoje)
            if os.path.exists(cache_hoje):
                try:
                    with open(cache_hoje, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Remover apostas_hot se existir
                    if 'apostas_hot' in cache_data:
                        del cache_data['apostas_hot']
                        
                        # Salvar cache atualizado
                        with open(cache_hoje, 'w', encoding='utf-8') as f:
                            json.dump(cache_data, f, ensure_ascii=False, indent=4)
                        
                        print("✅ Cache de apostas hot de hoje removido")
                except Exception as e:
                    print(f"Erro ao atualizar cache de hoje: {e}")
            
            # Remover cache de amanhã
            cache_amanha = self.get_cache_file_path(data_amanha)
            if os.path.exists(cache_amanha):
                try:
                    with open(cache_amanha, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Remover apostas_hot se existir
                    if 'apostas_hot' in cache_data:
                        del cache_data['apostas_hot']
                        
                        # Salvar cache atualizado
                        with open(cache_amanha, 'w', encoding='utf-8') as f:
                            json.dump(cache_data, f, ensure_ascii=False, indent=4)
                        
                        print("✅ Cache de apostas hot de amanhã removido")
                except Exception as e:
                    print(f"Erro ao atualizar cache de amanhã: {e}")
            
            # Recarregar todas as apostas
            self.analisar_apostas_thread()
            
        except Exception as e:
            def mostrar_erro():
                self.status_hot.config(text=f"❌ Erro ao atualizar apostas: {str(e)}", 
                                     style='Warning.TLabel')
            self.root.after(0, mostrar_erro)
            print(f"Erro ao atualizar apostas hot em thread: {e}")
            
    def carregar_apostas_hoje_amanha_thread(self):
        """Thread para carregar apostas de hoje e amanhã do cache sem travar a interface"""
        try:
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            data_formatada_hoje = datetime.now().strftime('%d/%m/%Y')
            data_formatada_amanha = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
            
            def atualizar_status(texto):
                self.status_hot.config(text=texto, style='Warning.TLabel')
                
            self.root.after(0, lambda: atualizar_status("🔄 Verificando cache de apostas para hoje e amanhã..."))
            
            # Verificar e carregar do cache
            cache_hoje = self.get_cache_file_path(data_hoje)
            cache_amanha = self.get_cache_file_path(data_amanha)
            
            apostas_todas = []
            cache_encontrado = False
            
            # Verificar cache de hoje
            if os.path.exists(cache_hoje):
                try:
                    with open(cache_hoje, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Verificar se contém apostas_hot
                    if 'apostas_hot' in cache_data and cache_data['apostas_hot']:
                        # Adicionar data_jogo a cada aposta para filtro correto
                        for aposta in cache_data['apostas_hot']:
                            aposta['data_jogo'] = data_hoje
                            # Garantir que o período seja 'Hoje'
                            aposta['periodo'] = 'Hoje'
                        
                        apostas_todas.extend(cache_data['apostas_hot'])
                        cache_encontrado = True
                        print(f"✅ Carregadas {len(cache_data['apostas_hot'])} apostas do cache de hoje")
                except Exception as e:
                    print(f"Erro ao carregar cache de hoje: {e}")
            
            # Verificar cache de amanhã
            if os.path.exists(cache_amanha):
                try:
                    with open(cache_amanha, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Verificar se contém apostas_hot
                    if 'apostas_hot' in cache_data and cache_data['apostas_hot']:
                        # Adicionar data_jogo a cada aposta para filtro correto
                        for aposta in cache_data['apostas_hot']:
                            aposta['data_jogo'] = data_amanha
                            # Garantir que o período seja 'Amanhã'
                            aposta['periodo'] = 'Amanhã'
                        
                        apostas_todas.extend(cache_data['apostas_hot'])
                        cache_encontrado = True
                        print(f"✅ Carregadas {len(cache_data['apostas_hot'])} apostas do cache de amanhã")
                except Exception as e:
                    print(f"Erro ao carregar cache de amanhã: {e}")
            
            # Exibir apostas se encontradas no cache
            if cache_encontrado and apostas_todas:
                def exibir_apostas_cache():
                    self.exibir_apostas_hot(apostas_todas)
                    self.status_hot.config(text=f"✅ {len(apostas_todas)} apostas carregadas do cache (Hoje/Amanhã)", 
                                         style='Success.TLabel')
                self.root.after(0, exibir_apostas_cache)
            else:
                # Se não encontrou no cache, executar análise completa
                self.root.after(0, lambda: atualizar_status("🔄 Cache não encontrado, analisando apostas..."))
                self.analisar_apostas_thread()
                
        except Exception as e:
            def mostrar_erro():
                self.status_hot.config(text=f"❌ Erro ao carregar apostas: {str(e)}", 
                                     style='Warning.TLabel')
            self.root.after(0, mostrar_erro)
            print(f"Erro ao carregar apostas hoje/amanhã em thread: {e}")
    
    def atualizar_apostas_data_especifica_thread_silent(self, data_api, data_formatada):
        """Thread para atualizar apostas de uma data específica sem notificar o usuário"""
        try:
            # Remover cache da data específica
            cache_path = self.get_cache_file_path(data_api)
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                    print(f"🗑️ Cache removido para {data_formatada}")
                except Exception as e:
                    print(f"Erro ao remover cache para {data_formatada}: {e}")
            
            # Buscar jogos da API e analisar
            jogos = self.api.buscar_jogos_do_dia(data_api)
            if not jogos:
                print(f"❌ Nenhum jogo encontrado para {data_formatada}")
                return
                
            print(f"🌐 {len(jogos)} jogos encontrados para {data_formatada}")
            
            # Processar jogos válidos
            jogos_validos = self.processar_todos_jogos(jogos)  # Limitar a 100 jogos
            if not jogos_validos:
                print(f"❌ Nenhum jogo válido para {data_formatada}")
                return
                
            print(f"✅ {len(jogos_validos)} jogos válidos para {data_formatada}")
            
            # Analisar jogos e gerar apostas hot
            apostas_recomendadas, jogos_com_odds = self.analisar_jogos_completo_com_progresso(
                jogos_validos, data_formatada
            )
            
            # Adicionar data_jogo a cada aposta para filtro correto
            for aposta in apostas_recomendadas:
                aposta['data_jogo'] = data_api
            
            # Salvar no cache
            dados_cache = {
                'jogos': jogos_com_odds,
                'apostas_hot': apostas_recomendadas
            }
            self.salvar_jogos_cache(data_api, dados_cache)
            
            print(f"💾 Cache atualizado para {data_formatada} com {len(apostas_recomendadas)} apostas")
            
        except Exception as e:
            print(f"Erro ao atualizar apostas para {data_formatada} em background: {e}")
    
    def atualizar_apostas_data_especifica_thread(self, data_api, data_formatada):
        """Thread para atualizar apostas de data específica sem travar a interface"""
        try:
            # Verificar se existe cache para esta data
            cache_path = self.get_cache_file_path(data_api)
            
            def atualizar_status(texto):
                self.status_hot.config(text=texto, style='Warning.TLabel')
                
            self.root.after(0, lambda: atualizar_status(f"🔄 Atualizando apostas para {data_formatada}..."))
            
            if os.path.exists(cache_path):
                # Remover apenas as apostas hot do cache
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Remover apostas_hot se existir
                    if 'apostas_hot' in cache_data:
                        del cache_data['apostas_hot']
                        
                        # Salvar cache atualizado
                        with open(cache_path, 'w', encoding='utf-8') as f:
                            json.dump(cache_data, f, ensure_ascii=False, indent=4)
                        
                        print(f"✅ Cache de apostas hot removido para {data_formatada}")
                except Exception as e:
                    print(f"Erro ao atualizar cache: {e}")
            
            # Buscar e analisar jogos novamente (usando a função threaded)
            self.analisar_jogos_data_especifica_thread(data_api, data_formatada)
            
        except Exception as e:
            def mostrar_erro():
                self.status_hot.config(text=f"❌ Erro ao atualizar apostas: {str(e)}", 
                                     style='Warning.TLabel')
            self.root.after(0, mostrar_erro)
            print(f"Erro ao atualizar apostas hot em thread: {e}")

    def analisar_apostas(self):
        """Analisa todas as apostas do sistema, carregando dados de hoje e amanhã"""
        try:
            self.status_hot.config(text="🔄 Analisando apostas hot...", style='Warning.TLabel')
            self.root.update()
            
            # Verificar se há cache para hoje e amanhã
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            cache_hoje = self.carregar_jogos_cache(data_hoje)
            cache_amanha = self.carregar_jogos_cache(data_amanha)
            
            # Se ambos os caches existem e têm apostas_hot, usar diretamente
            if (cache_hoje and 'apostas_hot' in cache_hoje and cache_hoje['apostas_hot'] and
                cache_amanha and 'apostas_hot' in cache_amanha and cache_amanha['apostas_hot']):
                
                # Combinar apostas de hoje e amanhã
                apostas_todas = []
                
                # Adicionar data_jogo para filtro correto
                for aposta in cache_hoje['apostas_hot']:
                    aposta['data_jogo'] = data_hoje
                    apostas_todas.append(aposta)
                    
                for aposta in cache_amanha['apostas_hot']:
                    aposta['data_jogo'] = data_amanha
                    apostas_todas.append(aposta)
                
                # Exibir apostas
                self.exibir_apostas_hot(apostas_todas)
                self.status_hot.config(text=f"✅ {len(apostas_todas)} apostas carregadas do cache (Hoje e Amanhã)", 
                                     style='Success.TLabel')
                return
            
            # Se não há cache completo, iniciar análise em thread separada
            threading.Thread(
                target=self.analisar_apostas_thread,
                daemon=True
            ).start()
                
        except Exception as e:
            self.status_hot.config(text=f"❌ Erro: {str(e)}", style='Warning.TLabel')
            print(f"Erro ao analisar apostas: {e}")
            
    def analisar_apostas_thread(self):
        """Versão em thread da análise de apostas para não travar a interface"""
        try:
            # Atualizar status na thread principal
            def atualizar_status(texto):
                self.status_hot.config(text=texto, style='Warning.TLabel')
            
            self.root.after(0, lambda: atualizar_status("🔄 Buscando jogos de hoje e amanhã..."))
            
            # Buscar jogos de hoje
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            jogos_hoje = self.api.buscar_jogos_do_dia(data_hoje)
            
            # Buscar jogos de amanhã
            data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            jogos_amanha = self.api.buscar_jogos_do_dia(data_amanha)
            
            if not jogos_hoje and not jogos_amanha:
                self.root.after(0, lambda: atualizar_status("❌ Nenhum jogo encontrado para hoje e amanhã"))
                return
            
            # Criar e exibir barra de progresso
            def criar_barra_progresso():
                # Frame para barra de progresso
                self.progresso_frame = ttk.Frame(self.tab_apostas_hot)
                self.progresso_frame.pack(fill='x', padx=20, pady=5)
                
                self.progresso_var = tk.DoubleVar()
                self.progresso_barra = ttk.Progressbar(
                    self.progresso_frame, 
                    variable=self.progresso_var,
                    maximum=100,
                    length=400
                )
                self.progresso_barra.pack(fill='x')
                
                self.progresso_texto = ttk.Label(self.progresso_frame, text="0%")
                self.progresso_texto.pack()
            
            self.root.after(0, criar_barra_progresso)
            
            # Função para atualizar o progresso
            def atualizar_progresso(valor, texto):
                def _atualizar():
                    self.progresso_var.set(valor)
                    self.progresso_texto.config(text=texto)
                self.root.after(0, _atualizar)
            
            # Processar jogos e gerar apostas hot
            apostas_todas = []
            
            # Processar jogos de hoje se tiver
            if jogos_hoje:
                self.root.after(0, lambda: atualizar_status("🔄 Analisando jogos de hoje..."))
                
                jogos_validos_hoje = self.processar_todos_jogos(jogos_hoje)  # Limitar a 100 jogos
                
                # Função para progresso de hoje (0-50%)
                def progress_callback_hoje(valor, texto):
                    progresso_hoje = valor / 2  # Converter para escala 0-50%
                    atualizar_progresso(progresso_hoje, f"Hoje: {texto}")
                
                apostas_hoje, jogos_hoje_com_odds = self.analisar_jogos_completo_com_progresso(
                    jogos_validos_hoje, 'Hoje', progress_callback_hoje
                )
                
                # Adicionar data_jogo às apostas de hoje
                for aposta in apostas_hoje:
                    aposta['data_jogo'] = data_hoje
                
                apostas_todas.extend(apostas_hoje)
                
                # Salvar cache de hoje
                dados_cache_hoje = {
                    'jogos': jogos_hoje_com_odds,
                    'apostas_hot': apostas_hoje,
                    'timestamp': datetime.now().timestamp()
                }
                self.salvar_jogos_cache(data_hoje, dados_cache_hoje)
            
            # Processar jogos de amanhã se tiver
            if jogos_amanha:
                self.root.after(0, lambda: atualizar_status("🔄 Analisando jogos de amanhã..."))
                
                jogos_validos_amanha = self.processar_todos_jogos(jogos_amanha)  # Limitar a 100 jogos
                
                # Função para progresso de amanhã (50-100%)
                def progress_callback_amanha(valor, texto):
                    progresso_amanha = 50 + (valor / 2)  # Converter para escala 50-100%
                    atualizar_progresso(progresso_amanha, f"Amanhã: {texto}")
                
                apostas_amanha, jogos_amanha_com_odds = self.analisar_jogos_completo_com_progresso(
                    jogos_validos_amanha, 'Amanhã', progress_callback_amanha
                )
                
                # Adicionar data_jogo às apostas de amanhã
                for aposta in apostas_amanha:
                    aposta['data_jogo'] = data_amanha
                
                apostas_todas.extend(apostas_amanha)
                
                # Salvar cache de amanhã
                dados_cache_amanha = {
                    'jogos': jogos_amanha_com_odds,
                    'apostas_hot': apostas_amanha,
                    'timestamp': datetime.now().timestamp()
                }
                self.salvar_jogos_cache(data_amanha, dados_cache_amanha)
            
            # Remover barra de progresso e exibir apostas na thread principal
            def finalizar_processamento():
                # Remover barra de progresso
                if hasattr(self, 'progresso_frame'):
                    self.progresso_frame.destroy()
                
                # Exibir apostas
                if apostas_todas:
                    self.exibir_apostas_hot(apostas_todas)
                    self.status_hot.config(text=f"✅ {len(apostas_todas)} apostas analisadas", 
                                         style='Success.TLabel')
                else:
                    self.status_hot.config(text="❌ Nenhuma aposta encontrada", 
                                         style='Warning.TLabel')
            
            self.root.after(0, finalizar_processamento)
                
        except Exception as e:
            def mostrar_erro():
                # Remover barra de progresso
                if hasattr(self, 'progresso_frame'):
                    self.progresso_frame.destroy()
                    
                self.status_hot.config(text=f"❌ Erro: {str(e)}", style='Warning.TLabel')
            self.root.after(0, mostrar_erro)
            print(f"Erro ao analisar apostas em thread: {e}")
    
    def atualizar_apostas_hot_interface(self, apostas_lista=None):
        """Atualiza a interface das apostas hot com a lista fornecida ou completa"""
        try:
            # Limpar frame
            for widget in self.apostas_hot_frame.winfo_children():
                widget.destroy()
            
            # Usar lista fornecida ou lista completa
            apostas_para_mostrar = apostas_lista if apostas_lista is not None else self.apostas_hot
            
            if not apostas_para_mostrar:
                ttk.Label(self.apostas_hot_frame, text="🔍 Nenhuma aposta encontrada com os filtros selecionados", 
                         style='Subtitle.TLabel').pack(pady=20)
                return
            
            # As apostas já vêm ordenadas do método aplicar_filtros_hot
            apostas_ordenadas = apostas_para_mostrar
            
            # Criar container para organizar apostas em duas colunas
            container_frame = ttk.Frame(self.apostas_hot_frame)
            container_frame.pack(fill='both', expand=True)
            
            # Criar dois frames lado a lado para as colunas
            col1_frame = ttk.Frame(container_frame)
            col1_frame.pack(side='left', fill='both', expand=True, padx=5)
            
            col2_frame = ttk.Frame(container_frame)
            col2_frame.pack(side='left', fill='both', expand=True, padx=5)
            
            # Distribuir apostas entre as duas colunas
            for i, aposta in enumerate(apostas_ordenadas):
                # Decidir em qual coluna colocar com base no índice (par/ímpar)
                parent_frame = col1_frame if i % 2 == 0 else col2_frame
                
                # Criar o card da aposta no frame da coluna correta
                self.criar_card_aposta_hot(aposta, i, parent_frame)
                
        except Exception as e:
            print(f"Erro ao atualizar interface de apostas hot: {e}")
            ttk.Label(self.apostas_hot_frame, text=f"❌ Erro ao carregar apostas: {str(e)}", 
                     style='Warning.TLabel').pack(pady=20)
    
    def create_jogos_do_dia_tab(self):
        """Aba atualizada: Jogos do Dia com novas funcionalidades"""
        self.tab_jogos_dia = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_jogos_dia, text="⚽ Jogos do Dia")
        
        # Título
        ttk.Label(self.tab_jogos_dia, text="⚽ JOGOS DO DIA - Análise Completa", 
                 style='Title.TLabel').pack(pady=10)
        
        # Frame de controles
        controles_frame = ttk.LabelFrame(self.tab_jogos_dia, text="Controles", padding=15)
        controles_frame.pack(fill='x', padx=20, pady=10)
        
        # Linha 1: Data e busca
        linha1 = ttk.Frame(controles_frame)
        linha1.pack(fill='x', pady=5)
        
        ttk.Label(linha1, text="📅 Data:").pack(side='left', padx=(0, 5))
        
        # Substituir Entry por DateEntry
        data_atual = datetime.now()
        self.entry_data = DateEntry(linha1, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, year=data_atual.year,
                                  month=data_atual.month, day=data_atual.day,
                                  date_pattern='dd/mm/yyyy')
        self.entry_data.pack(side='left', padx=(0, 10))
        
        ttk.Button(linha1, text="🔍 Buscar Jogos", 
                  command=self.buscar_jogos_do_dia).pack(side='left', padx=5)
        ttk.Button(linha1, text="🔄 Atualizar Jogos", 
                  command=self.forcar_atualizacao_jogos).pack(side='left', padx=5)
        
        # Linha 2: Opções de análise
        linha2 = ttk.Frame(controles_frame)
        linha2.pack(fill='x', pady=5)
        
        ttk.Label(linha2, text="Modo:").pack(side='left', padx=(0, 5))
        self.modo_analise = ttk.Combobox(linha2, values=["Dados Gerais"], 
                                        state="readonly", width=15)
        self.modo_analise.pack(side='left', padx=(0, 10))
        self.modo_analise.set("Dados Gerais")
        
        # Status
        self.status_jogos = ttk.Label(controles_frame, text="Pronto", style='Success.TLabel')
        self.status_jogos.pack(pady=5)
        
        # Frame da lista de jogos
        # Frame para pesquisa
        pesquisa_frame = ttk.LabelFrame(self.tab_jogos_dia, text="🔍 Filtrar Jogos", padding=10)
        pesquisa_frame.pack(fill='x', padx=20, pady=(10, 5))
        
        ttk.Label(pesquisa_frame, text="Pesquisar por liga ou time:").pack(side='left', padx=(0, 10))
        self.entry_pesquisa_jogos = ttk.Entry(pesquisa_frame, width=30)
        self.entry_pesquisa_jogos.pack(side='left', padx=(0, 10))
        self.entry_pesquisa_jogos.bind('<KeyRelease>', self.filtrar_jogos)
        
        ttk.Button(pesquisa_frame, text="🧹 Limpar", 
                  command=self.limpar_filtro_jogos).pack(side='left', padx=5)
        
        lista_frame = ttk.LabelFrame(self.tab_jogos_dia, text="Lista de Jogos", padding=10)
        lista_frame.pack(fill='both', expand=True, padx=20, pady=(5, 10))
        
        # Treeview para jogos
        columns = ('✓', 'Horário', 'Casa', 'Visitante', 'Liga', 'Odds H/E/A')
        self.tree_jogos = ttk.Treeview(lista_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.tree_jogos.heading(col, text=col)
            if col == '✓':
                self.tree_jogos.column(col, width=30, anchor='center')
            elif col == 'Horário':
                self.tree_jogos.column(col, width=80, anchor='center')
            elif col == 'Odds H/E/A':
                self.tree_jogos.column(col, width=120, anchor='center')
            else:
                self.tree_jogos.column(col, width=150)
        
        self.tree_jogos.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar_jogos = ttk.Scrollbar(lista_frame, orient="vertical", command=self.tree_jogos.yview)
        scrollbar_jogos.pack(side="right", fill="y")
        self.tree_jogos.configure(yscrollcommand=scrollbar_jogos.set)
        
        # Bind para seleção
        self.tree_jogos.bind('<Button-1>', self.on_jogo_clicado)
        self.tree_jogos.bind('<Double-1>', self.on_jogo_selecionado)
        
        # Variáveis de controle de seleção
        self.jogos_selecionados = []  # Lista de índices selecionados
        self.jogo_selecionado_index = None  # Jogo principal selecionado
        
        # Frame de ações
        acoes_frame = ttk.LabelFrame(self.tab_jogos_dia, text="Ações do Jogo Selecionado", padding=10)
        acoes_frame.pack(fill='x', padx=20, pady=10)
        
        # Linha 1: Controles de seleção
        selecao_frame = ttk.Frame(acoes_frame)
        selecao_frame.pack(fill='x', pady=5)
        
        ttk.Label(selecao_frame, text="🎯 Seleção:").pack(side='left', padx=(0, 5))
        ttk.Button(selecao_frame, text="🎯 Primeiro Jogo", 
                  command=self.selecionar_todos_jogos).pack(side='left', padx=5)
        ttk.Button(selecao_frame, text="❌ Limpar Seleção", 
                  command=self.limpar_selecao_jogos).pack(side='left', padx=5)
        
        # Label de status da seleção
        self.status_selecao = ttk.Label(selecao_frame, text="Nenhum jogo selecionado", 
                                       style='Subtitle.TLabel')
        self.status_selecao.pack(side='right')
        
        # Linha 2: Botões de ação
        acoes_buttons = ttk.Frame(acoes_frame)
        acoes_buttons.pack(fill='x', pady=5)
        
        ttk.Button(acoes_buttons, text="📊 Calcular Probabilidades", 
                  command=self.calcular_prob_jogo_selecionado).pack(side='left', padx=5)
        ttk.Button(acoes_buttons, text="💰 Aposta Simples", 
                  command=self.aposta_simples_jogo).pack(side='left', padx=5)
        ttk.Button(acoes_buttons, text="📋 Adicionar à Múltipla", 
                  command=self.adicionar_multipla_jogo).pack(side='left', padx=5)
    
    def create_cadastro_tab(self):
        """Aba de cadastro manual (mantida)"""
        self.tab_cadastro = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cadastro, text="➕ Cadastro Manual")
        
        ttk.Label(self.tab_cadastro, text="➕ CADASTRO MANUAL DE TIMES", 
                 style='Title.TLabel').pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(self.tab_cadastro)
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # Frame de cadastro
        cadastro_frame = ttk.LabelFrame(main_frame, text="Cadastrar Novo Time", padding=15)
        cadastro_frame.pack(fill='x', pady=10)
        
        # Nome do time
        ttk.Label(cadastro_frame, text="Nome do Time:").pack(anchor='w')
        self.entry_nome_time = ttk.Entry(cadastro_frame, width=30)
        self.entry_nome_time.pack(fill='x', pady=5)
        
        # Liga
        ttk.Label(cadastro_frame, text="Liga:").pack(anchor='w')
        self.entry_liga_time = ttk.Entry(cadastro_frame, width=30)
        self.entry_liga_time.pack(fill='x', pady=5)
        
        # Frame de estatísticas gerais
        stats_geral_frame = ttk.LabelFrame(cadastro_frame, text="Estatísticas Gerais", padding=10)
        stats_geral_frame.pack(fill='x', pady=10)
        
        # Linha 1: Gols
        linha1 = ttk.Frame(stats_geral_frame)
        linha1.pack(fill='x', pady=2)
        
        ttk.Label(linha1, text="Gols Marcados:").pack(side='left')
        self.entry_gols_marcados = ttk.Entry(linha1, width=10)
        self.entry_gols_marcados.pack(side='left', padx=(10, 20))
        
        ttk.Label(linha1, text="Gols Sofridos:").pack(side='left')
        self.entry_gols_sofridos = ttk.Entry(linha1, width=10)
        self.entry_gols_sofridos.pack(side='left', padx=10)
        
        # Linha 2: Resultados
        linha2 = ttk.Frame(stats_geral_frame)
        linha2.pack(fill='x', pady=2)
        
        ttk.Label(linha2, text="Vitórias:").pack(side='left')
        self.entry_vitorias = ttk.Entry(linha2, width=8)
        self.entry_vitorias.pack(side='left', padx=(10, 10))
        
        ttk.Label(linha2, text="Empates:").pack(side='left')
        self.entry_empates = ttk.Entry(linha2, width=8)
        self.entry_empates.pack(side='left', padx=(10, 10))
        
        ttk.Label(linha2, text="Derrotas:").pack(side='left')
        self.entry_derrotas = ttk.Entry(linha2, width=8)
        self.entry_derrotas.pack(side='left', padx=10)
        
        # Forma recente
        forma_frame = ttk.LabelFrame(cadastro_frame, text="Forma Recente (últimos 5 jogos)", padding=10)
        forma_frame.pack(fill='x', pady=10)
        
        ttk.Label(forma_frame, text="Use V (Vitória), E (Empate), D (Derrota) - Ex: V V E D V").pack()
        self.entry_forma_recente = ttk.Entry(forma_frame, width=20)
        self.entry_forma_recente.pack(pady=5)
        
        # Botões
        btn_cadastro_frame = ttk.Frame(cadastro_frame)
        btn_cadastro_frame.pack(fill='x', pady=10)
        
        ttk.Button(btn_cadastro_frame, text="💾 Cadastrar Time", 
                  command=self.cadastrar_time_manual).pack(side='left', padx=5)
        ttk.Button(btn_cadastro_frame, text="🧹 Limpar Campos", 
                  command=self.limpar_campos_cadastro).pack(side='left', padx=5)
        
        # Lista de times cadastrados
        lista_frame = ttk.LabelFrame(main_frame, text="Times Cadastrados", padding=10)
        lista_frame.pack(fill='both', expand=True, pady=10)
        
        # Treeview
        columns_times = ('Nome', 'Liga', 'Gols M/S', 'V-E-D', 'Origem')
        self.tree_times = ttk.Treeview(lista_frame, columns=columns_times, show='headings', height=10)
        
        for col in columns_times:
            self.tree_times.heading(col, text=col)
            if col == 'Nome':
                self.tree_times.column(col, width=150)
            elif col == 'Liga':
                self.tree_times.column(col, width=120)
            elif col == 'Gols M/S':
                self.tree_times.column(col, width=80, anchor='center')
            elif col == 'V-E-D':
                self.tree_times.column(col, width=80, anchor='center')
            else:
                self.tree_times.column(col, width=200)
        
        self.tree_times.pack(side='left', fill='both', expand=True)
        
        # Scrollbar para times
        scrollbar_times = ttk.Scrollbar(lista_frame, orient="vertical", command=self.tree_times.yview)
        scrollbar_times.pack(side="right", fill="y")
        self.tree_times.configure(yscrollcommand=scrollbar_times.set)
        
        # Botões de gerenciamento
        mgmt_frame = ttk.Frame(lista_frame)
        mgmt_frame.pack(fill='x', pady=10)
        
        ttk.Button(mgmt_frame, text="🔄 Atualizar Lista", 
                  command=self.atualizar_lista_times).pack(side='left', padx=5)
        ttk.Button(mgmt_frame, text="🗑️ Remover Selecionado", 
                  command=self.remover_time_selecionado).pack(side='left', padx=5)
        ttk.Button(mgmt_frame, text="📊 Ver Detalhes", 
                  command=self.ver_detalhes_time).pack(side='left', padx=5)
    
    def create_analise_tab(self):
        """Aba de análise de confrontos (atualizada)"""
        self.tab_analise = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analise, text="📊 Análise")
        
        ttk.Label(self.tab_analise, text="📊 ANÁLISE DE CONFRONTOS", 
                 style='Title.TLabel').pack(pady=10)
        
        # Frame de seleção
        selecao_frame = ttk.LabelFrame(self.tab_analise, text="Seleção de Times", padding=15)
        selecao_frame.pack(fill='x', padx=20, pady=10)
        
        # Linha 1: Times
        linha_times = ttk.Frame(selecao_frame)
        linha_times.pack(fill='x', pady=5)
        
        ttk.Label(linha_times, text="🏠 Time Casa:").pack(side='left')
        self.combo_time_casa = ttk.Combobox(linha_times, width=25, state="readonly")
        self.combo_time_casa.pack(side='left', padx=(10, 20))
        
        ttk.Label(linha_times, text="✈️ Time Visitante:").pack(side='left')
        self.combo_time_visitante = ttk.Combobox(linha_times, width=25, state="readonly")
        self.combo_time_visitante.pack(side='left', padx=10)
        
        # Linha 2: Configurações
        linha_config = ttk.Frame(selecao_frame)
        linha_config.pack(fill='x', pady=5)
        
        ttk.Label(linha_config, text="Modo de Análise:").pack(side='left')
        self.combo_modo_analise = ttk.Combobox(linha_config, values=["Dados Gerais"], 
                                              state="readonly", width=15)
        self.combo_modo_analise.pack(side='left', padx=(10, 20))
        self.combo_modo_analise.set("Dados Gerais")
        
        # Botões
        ttk.Button(linha_config, text="🔄 Atualizar Times", 
                  command=self.atualizar_combos_times).pack(side='left', padx=10)
        ttk.Button(linha_config, text="📊 Analisar Confronto", 
                  command=self.analisar_confronto_manual).pack(side='left', padx=5)
        
        # Resultado da análise
        resultado_frame = ttk.LabelFrame(self.tab_analise, text="Resultado da Análise", padding=15)
        resultado_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.texto_analise = scrolledtext.ScrolledText(resultado_frame, height=25, width=80,
                                                       bg=self.cores['bg_input'],
                                                       fg=self.cores['fg_input'],
                                                       insertbackground=self.cores['fg_input'])
        self.texto_analise.pack(fill='both', expand=True)
    
    # Métodos para cadastro manual
    def cadastrar_time_manual(self):
        """Cadastra time manualmente"""
        try:
            nome = self.entry_nome_time.get().strip()
            if not nome:
                messagebox.showwarning("Aviso", "Digite o nome do time")
                return
            
            liga = self.entry_liga_time.get().strip() or "Liga Personalizada"
            
            # Validar campos numéricos
            try:
                gols_marcados = float(self.entry_gols_marcados.get() or "0")
                gols_sofridos = float(self.entry_gols_sofridos.get() or "0")
                vitorias = int(self.entry_vitorias.get() or "0")
                empates = int(self.entry_empates.get() or "0")
                derrotas = int(self.entry_derrotas.get() or "0")
                
            except ValueError:
                messagebox.showerror("Erro", "Valores numéricos inválidos")
                return
            
            # Processar forma recente
            forma_input = self.entry_forma_recente.get().strip().upper()
            forma_recente = []
            if forma_input:
                forma_parts = forma_input.replace(',', ' ').split()
                for part in forma_parts:
                    if part in ['V', 'E', 'D', 'W', 'L']:
                        if part == 'W':
                            forma_recente.append('V')
                        elif part == 'L':
                            forma_recente.append('D')
                        else:
                            forma_recente.append(part)
            
            # Criar registro do time
            time_data = {
                'nome': nome,
                'liga': liga,
                'origem': "Cadastro Manual",
                'data_cadastro': datetime.now().isoformat(),
                'gols_marcados': gols_marcados,
                'gols_sofridos': gols_sofridos,
                'vitorias': vitorias,
                'empates': empates,
                'derrotas': derrotas,
                'forma_recente': forma_recente,
                'forca_ofensiva': gols_marcados / 1.2 if gols_marcados > 0 else 1.0,
                'forca_defensiva': gols_sofridos / 1.2 if gols_sofridos > 0 else 1.0
            }
            
            # Salvar no database
            self.times_database[nome] = time_data
            self.salvar_dados()
            
            # Atualizar interface
            self.atualizar_lista_times()
            self.atualizar_combos_times()
            self.limpar_campos_cadastro()
            
            messagebox.showinfo("Sucesso", f"Time '{nome}' cadastrado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar time: {str(e)}")
    
    def limpar_campos_cadastro(self):
        """Limpa todos os campos de cadastro"""
        campos = [
            self.entry_nome_time, self.entry_liga_time,
            self.entry_gols_marcados, self.entry_gols_sofridos,
            self.entry_vitorias, self.entry_empates, self.entry_derrotas,
            self.entry_forma_recente
        ]
        
        for campo in campos:
            campo.delete(0, tk.END)
    
    def atualizar_lista_times(self):
        """Atualiza a lista visual de times cadastrados"""
        # Limpar árvore
        for item in self.tree_times.get_children():
            self.tree_times.delete(item)
        
        # Adicionar times
        for nome, dados in self.times_database.items():
            gols_texto = f"{dados.get('gols_marcados', 0):.1f}/{dados.get('gols_sofridos', 0):.1f}"
            ved_texto = f"{dados.get('vitorias', 0)}-{dados.get('empates', 0)}-{dados.get('derrotas', 0)}"
            origem = dados.get('origem', 'Desconhecido')
            
            self.tree_times.insert('', 'end', values=(
                nome, dados.get('liga', ''), gols_texto, ved_texto, origem
            ))
    
    def atualizar_combos_times(self):
        """Atualiza os comboboxes de seleção de times"""
        times_nomes = list(self.times_database.keys())
        times_nomes.sort()
        
        self.combo_time_casa['values'] = times_nomes
        self.combo_time_visitante['values'] = times_nomes
    
    def remover_time_selecionado(self):
        """Remove time selecionado"""
        selection = self.tree_times.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um time para remover")
            return
        
        item = self.tree_times.item(selection[0])
        nome_time = item['values'][0]
        
        if messagebox.askyesno("Confirmar", f"Remover time '{nome_time}'?"):
            if nome_time in self.times_database:
                del self.times_database[nome_time]
                self.salvar_dados()
                self.atualizar_lista_times()
                self.atualizar_combos_times()
                messagebox.showinfo("Sucesso", f"Time '{nome_time}' removido")
    
    def ver_detalhes_time(self):
        """Mostra detalhes do time selecionado"""
        selection = self.tree_times.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um time")
            return
        
        item = self.tree_times.item(selection[0])
        nome_time = item['values'][0]
        
        if nome_time in self.times_database:
            dados = self.times_database[nome_time]
            detalhes = f"""
📊 DETALHES DO TIME: {nome_time}
═══════════════════════════════════════

🏆 Liga: {dados.get('liga', 'N/A')}
📅 Cadastrado em: {dados.get('data_cadastro', 'N/A')[:10]}
🎯 Origem: {dados.get('origem', 'N/A')}

📈 ESTATÍSTICAS GERAIS:
═══════════════════════════════════════
⚽ Gols Marcados: {dados.get('gols_marcados', 0):.2f}
🥅 Gols Sofridos: {dados.get('gols_sofridos', 0):.2f}
🏆 Vitórias: {dados.get('vitorias', 0)}
🤝 Empates: {dados.get('empates', 0)}
❌ Derrotas: {dados.get('derrotas', 0)}

🔥 FORMA RECENTE:
{' '.join(dados.get('forma_recente', ['N/A']))}
"""
            messagebox.showinfo(f"Detalhes - {nome_time}", detalhes)
    
    # Métodos para análise de confrontos
    def analisar_confronto_manual(self):
        """Analisa confronto entre times selecionados"""
        time_casa = self.combo_time_casa.get()
        time_visitante = self.combo_time_visitante.get()
        
        if not time_casa or not time_visitante:
            messagebox.showwarning("Aviso", "Selecione ambos os times")
            return
        
        if time_casa == time_visitante:
            messagebox.showwarning("Aviso", "Selecione times diferentes")
            return
        
        if time_casa not in self.times_database or time_visitante not in self.times_database:
            messagebox.showerror("Erro", "Times não encontrados no database")
            return
        
        # Realizar análise
        modo = self.combo_modo_analise.get()
        relatorio = self.gerar_relatorio_confronto(time_casa, time_visitante, modo)
        
        # Exibir resultado
        self.texto_analise.delete(1.0, tk.END)
        self.texto_analise.insert(1.0, relatorio)
    
    def gerar_relatorio_confronto(self, nome_casa, nome_visitante, modo):
        """Gera relatório completo do confronto"""
        dados_casa = self.times_database[nome_casa]
        dados_visitante = self.times_database[nome_visitante]
        
        # Usar APENAS dados gerais (anyField)
        gols_casa = dados_casa.get('gols_marcados', 0)
        gols_sofridos_casa = dados_casa.get('gols_sofridos', 0)
        gols_visitante = dados_visitante.get('gols_marcados', 0)
        gols_sofridos_visitante = dados_visitante.get('gols_sofridos', 0)
        modo_texto = "DADOS GERAIS"
        
        # Calcular probabilidades
        probabilidades = self.calcular_probabilidades_confronto_manual(
            gols_casa, gols_sofridos_casa, gols_visitante, gols_sofridos_visitante)
        
        # Formatar formas recentes
        forma_casa = self.formatar_forma_recente(dados_casa.get('forma_recente', []))
        forma_visitante = self.formatar_forma_recente(dados_visitante.get('forma_recente', []))
        
        relatorio = f"""
🏆 ANÁLISE DE CONFRONTO - {modo_texto}
═══════════════════════════════════════════════════════════════

🏠 {nome_casa.upper()} vs ✈️ {nome_visitante.upper()}

📊 ESTATÍSTICAS DOS TIMES:
═══════════════════════════════════════

🏠 {nome_casa}:
   ⚽ Gols Marcados: {gols_casa:.2f}
   🥅 Gols Sofridos: {gols_sofridos_casa:.2f}
   🔥 Forma: {forma_casa}
   🏆 Liga: {dados_casa.get('liga', 'N/A')}

✈️ {nome_visitante}:
   ⚽ Gols Marcados: {gols_visitante:.2f}
   🥅 Gols Sofridos: {gols_sofridos_visitante:.2f}
   🔥 Forma: {forma_visitante}
   🏆 Liga: {dados_visitante.get('liga', 'N/A')}

📈 EXPECTATIVA DE GOLS:
═══════════════════════════════════════
🏠 Gols Esperados {nome_casa}: {probabilidades['gols_esperados_casa']:.2f}
✈️ Gols Esperados {nome_visitante}: {probabilidades['gols_esperados_visitante']:.2f}
🎯 Total de Gols Esperados: {probabilidades['gols_esperados_total']:.2f}

🎲 PROBABILIDADES DE RESULTADO:
═══════════════════════════════════════
🏠 Vitória {nome_casa}: {probabilidades['vitoria_casa']:.1f}%
🤝 Empate: {probabilidades['empate']:.1f}%
✈️ Vitória {nome_visitante}: {probabilidades['vitoria_visitante']:.1f}%

🎯 PROBABILIDADES DE GOLS:
═══════════════════════════════════════
📊 Mais de 1.5 gols: {probabilidades['over_15']:.1f}%
📊 Menos de 1.5 gols: {probabilidades['under_15']:.1f}%
📊 Mais de 2.5 gols: {probabilidades['over_25']:.1f}%
📊 Menos de 2.5 gols: {probabilidades['under_25']:.1f}%
📊 Mais de 3.5 gols: {probabilidades['over_35']:.1f}%
📊 Menos de 3.5 gols: {probabilidades['under_35']:.1f}%

💰 RECOMENDAÇÕES DE APOSTAS:
═══════════════════════════════════════
"""
        
        # Adicionar recomendações baseadas nas probabilidades
        recomendacoes = self.gerar_recomendacoes_confronto(probabilidades, nome_casa, nome_visitante)
        relatorio += recomendacoes
        
        relatorio += f"""
═══════════════════════════════════════
⏰ Análise gerada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🔍 Modo de análise: {modo_texto}
"""
        
        return relatorio
    
    def calcular_probabilidades_confronto_manual(self, gols_casa, gols_sofridos_casa, gols_visitante, gols_sofridos_visitante):
        """Calcula probabilidades do confronto manual"""
        # Calcular gols esperados
        gols_esperados_casa = (gols_casa + gols_sofridos_visitante) / 2
        gols_esperados_visitante = (gols_visitante + gols_sofridos_casa) / 2
        gols_esperados_total = gols_esperados_casa + gols_esperados_visitante
        
        # Distribuição de Poisson para probabilidades
        from math import exp, factorial
        
        max_gols = 7
        
        # Matriz de probabilidades
        prob_vitoria_casa = 0
        prob_empate = 0
        prob_vitoria_visitante = 0
        
        for casa in range(max_gols):
            for visitante in range(max_gols):
                prob_casa = (gols_esperados_casa ** casa * exp(-gols_esperados_casa)) / factorial(casa)
                prob_visitante = (gols_esperados_visitante ** visitante * exp(-gols_esperados_visitante)) / factorial(visitante)
                prob_resultado = prob_casa * prob_visitante
                
                if casa > visitante:
                    prob_vitoria_casa += prob_resultado
                elif casa == visitante:
                    prob_empate += prob_resultado
                else:
                    prob_vitoria_visitante += prob_resultado
        
        # Normalizar
        total = prob_vitoria_casa + prob_empate + prob_vitoria_visitante
        if total > 0:
            prob_vitoria_casa = (prob_vitoria_casa / total) * 100
            prob_empate = (prob_empate / total) * 100
            prob_vitoria_visitante = (prob_vitoria_visitante / total) * 100
        
        # Calcular probabilidades de over/under
        over_15 = self.calcular_prob_over_under(gols_esperados_total, 1.5, 'over')
        under_15 = 100 - over_15
        over_25 = self.calcular_prob_over_under(gols_esperados_total, 2.5, 'over')
        under_25 = 100 - over_25
        over_35 = self.calcular_prob_over_under(gols_esperados_total, 3.5, 'over')
        under_35 = 100 - over_35
        
        return {
            'vitoria_casa': prob_vitoria_casa,
            'empate': prob_empate,
            'vitoria_visitante': prob_vitoria_visitante,
            'gols_esperados_casa': gols_esperados_casa,
            'gols_esperados_visitante': gols_esperados_visitante,
            'gols_esperados_total': gols_esperados_total,
            'over_15': over_15,
            'under_15': under_15,
            'over_25': over_25,
            'under_25': under_25,
            'over_35': over_35,
            'under_35': under_35
        }
    
    def gerar_recomendacoes_confronto(self, probabilidades, nome_casa, nome_visitante):
        """Gera recomendações baseadas nas probabilidades"""
        recomendacoes = ""
        
        # Recomendação para resultado
        maior_prob = max(probabilidades['vitoria_casa'], probabilidades['empate'], probabilidades['vitoria_visitante'])
        
        if probabilidades['vitoria_casa'] == maior_prob and maior_prob >= 40:
            recomendacoes += f"🟢 FORTE: Vitória {nome_casa} ({maior_prob:.1f}%)\n"
        elif probabilidades['vitoria_visitante'] == maior_prob and maior_prob >= 40:
            recomendacoes += f"🟢 FORTE: Vitória {nome_visitante} ({maior_prob:.1f}%)\n"
        elif probabilidades['empate'] == maior_prob and maior_prob >= 33:
            recomendacoes += f"🟢 FORTE: Empate ({maior_prob:.1f}%)\n"
        
        # Recomendações para gols
        gols_esperados_total = probabilidades['gols_esperados_total']
        
        # Apenas recomendar over 2.5 se gols esperados > 4
        if probabilidades['over_25'] >= 60 and gols_esperados_total >= 4.0:
            recomendacoes += f"🟢 FORTE: Mais de 2.5 gols ({probabilidades['over_25']:.1f}%)\n"
        elif probabilidades['under_25'] >= 60 and gols_esperados_total <= 2.0:
            recomendacoes += f"🟢 FORTE: Menos de 2.5 gols ({probabilidades['under_25']:.1f}%)\n"
        
        if probabilidades['over_15'] >= 75:
            recomendacoes += f"🟡 ARRISCADA: Mais de 1.5 gols ({probabilidades['over_15']:.1f}%)\n"
        
        if probabilidades['over_35'] >= 30:
            recomendacoes += f"🟡 ARRISCADA: Mais de 3.5 gols ({probabilidades['over_35']:.1f}%)\n"
        
        if not recomendacoes:
            recomendacoes = "⚪ Nenhuma recomendação forte identificada.\n"
        
        return recomendacoes
    
    def formatar_forma_recente(self, forma_lista):
        """Formata lista de forma recente para exibição"""
        if not forma_lista:
            return "Sem dados"
        
        # Mapear para emoji ou manter letras
        mapa_forma = {'V': 'V', 'E': 'E', 'D': 'D', 'W': 'V', 'L': 'D'}
        forma_formatada = []
        
        for resultado in forma_lista[:5]:  # Últimos 5
            forma_formatada.append(mapa_forma.get(resultado, resultado))
        
        return ' '.join(forma_formatada)
    
    def converter_forma_recente_para_vde(self, forma_lista):
        """
        Converte lista de forma recente da API (Win/Draw/Loss) para formato V/E/D
        e inverte a ordem para mostrar do mais antigo para o mais recente
        
        Args:
            forma_lista: Lista de resultados da API
        
        Returns:
            list: Lista de resultados convertidos [V, E, D]
        """
        if not forma_lista:
            return []
        
        # Mapeamento da API para nosso formato
        conversao = {
            'Win': 'V',    # Vitória
            'Draw': 'E',   # Empate  
            'Loss': 'D',   # Derrota
            'W': 'V',      # Alternativo para Win
            'D': 'E',      # Alternativo para Draw (assumindo Draw)
            'L': 'D'       # Alternativo para Loss
        }
        
        # Converter resultados
        resultados_convertidos = []
        for resultado in forma_lista:
            resultado_str = str(resultado).strip()
            if resultado_str in conversao:
                resultados_convertidos.append(conversao[resultado_str])
            else:
                # Se não reconhecer o formato, tentar primeira letra
                primeira_letra = resultado_str[0].upper() if resultado_str else '?'
                if primeira_letra in ['W']:
                    resultados_convertidos.append('V')
                elif primeira_letra in ['D']:
                    # Para 'D', assumir que é Draw (Empate) se vier da API
                    # A menos que seja especificamente "Defeat" ou "Loss"
                    if 'raw' in resultado_str.lower():
                        resultados_convertidos.append('E')  # Draw = Empate
                    else:
                        resultados_convertidos.append('E')  # Assume Draw por padrão para 'D'
                elif primeira_letra in ['L']:
                    resultados_convertidos.append('D')  # Loss = Derrota
                elif primeira_letra in ['V']:
                    resultados_convertidos.append('V')  # Vitória
                elif primeira_letra in ['E']:
                    resultados_convertidos.append('E')  # Empate
                else:
                    resultados_convertidos.append('?')  # Desconhecido
        
        # Inverter ordem (API retorna mais recentes primeiro, queremos mais antigos primeiro)
        return resultados_convertidos[::-1]
    
    def formatar_forma_visual(self, forma_vde, nome_time):
        """
        Formata a forma recente com indicação de cores para exibição visual
        
        Args:
            forma_vde: Lista de resultados [V, E, D]
            nome_time: Nome do time
        
        Returns:
            str: String formatada para exibição
        """
        if not forma_vde:
            return f"Últimos 5 {nome_time}: N/A"
        
        # Pegar apenas os últimos 5 resultados
        ultimos_5 = forma_vde[-5:] if len(forma_vde) >= 5 else forma_vde
        
        # Completar com espaços se não tiver 5 resultados
        while len(ultimos_5) < 5:
            ultimos_5.insert(0, '-')
        
        # Adicionar espaços entre as letras para melhor visualização
        forma_formatada = " ".join(ultimos_5)
        
        return f"Últimos 5 {nome_time}: {forma_formatada}"
    
    def create_multiplas_tab(self):
        """Nova aba: Gestão de Múltiplas com Banca Simulada"""
        self.tab_multiplas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_multiplas, text="🎯 Múltiplas")
        
        ttk.Label(self.tab_multiplas, text="🎯 BANCA SIMULADA & MÚLTIPLAS", 
                 style='Title.TLabel').pack(pady=10)
        
        # Criar notebook interno para organizar melhor
        self.notebook_multiplas = ttk.Notebook(self.tab_multiplas)
        self.notebook_multiplas.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Aba 1: Gestão da Banca
        self.create_banca_tab()
        
        # Aba 2: Múltipla Atual
        self.create_multipla_atual_tab()
        
        # Aba 3: Apostas Ativas
        self.create_apostas_ativas_tab()
        
        # Aba 4: Histórico
        self.create_historico_tab()
    
    def create_banca_tab(self):
        """Aba de gestão da banca simulada"""
        self.tab_banca = ttk.Frame(self.notebook_multiplas)
        self.notebook_multiplas.add(self.tab_banca, text="💰 Banca")
        
        # Informações da banca
        banca_info_frame = ttk.LabelFrame(self.tab_banca, text="Informações da Banca", padding=15)
        banca_info_frame.pack(fill='x', padx=20, pady=10)
        
        # Saldo atual
        self.label_saldo = ttk.Label(banca_info_frame, text="Saldo Atual: R$ 0.00", 
                                   font=('Arial', 16, 'bold'), foreground='green')
        self.label_saldo.pack(pady=5)
        
        # Estatísticas
        stats_frame = ttk.Frame(banca_info_frame)
        stats_frame.pack(fill='x', pady=10)
        
        # Coluna esquerda
        left_stats = ttk.Frame(stats_frame)
        left_stats.pack(side='left', fill='both', expand=True)
        
        self.label_total_depositado = ttk.Label(left_stats, text="Total Depositado: R$ 0.00")
        self.label_total_depositado.pack(anchor='w', pady=2)
        
        self.label_total_ganhos = ttk.Label(left_stats, text="Total Ganhos: R$ 0.00", foreground='green')
        self.label_total_ganhos.pack(anchor='w', pady=2)
        
        # Coluna direita
        right_stats = ttk.Frame(stats_frame)
        right_stats.pack(side='right', fill='both', expand=True)
        
        self.label_total_perdas = ttk.Label(right_stats, text="Total Perdas: R$ 0.00", foreground='red')
        self.label_total_perdas.pack(anchor='w', pady=2)
        
        self.label_lucro_total = ttk.Label(right_stats, text="Lucro Total: R$ 0.00")
        self.label_lucro_total.pack(anchor='w', pady=2)
        
        # Adicionar saldo
        adicionar_frame = ttk.LabelFrame(self.tab_banca, text="Adicionar Saldo", padding=15)
        adicionar_frame.pack(fill='x', padx=20, pady=10)
        
        entrada_frame = ttk.Frame(adicionar_frame)
        entrada_frame.pack(fill='x')
        
        ttk.Label(entrada_frame, text="Valor (R$):").pack(side='left', padx=5)
        self.entry_saldo = ttk.Entry(entrada_frame, width=15)
        self.entry_saldo.pack(side='left', padx=5)
        
        ttk.Button(entrada_frame, text="💰 Depositar", 
                  command=self.depositar_saldo).pack(side='left', padx=5)
        
        # Atualizar informações da banca
        self.atualizar_info_banca()
    
    def create_multipla_atual_tab(self):
        """Aba da múltipla atual"""
        self.tab_multipla_atual = ttk.Frame(self.notebook_multiplas)
        self.notebook_multiplas.add(self.tab_multipla_atual, text="⚽ Múltipla")
        
        # Frame da múltipla atual
        multipla_frame = ttk.LabelFrame(self.tab_multipla_atual, text="Múltipla Atual", padding=15)
        multipla_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Lista de apostas na múltipla
        columns_multipla = ('Jogo', 'Aposta', 'Odd', 'Prob. Bet Booster', 'Prob. Bet365')
        self.tree_multipla = ttk.Treeview(multipla_frame, columns=columns_multipla, show='headings', height=8)
        
        for col in columns_multipla:
            self.tree_multipla.heading(col, text=col)
            if col == 'Jogo':
                self.tree_multipla.column(col, width=250)
            elif col == 'Aposta':
                self.tree_multipla.column(col, width=150)
            elif col in ['Prob. Bet Booster', 'Prob. Bet365']:
                self.tree_multipla.column(col, width=120)
            else:
                self.tree_multipla.column(col, width=80)
        
        self.tree_multipla.pack(fill='both', expand=True)
        
        # Informações da múltipla
        info_frame = ttk.Frame(multipla_frame)
        info_frame.pack(fill='x', pady=10)
        
        self.label_odd_total = ttk.Label(info_frame, text="Odd Total: 1.00", 
                                       font=('Arial', 12, 'bold'))
        self.label_odd_total.pack(side='left', padx=10)
        
        self.label_prob_nossa = ttk.Label(info_frame, text="📊 Prob. Bet Booster: 100%", 
                                        foreground='green')
        self.label_prob_nossa.pack(side='left', padx=10)
        
        self.label_prob_total = ttk.Label(info_frame, text="🎯 Prob. Bet365: 100%")
        self.label_prob_total.pack(side='left', padx=10)
        
        # Frame de apostas
        apostar_frame = ttk.LabelFrame(multipla_frame, text="Realizar Aposta", padding=10)
        apostar_frame.pack(fill='x', pady=10)
        
        entrada_aposta_frame = ttk.Frame(apostar_frame)
        entrada_aposta_frame.pack(fill='x')
        
        ttk.Label(entrada_aposta_frame, text="Valor da Aposta (R$):").pack(side='left', padx=5)
        self.entry_valor_aposta = ttk.Entry(entrada_aposta_frame, width=15)
        self.entry_valor_aposta.pack(side='left', padx=5)
        
        self.label_retorno_potencial = ttk.Label(entrada_aposta_frame, text="Retorno Potencial: R$ 0.00", 
                                               foreground='green')
        self.label_retorno_potencial.pack(side='left', padx=10)
        
        # Botões de controle
        controle_frame = ttk.Frame(apostar_frame)
        controle_frame.pack(fill='x', pady=5)
        
        ttk.Button(controle_frame, text="🗑️ Limpar Múltipla", 
                  command=self.limpar_multipla).pack(side='left', padx=5)
        
        ttk.Button(controle_frame, text="� Apostar", 
                  command=self.realizar_aposta_multipla).pack(side='left', padx=5)
        
        # Bind para calcular retorno em tempo real
        self.entry_valor_aposta.bind('<KeyRelease>', self.calcular_retorno_tempo_real)
    
    def create_apostas_ativas_tab(self):
        """Aba das apostas ativas"""
        self.tab_apostas_ativas = ttk.Frame(self.notebook_multiplas)
        self.notebook_multiplas.add(self.tab_apostas_ativas, text="🎯 Apostas Ativas")
        
        # Frame das apostas ativas
        ativas_frame = ttk.LabelFrame(self.tab_apostas_ativas, text="Apostas em Andamento", padding=15)
        ativas_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Lista de apostas ativas
        columns_ativas = ('ID', 'Data', 'Valor', 'Odd Total', 'Retorno Pot.', 'Status', 'Jogos Green/Total')
        self.tree_apostas_ativas = ttk.Treeview(ativas_frame, columns=columns_ativas, show='headings', height=8)
        
        for col in columns_ativas:
            self.tree_apostas_ativas.heading(col, text=col)
            if col == 'ID':
                self.tree_apostas_ativas.column(col, width=150)
            elif col == 'Data':
                self.tree_apostas_ativas.column(col, width=120)
            elif col in ['Valor', 'Odd Total', 'Retorno Pot.']:
                self.tree_apostas_ativas.column(col, width=100)
            else:
                self.tree_apostas_ativas.column(col, width=100)
        
        self.tree_apostas_ativas.pack(fill='both', expand=True)
        
        # Botões de ação
        acoes_frame = ttk.Frame(ativas_frame)
        acoes_frame.pack(fill='x', pady=10)
        
        ttk.Button(acoes_frame, text="👁️ Ver Detalhes", 
                  command=self.ver_detalhes_aposta).pack(side='left', padx=5)
        ttk.Button(acoes_frame, text="💰 Cashout", 
                  command=self.fazer_cashout_aposta).pack(side='left', padx=5)
        ttk.Button(acoes_frame, text="🔄 Atualizar", 
                  command=self.atualizar_apostas_ativas).pack(side='left', padx=5)
        
        # Atualizar lista
        self.atualizar_apostas_ativas()
    
    def create_historico_tab(self):
        """Aba do histórico"""
        self.tab_historico = ttk.Frame(self.notebook_multiplas)
        self.notebook_multiplas.add(self.tab_historico, text="📊 Histórico")
        
        # Frame do histórico
        historico_frame = ttk.LabelFrame(self.tab_historico, text="Histórico de Apostas", padding=15)
        historico_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Lista do histórico
        columns_historico = ('ID', 'Data', 'Valor', 'Odd', 'Resultado', 'Retorno', 'Lucro/Perda')
        self.tree_historico = ttk.Treeview(historico_frame, columns=columns_historico, show='headings', height=10)
        
        for col in columns_historico:
            self.tree_historico.heading(col, text=col)
            if col == 'ID':
                self.tree_historico.column(col, width=150)
            elif col == 'Data':
                self.tree_historico.column(col, width=120)
            else:
                self.tree_historico.column(col, width=100)
        
        self.tree_historico.pack(fill='both', expand=True)
        
        # Botões do histórico
        hist_acoes_frame = ttk.Frame(historico_frame)
        hist_acoes_frame.pack(fill='x', pady=10)
        
        ttk.Button(hist_acoes_frame, text="👁️ Ver Detalhes", 
                  command=self.ver_detalhes_historico).pack(side='left', padx=5)
        ttk.Button(hist_acoes_frame, text="🔄 Atualizar", 
                  command=self.atualizar_historico).pack(side='left', padx=5)
        
        # Atualizar histórico
        self.atualizar_historico()
    
    # Métodos para Apostas Hot
    def auto_carregar_apostas_hot(self):
        """Carrega apostas hot apenas se não foram carregadas na inicialização"""
        if hasattr(self, 'apostas_hot_carregadas') and self.apostas_hot_carregadas:
            # Já foram carregadas, apenas exibir
            self.exibir_apostas_hot_prontas()
        else:
            # Carregar pela primeira vez
            threading.Thread(target=self.carregar_apostas_data_atual, daemon=True).start()
    
    def carregar_apostas_hot(self):
        """Carrega e analisa as melhores apostas de hoje e amanhã"""
        try:
            self.status_hot.config(text="🔄 Analisando jogos de hoje e amanhã...", style='Warning.TLabel')
            self.root.update()
            
            # Buscar jogos de hoje e amanhã
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Buscar jogos dos dois dias
            jogos_hoje = self.api.buscar_jogos_do_dia(data_hoje)
            jogos_amanha = self.api.buscar_jogos_do_dia(data_amanha)
            
            if not jogos_hoje and not jogos_amanha:
                self.status_hot.config(text="❌ Nenhum jogo encontrado para hoje e amanhã", style='Warning.TLabel')
                return
            
            # Filtrar jogos de hoje que ainda não encerraram
            jogos_validos_hoje = []
            agora = datetime.now()
            
            for jogo in jogos_hoje or []:
                try:
                    # Verificar se o jogo ainda não encerrou
                    status = jogo.get('status', {})
                    
                    # Se não tem status ou está "Not Started" ou "In Progress"
                    if (not status or 
                        status.get('description') in ['Not Started', 'In Progress', '1st Half', '2nd Half'] or
                        status.get('type') in ['inprogress', 'notstarted']):
                        
                        # Verificar horário do jogo
                        start_time_str = jogo.get('start_time')
                        if start_time_str:
                            try:
                                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                                # Se o jogo começa em menos de 6 horas no passado, considerar válido
                                if (start_time - agora).total_seconds() > -21600:  # -6 horas
                                    jogos_validos_hoje.append(jogo)
                            except:
                                # Se não conseguir parsear a data, incluir mesmo assim
                                jogos_validos_hoje.append(jogo)
                        else:
                            # Se não tem horário, incluir
                            jogos_validos_hoje.append(jogo)
                except Exception as e:
                    print(f"Erro ao filtrar jogo: {e}")
                    # Em caso de erro, incluir o jogo
                    jogos_validos_hoje.append(jogo)
            
            # Todos os jogos de amanhã são válidos
            jogos_validos_amanha = jogos_amanha or []
            
            print(f"✅ {len(jogos_validos_hoje)} jogos válidos hoje, {len(jogos_validos_amanha)} jogos amanhã")
            
            # Analisar cada jogo
            apostas_recomendadas = []
            
            # Processar jogos de hoje primeiro (prioridade)
            for jogo in jogos_validos_hoje[:8]:  # Máximo 8 de hoje
                try:
                    jogo['periodo'] = 'Hoje'
                    recomendacoes = self.processar_jogo_para_hot(jogo)
                    apostas_recomendadas.extend(recomendacoes)
                except Exception as e:
                    print(f"Erro ao analisar recomendações: {e}")
                    continue
                time.sleep(0.3)  # Pausa entre requisições
            
            # Processar jogos de amanhã
            for jogo in jogos_validos_amanha[:7]:  # Máximo 7 de amanhã
                try:
                    jogo['periodo'] = 'Amanhã'
                    recomendacoes = self.processar_jogo_para_hot(jogo)
                    apostas_recomendadas.extend(recomendacoes)
                except Exception as e:
                    print(f"Erro ao analisar recomendações: {e}")
                    continue
                time.sleep(0.3)  # Pausa entre requisições
            
            # Ordenar pela média de probabilidades (prob_implicita + prob_calculada)
            apostas_recomendadas.sort(key=lambda x: (
                0 if x.get('periodo') == 'Hoje' else 1,  # Hoje primeiro
                -((float(x.get('prob_calculada', 0)) + float(x.get('prob_implicita', 0)))/2)  # Depois pela média de probabilidades (maior para menor)
            ))
            
            # Calcular e adicionar a prob_media para cada aposta
            for aposta in apostas_recomendadas:
                prob_calc = float(aposta.get('prob_calculada', 0))
                prob_impl = float(aposta.get('prob_implicita', 0))
                aposta['prob_media'] = (prob_calc + prob_impl) / 2
            
            # Exibir apostas hot
            self.exibir_apostas_hot(apostas_recomendadas)
            
            # VERIFICAR E ATUALIZAR PERÍODOS antes de exibir
            self.verificar_e_atualizar_periodos_apostas_hot()
            
            self.status_hot.config(text=f"✅ {len(apostas_recomendadas)} apostas analisadas (Hoje e Amanhã)", 
                                 style='Success.TLabel')
            
        except Exception as e:
            self.status_hot.config(text=f"❌ Erro: {str(e)}", style='Warning.TLabel')
    
    def processar_jogo_para_hot_paralelo(self, jogo, periodo):
        """Versão paralela do processamento de jogo para hot"""
        try:
            # Extrair dados do jogo
            if isinstance(jogo, dict):
                jogo_id = jogo.get('id', 'N/A')
                time_casa = jogo.get('home_team', jogo.get('time_casa', 'N/A'))
                time_visitante = jogo.get('away_team', jogo.get('time_visitante', 'N/A'))
            else:
                jogo_id = str(jogo)
                time_casa = 'N/A'
                time_visitante = 'N/A'
            
            # Buscar odds detalhadas
            odds_detalhadas = None
            if jogo_id and jogo_id != 'N/A':
                try:
                    odds_detalhadas = self.buscar_odds_detalhadas(jogo_id)
                except Exception as e:
                    print(f"⚠️ Erro ao buscar odds para {jogo_id}: {e}")
            
            # Criar jogo completo sempre (com ou sem odds)
            if odds_detalhadas:
                jogo_completo = {**jogo, **odds_detalhadas} if isinstance(jogo, dict) else {**odds_detalhadas, 'id': jogo_id}
                jogo_completo['periodo'] = periodo
                print(f"✅ Jogo {time_casa} vs {time_visitante} - COM odds")
            else:
                jogo_completo = jogo.copy() if isinstance(jogo, dict) else {'id': jogo_id}
                jogo_completo.update({
                    'periodo': periodo,
                    'odds': None,
                    'home_team': time_casa,
                    'away_team': time_visitante,
                    'start_time': jogo_completo.get('start_time', ''),
                    'league': jogo_completo.get('league', 'N/A')
                })
                print(f"⚠️ Jogo {time_casa} vs {time_visitante} - SEM odds (dados básicos)")
            
            # Processar apostas hot se tiver dados válidos
            recomendacoes = []
            if isinstance(jogo, dict):
                jogo['periodo'] = periodo
                try:
                    recomendacoes = self.processar_jogo_para_hot(jogo)
                    print(f"📊 {len(recomendacoes)} apostas hot geradas")
                except Exception as e:
                    print(f"⚠️ Erro ao processar apostas hot: {e}")
            
            return jogo_completo, recomendacoes
            
        except Exception as e:
            print(f"❌ ERRO no processamento paralelo: {e}")
            # Retornar jogo básico em caso de erro
            jogo_erro = {
                'id': jogo.get('id') if isinstance(jogo, dict) else str(jogo),
                'home_team': 'Erro',
                'away_team': 'Erro',
                'periodo': periodo,
                'odds': None
            }
            return jogo_erro, []

    def processar_jogo_para_hot(self, jogo):
        """Processa um jogo para gerar recomendações hot"""
        try:
            # Verificar se jogo é um dicionário ou apenas ID
            if isinstance(jogo, str):
                jogo_id = jogo
                jogo_dict = {'id': jogo}
            else:
                jogo_id = jogo.get('id')
                jogo_dict = jogo
            
            if not jogo_id:
                return []
            
            # Buscar odds detalhadas
            odds_detalhadas = self.buscar_odds_detalhadas(jogo_id)
            if not odds_detalhadas:
                return []
            
            # Buscar estatísticas dos times
            stats = self.api.buscar_estatisticas_detalhadas_time(jogo_id)
            if not stats:
                return []
            
            # Calcular probabilidades - USAR A MESMA FUNÇÃO DOS JOGOS DO DIA
            modo = self.modo_analise.get() if hasattr(self, 'modo_analise') else "Geral"
            probabilidades = self.calcular_probabilidades_completas(stats, modo)
            
            # Analisar apostas recomendadas
            recomendacoes = self.analisar_apostas_recomendadas(
                jogo_dict, odds_detalhadas, probabilidades, stats)
            
            # Adicionar informação do período
            for rec in recomendacoes:
                rec['periodo'] = jogo_dict.get('periodo', 'Hoje')
            
            return recomendacoes
            
        except Exception as e:
            home_team = jogo_dict.get('home_team', 'Time')
            away_team = jogo_dict.get('away_team', 'Time')
            print(f"Erro ao processar jogo {home_team} vs {away_team}: {e}")
            return []
    
    def buscar_odds_detalhadas(self, match_id):
        """Busca odds detalhadas de uma partida"""
        try:
            url = f"https://api.radaresportivo.com/public/prepRadar/{match_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'marketOdds' in data:
                return {
                    'match_id': match_id,
                    'start_time': data.get('startTime', ''),
                    'odds': data['marketOdds'],
                    'home_team': data.get('homeTeam', {}).get('name', ''),
                    'away_team': data.get('awayTeam', {}).get('name', ''),
                    'league': data.get('league', {}).get('name', ''),
                    'status': data.get('status', 'not_started')
                }
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar odds para match {match_id}: {e}")
            return None
    
    def analisar_apostas_recomendadas(self, jogo, odds_detalhadas, probabilidades, stats):
        """Analisa e gera recomendações de apostas"""
        recomendacoes = []
        
        try:
            # Filtrar por código de região permitido
            codigos_regiao_permitidos = ['ES', 'FR', 'SA', 'BR', 'AR', 'PT', 'IT', 'GB', 'TR', 'DE', '00', '01', '04']
            codigo_regiao = jogo.get('codigo_regiao', '')
            
            # Se o jogo não tem região permitida, retornar lista vazia
            if codigo_regiao not in codigos_regiao_permitidos:
                print(f"⚠️ Jogo filtrado por região não permitida: {codigo_regiao}")
                return []
            
            # Filtrar por relevância da liga (apenas high)
            relevancia_liga = jogo.get('relevancia_liga', '')
            if relevancia_liga != 'high':
                print(f"⚠️ Jogo filtrado por relevância da liga: {relevancia_liga}")
                return []
            
            odds = odds_detalhadas['odds']
            
            # 1. Analisar Resultado Final (1X2)
            if 'resultFt' in odds:
                result_odds = odds['resultFt']
                
                # Calcular probabilidades implícitas com margem de 7.5%
                prob_casa_implicita = (1 / result_odds['home'] * (1 - 0.05)) * 100
                prob_empate_implicita = (1 / result_odds['draw'] * (1 - 0.05)) * 100
                prob_fora_implicita = (1 / result_odds['away'] * (1 - 0.05)) * 100
                
                # Comparar com probabilidades Bet Booster calculadas
                prob_casa_calc = probabilidades.get('vitoria_casa', 0)
                prob_empate_calc = probabilidades.get('empate', 0)
                prob_fora_calc = probabilidades.get('vitoria_visitante', 0)
                
                # Identificar value bets
                value_casa = (prob_casa_calc / prob_casa_implicita) if prob_casa_implicita > 0 else 0
                value_empate = (prob_empate_calc / prob_empate_implicita) if prob_empate_implicita > 0 else 0
                value_fora = (prob_fora_calc / prob_fora_implicita) if prob_fora_implicita > 0 else 0
                
                # Recomendações baseadas nos critérios
                home_team = odds_detalhadas.get('home_team', 'Casa')
                away_team = odds_detalhadas.get('away_team', 'Visitante')
                
                apostas_resultado = [
                    (f'Vitória {home_team}', 'casa', value_casa, prob_casa_calc, prob_casa_implicita, result_odds['home']),
                    ('Empate', 'empate', value_empate, prob_empate_calc, prob_empate_implicita, result_odds['draw']),
                    (f'Vitória {away_team}', 'visitante', value_fora, prob_fora_calc, prob_fora_implicita, result_odds['away'])
                ]
                
                for aposta, tipo_aposta, value, prob_calc, prob_impl, odd in apostas_resultado:
                    # Converter value para porcentagem
                    value_percent = (value - 1) * 100
                    
                    # Aplicar NOVAS regras para apostas de vencedor:
                    # Forte: Prob. Bet365 >= 40%, value > 0%
                    # Moderada: Prob. Booster >= 40%, Prob. Bet365 >= 30%, value > 0%
                    # Arriscada: Prob. Bet365 >= 40%, Prob. Bet365 >= 15% E < 30%, value > 0%
                    # Muito Arriscada: Prob. Bet365 >= 40%, Prob. Bet365 >= 5% E < 15%, value > 0%
                    tipo_recomendacao = None


                    if (odd >= 1.5) and (odd < 2) and (prob_calc >= 40):
                        tipo_recomendacao = "FORTE"
                    elif (odd >= 2) and (odd < 2.5) and (prob_calc >= 40):
                        tipo_recomendacao = "MODERADA"
                    elif (odd >= 2.5) and (odd < 3) and (prob_calc >= 40):
                        tipo_recomendacao = "ARRISCADA"
                    elif (odd >= 3) and (odd < 5.5) and (prob_calc >= 40):
                        tipo_recomendacao = "MUITO_ARRISCADA"
                    
                    if tipo_recomendacao:  # Mínimo de confiança na probabilidade Bet Booster
                        
                        forca = value * (prob_calc / 100)  # Força baseada em value e probabilidade
                        recomendacoes.append({
                            'jogo': f"{odds_detalhadas['home_team']} vs {odds_detalhadas['away_team']}",
                            'aposta': aposta,
                            'tipo': tipo_recomendacao,
                            'odd': odd,
                            'value': value,
                            'value_percent': value_percent,
                            'prob_calculada': prob_calc,
                            'nossa_prob': prob_calc,  # Adicionar para compatibilidade
                            'prob_implicita': prob_impl,
                            'prob_media': (prob_calc + prob_impl) / 2,  # Média de probabilidades
                            'forca_recomendacao': forca,
                            'match_id': odds_detalhadas['match_id'],
                            'liga': odds_detalhadas['league'],
                            'horario': self.formatar_horario(odds_detalhadas['start_time'])
                        })
            
            # 2. Analisar Over/Under 2.5 gols
            if 'goalsOu25' in odds:
                gols_odds = odds['goalsOu25']
                
                # Calcular gols esperados
                gols_esperados = probabilidades.get('gols_esperados_total', 0)
                
                # Probabilidades para over/under 2.5
                prob_over25_calc = self.calcular_prob_over_under(gols_esperados, 2.5, 'over')
                prob_under25_calc = 100 - prob_over25_calc
                
                # Probabilidades implícitas com margem de 7.5%
                prob_over25_impl = (1 / gols_odds['over'] * (1 - 0.05)) * 100
                prob_under25_impl = (1 / gols_odds['under'] * (1 - 0.05)) * 100
                
                # Value bets
                value_over = (prob_over25_calc / prob_over25_impl) if prob_over25_impl > 0 else 0
                value_under = (prob_under25_calc / prob_under25_impl) if prob_under25_impl > 0 else 0
                
                apostas_gols = [
                    ('Mais de 2.5 gols', value_over, prob_over25_calc, prob_over25_impl, gols_odds['over']),
                    ('Menos de 2.5 gols', value_under, prob_under25_calc, prob_under25_impl, gols_odds['under'])
                ]
                
                for aposta, value, prob_calc, prob_impl, odd in apostas_gols:
                    # Converter value para porcentagem
                    value_percent = (value - 1) * 100
                    
                    # Filtrar apostas over 2.5 com poucos gols esperados
                    if aposta == 'Mais de 2.5 gols' and gols_esperados < 4.0:
                        continue  # Pular apostas over 2.5 quando gols esperados for menor que 4
                    
                    # Filtrar apostas under 2.5 com muitos gols esperados
                    if aposta == 'Menos de 2.5 gols' and gols_esperados > 2.0:
                        continue  # Pular apostas under 2.5 quando gols esperados for maior que 2
                    
                    # Aplicar NOVAS regras para apostas Over/Under:
                    # Forte: Prob. Booster > 50%, Prob. Bet365 >= 45%, value > 0
                    # Moderada: Prob. Booster > 50%, Prob. Bet365 >= 35%, value > 0
                    # Arriscada: Prob. Booster > 50%, Prob. Bet365 >= 20% E < 35%, value > 0
                    # Muito Arriscada: Prob. Booster > 50%, Prob. Bet365 >= 5% E < 20%, value > 0
                    tipo_recomendacao = None
                    
                    if odd <= 1.8 and prob_calc >= 70:
                        tipo_recomendacao = "FORTE"
                    elif (odd <= 2.5 and prob_calc >= 70) or (odd <= 1.8 and prob_calc >= 65):
                        tipo_recomendacao = "MODERADA"
                    
                    if tipo_recomendacao and prob_calc >= 15:  # Mínimo de confiança na probabilidade Bet Booster
                        
                        forca = value * (prob_calc / 100)
                        
                        recomendacoes.append({
                            'jogo': f"{odds_detalhadas['home_team']} vs {odds_detalhadas['away_team']}",
                            'aposta': aposta,
                            'tipo': tipo_recomendacao,
                            'odd': odd,
                            'value': value,
                            'value_percent': value_percent,
                            'prob_calculada': prob_calc,
                            'nossa_prob': prob_calc,  # Adicionar para compatibilidade
                            'prob_implicita': prob_impl,
                            'prob_media': (prob_calc + prob_impl) / 2,  # Média de probabilidades
                            'forca_recomendacao': forca,
                            'match_id': odds_detalhadas['match_id'],
                            'liga': odds_detalhadas['league'],
                            'horario': self.formatar_horario(odds_detalhadas['start_time'])
                        })
            
        except Exception as e:
            print(f"Erro ao analisar recomendações: {e}")
        
        return recomendacoes
    
    def exibir_apostas_hot(self, apostas):
        """Exibe as apostas hot na interface usando a ordenação selecionada no filtro"""
        # Armazenar as apostas
        self.apostas_hot = apostas
        
        # Aplicar filtros para ordenar e exibir conforme selecionado pelo usuário
        self.aplicar_filtros_hot()  # Aplicar filtros atuais incluindo a ordenação
    
    def criar_card_aposta_hot(self, aposta, index, parent_frame):
        """Cria um card visual para uma aposta recomendada"""
        # Frame do card com cor de fundo do tema
        card_frame = tk.Frame(parent_frame, bg=self.cores['bg_card'], relief='ridge', borderwidth=2, padx=15, pady=15)
        card_frame.pack(fill='x', pady=5, padx=5, expand=True)
        
        # Linha 1: Jogo, horário e ranking
        linha1 = tk.Frame(card_frame, bg=self.cores['bg_card'])
        linha1.pack(fill='x', padx=15, pady=10)
        
        # Adicionar número da posição e medalha (se for top 3)
        if index == 0:
            ranking_text = "🥇 #1"
            ranking_color = "gold"
        elif index == 1:
            ranking_text = "🥈 #2"
            ranking_color = "silver"
        elif index == 2:
            ranking_text = "🥉 #3"
            ranking_color = "#CD7F32"  # Bronze
        else:
            ranking_text = f"#{index+1}"
            ranking_color = "black"
            
        ranking_label = tk.Label(linha1, text=ranking_text, font=('Arial', 10, 'bold'),
                                bg=self.cores['bg_card'], fg=ranking_color)
        ranking_label.pack(side='left', padx=(0, 10))
        
        jogo_label = tk.Label(linha1, text=aposta['jogo'], 
                             font=('Arial', 12, 'bold'), bg=self.cores['bg_card'], fg=self.cores['fg_titulo'])
        jogo_label.pack(side='left')
        
        # Mostrar período (Hoje/Amanhã) ou data formatada
        periodo = aposta.get('periodo', '')
        data_jogo = aposta.get('data_jogo', '')
        
        # Se tiver data_jogo, formatar como DD/MM/YYYY
        if data_jogo:
            # Converter formato YYYY-MM-DD para DD/MM/YYYY
            try:
                data_obj = datetime.strptime(data_jogo, '%Y-%m-%d')
                data_formatada = data_obj.strftime('%d/%m/%Y')
                periodo = data_formatada
                periodo_color = 'purple'  # Cor diferente para datas específicas
            except:
                # Em caso de erro, usar o período já formatado se estiver disponível
                if periodo and '/' in periodo:  # Já é uma data formatada
                    periodo_color = 'purple'
                else:
                    periodo = data_jogo  # Fallback para a string da data
                    periodo_color = 'purple'
        elif periodo and '/' in periodo:  # Já é uma data formatada
            periodo_color = 'purple'
        else:
            # Se não tiver data nem período formatado, usar o padrão de hoje
            periodo = datetime.now().strftime('%d/%m/%Y')
            periodo_color = 'red'
            
        periodo_label = tk.Label(linha1, text=f"📅 {periodo}", 
                                font=('Arial', 10, 'bold'), bg=self.cores['bg_card'], fg=periodo_color)
        periodo_label.pack(side='right')
        
        horario_label = tk.Label(linha1, text=f"⏰ {aposta['horario']}", 
                                font=('Arial', 10, 'bold'), bg=self.cores['bg_card'], fg='green')
        horario_label.pack(side='right')
        
        # Linha 2: Liga
        liga_label = tk.Label(card_frame, text=f"🏆 {aposta['liga']}", 
                             font=('Arial', 9), bg=self.cores['bg_card'], fg=self.cores['fg_normal'])
        liga_label.pack(anchor='w')
        
        # Linha 3: Aposta e tipo
        linha3 = tk.Frame(card_frame, bg=self.cores['bg_card'])
        linha3.pack(fill='x', pady=5)
        
        # Definir cor e emoji baseado no tipo
        if aposta['tipo'] == 'FORTE':
            tipo_color_fg = 'green'
            tipo_emoji = '🟢'
        elif aposta['tipo'] == 'MODERADA':
            tipo_color_fg = '#4A90E2'
            tipo_emoji = '🔵'
        elif aposta['tipo'] == 'MUITO_ARRISCADA':
            tipo_color_fg = 'red'
            tipo_emoji = '🔴'
        else:  # ARRISCADA
            tipo_color_fg = 'orange'
            tipo_emoji = '🟡'
        
        aposta_label = tk.Label(linha3, text=f"{tipo_emoji} {aposta['aposta']}", 
                               font=('Arial', 11, 'bold'), bg=self.cores['bg_card'], fg=tipo_color_fg)
        aposta_label.pack(side='left')
        
        odd_label = tk.Label(linha3, text=f"Odd: {aposta['odd']:.2f}", 
                            font=('Arial', 11, 'bold'), bg=self.cores['bg_card'], fg=self.cores['fg_titulo'])
        odd_label.pack(side='right')
        
        # Linha 4: Probabilidades e value
        linha4 = tk.Frame(card_frame, bg=self.cores['bg_card'])
        linha4.pack(fill='x')
        
        prob_calc_label = tk.Label(linha4, text=f"📊 Prob. Bet Booster: {aposta['prob_calculada']:.1f}%",
                                   bg=self.cores['bg_card'], fg=self.cores['fg_normal'])
        prob_calc_label.pack(side='left')
        
        prob_impl_label = tk.Label(linha4, text=f"🎯 Prob. Bet365: {aposta['prob_implicita']:.1f}%",
                                   bg=self.cores['bg_card'], fg=self.cores['fg_normal'])
        prob_impl_label.pack(side='left', padx=20)
        
        value_label = tk.Label(linha4, text=f"💎 Value: {((aposta['value'] - 1) * 100):.1f}%", 
                              font=('Arial', 10, 'bold'), bg=self.cores['bg_card'], fg='green')
        value_label.pack(side='right')
        
        # Adicionar linha com a média das probabilidades
        linha_media = tk.Frame(card_frame, bg=self.cores['bg_card'])
        linha_media.pack(fill='x', pady=(5, 0))
        
        media_prob = (aposta['prob_calculada'] + aposta['prob_implicita']) / 2
        media_label = tk.Label(linha_media, 
                              text=f"⭐ Média Prob.: {media_prob:.1f}%",
                              font=('Arial', 10, 'bold'), bg=self.cores['bg_card'], fg='purple')
        media_label.pack(side='left')
        
        # Botões de ação
        acoes_frame = tk.Frame(card_frame, bg=self.cores['bg_card'])
        acoes_frame.pack(fill='x', pady=10)
        
        ttk.Button(acoes_frame, text="📋 Adicionar à Múltipla", 
                  command=lambda a=aposta: self.adicionar_aposta_multipla(a)).pack(side='left', padx=5)
        ttk.Button(acoes_frame, text="📊 Ver Análise Completa", 
                  command=lambda a=aposta: self.ver_analise_completa(a)).pack(side='left', padx=5)
        ttk.Button(acoes_frame, text="🗑️ Deletar Aposta", 
                  command=lambda a=aposta, cf=card_frame: self.deletar_aposta_hot(a, cf)).pack(side='left', padx=5)
    
    # Métodos para Jogos do Dia
    def buscar_jogos_do_dia(self):
        """Busca jogos do dia selecionado com cache inteligente"""
        try:
            self.status_jogos.config(text="🔄 Verificando cache...", style='Warning.TLabel')
            self.root.update()
            
            # Obter data diretamente do DateEntry
            data_obj = self.entry_data.get_date()
            data_api = data_obj.strftime('%Y-%m-%d')
            
            # Tentar carregar do cache primeiro
            if self.atualizar_jogos_do_dia_com_cache(data_api):
                return  # Se conseguiu carregar do cache, termina aqui
            
            # Se não há cache válido, carregar da API
            self.status_jogos.config(text="🌐 Buscando jogos da API...", style='Warning.TLabel')
            self.root.update()
            
            jogos = self.api.buscar_jogos_do_dia(data_api)
            
            if not jogos:
                self.status_jogos.config(text="❌ Nenhum jogo encontrado", style='Warning.TLabel')
                return
            
            # Buscar odds para cada jogo em paralelo
            self.status_jogos.config(text="📊 Carregando odds (processamento paralelo)...", style='Warning.TLabel')
            self.root.update()
            
            self.jogos_do_dia = []
            
            # Usar ThreadPoolExecutor para processamento paralelo
            max_workers = 10  # Máximo 10 threads simultâneas
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submeter todas as tarefas
                futures = []
                for jogo in jogos:
                    future = executor.submit(self.processar_jogo_odds_paralelo, jogo)  # Só odds, não apostas hot
                    futures.append((future, jogo))
                
                # Coletar resultados conforme completam
                for i, (future, jogo_original) in enumerate(futures):
                    try:
                        # Atualizar progresso
                        progresso = (i + 1) / len(jogos) * 100
                        self.status_jogos.config(
                            text=f"⚽ Processando jogo {i+1}/{len(jogos)} ({progresso:.0f}%) - Paralelo", 
                            style='Warning.TLabel'
                        )
                        self.root.update()
                        
                        # Obter resultado com timeout (só jogo com odds)
                        jogo_completo = future.result(timeout=3)  # Timeout de 3 segundos por jogo
                        self.jogos_do_dia.append(jogo_completo)
                        
                    except Exception as e:
                        print(f"Erro ao processar jogo {jogo_original.get('id', 'desconhecido')}: {e}")
                        jogo_original['odds'] = None
                        self.jogos_do_dia.append(jogo_original)
            
            # Salvar no cache (SOMENTE OS JOGOS, sem afetar apostas hot)
            dados_cache = {
                'jogos': self.jogos_do_dia,
                'apostas_hot': []  # Não salvar apostas hot aqui para não afetar a aba
            }
            self.salvar_jogos_cache(data_api, dados_cache)
            
            # Atualizar lista visual
            self.atualizar_lista_jogos()
            
            tempo_agora = datetime.now().strftime('%H:%M:%S')
            self.status_jogos.config(
                text=f"✅ {len(self.jogos_do_dia)} jogos carregados - Paralelo - {tempo_agora}", 
                style='Success.TLabel'
            )
            
        except Exception as e:
            self.status_jogos.config(text=f"❌ Erro: {str(e)}", style='Warning.TLabel')
    

    
    def atualizar_lista_jogos(self):
        """Atualiza a lista visual de jogos preservando filtro ativo"""
        # Verificar se há filtro ativo
        texto_filtro = ""
        if hasattr(self, 'entry_pesquisa_jogos'):
            texto_filtro = self.entry_pesquisa_jogos.get().lower().strip()
        
        # Limpar árvore
        for item in self.tree_jogos.get_children():
            self.tree_jogos.delete(item)
        
        # Resetar seleções
        if not hasattr(self, 'jogos_selecionados'):
            self.jogos_selecionados = []
        
        # Reinicializar dados originais para filtro
        self.jogos_originais = []
        
        # Adicionar jogos
        for i, jogo in enumerate(self.jogos_do_dia):
            # Checkbox de seleção
            checkbox = "☑" if i in self.jogos_selecionados else "☐"
            
            # Horário
            start_time = jogo.get('start_time', '') or jogo.get('horario', '')
            horario = self.formatar_horario(start_time)
            
            # Times
            casa = jogo.get('home_team', jogo.get('time_casa', '')) or ''
            visitante = jogo.get('away_team', jogo.get('time_visitante', '')) or ''
            
            # Liga
            liga = jogo.get('league', jogo.get('liga', '')) or ''
            
            # Formatear odds - tratamento mais robusto
            odds_text = "N/A"
            try:
                if jogo.get('odds') and isinstance(jogo['odds'], dict):
                    if 'resultFt' in jogo['odds'] and jogo['odds']['resultFt']:
                        result_odds = jogo['odds']['resultFt']
                        if all(key in result_odds for key in ['home', 'draw', 'away']):
                            home_odd = result_odds['home']
                            draw_odd = result_odds['draw'] 
                            away_odd = result_odds['away']
                            
                            # Verificar se os valores não são None
                            if home_odd is not None and draw_odd is not None and away_odd is not None:
                                odds_text = f"{home_odd:.2f} / {draw_odd:.2f} / {away_odd:.2f}"
                elif jogo.get('odds_casa') and jogo.get('odds_empate') and jogo.get('odds_visitante'):
                    # Formato alternativo do cache
                    odds_text = f"{jogo['odds_casa']:.2f} / {jogo['odds_empate']:.2f} / {jogo['odds_visitante']:.2f}"
            except (TypeError, KeyError, ValueError) as e:
                print(f"Erro ao formatar odds: {e}")
                odds_text = "N/A"
            
            # Inserir na árvore com checkbox
            item_id = self.tree_jogos.insert('', 'end', values=(
                checkbox, horario, casa, visitante, liga, odds_text
            ))
            
            # Armazenar dados originais para filtro
            self.jogos_originais.append((checkbox, horario, casa, visitante, liga, odds_text))
        
        # APLICAR FILTRO SE HAVIA UM ATIVO
        if texto_filtro:
            self.aplicar_filtro_preservado(texto_filtro)
        
        # Atualizar status da seleção
        self.atualizar_status_selecao()
    
    def aplicar_filtro_preservado(self, texto_filtro):
        """Aplica filtro preservando a pesquisa anterior"""
        try:
            # Limpar tree
            for item in self.tree_jogos.get_children():
                self.tree_jogos.delete(item)
            
            # Filtrar e repovoar
            for jogo_data in self.jogos_originais:
                if len(jogo_data) >= 5:  # Verificar se tem dados suficientes
                    casa = str(jogo_data[2]).lower()
                    visitante = str(jogo_data[3]).lower()
                    liga = str(jogo_data[4]).lower()
                    
                    # Verificar se o texto de pesquisa está em algum campo
                    if (texto_filtro in casa or 
                        texto_filtro in visitante or 
                        texto_filtro in liga):
                        self.tree_jogos.insert('', 'end', values=jogo_data)
                        
        except Exception as e:
            print(f"Erro ao aplicar filtro preservado: {e}")
    
    def on_jogo_clicado(self, event):
        """Callback quando um jogo é clicado (para seleção/deseleção)"""
        try:
            selection = self.tree_jogos.selection()
            if not selection:
                return
            
            # Obter dados do item clicado
            item = self.tree_jogos.item(selection[0])
            values = item['values']
            
            # Encontrar índice real do jogo baseado nos dados (casa e visitante)
            if len(values) >= 4:
                casa_clicada = values[2]  # Casa
                visitante_clicada = values[3]  # Visitante
                
                # Buscar índice real no array jogos_do_dia
                index_real = None
                for i, jogo in enumerate(self.jogos_do_dia):
                    casa_original = jogo.get('home_team', jogo.get('time_casa', '')) or ''
                    visitante_original = jogo.get('away_team', jogo.get('time_visitante', '')) or ''
                    
                    if casa_clicada == casa_original and visitante_clicada == visitante_original:
                        index_real = i
                        break
                
                if index_real is not None:
                    # Verificar se clicou na coluna de checkbox
                    region = self.tree_jogos.identify_region(event.x, event.y)
                    column = self.tree_jogos.identify_column(event.x)
                    
                    if column == '#1':  # Primeira coluna (checkbox)
                        self.selecionar_unico_jogo(index_real)
                    else:
                        # Seleção única também para clique normal
                        self.selecionar_unico_jogo(index_real)
                else:
                    print(f"⚠️ Não foi possível encontrar o jogo clicado: {casa_clicada} vs {visitante_clicada}")
                
        except Exception as e:
            print(f"Erro ao clicar no jogo: {e}")
    
    def selecionar_unico_jogo(self, index):
        """Seleciona apenas um jogo, removendo seleções anteriores"""
        # Se o jogo já está selecionado, deselecionar
        if index in self.jogos_selecionados:
            self.jogos_selecionados = []
            self.jogo_selecionado_index = None
        else:
            # Seleção única - apenas um jogo
            self.jogos_selecionados = [index]
            self.jogo_selecionado_index = index
        
        # Atualizar apenas checkboxes sem resetar filtro
        self.atualizar_checkboxes_jogos()
    
    def atualizar_checkboxes_jogos(self):
        """Atualiza apenas os checkboxes dos jogos sem resetar filtro"""
        try:
            # Obter todos os itens visíveis na tree
            items = self.tree_jogos.get_children()
            
            for item in items:
                values = list(self.tree_jogos.item(item)['values'])
                if len(values) >= 6:
                    # Encontrar índice do jogo original baseado nos dados
                    casa = values[2]
                    visitante = values[3]
                    
                    # Procurar índice no jogos_do_dia
                    jogo_index = None
                    for i, jogo in enumerate(self.jogos_do_dia):
                        casa_original = jogo.get('home_team', jogo.get('time_casa', '')) or ''
                        visitante_original = jogo.get('away_team', jogo.get('time_visitante', '')) or ''
                        
                        if casa == casa_original and visitante == visitante_original:
                            jogo_index = i
                            break
                    
                    # Atualizar checkbox
                    if jogo_index is not None:
                        checkbox = "☑" if jogo_index in self.jogos_selecionados else "☐"
                        values[0] = checkbox
                        self.tree_jogos.item(item, values=values)
            
            # Atualizar status da seleção
            self.atualizar_status_selecao()
            
        except Exception as e:
            print(f"Erro ao atualizar checkboxes: {e}")
            # Em caso de erro, usar método tradicional
            self.atualizar_lista_jogos()
    
    def toggle_selecao_jogo(self, index):
        """Alterna a seleção de um jogo (DEPRECATED - usar selecionar_unico_jogo)"""
        self.selecionar_unico_jogo(index)
    
    def selecionar_todos_jogos(self):
        """Seleciona o primeiro jogo da lista"""
        if self.jogos_do_dia:
            self.selecionar_unico_jogo(0)
    
    def limpar_selecao_jogos(self):
        """Limpa toda a seleção"""
        self.jogos_selecionados = []
        self.jogo_selecionado_index = None
        self.atualizar_checkboxes_jogos()  # Usar função que preserva filtro
    
    def atualizar_status_selecao(self):
        """Atualiza o status da seleção"""
        if not hasattr(self, 'status_selecao'):
            return
            
        if not self.jogos_selecionados:
            texto = "Nenhum jogo selecionado"
            estilo = 'Subtitle.TLabel'
        else:
            # Só pode haver um jogo selecionado
            jogo = self.jogos_do_dia[self.jogos_selecionados[0]]
            casa = jogo.get('home_team', jogo.get('time_casa', ''))
            visitante = jogo.get('away_team', jogo.get('time_visitante', ''))
            texto = f"✅ Jogo selecionado: {casa} vs {visitante}"
            estilo = 'Success.TLabel'
        
        self.status_selecao.config(text=texto, style=estilo)
    
    def on_jogo_selecionado(self, event):
        """Callback quando um jogo é selecionado com duplo clique"""
        try:
            selection = self.tree_jogos.selection()
            if not selection:
                return
            
            # Obter dados do item clicado
            item = self.tree_jogos.item(selection[0])
            values = item['values']
            
            # Encontrar índice real do jogo baseado nos dados (casa e visitante)
            if len(values) >= 4:
                casa_clicada = values[2]  # Casa
                visitante_clicada = values[3]  # Visitante
                
                # Buscar índice real no array jogos_do_dia
                index_real = None
                for i, jogo in enumerate(self.jogos_do_dia):
                    casa_original = jogo.get('home_team', jogo.get('time_casa', '')) or ''
                    visitante_original = jogo.get('away_team', jogo.get('time_visitante', '')) or ''
                    
                    if casa_clicada == casa_original and visitante_clicada == visitante_original:
                        index_real = i
                        break
                
                if index_real is not None:
                    # Seleção única - substituir seleção anterior
                    self.jogo_selecionado_index = index_real
                    self.jogos_selecionados = [index_real]  # Apenas um jogo selecionado
                    
                    # Atualizar interface preservando filtro
                    self.atualizar_checkboxes_jogos()
                else:
                    print(f"⚠️ Não foi possível encontrar o jogo duplo-clicado: {casa_clicada} vs {visitante_clicada}")
            
        except Exception as e:
            print(f"Erro ao selecionar jogo: {e}")
            
        except Exception as e:
            print(f"Erro ao selecionar jogo: {e}")
    
    def calcular_prob_jogo_selecionado(self):
        """Calcula probabilidades do jogo selecionado com análise completa"""
        if not hasattr(self, 'jogo_selecionado_index') or self.jogo_selecionado_index is None:
            messagebox.showwarning("Aviso", "Selecione um jogo primeiro.\n\nClique em um jogo da lista ou use duplo clique para selecioná-lo.")
            return
        
        jogo = self.jogos_do_dia[self.jogo_selecionado_index]
        
        try:
            # Buscar estatísticas do jogo
            jogo_id = jogo.get('id')
            if not jogo_id:
                messagebox.showerror("Erro", "ID do jogo não encontrado")
                return
            
            # Buscar estatísticas
            stats = self.api.buscar_estatisticas_detalhadas_time(jogo_id)
            if not stats:
                messagebox.showerror("Erro", "Não foi possível obter estatísticas do jogo")
                return
            
            # Calcular probabilidades
            probabilidades = self.calcular_probabilidades_completas(stats, self.modo_analise.get())
            
            # Extrair nomes dos times
            casa = jogo.get('home_team', jogo.get('time_casa', ''))
            visitante = jogo.get('away_team', jogo.get('time_visitante', ''))
            
            # Converter e formatar forma recente (igual à análise completa das apostas hot)
            forma_casa_raw = stats.get('time_casa', {}).get('geral', {}).get('forma', [])
            forma_visitante_raw = stats.get('time_visitante', {}).get('geral', {}).get('forma', [])
            
            forma_casa_vde = self.converter_forma_recente_para_vde(forma_casa_raw)
            forma_visitante_vde = self.converter_forma_recente_para_vde(forma_visitante_raw)
            
            # Criar objeto aposta simulado para usar a mesma função de análise completa
            aposta_simulada = {
                'jogo': f"{casa} vs {visitante}",
                'aposta': "Análise Completa",
                'odd': 0.0,
                'nossa_prob': 0.0,
                'prob_implicita': 0.0,
                'value': 1.0,
                'tipo': 'analise_jogos_do_dia',
                'periodo': jogo.get('date', 'Hoje'),
                'liga': jogo.get('league_name', 'Liga não informada'),
                'horario': jogo.get('time', 'Horário não informado'),
                'match_id': jogo_id
            }
            
            # Usar a mesma função de análise completa personalizada das apostas hot
            self.mostrar_analise_completa_personalizada(aposta_simulada, casa, visitante, probabilidades, 
                                                       forma_casa_vde, forma_visitante_vde, "")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular probabilidades:\n{str(e)}")
            print(f"Erro detalhado: {e}")
            import traceback
            traceback.print_exc()
    
    def forcar_atualizacao_jogos(self):
        """Atualiza apenas os jogos na aba sem mexer no cache"""
        try:
            # Obter data diretamente do DateEntry
            data_obj = self.entry_data.get_date()
            data_api = data_obj.strftime('%Y-%m-%d')
            
            # Atualizar status
            self.status_jogos.config(text="🔄 Atualizando jogos da aba...", style='Warning.TLabel')
            self.root.update()
            
            # Buscar jogos da API sem mexer no cache
            self.atualizar_jogos_sem_cache(data_api)
            
        except Exception as e:
            self.status_jogos.config(text=f"❌ Erro na atualização: {str(e)}", style='Warning.TLabel')
            messagebox.showerror("Erro", f"Erro ao atualizar jogos: {str(e)}")
    
    def atualizar_jogos_sem_cache(self, data_api):
        """Atualiza jogos na interface sem mexer no cache - VERSÃO PARALELA"""
        try:
            # Buscar jogos da API
            self.status_jogos.config(text="🌐 Buscando jogos da API...", style='Warning.TLabel')
            self.root.update()
            
            jogos = self.api.buscar_jogos_do_dia(data_api)
            
            if not jogos:
                self.status_jogos.config(text="❌ Nenhum jogo encontrado", style='Warning.TLabel')
                return
            
            # Buscar odds para cada jogo em paralelo
            self.status_jogos.config(text="📊 Carregando odds (processamento paralelo)...", style='Warning.TLabel')
            self.root.update()
            
            jogos_atualizados = []
            
            # Usar ThreadPoolExecutor para processamento paralelo
            max_workers = 10  # Máximo 10 threads simultâneas
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submeter todas as tarefas
                futures = []
                for jogo in jogos:
                    future = executor.submit(self.processar_jogo_odds_paralelo, jogo)
                    futures.append((future, jogo))
                
                # Coletar resultados conforme completam
                for i, (future, jogo_original) in enumerate(futures):
                    try:
                        # Atualizar progresso
                        progresso = (i + 1) / len(jogos) * 100
                        self.status_jogos.config(
                            text=f"⚽ Processando jogo {i+1}/{len(jogos)} ({progresso:.0f}%) - Paralelo", 
                            style='Warning.TLabel'
                        )
                        self.root.update()
                        
                        # Obter resultado com timeout
                        jogo_completo = future.result(timeout=3)  # Timeout de 3 segundos por jogo
                        jogos_atualizados.append(jogo_completo)
                        
                    except Exception as e:
                        print(f"Erro ao processar jogo {jogo_original.get('id', 'desconhecido')}: {e}")
                        jogo_original['odds'] = None
                        jogos_atualizados.append(jogo_original)
            
            # Atualizar apenas os jogos na interface (sem modificar o cache)
            self.jogos_do_dia = jogos_atualizados
            self.atualizar_lista_jogos()
            
            tempo_agora = datetime.now().strftime('%H:%M:%S')
            self.status_jogos.config(
                text=f"🔄 {len(self.jogos_do_dia)} jogos atualizados - {tempo_agora}", 
                style='Success.TLabel'
            )
            
        except Exception as e:
            self.status_jogos.config(text=f"❌ Erro ao atualizar: {str(e)}", style='Warning.TLabel')
            print(f"Erro detalhado: {e}")
    
    def processar_jogo_odds_paralelo(self, jogo):
        """Processa odds de um jogo para atualização paralela"""
        try:
            odds_detalhadas = self.buscar_odds_detalhadas(jogo['id'])
            if odds_detalhadas:
                jogo_completo = {**jogo, **odds_detalhadas}
                return jogo_completo
            else:
                jogo['odds'] = None
                return jogo
        except Exception as e:
            print(f"Erro ao buscar odds para jogo {jogo.get('id', 'desconhecido')}: {e}")
            jogo['odds'] = None
            return jogo
    
    def processar_jogo_completo_paralelo(self, jogo):
        """Processa jogo completo (odds + apostas hot) para busca paralela"""
        try:
            apostas_jogo = []
            
            # Buscar odds detalhadas
            odds_detalhadas = self.buscar_odds_detalhadas(jogo['id'])
            if odds_detalhadas:
                jogo_completo = {**jogo, **odds_detalhadas}
                
                # Analisar apostas hot para este jogo
                apostas_jogo = self.processar_jogo_para_hot(jogo)
                
                return jogo_completo, apostas_jogo
            else:
                jogo['odds'] = None
                return jogo, apostas_jogo
                
        except Exception as e:
            print(f"Erro ao processar jogo completo {jogo.get('id', 'desconhecido')}: {e}")
            jogo['odds'] = None
            return jogo, []
    
    # Métodos auxiliares
    def formatar_horario(self, start_time):
        """Formata horário de UTC para local"""
        if not start_time:
            return ""
        
        try:
            # Se já estiver no formato HH:MM, retorna direto
            if isinstance(start_time, str) and len(start_time) == 5 and ':' in start_time:
                return start_time
            
            # Converter de ISO para datetime
            if isinstance(start_time, str):
                if 'T' in start_time:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    dt_local = dt - timedelta(hours=3)  # GMT-3
                    return dt_local.strftime('%H:%M')
                else:
                    return start_time  # Já está em formato simples
            
            return ""
        except Exception as e:
            print(f"Erro ao formatar horário {start_time}: {e}")
            return ""
    
    def calcular_prob_over_under(self, gols_esperados, linha, tipo):
        """Calcula probabilidade de over/under usando distribuição de Poisson"""
        from math import exp, factorial
        
        if tipo == 'over':
            prob_under = 0
            for k in range(int(linha) + 1):
                prob_under += (gols_esperados ** k * exp(-gols_esperados)) / factorial(k)
            return (1 - prob_under) * 100
        else:
            prob_under = 0
            for k in range(int(linha) + 1):
                prob_under += (gols_esperados ** k * exp(-gols_esperados)) / factorial(k)
            return prob_under * 100
    
    def adicionar_aposta_multipla(self, aposta):
        """Adiciona aposta à múltipla"""
        self.apostas_multipla.append(aposta)
        self.atualizar_multipla()
        messagebox.showinfo("Sucesso", f"Aposta adicionada à múltipla: {aposta['aposta']}")
    
    def deletar_aposta_hot(self, aposta, card_frame):
        """Remove aposta da lista de apostas hot e atualiza a interface preservando filtros"""
        try:
            # Confirmar com o usuário
            confirmacao = messagebox.askyesno(
                "Confirmar Exclusão", 
                f"Deseja realmente deletar esta aposta?\n\n"
                f"Jogo: {aposta['jogo']}\n"
                f"Aposta: {aposta['aposta']}\n\n"
                f"Esta ação irá remover a aposta da lista de Apostas Hot."
            )
            
            if not confirmacao:
                return
            
            # Remover da lista de apostas hot
            if hasattr(self, 'apostas_hot') and aposta in self.apostas_hot:
                self.apostas_hot.remove(aposta)
                
                # Destruir o card visualmente
                card_frame.destroy()
                
                # Reaplicar filtros para atualizar a interface preservando a ordenação e filtros atuais
                self.aplicar_filtros_hot()
                
                messagebox.showinfo("Sucesso", f"Aposta deletada com sucesso!\n\n{aposta['aposta']}")
            else:
                messagebox.showwarning("Aviso", "Aposta não encontrada na lista")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao deletar aposta: {str(e)}")
    
    def ver_analise_completa(self, aposta):
        """Mostra análise completa de uma aposta com probabilidades dos resultados"""
        try:
            # Buscar o match_id da aposta
            match_id = aposta.get('match_id')
            if not match_id:
                messagebox.showerror("Erro", "ID da partida não encontrado")
                return
            
            # Buscar estatísticas detalhadas
            stats = self.api.buscar_estatisticas_detalhadas_time(match_id)
            if not stats:
                messagebox.showerror("Erro", "Não foi possível obter estatísticas da partida")
                return
            
            # Calcular probabilidades
            probabilidades = self.calcular_probabilidades_completas(stats, "Geral")
            
            # Extrair nomes dos times da aposta
            partes_jogo = aposta['jogo'].split(' vs ')
            if len(partes_jogo) == 2:
                casa, visitante = partes_jogo
            else:
                casa = stats['time_casa']['nome']
                visitante = stats['time_visitante']['nome']
            
            # Converter e formatar forma recente
            forma_casa_raw = stats.get('time_casa', {}).get('geral', {}).get('forma', [])
            forma_visitante_raw = stats.get('time_visitante', {}).get('geral', {}).get('forma', [])
            
            forma_casa_vde = self.converter_forma_recente_para_vde(forma_casa_raw)
            forma_visitante_vde = self.converter_forma_recente_para_vde(forma_visitante_raw)
            
            forma_casa_formatada = self.formatar_forma_visual(forma_casa_vde, casa)
            forma_visitante_formatada = self.formatar_forma_visual(forma_visitante_vde, visitante)
            
            # Formatar resultado completo
            resultado = f"""
🎲 ANÁLISE COMPLETA - {aposta['periodo']}
═══════════════════════════════════════

🏠 {casa} vs ✈️ {visitante}
🏆 {aposta['liga']} | ⏰ {aposta['horario']}

📊 RESULTADOS:
🏠 Vitória {casa}: {probabilidades['vitoria_casa']:.1f}%
🤝 Empate: {probabilidades['empate']:.1f}%
✈️ Vitória {visitante}: {probabilidades['vitoria_visitante']:.1f}%

⚽ GOLS ESPERADOS:
🏠 {casa}: {probabilidades['gols_esperados_casa']:.2f}
✈️ {visitante}: {probabilidades['gols_esperados_visitante']:.2f}
🎯 Total: {probabilidades['gols_esperados_total']:.2f}

� FORMA RECENTE:
{forma_casa_formatada}
{forma_visitante_formatada}

Legenda: V = Vitória (Verde) | E = Empate (Cinza) | D = Derrota (Vermelho)

�📈 MERCADOS DE GOLS:
Mais de 1.5: {probabilidades['over_15']:.1f}%
Menos de 1.5: {probabilidades['under_15']:.1f}%
Mais de 2.5: {probabilidades['over_25']:.1f}%
Menos de 2.5: {probabilidades['under_25']:.1f}%
Mais de 3.5: {probabilidades['over_35']:.1f}%
Menos de 3.5: {probabilidades['under_35']:.1f}%

💰 APOSTA RECOMENDADA:
{aposta['aposta']} (Odd: {aposta['odd']:.2f})
📊 Prob. Bet Booster: {aposta['nossa_prob']:.1f}%
📈 Prob. Bet365: {aposta['prob_implicita']:.1f}%
💎 Value: {((aposta['value'] - 1) * 100):.1f}%
🎯 Tipo: {aposta['tipo'].replace('_', ' ')}
"""
            
            # Criar janela customizada para mostrar as informações com cores
            self.mostrar_analise_completa_personalizada(aposta, casa, visitante, probabilidades, 
                                                       forma_casa_vde, forma_visitante_vde, resultado)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar análise completa: {str(e)}")
    
    def mostrar_analise_completa_personalizada(self, aposta, casa, visitante, probabilidades, 
                                             forma_casa_vde, forma_visitante_vde, resultado_texto):
        """
        Mostra análise completa em janela personalizada com cores para as últimas partidas
        """
        try:
            # Criar janela
            janela = tk.Toplevel(self.root)
            janela.title(f"Análise Completa - {aposta['aposta']}")
            janela.geometry("600x700")
            janela.configure(bg='white')
            
            # Frame principal com scroll
            main_frame = tk.Frame(janela, bg='white')
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Título
            titulo = tk.Label(main_frame, text=f"🎲 ANÁLISE COMPLETA - {aposta['periodo']}", 
                             font=('Arial', 16, 'bold'), bg='white', fg='#1e40af')
            titulo.pack(pady=(0, 20))
            
            # Informações do jogo
            info_jogo = tk.Label(main_frame, 
                               text=f"🏠 {casa} vs ✈️ {visitante}\n🏆 {aposta['liga']} | ⏰ {aposta['horario']}", 
                               font=('Arial', 12), bg='white', fg='#374151')
            info_jogo.pack(pady=(0, 20))
            
            # Probabilidades
            prob_frame = tk.LabelFrame(main_frame, text="📊 PROBABILIDADES", 
                                     font=('Arial', 12, 'bold'), bg='white')
            prob_frame.pack(fill='x', pady=(0, 15))
            
            tk.Label(prob_frame, 
                    text=f"🏠 Vitória {casa}: {probabilidades['vitoria_casa']:.1f}%\n" +
                         f"🤝 Empate: {probabilidades['empate']:.1f}%\n" +
                         f"✈️ Vitória {visitante}: {probabilidades['vitoria_visitante']:.1f}%", 
                    font=('Arial', 10), bg='white', justify='left').pack(anchor='w', padx=10, pady=5)
            
            # Gols Esperados
            gols_frame = tk.LabelFrame(main_frame, text="⚽ GOLS ESPERADOS", 
                                     font=('Arial', 12, 'bold'), bg='white')
            gols_frame.pack(fill='x', pady=(0, 15))
            
            tk.Label(gols_frame, 
                    text=f"🏠 {casa}: {probabilidades['gols_esperados_casa']:.2f}\n" +
                         f"✈️ {visitante}: {probabilidades['gols_esperados_visitante']:.2f}\n" +
                         f"🎯 Total: {probabilidades['gols_esperados_total']:.2f}", 
                    font=('Arial', 10), bg='white', justify='left').pack(anchor='w', padx=10, pady=5)
            
            # Forma Recente com cores
            forma_frame = tk.LabelFrame(main_frame, text="📊 FORMA RECENTE (Últimos 5 Jogos)", 
                                      font=('Arial', 12, 'bold'), bg='white')
            forma_frame.pack(fill='x', pady=(0, 15))
            
            # Time casa
            casa_frame = tk.Frame(forma_frame, bg='white')
            casa_frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(casa_frame, text=f"🏠 {casa}: ", font=('Arial', 10, 'bold'), 
                    bg='white', fg='#374151').pack(side='left')
            
            # Adicionar quadrados coloridos para o time da casa
            self.adicionar_quadrados_forma(casa_frame, forma_casa_vde)
            
            # Time visitante  
            visit_frame = tk.Frame(forma_frame, bg='white')
            visit_frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(visit_frame, text=f"✈️ {visitante}: ", font=('Arial', 10, 'bold'), 
                    bg='white', fg='#374151').pack(side='left')
            
            # Adicionar quadrados coloridos para o time visitante
            self.adicionar_quadrados_forma(visit_frame, forma_visitante_vde)
            
            # Legenda
            legenda_frame = tk.Frame(forma_frame, bg='white')
            legenda_frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(legenda_frame, text="Legenda: ", font=('Arial', 9), 
                    bg='white', fg='#6b7280').pack(side='left')
            
            # Quadrado V (Verde)
            v_frame = tk.Frame(legenda_frame, bg='#10b981', width=15, height=15)
            v_frame.pack(side='left', padx=2)
            v_frame.pack_propagate(False)
            tk.Label(v_frame, text="V", font=('Arial', 8, 'bold'), 
                    bg='#10b981', fg='black').pack()
            
            tk.Label(legenda_frame, text=" = Vitória  ", font=('Arial', 9), 
                    bg='white', fg='#6b7280').pack(side='left')
            
            # Quadrado E (Cinza)
            e_frame = tk.Frame(legenda_frame, bg='#6b7280', width=15, height=15)
            e_frame.pack(side='left', padx=2)
            e_frame.pack_propagate(False)
            tk.Label(e_frame, text="E", font=('Arial', 8, 'bold'), 
                    bg='#6b7280', fg='black').pack()
            
            tk.Label(legenda_frame, text=" = Empate  ", font=('Arial', 9), 
                    bg='white', fg='#6b7280').pack(side='left')
            
            # Quadrado D (Vermelho)
            d_frame = tk.Frame(legenda_frame, bg='#ef4444', width=15, height=15)
            d_frame.pack(side='left', padx=2)
            d_frame.pack_propagate(False)
            tk.Label(d_frame, text="D", font=('Arial', 8, 'bold'), 
                    bg='#ef4444', fg='black').pack()
            
            tk.Label(legenda_frame, text=" = Derrota", font=('Arial', 9), 
                    bg='white', fg='#6b7280').pack(side='left')
            
            # Mercados de Gols
            mercados_frame = tk.LabelFrame(main_frame, text="📈 MERCADOS DE GOLS", 
                                         font=('Arial', 12, 'bold'), bg='white')
            mercados_frame.pack(fill='x', pady=(0, 15))
            
            tk.Label(mercados_frame, 
                    text=f"Mais de 1.5: {probabilidades['over_15']:.1f}%  |  Menos de 1.5: {probabilidades['under_15']:.1f}%\n" +
                         f"Mais de 2.5: {probabilidades['over_25']:.1f}%  |  Menos de 2.5: {probabilidades['under_25']:.1f}%\n" +
                         f"Mais de 3.5: {probabilidades['over_35']:.1f}%  |  Menos de 3.5: {probabilidades['under_35']:.1f}%", 
                    font=('Arial', 10), bg='white', justify='center').pack(padx=10, pady=5)
            
            # Aposta Recomendada (apenas para apostas hot, não para jogos do dia)
            if aposta.get('tipo') != 'analise_jogos_do_dia':
                aposta_frame = tk.LabelFrame(main_frame, text="💰 APOSTA RECOMENDADA", 
                                           font=('Arial', 12, 'bold'), bg='white')
                aposta_frame.pack(fill='x', pady=(0, 15))
                
                tk.Label(aposta_frame, 
                        text=f"{aposta['aposta']} (Odd: {aposta['odd']:.2f})\n" +
                             f"📊 Prob. Bet Booster: {aposta['nossa_prob']:.1f}%\n" +
                             f"📈 Prob. Bet365: {aposta['prob_implicita']:.1f}%\n" +
                             f"💎 Value: {((aposta['value'] - 1) * 100):.1f}%\n" +
                             f"🎯 Tipo: {aposta['tipo'].replace('_', ' ')}", 
                        font=('Arial', 10), bg='white', justify='left').pack(anchor='w', padx=10, pady=5)
            else:
                # Para jogos do dia, mostrar informações do modo de análise
                info_frame = tk.LabelFrame(main_frame, text="🎯 INFORMAÇÕES DA ANÁLISE", 
                                         font=('Arial', 12, 'bold'), bg='white')
                info_frame.pack(fill='x', pady=(0, 15))
                
                tk.Label(info_frame, 
                        text=f"📊 Modo de Análise: {self.modo_analise.get()}\n" +
                             f"🎲 Análise completa calculada pelo Bet Booster\n" +
                             f"📈 Use estas informações para suas apostas", 
                        font=('Arial', 10), bg='white', justify='left').pack(anchor='w', padx=10, pady=5)
            
            # Botão fechar
            tk.Button(main_frame, text="Fechar", command=janela.destroy, 
                     font=('Arial', 12), bg='#ef4444', fg='white', 
                     padx=20, pady=5).pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar janela personalizada: {str(e)}")
    
    def adicionar_quadrados_forma(self, parent_frame, forma_vde):
        """
        Adiciona quadrados coloridos para representar a forma recente
        """
        # Pegar últimos 5 resultados
        ultimos_5 = forma_vde[-5:] if len(forma_vde) >= 5 else forma_vde
        
        # Completar com espaços se não tiver 5 resultados
        while len(ultimos_5) < 5:
            ultimos_5.insert(0, '-')
        
        # Cores para cada resultado
        cores = {
            'V': '#10b981',  # Verde
            'E': '#6b7280',  # Cinza
            'D': '#ef4444',  # Vermelho
            '-': '#e5e7eb'   # Cinza claro para dados faltantes
        }
        
        for resultado in ultimos_5:
            cor = cores.get(resultado, '#e5e7eb')
            
            # Criar frame para o quadrado
            quad_frame = tk.Frame(parent_frame, bg=cor, width=20, height=20)
            quad_frame.pack(side='left', padx=2)
            quad_frame.pack_propagate(False)
            
            # Adicionar texto
            texto = resultado if resultado != '-' else ''
            tk.Label(quad_frame, text=texto, font=('Arial', 8, 'bold'), 
                    bg=cor, fg='black').pack()
    
    def atualizar_multipla(self):
        """Atualiza a visualização da múltipla"""
        # Limpar árvore
        for item in self.tree_multipla.get_children():
            self.tree_multipla.delete(item)
        
        # Adicionar apostas
        odd_total = 1.0
        for aposta in self.apostas_multipla:
            self.tree_multipla.insert('', 'end', values=(
                aposta['jogo'],
                aposta['aposta'],
                f"{aposta['odd']:.2f}",
                f"{aposta.get('prob_calculada', 0):.1f}%",
                f"{aposta['prob_implicita']:.1f}%",
                aposta['tipo']
            ))
            odd_total *= aposta['odd']
        
        # Atualizar labels
        prob_total_implicita = (1 / odd_total * (1 - 0.05)) * 100 if odd_total > 0 else 0
        
        # Calcular probabilidade Bet Booster combinada
        prob_nossa_combinada = 1.0
        tem_prob_calculada = False
        for aposta in self.apostas_multipla:
            nossa_prob = aposta.get('prob_calculada', 0)
            if nossa_prob > 0:
                prob_nossa_combinada *= (nossa_prob / 100)
                tem_prob_calculada = True
        
        if tem_prob_calculada:
            prob_nossa_combinada *= 100
        else:
            prob_nossa_combinada = prob_total_implicita  # Fallback para prob Bet365
        
        self.label_odd_total.config(text=f"Odd Total: {odd_total:.2f}")
        self.label_prob_nossa.config(text=f"📊 Prob. Bet Booster: {prob_nossa_combinada:.1f}%")
        self.label_prob_total.config(text=f"🎯 Prob. Bet365: {prob_total_implicita:.1f}%")
        
        # Atualizar retorno potencial também
        self.calcular_retorno_tempo_real()
    
    def limpar_multipla(self):
        """Limpa a múltipla atual"""
        self.apostas_multipla.clear()
        self.atualizar_multipla()
        self.calcular_retorno_tempo_real()
        messagebox.showinfo("Sucesso", "Múltipla limpa")
    
    def salvar_multipla(self):
        """Salva a múltipla atual"""
        if not self.apostas_multipla:
            messagebox.showwarning("Aviso", "Múltipla vazia")
            return
        messagebox.showinfo("Sucesso", "Múltipla salva")
    
    def calcular_retorno_multipla(self):
        """Calcula retorno da múltipla"""
        if not self.apostas_multipla:
            messagebox.showwarning("Aviso", "Múltipla vazia")
            return
        
        # Abrir janela de cálculo
        window = tk.Toplevel(self.root)
        window.title("📊 Cálculo de Retorno - Múltipla")
        window.geometry("650x700")
        window.transient(self.root)
        window.grab_set()
        
        # Título
        ttk.Label(window, text="📊 CÁLCULO DE RETORNO - MÚLTIPLA", 
                 style='Title.TLabel').pack(pady=10)
        
        # Resumo da múltipla
        resumo_frame = ttk.LabelFrame(window, text="Resumo da Múltipla", padding=15)
        resumo_frame.pack(fill='x', padx=20, pady=10)
        
        # Calcular odd total e probabilidade nossa
        odd_total = 1.0
        prob_nossa_total = 1.0
        for aposta in self.apostas_multipla:
            odd_total *= aposta['odd']
            # Calcular probabilidade Bet Booster multiplicando as individuais
            nossa_prob_valor = aposta.get('nossa_prob') or aposta.get('prob_calculada')
            if nossa_prob_valor:
                # Converter percentual para decimal se necessário
                nossa_prob = float(str(nossa_prob_valor).replace('%', ''))
                if nossa_prob > 1:  # Se está em percentual
                    nossa_prob = nossa_prob / 100
                prob_nossa_total *= nossa_prob
        
        prob_total = (1 / odd_total * (1 - 0.05)) * 100 if odd_total > 0 else 0
        prob_nossa_percentual = prob_nossa_total * 100
        
        ttk.Label(resumo_frame, text=f"📋 Apostas: {len(self.apostas_multipla)}", 
                 style='Subtitle.TLabel').pack(anchor='w')
        ttk.Label(resumo_frame, text=f"🎯 Odd Total: {odd_total:.2f}", 
                 style='Subtitle.TLabel').pack(anchor='w')
        ttk.Label(resumo_frame, text=f"📊 Prob. Bet Booster: {prob_nossa_percentual:.1f}%", 
                 style='Success.TLabel').pack(anchor='w')
        ttk.Label(resumo_frame, text=f"📈 Prob. Bet365 (Odds): {prob_total:.1f}%", 
                 style='Subtitle.TLabel').pack(anchor='w')
        
        # Input de valor
        valor_frame = ttk.LabelFrame(window, text="Valor da Aposta", padding=15)
        valor_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(valor_frame, text="Valor a apostar (R$):").pack(anchor='w')
        valor_entry = ttk.Entry(valor_frame, width=15, font=('Arial', 12))
        valor_entry.pack(anchor='w', pady=5)
        valor_entry.insert(0, "10.00")
        
        # Resultado
        resultado_frame = ttk.LabelFrame(window, text="Cálculos", padding=15)
        resultado_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        resultado_text = scrolledtext.ScrolledText(resultado_frame, height=15, width=50,
                                                   bg=self.cores['bg_input'],
                                                   fg=self.cores['fg_input'],
                                                   insertbackground=self.cores['fg_input'])
        resultado_text.pack(fill='both', expand=True)
        
        def calcular():
            try:
                valor = float(valor_entry.get())
                
                retorno_bruto = valor * odd_total
                lucro = retorno_bruto - valor
                
                relatorio = f"""
🎯 RELATÓRIO DE MÚLTIPLA
═══════════════════════════════════════

📋 APOSTAS INCLUÍDAS:
"""
                
                for i, aposta in enumerate(self.apostas_multipla, 1):
                    # Buscar probabilidade Bet Booster com fallback
                    nossa_prob_valor = aposta.get('nossa_prob') or aposta.get('prob_calculada') or 'N/A'
                    if nossa_prob_valor != 'N/A':
                        nossa_prob_str = f"{nossa_prob_valor:.1f}%"
                    else:
                        nossa_prob_str = "N/A"
                    
                    relatorio += f"""
{i}. {aposta['jogo']}
   💰 Aposta: {aposta['aposta']}
   🎯 Odd: {aposta['odd']:.2f}
   📊 Prob. Bet Booster: {nossa_prob_str}
   📈 Prob. Bet365: {aposta['prob_implicita']:.1f}%
"""
                
                relatorio += f"""
═══════════════════════════════════════
📊 CÁLCULOS FINANCEIROS:
═══════════════════════════════════════

💵 Valor Apostado: R$ {valor:.2f}
🎯 Odd Total: {odd_total:.2f}
📊 Prob. Bet Booster: {prob_nossa_percentual:.1f}%
📈 Prob. Bet365 (Odds): {prob_total:.1f}%

💰 Retorno Bruto: R$ {retorno_bruto:.2f}
💎 Lucro Líquido: R$ {lucro:.2f}
📈 Retorno: {((retorno_bruto / valor - 1) * 100):+.1f}%

═══════════════════════════════════════
⚖️ ANÁLISE DE RISCO:
═══════════════════════════════════════
"""
                
                # Análise de risco
                if prob_total >= 30:
                    relatorio += "🟢 RISCO BAIXO - Probabilidade razoável\n"
                elif prob_total >= 15:
                    relatorio += "🟡 RISCO MÉDIO - Probabilidade moderada\n"
                elif prob_total >= 5:
                    relatorio += "🟠 RISCO ALTO - Probabilidade baixa\n"
                else:
                    relatorio += "🔴 RISCO MUITO ALTO - Probabilidade muito baixa\n"
                
                # Recomendação
                if prob_total >= 20 and odd_total >= 2.0:
                    relatorio += "\n✅ RECOMENDAÇÃO: Múltipla interessante"
                elif prob_total >= 10:
                    relatorio += "\n⚠️ RECOMENDAÇÃO: Considerar valor menor"
                else:
                    relatorio += "\n❌ RECOMENDAÇÃO: Muito arriscada"
                
                relatorio += f"\n\n⏰ Calculado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                
                resultado_text.delete(1.0, tk.END)
                resultado_text.insert(1.0, relatorio)
                
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido")
        
        # Botões
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="🧮 Calcular", command=calcular).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="💾 Salvar Relatório", 
                  command=lambda: self.salvar_relatorio_multipla(resultado_text.get(1.0, tk.END))).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Fechar", command=window.destroy).pack(side='right', padx=5)
    
    def salvar_relatorio_multipla(self, relatorio):
        """Salva relatório da múltipla"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
                title="Salvar Relatório da Múltipla"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(relatorio)
                messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar relatório: {str(e)}")
    
    # Métodos auxiliares adicionais
    
    def carregar_dados(self):
        """Carrega dados salvos"""
        try:
            database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'times_database.json')
            if os.path.exists(database_path):
                with open(database_path, 'r', encoding='utf-8') as f:
                    self.times_database = json.load(f)
                print(f"✅ Database carregado: {len(self.times_database)} times")
                
                # Atualizar interfaces após carregar
                self.root.after(100, self.pos_carregamento_inicial)
            else:
                print("⚠️ Database não encontrado, criando novo")
                self.times_database = {}
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            self.times_database = {}
    
    # ==========================================
    # SISTEMA DE BANCA SIMULADA
    # ==========================================
    
    def carregar_dados_banca(self):
        """Carrega dados da banca simulada"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Carregar dados da banca
            banca_file = os.path.join(data_dir, 'banca_simulada.json')
            if os.path.exists(banca_file):
                with open(banca_file, 'r', encoding='utf-8') as f:
                    self.banca_data = json.load(f)
            else:
                self.banca_data = {
                    'saldo_atual': 0.0,
                    'total_depositado': 0.0,
                    'total_ganhos': 0.0,
                    'total_perdas': 0.0,
                    'lucro_total': 0.0,
                    'created_at': datetime.now().isoformat()
                }
            
            # Carregar apostas ativas
            apostas_ativas_file = os.path.join(data_dir, 'apostas_ativas.json')
            if os.path.exists(apostas_ativas_file):
                with open(apostas_ativas_file, 'r', encoding='utf-8') as f:
                    self.apostas_ativas = json.load(f)
            else:
                self.apostas_ativas = []
            
            # Carregar histórico
            historico_file = os.path.join(data_dir, 'historico_apostas.json')
            if os.path.exists(historico_file):
                with open(historico_file, 'r', encoding='utf-8') as f:
                    self.historico_apostas = json.load(f)
            else:
                self.historico_apostas = []
                
            print(f"✅ Banca carregada - Saldo: R$ {self.banca_data['saldo_atual']:.2f}")
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados da banca: {e}")
            self.banca_data = {
                'saldo_atual': 0.0,
                'total_depositado': 0.0,
                'total_ganhos': 0.0,
                'total_perdas': 0.0,
                'lucro_total': 0.0,
                'created_at': datetime.now().isoformat()
            }
            self.apostas_ativas = []
            self.historico_apostas = []
    
    def salvar_dados_banca(self):
        """Salva dados da banca simulada"""
        try:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            
            # Salvar dados da banca
            banca_file = os.path.join(data_dir, 'banca_simulada.json')
            with open(banca_file, 'w', encoding='utf-8') as f:
                json.dump(self.banca_data, f, indent=2, ensure_ascii=False)
            
            # Salvar apostas ativas
            apostas_ativas_file = os.path.join(data_dir, 'apostas_ativas.json')
            with open(apostas_ativas_file, 'w', encoding='utf-8') as f:
                json.dump(self.apostas_ativas, f, indent=2, ensure_ascii=False)
            
            # Salvar histórico
            historico_file = os.path.join(data_dir, 'historico_apostas.json')
            with open(historico_file, 'w', encoding='utf-8') as f:
                json.dump(self.historico_apostas, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Erro ao salvar dados da banca: {e}")
    
    def adicionar_saldo(self, valor):
        """Adiciona saldo à banca simulada"""
        try:
            valor = float(valor)
            if valor <= 0:
                return False, "Valor deve ser maior que zero"
            
            self.banca_data['saldo_atual'] += valor
            self.banca_data['total_depositado'] += valor
            self.salvar_dados_banca()
            
            return True, f"R$ {valor:.2f} adicionado à banca"
            
        except Exception as e:
            return False, f"Erro ao adicionar saldo: {str(e)}"
    
    def criar_aposta_multipla(self, valor_aposta):
        """Cria uma nova aposta múltipla"""
        try:
            valor_aposta = float(valor_aposta)
            
            if valor_aposta <= 0:
                return False, "Valor da aposta deve ser maior que zero"
            
            if valor_aposta > self.banca_data['saldo_atual']:
                return False, "Saldo insuficiente"
            
            if not self.apostas_multipla:
                return False, "Adicione pelo menos uma aposta à múltipla"
            
            # Calcular odd total
            odd_total = 1.0
            for aposta in self.apostas_multipla:
                odd_total *= aposta['odd']
            
            # Criar ID único da aposta
            aposta_id = f"APT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.apostas_ativas) + 1}"
            
            # Criar estrutura da aposta
            nova_aposta = {
                'id': aposta_id,
                'valor_apostado': valor_aposta,
                'odd_total': odd_total,
                'retorno_potencial': valor_aposta * odd_total,
                'jogos': [],
                'status': 'ativa',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Copiar jogos da múltipla
            for aposta in self.apostas_multipla:
                jogo_info = {
                    'jogo': aposta['jogo'],
                    'aposta': aposta['aposta'],
                    'odd': aposta['odd'],
                    'resultado': 'pendente',  # pendente, green, red
                    'data_resultado': None
                }
                nova_aposta['jogos'].append(jogo_info)
            
            # Debitar da banca
            self.banca_data['saldo_atual'] -= valor_aposta
            
            # Adicionar às apostas ativas
            self.apostas_ativas.append(nova_aposta)
            
            # Limpar múltipla atual
            self.apostas_multipla.clear()
            
            # Salvar dados
            self.salvar_dados_banca()
            
            return True, f"Aposta criada! ID: {aposta_id}"
            
        except Exception as e:
            return False, f"Erro ao criar aposta: {str(e)}"
    
    def marcar_resultado_jogo(self, aposta_id, jogo_index, resultado):
        """Marca resultado de um jogo (green/red)"""
        try:
            # Encontrar a aposta
            aposta = None
            for apt in self.apostas_ativas:
                if apt['id'] == aposta_id:
                    aposta = apt
                    break
            
            if not aposta:
                return False, "Aposta não encontrada"
            
            if aposta['status'] != 'ativa':
                return False, "Aposta não está ativa"
            
            if jogo_index < 0 or jogo_index >= len(aposta['jogos']):
                return False, "Jogo não encontrado"
            
            # Marcar resultado
            aposta['jogos'][jogo_index]['resultado'] = resultado
            aposta['jogos'][jogo_index]['data_resultado'] = datetime.now().isoformat()
            aposta['updated_at'] = datetime.now().isoformat()
            
            # Verificar se todos os jogos foram marcados
            jogos_pendentes = [j for j in aposta['jogos'] if j['resultado'] == 'pendente']
            jogos_green = [j for j in aposta['jogos'] if j['resultado'] == 'green']
            jogos_red = [j for j in aposta['jogos'] if j['resultado'] == 'red']
            
            # Se algum jogo deu red, a aposta toda é red
            if jogos_red:
                aposta['status'] = 'perdida'
                self.banca_data['total_perdas'] += aposta['valor_apostado']
                self.banca_data['lucro_total'] -= aposta['valor_apostado']
                
                # Mover para histórico
                self.mover_aposta_para_historico(aposta)
                return True, "Aposta perdida (RED)"
            
            # Se todos os jogos deram green, a aposta é vencedora
            elif not jogos_pendentes and len(jogos_green) == len(aposta['jogos']):
                aposta['status'] = 'ganha'
                retorno = aposta['retorno_potencial']
                self.banca_data['saldo_atual'] += retorno
                self.banca_data['total_ganhos'] += retorno
                self.banca_data['lucro_total'] += (retorno - aposta['valor_apostado'])
                
                # Mover para histórico
                self.mover_aposta_para_historico(aposta)
                return True, f"Aposta ganha! Retorno: R$ {retorno:.2f}"
            
            # Ainda tem jogos pendentes
            else:
                self.salvar_dados_banca()
                return True, f"Resultado marcado. Restam {len(jogos_pendentes)} jogos"
            
        except Exception as e:
            return False, f"Erro ao marcar resultado: {str(e)}"
    
    def fazer_cashout(self, aposta_id):
        """Realiza cashout da aposta"""
        try:
            # Encontrar a aposta
            aposta = None
            aposta_index = None
            for i, apt in enumerate(self.apostas_ativas):
                if apt['id'] == aposta_id:
                    aposta = apt
                    aposta_index = i
                    break
            
            if not aposta:
                return False, "Aposta não encontrada"
            
            if aposta['status'] != 'ativa':
                return False, "Aposta não está ativa"
            
            # Verificar quantos jogos já foram marcados como green
            jogos_green = [j for j in aposta['jogos'] if j['resultado'] == 'green']
            jogos_red = [j for j in aposta['jogos'] if j['resultado'] == 'red']
            jogos_pendentes = [j for j in aposta['jogos'] if j['resultado'] == 'pendente']
            
            # Se tem algum red, não pode fazer cashout
            if jogos_red:
                return False, "Não é possível fazer cashout: há jogos perdidos"
            
            # Se não tem nenhum green, devolve o valor integral
            if not jogos_green:
                valor_cashout = aposta['valor_apostado']
                self.banca_data['saldo_atual'] += valor_cashout
                
                aposta['status'] = 'cashout'
                aposta['valor_cashout'] = valor_cashout
                
                # Mover para histórico
                self.mover_aposta_para_historico(aposta)
                
                return True, f"Cashout realizado: R$ {valor_cashout:.2f} (valor integral)"
            
            # Calcular cashout proporcional aos jogos que deram green
            total_jogos = len(aposta['jogos'])
            jogos_green_count = len(jogos_green)
            jogos_pendentes_count = len(jogos_pendentes)
            
            # Odd dos jogos que deram green
            odd_green = 1.0
            for jogo in jogos_green:
                odd_green *= jogo['odd']
            
            # Valor proporcional baseado nos jogos que já deram green
            # Fórmula: valor_apostado * odd_dos_greens * fator_de_desconto
            fator_desconto = 0.85  # 15% de desconto para cashout antecipado
            valor_cashout = aposta['valor_apostado'] * odd_green * fator_desconto
            
            self.banca_data['saldo_atual'] += valor_cashout
            self.banca_data['total_ganhos'] += valor_cashout
            self.banca_data['lucro_total'] += (valor_cashout - aposta['valor_apostado'])
            
            aposta['status'] = 'cashout'
            aposta['valor_cashout'] = valor_cashout
            
            # Mover para histórico
            self.mover_aposta_para_historico(aposta)
            
            return True, f"Cashout realizado: R$ {valor_cashout:.2f} ({jogos_green_count}/{total_jogos} jogos green)"
            
        except Exception as e:
            return False, f"Erro no cashout: {str(e)}"
    
    def mover_aposta_para_historico(self, aposta):
        """Move aposta das ativas para o histórico"""
        try:
            # Adicionar ao histórico
            self.historico_apostas.append(aposta.copy())
            
            # Remover das ativas
            self.apostas_ativas = [apt for apt in self.apostas_ativas if apt['id'] != aposta['id']]
            
            # Salvar dados
            self.salvar_dados_banca()
            
        except Exception as e:
            print(f"❌ Erro ao mover aposta para histórico: {e}")
    
    # ==========================================
    # FUNÇÕES DA INTERFACE BANCA SIMULADA
    # ==========================================
    
    def atualizar_info_banca(self):
        """Atualiza as informações da banca na interface"""
        try:
            if hasattr(self, 'label_saldo'):
                self.label_saldo.config(text=f"Saldo Atual: R$ {self.banca_data['saldo_atual']:.2f}")
                self.label_total_depositado.config(text=f"Total Depositado: R$ {self.banca_data['total_depositado']:.2f}")
                self.label_total_ganhos.config(text=f"Total Ganhos: R$ {self.banca_data['total_ganhos']:.2f}")
                self.label_total_perdas.config(text=f"Total Perdas: R$ {self.banca_data['total_perdas']:.2f}")
                
                # Cor do lucro (verde para positivo, vermelho para negativo)
                lucro_cor = 'green' if self.banca_data['lucro_total'] >= 0 else 'red'
                self.label_lucro_total.config(text=f"Lucro Total: R$ {self.banca_data['lucro_total']:.2f}", 
                                            foreground=lucro_cor)
        except Exception as e:
            print(f"❌ Erro ao atualizar info da banca: {e}")
    
    def depositar_saldo(self):
        """Deposita saldo na banca"""
        try:
            valor = self.entry_saldo.get().strip()
            if not valor:
                messagebox.showwarning("Aviso", "Digite um valor para depositar")
                return
            
            sucesso, mensagem = self.adicionar_saldo(valor)
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.entry_saldo.delete(0, tk.END)
                self.atualizar_info_banca()
            else:
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao depositar: {str(e)}")
    
    def calcular_retorno_tempo_real(self, event=None):
        """Calcula retorno potencial em tempo real"""
        try:
            if not hasattr(self, 'label_retorno_potencial'):
                return
                
            valor = self.entry_valor_aposta.get().strip()
            if not valor:
                self.label_retorno_potencial.config(text="Retorno Potencial: R$ 0.00")
                return
            
            valor_float = float(valor)
            
            # Calcular odd total
            odd_total = 1.0
            for aposta in self.apostas_multipla:
                odd_total *= aposta['odd']
            
            retorno = valor_float * odd_total
            self.label_retorno_potencial.config(text=f"Retorno Potencial: R$ {retorno:.2f}")
            
        except ValueError:
            self.label_retorno_potencial.config(text="Retorno Potencial: R$ 0.00")
        except Exception as e:
            print(f"❌ Erro ao calcular retorno: {e}")
    
    def realizar_aposta_multipla(self):
        """Realiza uma aposta múltipla"""
        try:
            valor = self.entry_valor_aposta.get().strip()
            if not valor:
                messagebox.showwarning("Aviso", "Digite o valor da aposta")
                return
            
            sucesso, mensagem = self.criar_aposta_multipla(valor)
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.entry_valor_aposta.delete(0, tk.END)
                self.atualizar_multipla()
                self.atualizar_info_banca()
                self.atualizar_apostas_ativas()
                self.calcular_retorno_tempo_real()
            else:
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar aposta: {str(e)}")
    
    def atualizar_apostas_ativas(self):
        """Atualiza lista de apostas ativas"""
        try:
            if not hasattr(self, 'tree_apostas_ativas'):
                return
                
            # Limpar árvore
            for item in self.tree_apostas_ativas.get_children():
                self.tree_apostas_ativas.delete(item)
            
            # Adicionar apostas ativas
            for aposta in self.apostas_ativas:
                jogos_green = len([j for j in aposta['jogos'] if j['resultado'] == 'green'])
                total_jogos = len(aposta['jogos'])
                
                data_created = datetime.fromisoformat(aposta['created_at']).strftime('%d/%m/%Y %H:%M')
                
                self.tree_apostas_ativas.insert('', 'end', values=(
                    aposta['id'],
                    data_created,
                    f"R$ {aposta['valor_apostado']:.2f}",
                    f"{aposta['odd_total']:.2f}",
                    f"R$ {aposta['retorno_potencial']:.2f}",
                    aposta['status'].title(),
                    f"{jogos_green}/{total_jogos}"
                ), tags=(aposta['id'],))
                
        except Exception as e:
            print(f"❌ Erro ao atualizar apostas ativas: {e}")
    
    def ver_detalhes_aposta(self):
        """Mostra detalhes da aposta selecionada"""
        try:
            selected = self.tree_apostas_ativas.selection()
            if not selected:
                messagebox.showwarning("Aviso", "Selecione uma aposta")
                return
            
            # Obter ID da aposta
            aposta_id = self.tree_apostas_ativas.item(selected[0])['tags'][0]
            
            # Encontrar aposta
            aposta = None
            for apt in self.apostas_ativas:
                if apt['id'] == aposta_id:
                    aposta = apt
                    break
            
            if not aposta:
                messagebox.showerror("Erro", "Aposta não encontrada")
                return
            
            # Criar janela de detalhes
            self.mostrar_janela_detalhes_aposta(aposta)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ver detalhes: {str(e)}")
    
    def mostrar_janela_detalhes_aposta(self, aposta):
        """Mostra janela com detalhes da aposta"""
        janela = tk.Toplevel(self.root)
        janela.title(f"Detalhes da Aposta - {aposta['id']}")
        janela.geometry("700x600")
        janela.transient(self.root)
        janela.grab_set()
        
        # Informações gerais
        info_frame = ttk.LabelFrame(janela, text="Informações da Aposta", padding=15)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        data_created = datetime.fromisoformat(aposta['created_at']).strftime('%d/%m/%Y %H:%M:%S')
        
        info_text = f"""
ID: {aposta['id']}
Data de Criação: {data_created}
Valor Apostado: R$ {aposta['valor_apostado']:.2f}
Odd Total: {aposta['odd_total']:.2f}
Retorno Potencial: R$ {aposta['retorno_potencial']:.2f}
Status: {aposta['status'].title()}
        """
        
        ttk.Label(info_frame, text=info_text.strip(), justify='left').pack(anchor='w')
        
        # Lista de jogos
        jogos_frame = ttk.LabelFrame(janela, text="Jogos da Aposta", padding=15)
        jogos_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview para jogos
        columns_jogos = ('Jogo', 'Aposta', 'Odd', 'Resultado', 'Data Resultado')
        tree_jogos = ttk.Treeview(jogos_frame, columns=columns_jogos, show='headings', height=8)
        
        for col in columns_jogos:
            tree_jogos.heading(col, text=col)
            if col == 'Jogo':
                tree_jogos.column(col, width=200)
            elif col == 'Aposta':
                tree_jogos.column(col, width=120)
            else:
                tree_jogos.column(col, width=80)
        
        tree_jogos.pack(fill='both', expand=True)
        
        # Preencher jogos
        for i, jogo in enumerate(aposta['jogos']):
            resultado_text = jogo['resultado'].upper()
            if resultado_text == 'PENDENTE':
                resultado_text = '⏳ PENDENTE'
            elif resultado_text == 'GREEN':
                resultado_text = '🟢 GREEN'
            elif resultado_text == 'RED':
                resultado_text = '🔴 RED'
            
            data_resultado = ''
            if jogo['data_resultado']:
                data_resultado = datetime.fromisoformat(jogo['data_resultado']).strftime('%d/%m %H:%M')
            
            tree_jogos.insert('', 'end', values=(
                jogo['jogo'],
                jogo['aposta'],
                f"{jogo['odd']:.2f}",
                resultado_text,
                data_resultado
            ), tags=(str(i),))
        
        # Botões de ação
        acoes_frame = ttk.Frame(jogos_frame)
        acoes_frame.pack(fill='x', pady=10)
        
        if aposta['status'] == 'ativa':
            ttk.Button(acoes_frame, text="🟢 Marcar GREEN", 
                      command=lambda: self.marcar_jogo_resultado('green', aposta, tree_jogos, janela)).pack(side='left', padx=5)
            ttk.Button(acoes_frame, text="🔴 Marcar RED", 
                      command=lambda: self.marcar_jogo_resultado('red', aposta, tree_jogos, janela)).pack(side='left', padx=5)
        
        ttk.Button(acoes_frame, text="Fechar", command=janela.destroy).pack(side='right', padx=5)
    
    def marcar_jogo_resultado(self, resultado, aposta, tree_jogos, janela):
        """Marca resultado de um jogo específico"""
        try:
            selected = tree_jogos.selection()
            if not selected:
                messagebox.showwarning("Aviso", "Selecione um jogo")
                return
            
            jogo_index = int(tree_jogos.item(selected[0])['tags'][0])
            
            sucesso, mensagem = self.marcar_resultado_jogo(aposta['id'], jogo_index, resultado)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                janela.destroy()
                self.atualizar_apostas_ativas()
                self.atualizar_info_banca()
                self.atualizar_historico()
            else:
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar resultado: {str(e)}")
    
    def fazer_cashout_aposta(self):
        """Faz cashout da aposta selecionada"""
        try:
            selected = self.tree_apostas_ativas.selection()
            if not selected:
                messagebox.showwarning("Aviso", "Selecione uma aposta")
                return
            
            aposta_id = self.tree_apostas_ativas.item(selected[0])['tags'][0]
            
            resposta = messagebox.askyesno("Confirmação", 
                                         "Deseja fazer o cashout desta aposta?\n\n"
                                         "Atenção: Cashout antecipado tem desconto de 15%")
            if not resposta:
                return
            
            sucesso, mensagem = self.fazer_cashout(aposta_id)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.atualizar_apostas_ativas()
                self.atualizar_info_banca()
                self.atualizar_historico()
            else:
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no cashout: {str(e)}")
    
    def atualizar_historico(self):
        """Atualiza lista do histórico"""
        try:
            if not hasattr(self, 'tree_historico'):
                return
                
            # Limpar árvore
            for item in self.tree_historico.get_children():
                self.tree_historico.delete(item)
            
            # Adicionar histórico (mais recentes primeiro)
            for aposta in reversed(self.historico_apostas):
                data_created = datetime.fromisoformat(aposta['created_at']).strftime('%d/%m/%Y')
                
                # Calcular resultado
                if aposta['status'] == 'ganha':
                    resultado = "🟢 GANHA"
                    retorno = aposta['retorno_potencial']
                    lucro_perda = retorno - aposta['valor_apostado']
                elif aposta['status'] == 'perdida':
                    resultado = "🔴 PERDIDA"
                    retorno = 0.0
                    lucro_perda = -aposta['valor_apostado']
                elif aposta['status'] == 'cashout':
                    resultado = "💰 CASHOUT"
                    retorno = aposta.get('valor_cashout', 0)
                    lucro_perda = retorno - aposta['valor_apostado']
                else:
                    resultado = aposta['status'].upper()
                    retorno = 0.0
                    lucro_perda = 0.0
                
                # Cor do lucro/perda
                cor = 'green' if lucro_perda >= 0 else 'red'
                
                self.tree_historico.insert('', 'end', values=(
                    aposta['id'],
                    data_created,
                    f"R$ {aposta['valor_apostado']:.2f}",
                    f"{aposta['odd_total']:.2f}",
                    resultado,
                    f"R$ {retorno:.2f}",
                    f"R$ {lucro_perda:.2f}"
                ), tags=(aposta['id'], cor))
            
            # Configurar cores
            self.tree_historico.tag_configure('green', foreground='green')
            self.tree_historico.tag_configure('red', foreground='red')
                
        except Exception as e:
            print(f"❌ Erro ao atualizar histórico: {e}")
    
    def ver_detalhes_historico(self):
        """Mostra detalhes da aposta do histórico"""
        try:
            selected = self.tree_historico.selection()
            if not selected:
                messagebox.showwarning("Aviso", "Selecione uma aposta do histórico")
                return
            
            aposta_id = self.tree_historico.item(selected[0])['tags'][0]
            
            # Encontrar aposta no histórico
            aposta = None
            for apt in self.historico_apostas:
                if apt['id'] == aposta_id:
                    aposta = apt
                    break
            
            if not aposta:
                messagebox.showerror("Erro", "Aposta não encontrada no histórico")
                return
            
            self.mostrar_janela_detalhes_aposta(aposta)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ver detalhes: {str(e)}")
    
    def pos_carregamento_inicial(self):
        """Executa após carregamento inicial dos dados"""
        try:
            # Atualizar lista de times se a aba já foi criada
            if hasattr(self, 'tree_times'):
                self.atualizar_lista_times()
            
            # Atualizar combos se já foram criados
            if hasattr(self, 'combo_time_casa'):
                self.atualizar_combos_times()
                
        except Exception as e:
            print(f"❌ Erro no pós-carregamento: {e}")
    
    def salvar_dados(self):
        """Salva dados do sistema"""
        try:
            database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'times_database.json')
            os.makedirs(os.path.dirname(database_path), exist_ok=True)
            
            with open(database_path, 'w', encoding='utf-8') as f:
                json.dump(self.times_database, f, ensure_ascii=False, indent=2)
                
            # Salvar também os dados da banca
            self.salvar_dados_banca()
            
            print(f"💾 Database salvo: {len(self.times_database)} times")
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
    
    def verificar_e_atualizar_periodos_apostas_hot(self):
        """Verifica e atualiza os períodos das apostas hot (Amanhã -> Hoje quando necessário)"""
        try:
            if not hasattr(self, 'apostas_hot') or not self.apostas_hot:
                return
            
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            apostas_atualizadas = []
            mudancas = 0
            
            print(f"🔍 Verificando períodos das apostas hot para data de hoje: {data_hoje}")
            
            for aposta in self.apostas_hot:
                # Verificar múltiplas fontes para determinar a data do jogo
                data_jogo = None
                
                # 1. Verificar se há match_id e buscar no cache de hoje/amanhã
                match_id = aposta.get('match_id')
                if match_id:
                    # Verificar cache de hoje
                    cache_hoje = self.carregar_jogos_cache(data_hoje)
                    if cache_hoje and cache_hoje.get('jogos'):
                        for jogo in cache_hoje['jogos']:
                            if jogo.get('id') == match_id or jogo.get('match_id') == match_id:
                                data_jogo = data_hoje
                                break
                    
                    # Se não encontrou hoje, verificar cache de amanhã
                    if not data_jogo:
                        data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                        cache_amanha = self.carregar_jogos_cache(data_amanha)
                        if cache_amanha and cache_amanha.get('jogos'):
                            for jogo in cache_amanha['jogos']:
                                if jogo.get('id') == match_id or jogo.get('match_id') == match_id:
                                    data_jogo = data_amanha
                                    break
                
                # 2. Se não conseguiu pelo match_id, tentar por horário/data
                if not data_jogo:
                    horario_str = aposta.get('horario', '')
                    if len(horario_str) >= 10:  # '2024-08-27 15:30' ou similar
                        try:
                            if ' ' in horario_str:
                                data_part = horario_str.split(' ')[0]
                            else:
                                data_part = horario_str[:10]
                            
                            # Verificar se é data válida
                            datetime.strptime(data_part, '%Y-%m-%d')
                            data_jogo = data_part
                        except:
                            pass
                
                # 3. Determinar período baseado na data do jogo
                if data_jogo:
                    periodo_atual = aposta.get('periodo', 'Hoje')
                    periodo_correto = 'Hoje' if data_jogo == data_hoje else 'Amanhã'
                    
                    if periodo_atual != periodo_correto:
                        aposta['periodo'] = periodo_correto
                        mudancas += 1
                        print(f"🔄 Aposta atualizada: {aposta.get('jogo', 'N/A')} - {periodo_atual} -> {periodo_correto}")
                else:
                    # Se não conseguiu determinar a data, manter período atual
                    print(f"⚠️ Não foi possível determinar data para aposta: {aposta.get('jogo', 'N/A')}")
                
                apostas_atualizadas.append(aposta)
            
            # Atualizar a lista
            self.apostas_hot = apostas_atualizadas
            
            if mudancas > 0:
                print(f"✅ {mudancas} apostas hot tiveram o período atualizado")
                
                # Se a interface de apostas hot já foi criada, atualizar
                if hasattr(self, 'apostas_hot_frame'):
                    self.atualizar_apostas_hot_interface()
                    
        except Exception as e:
            print(f"❌ Erro ao verificar períodos das apostas hot: {e}")
    
    def atualizar_cache_periodo_apostas_hot(self):
        """Atualiza os períodos das apostas hot diretamente nos arquivos de cache"""
        try:
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            print(f"📁 Atualizando períodos nos arquivos de cache para data: {data_hoje}")
            
            # Carregar cache de hoje
            cache_hoje = self.carregar_jogos_cache(data_hoje)
            if cache_hoje and 'apostas_hot' in cache_hoje:
                mudancas = 0
                for aposta in cache_hoje['apostas_hot']:
                    if aposta.get('periodo') == 'Amanhã':
                        aposta['periodo'] = 'Hoje'
                        mudancas += 1
                        print(f"📝 Cache atualizado: {aposta.get('jogo', 'N/A')} - Amanhã -> Hoje")
                
                if mudancas > 0:
                    # Salvar cache atualizado
                    self.salvar_jogos_cache(data_hoje, cache_hoje)
                    print(f"✅ {mudancas} apostas hot atualizadas no cache de hoje")
                    
        except Exception as e:
            print(f"❌ Erro ao atualizar cache de períodos: {e}")
    
    # Métodos implementados
    def aposta_simples_jogo(self):
        """Calcula aposta simples para o jogo selecionado"""
        if not hasattr(self, 'jogo_selecionado_index'):
            messagebox.showwarning("Aviso", "Selecione um jogo primeiro")
            return
        
        jogo = self.jogos_do_dia[self.jogo_selecionado_index]
        
        # Abrir janela de aposta simples
        self.abrir_janela_aposta_simples(jogo)
    
    def adicionar_multipla_jogo(self):
        """Adiciona jogo selecionado à múltipla"""
        if not hasattr(self, 'jogo_selecionado_index'):
            messagebox.showwarning("Aviso", "Selecione um jogo primeiro")
            return
        
        jogo = self.jogos_do_dia[self.jogo_selecionado_index]
        
        # Abrir janela de seleção de aposta
        self.abrir_janela_selecao_aposta(jogo)
    

    
    def abrir_janela_aposta_simples(self, jogo):
        """Abre janela para calcular aposta simples"""
        window = tk.Toplevel(self.root)
        window.title("💰 Aposta Simples")
        window.geometry("600x650")
        window.transient(self.root)
        window.grab_set()
        
        # Título
        ttk.Label(window, text="💰 CÁLCULO DE APOSTA SIMPLES", 
                 style='Title.TLabel').pack(pady=10)
        
        # Informações do jogo
        info_frame = ttk.LabelFrame(window, text="Informações do Jogo", padding=15)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        casa = jogo.get('home_team', jogo.get('time_casa', ''))
        visitante = jogo.get('away_team', jogo.get('time_visitante', ''))
        
        ttk.Label(info_frame, text=f"🏠 Casa: {casa}", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(info_frame, text=f"✈️ Visitante: {visitante}", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(info_frame, text=f"🏆 Liga: {jogo.get('league', 'N/A')}").pack(anchor='w')
        ttk.Label(info_frame, text=f"⏰ Horário: {self.formatar_horario(jogo.get('start_time', ''))}").pack(anchor='w')
        
        # Seleção de aposta
        aposta_frame = ttk.LabelFrame(window, text="Selecionar Aposta", padding=15)
        aposta_frame.pack(fill='x', padx=20, pady=10)
        
        # Tipo de aposta
        casa = jogo.get('home_team', jogo.get('time_casa', 'Casa'))
        visitante = jogo.get('away_team', jogo.get('time_visitante', 'Visitante'))
        
        ttk.Label(aposta_frame, text="Tipo de Aposta:").pack(anchor='w')
        tipo_aposta = ttk.Combobox(aposta_frame, values=[
            f"Vitória {casa}", "Empate", f"Vitória {visitante}",
            "Mais de 2.5 gols", "Menos de 2.5 gols", "Ambos Marcam",
            "Mais de 1.5 gols", "Menos de 1.5 gols"
        ], state="readonly", width=30)
        tipo_aposta.pack(fill='x', pady=5)
        
        # Valor da aposta
        ttk.Label(aposta_frame, text="Valor da Aposta (R$):").pack(anchor='w', pady=(10, 0))
        valor_entry = ttk.Entry(aposta_frame, width=15)
        valor_entry.pack(anchor='w', pady=5)
        valor_entry.insert(0, "10.00")
        
        # Resultados
        resultado_frame = ttk.LabelFrame(window, text="Cálculos", padding=15)
        resultado_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        resultado_text = scrolledtext.ScrolledText(resultado_frame, height=10, width=50,
                                                   bg=self.cores['bg_input'],
                                                   fg=self.cores['fg_input'],
                                                   insertbackground=self.cores['fg_input'])
        resultado_text.pack(fill='both', expand=True)
        
        def calcular_aposta():
            if not tipo_aposta.get():
                messagebox.showwarning("Aviso", "Selecione o tipo de aposta")
                return
            
            try:
                valor = float(valor_entry.get())
            except ValueError:
                messagebox.showwarning("Aviso", "Valor inválido")
                return
            
            # Buscar estatísticas e calcular
            stats = self.api.buscar_estatisticas_detalhadas_time(jogo['id'])
            if not stats:
                messagebox.showerror("Erro", "Não foi possível obter estatísticas")
                return
            
            # Calcular probabilidades
            probabilidades = self.calcular_probabilidades_completas(stats, self.modo_analise.get())
            
            # Buscar odds
            odds_detalhadas = self.buscar_odds_detalhadas(jogo['id'])
            
            # Gerar relatório
            relatorio = self.gerar_relatorio_aposta_simples(
                tipo_aposta.get(), valor, probabilidades, odds_detalhadas, casa, visitante)
            
            resultado_text.delete(1.0, tk.END)
            resultado_text.insert(1.0, relatorio)
        
        # Botões
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(btn_frame, text="🧮 Calcular", command=calcular_aposta).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Fechar", command=window.destroy).pack(side='right', padx=5)
    
    def abrir_janela_selecao_aposta(self, jogo):
        """Abre janela para selecionar aposta para múltipla"""
        window = tk.Toplevel(self.root)
        window.title("📋 Adicionar à Múltipla")
        window.geometry("550x500")
        window.transient(self.root)
        window.grab_set()
        
        # Título
        ttk.Label(window, text="📋 ADICIONAR À MÚLTIPLA", 
                 style='Title.TLabel').pack(pady=10)
        
        casa = jogo.get('home_team', jogo.get('time_casa', ''))
        visitante = jogo.get('away_team', jogo.get('time_visitante', ''))
        
        ttk.Label(window, text=f"{casa} vs {visitante}", 
                 style='Subtitle.TLabel').pack(pady=5)
        
        # Opções de aposta
        aposta_frame = ttk.LabelFrame(window, text="Selecionar Aposta", padding=15)
        aposta_frame.pack(fill='x', padx=20, pady=10)
        
        # Buscar odds
        odds_detalhadas = self.buscar_odds_detalhadas(jogo['id'])
        
        if odds_detalhadas and 'odds' in odds_detalhadas:
            odds = odds_detalhadas['odds']
            
            # Resultado FT
            if 'resultFt' in odds:
                ttk.Label(aposta_frame, text="Resultado Final:", style='Subtitle.TLabel').pack(anchor='w')
                
                result_odds = odds['resultFt']
                opcoes_resultado = [
                    (f"Vitória {casa}", result_odds['home'], f'Vitória {casa}'),
                    ("Empate", result_odds['draw'], 'Empate'),
                    (f"Vitória {visitante}", result_odds['away'], f'Vitória {visitante}')
                ]
                
                for texto, odd, tipo in opcoes_resultado:
                    btn = ttk.Button(aposta_frame, text=f"{texto} - Odd: {odd:.2f}",
                                    command=lambda t=tipo, o=odd: self.adicionar_aposta_multipla_detalhada(
                                        jogo, t, o, odds_detalhadas, window))
                    btn.pack(fill='x', pady=2)
            
            # Gols
            if 'goalsOu25' in odds:
                ttk.Label(aposta_frame, text="Gols 2.5:", style='Subtitle.TLabel').pack(anchor='w', pady=(10, 0))
                
                gols_odds = odds['goalsOu25']
                opcoes_gols = [
                    ("Mais de 2.5 gols", gols_odds['over'], 'Mais de 2.5'),
                    ("Menos de 2.5 gols", gols_odds['under'], 'Menos de 2.5')
                ]
                
                for texto, odd, tipo in opcoes_gols:
                    btn = ttk.Button(aposta_frame, text=f"{texto} - Odd: {odd:.2f}",
                                    command=lambda t=tipo, o=odd: self.adicionar_aposta_multipla_detalhada(
                                        jogo, t, o, odds_detalhadas, window))
                    btn.pack(fill='x', pady=2)
        
        else:
            ttk.Label(aposta_frame, text="Odds não disponíveis", 
                     style='Warning.TLabel').pack()
        
        ttk.Button(window, text="❌ Cancelar", command=window.destroy).pack(pady=20)
    
    def abrir_janela_edicao_ao_vivo(self, jogo):
        """Abre janela para editar informações do jogo ao vivo"""
        window = tk.Toplevel(self.root)
        window.title("⚡ Editar Jogo Ao Vivo")
        window.geometry("550x600")
        window.transient(self.root)
        window.grab_set()
        
        # Título
        ttk.Label(window, text="⚡ JOGO AO VIVO", 
                 style='Title.TLabel').pack(pady=10)
        
        casa = jogo.get('home_team', jogo.get('time_casa', ''))
        visitante = jogo.get('away_team', jogo.get('time_visitante', ''))
        
        ttk.Label(window, text=f"{casa} vs {visitante}", 
                 style='Subtitle.TLabel').pack(pady=5)
        
        # Frame de informações atuais
        info_frame = ttk.LabelFrame(window, text="Informações Atuais", padding=15)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        # Placar atual
        placar_frame = ttk.Frame(info_frame)
        placar_frame.pack(fill='x', pady=5)
        
        ttk.Label(placar_frame, text="Placar Atual:").pack(side='left')
        
        placar_casa = ttk.Entry(placar_frame, width=5)
        placar_casa.pack(side='left', padx=(10, 5))
        placar_casa.insert(0, str(jogo.get('placar_casa', 0)))
        
        ttk.Label(placar_frame, text="x").pack(side='left', padx=5)
        
        placar_visitante = ttk.Entry(placar_frame, width=5)
        placar_visitante.pack(side='left', padx=(5, 0))
        placar_visitante.insert(0, str(jogo.get('placar_visitante', 0)))
        
        # Tempo de jogo
        tempo_frame = ttk.Frame(info_frame)
        tempo_frame.pack(fill='x', pady=5)
        
        ttk.Label(tempo_frame, text="Tempo (min):").pack(side='left')
        tempo_entry = ttk.Entry(tempo_frame, width=10)
        tempo_entry.pack(side='left', padx=(10, 0))
        tempo_entry.insert(0, "45")
        
        # Status adicional
        status_frame = ttk.Frame(info_frame)
        status_frame.pack(fill='x', pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side='left')
        status_combo = ttk.Combobox(status_frame, values=[
            "1º Tempo", "Intervalo", "2º Tempo", "Prorrogação", "Finalizado"
        ], state="readonly", width=15)
        status_combo.pack(side='left', padx=(10, 0))
        status_combo.set("1º Tempo")
        
        # Estatísticas ao vivo
        stats_frame = ttk.LabelFrame(window, text="Ajustar Estatísticas", padding=15)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(stats_frame, text="Cartões Casa:").pack(anchor='w')
        cartoes_casa = ttk.Entry(stats_frame, width=10)
        cartoes_casa.pack(anchor='w', pady=2)
        cartoes_casa.insert(0, "0")
        
        ttk.Label(stats_frame, text="Cartões Visitante:").pack(anchor='w')
        cartoes_visitante = ttk.Entry(stats_frame, width=10)
        cartoes_visitante.pack(anchor='w', pady=2)
        cartoes_visitante.insert(0, "0")
        
        ttk.Label(stats_frame, text="Escanteios Casa:").pack(anchor='w')
        escanteios_casa = ttk.Entry(stats_frame, width=10)
        escanteios_casa.pack(anchor='w', pady=2)
        escanteios_casa.insert(0, "0")
        
        ttk.Label(stats_frame, text="Escanteios Visitante:").pack(anchor='w')
        escanteios_visitante = ttk.Entry(stats_frame, width=10)
        escanteios_visitante.pack(anchor='w', pady=2)
        escanteios_visitante.insert(0, "0")
        
        def atualizar_jogo():
            try:
                # Validar dados
                gols_casa = int(placar_casa.get())
                gols_visitante = int(placar_visitante.get())
                tempo = int(tempo_entry.get())
                
                # Atualizar jogo na lista
                jogo.update({
                    'placar_casa_atual': gols_casa,
                    'placar_visitante_atual': gols_visitante,
                    'tempo_atual': tempo,
                    'status_jogo': status_combo.get(),
                    'cartoes_casa': int(cartoes_casa.get()),
                    'cartoes_visitante': int(cartoes_visitante.get()),
                    'escanteios_casa': int(escanteios_casa.get()),
                    'escanteios_visitante': int(escanteios_visitante.get()),
                    'atualizado_ao_vivo': True
                })
                
                # Atualizar lista visual
                self.atualizar_lista_jogos()
                
                messagebox.showinfo("Sucesso", "Jogo atualizado com sucesso!")
                window.destroy()
                
            except ValueError:
                messagebox.showerror("Erro", "Valores inválidos inseridos")
        
        # Botões
        btn_frame = ttk.Frame(window)
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(btn_frame, text="✅ Atualizar", command=atualizar_jogo).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Cancelar", command=window.destroy).pack(side='right', padx=5)
    
    def adicionar_aposta_multipla_detalhada(self, jogo, tipo_aposta, odd, odds_detalhadas, window):
        """Adiciona aposta detalhada à múltipla"""
        casa = jogo.get('home_team', jogo.get('time_casa', ''))
        visitante = jogo.get('away_team', jogo.get('time_visitante', ''))
        
        # Calcular probabilidade Bet365
        prob_implicita = (1 / odd * (1 - 0.05)) * 100 if odd > 0 else 0
        
        # Calcular probabilidade Bet Booster baseada no tipo de aposta
        nossa_prob = 0
        try:
            # Primeiro, tentar obter estatísticas do jogo atual
            match_id = jogo.get('id')
            stats = None
            
            # Se já temos stats cached do jogo selecionado e é o mesmo jogo
            if (hasattr(self, 'jogo_selecionado_stats') and 
                self.jogo_selecionado_stats and 
                hasattr(self, 'jogo_selecionado_index') and
                self.jogos_do_dia[self.jogo_selecionado_index].get('id') == match_id):
                stats = self.jogo_selecionado_stats
            else:
                # Buscar estatísticas automaticamente para este jogo
                print(f"📊 Buscando estatísticas detalhadas para Match ID: {match_id}")
                stats = self.api.buscar_estatisticas_detalhadas_time(match_id)
            
            if stats:
                probabilidades = self.calcular_probabilidades_completas(stats, "Geral")
                
                # Obter nomes dos times para comparação
                jogo_atual = self.jogos_do_dia[self.jogo_selecionado_index]
                casa_nome = jogo_atual.get('home_team', jogo_atual.get('time_casa', 'Casa'))
                visitante_nome = jogo_atual.get('away_team', jogo_atual.get('time_visitante', 'Visitante'))
                
                # Mapear tipo de aposta para probabilidade Bet Booster
                if (tipo_aposta == "Vitória Casa" or tipo_aposta == f"Vitória {casa_nome}" or tipo_aposta == f"Vitória {casa}"):
                    nossa_prob = probabilidades.get('vitoria_casa', 0)
                elif (tipo_aposta == "Vitória Visitante" or tipo_aposta == f"Vitória {visitante_nome}" or tipo_aposta == f"Vitória {visitante}"):
                    nossa_prob = probabilidades.get('vitoria_visitante', 0)
                elif tipo_aposta == "Empate":
                    nossa_prob = probabilidades.get('empate', 0)
                elif "Over 2.5" in tipo_aposta:
                    nossa_prob = probabilidades.get('over_25', 0)
                elif "Under 2.5" in tipo_aposta:
                    nossa_prob = probabilidades.get('under_25', 0)
                else:
                    nossa_prob = prob_implicita  # Fallback para prob implícita
            else:
                print(f"⚠️ Estatísticas não encontradas para o jogo, usando probabilidade Bet365")
                nossa_prob = prob_implicita  # Fallback se não conseguir obter stats
        except Exception as e:
            print(f"❌ Erro ao calcular probabilidade Bet Booster: {e}")
            nossa_prob = prob_implicita  # Fallback em caso de erro
        
        # Determinar tipo de recomendação baseado no value bet
        tipo_recomendacao = "FORTE"  # Default
        if nossa_prob > 0 and odd > 0:
            # Calcular value bet
            value = odd * (nossa_prob / 100)
            value_percent = (value - 1) * 100
            
            # Aplicar NOVAS regras: 
            # Forte: Prob. Bet365 >= 40%, value >= 10%
            # Moderada: Prob. Bet365 >= 30%, value >= 10%
            # Arriscada: Prob. Bet365 >= 15% E < 30%, value >= 10%
            # Muito Arriscada: Prob. Bet365 >= 5% E < 15%, value >= 30%
            if value_percent >= 10 and prob_implicita >= 40:
                tipo_recomendacao = "FORTE"
            elif value_percent >= 10 and prob_implicita >= 30:
                tipo_recomendacao = "MODERADA"
            elif value_percent >= 10 and prob_implicita >= 15 and prob_implicita < 30:
                tipo_recomendacao = "ARRISCADA"
            elif value_percent >= 30 and prob_implicita >= 5 and prob_implicita < 15:
                tipo_recomendacao = "MUITO_ARRISCADA"
            else:
                tipo_recomendacao = "MODERADA"  # Padrão para apostas não classificadas
        
        aposta_detalhada = {
            'jogo': f"{casa} vs {visitante}",
            'aposta': tipo_aposta,
            'tipo': tipo_recomendacao,
            'odd': odd,
            'nossa_prob': nossa_prob,
            'prob_calculada': nossa_prob,  # Manter ambos por compatibilidade
            'prob_implicita': prob_implicita,
            'match_id': jogo.get('id', ''),
            'liga': odds_detalhadas.get('league', ''),
            'horario': self.formatar_horario(odds_detalhadas.get('start_time', ''))
        }
        
        self.apostas_multipla.append(aposta_detalhada)
        self.atualizar_multipla()
        
        messagebox.showinfo("Sucesso", f"Aposta adicionada: {tipo_aposta}")
        window.destroy()
        
        # Mudar para aba de múltiplas
        self.notebook.select(4)  # Índice da aba múltiplas
    
    def calcular_probabilidades_completas(self, stats, modo):
        """Calcula probabilidades completas baseado nas estatísticas - USANDO APENAS ANYFIELD"""
        try:
            # SEMPRE USAR ESTATÍSTICAS GERAIS (ANYFIELD) INDEPENDENTE DO MODO
            # sameField só é usado para cadastrar dados, não para cálculos
            gols_casa = stats['time_casa']['geral']['gols_marcados']
            gols_sofridos_casa = stats['time_casa']['geral']['gols_sofridos']
            gols_visitante = stats['time_visitante']['geral']['gols_marcados']
            gols_sofridos_visitante = stats['time_visitante']['geral']['gols_sofridos']
            
            # Fórmula de Poisson para gols esperados
            gols_esperados_casa = (gols_casa + gols_sofridos_visitante) / 2
            gols_esperados_visitante = (gols_visitante + gols_sofridos_casa) / 2
            
            # Distribuição de Poisson para probabilidades de resultado
            from math import exp, factorial
            
            max_gols = 7
            probabilidades_matriz = []
            
            for casa in range(max_gols):
                linha = []
                for visitante in range(max_gols):
                    prob_casa = (gols_esperados_casa ** casa * exp(-gols_esperados_casa)) / factorial(casa)
                    prob_visitante = (gols_esperados_visitante ** visitante * exp(-gols_esperados_visitante)) / factorial(visitante)
                    prob_resultado = prob_casa * prob_visitante
                    linha.append(prob_resultado)
                probabilidades_matriz.append(linha)
            
            # Calcular probabilidades finais
            prob_vitoria_casa = 0
            prob_empate = 0
            prob_vitoria_visitante = 0
            
            for casa in range(max_gols):
                for visitante in range(max_gols):
                    prob = probabilidades_matriz[casa][visitante]
                    if casa > visitante:
                        prob_vitoria_casa += prob
                    elif casa == visitante:
                        prob_empate += prob
                    else:
                        prob_vitoria_visitante += prob
            
            # Normalizar para 100%
            total = prob_vitoria_casa + prob_empate + prob_vitoria_visitante
            if total > 0:
                prob_vitoria_casa = (prob_vitoria_casa / total) * 100
                prob_empate = (prob_empate / total) * 100
                prob_vitoria_visitante = (prob_vitoria_visitante / total) * 100

            # Adicionar 5% de vantagem para o time da casa
            vantagem_casa = prob_vitoria_casa * 0.05
            prob_vitoria_casa += vantagem_casa
            
            # Re-normalizar as outras probabilidades para que o total seja 100%
            total_outras = prob_empate + prob_vitoria_visitante
            if total_outras > 0:
                fator_ajuste = (100 - prob_vitoria_casa) / total_outras
                prob_empate *= fator_ajuste
                prob_vitoria_visitante *= fator_ajuste

            
            # Calcular gols esperados total
            gols_esperados_total = gols_esperados_casa + gols_esperados_visitante
            
            # Calcular probabilidades over/under para diferentes linhas
            over_15 = self.calcular_prob_over_under(gols_esperados_total, 1.5, 'over')
            under_15 = 100 - over_15
            over_25 = self.calcular_prob_over_under(gols_esperados_total, 2.5, 'over')
            under_25 = 100 - over_25
            over_35 = self.calcular_prob_over_under(gols_esperados_total, 3.5, 'over')
            under_35 = 100 - over_35
            
            return {
                'vitoria_casa': prob_vitoria_casa,
                'empate': prob_empate,
                'vitoria_visitante': prob_vitoria_visitante,
                'gols_esperados_casa': gols_esperados_casa,
                'gols_esperados_visitante': gols_esperados_visitante,
                'gols_esperados_total': gols_esperados_total,
                'over_15': over_15,
                'under_15': under_15,
                'over_25': over_25,
                'under_25': under_25,
                'over_35': over_35,
                'under_35': under_35
            }
            
        except Exception as e:
            print(f"Erro ao calcular probabilidades: {e}")
            return {
                'vitoria_casa': 33.33,
                'empate': 33.33,
                'vitoria_visitante': 33.33,
                'gols_esperados_casa': 1.25,
                'gols_esperados_visitante': 1.25,
                'gols_esperados_total': 2.5,
                'over_15': 70.0,
                'under_15': 30.0,
                'over_25': 50.0,
                'under_25': 50.0,
                'over_35': 30.0,
                'under_35': 70.0
            }
    
    def gerar_relatorio_aposta_simples(self, tipo_aposta, valor, probabilidades, odds_detalhadas, casa, visitante):
        """Gera relatório detalhado da aposta simples"""
        relatorio = f"""
📊 RELATÓRIO DE APOSTA SIMPLES
═══════════════════════════════════════

🏠 Casa: {casa}
✈️ Visitante: {visitante}
💰 Aposta: {tipo_aposta}
💵 Valor: R$ {valor:.2f}

📈 PROBABILIDADES CALCULADAS:
═══════════════════════════════════════
🏠 Vitória {casa}: {probabilidades['vitoria_casa']:.1f}%
🤝 Empate: {probabilidades['empate']:.1f}%
✈️ Vitória {visitante}: {probabilidades['vitoria_visitante']:.1f}%

⚽ EXPECTATIVA DE GOLS:
═══════════════════════════════════════
🏠 Gols Casa: {probabilidades['gols_esperados_casa']:.2f}
✈️ Gols Visitante: {probabilidades['gols_esperados_visitante']:.2f}
🎯 Total Esperado: {probabilidades['gols_esperados_total']:.2f}

"""
        
        if odds_detalhadas and 'odds' in odds_detalhadas:
            odds = odds_detalhadas['odds']
            
            # Mapear tipo de aposta para odds
            odd_aposta = None
            prob_nossa = None
            
            if (tipo_aposta == "Vitória Casa" or f"Vitória {casa}" in tipo_aposta) and 'resultFt' in odds:
                odd_aposta = odds['resultFt']['home']
                prob_nossa = probabilidades['vitoria_casa']
            elif tipo_aposta == "Empate" and 'resultFt' in odds:
                odd_aposta = odds['resultFt']['draw']
                prob_nossa = probabilidades['empate']
            elif (tipo_aposta == "Vitória Visitante" or f"Vitória {visitante}" in tipo_aposta) and 'resultFt' in odds:
                odd_aposta = odds['resultFt']['away']
                prob_nossa = probabilidades['vitoria_visitante']
            elif tipo_aposta == "Over 2.5" and 'goalsOu25' in odds:
                odd_aposta = odds['goalsOu25']['over']
                prob_nossa = self.calcular_prob_over_under(probabilidades['gols_esperados_total'], 2.5, 'over')
            elif tipo_aposta == "Under 2.5" and 'goalsOu25' in odds:
                odd_aposta = odds['goalsOu25']['under']
                prob_nossa = self.calcular_prob_over_under(probabilidades['gols_esperados_total'], 2.5, 'under')
            
            if odd_aposta and prob_nossa:
                prob_implicita = (1 / odd_aposta * 100)
                value_bet = (prob_nossa / prob_implicita)
                retorno_potencial = valor * odd_aposta
                lucro_potencial = retorno_potencial - valor
                
                relatorio += f"""💰 ANÁLISE FINANCEIRA:
═══════════════════════════════════════
🎯 Odd da Casa: {odd_aposta:.2f}
📊 Prob. Bet Booster: {prob_nossa:.1f}%
🏠 Prob. Bet365: {prob_implicita:.1f}%
💎 Value Bet: {value_bet:.3f} ({((value_bet - 1) * 100):+.1f}%)

💵 Retorno Potencial: R$ {retorno_potencial:.2f}
💰 Lucro Potencial: R$ {lucro_potencial:.2f}

"""
                
                # Aplicar novas regras de classificação
                value_percent = (value_bet - 1) * 100
                
                # Determinar tipo de aposta para aplicar regra correta
                is_vencedor = (tipo_aposta in ["Vitória Casa", "Empate", "Vitória Visitante"] or 
                              f"Vitória {casa}" in tipo_aposta or f"Vitória {visitante}" in tipo_aposta)
                
                if is_vencedor:
                    # NOVAS Regras para vencedor: 
                    # Forte: Prob. Bet365 >= 40%, value >= 10%
                    # Moderada: Prob. Bet365 >= 30%, value >= 10%
                    # Arriscada: Prob. Bet365 >= 15% E < 30%, value >= 10%
                    # Muito Arriscada: Prob. Bet365 >= 5% E < 15%, value >= 30%
                    if value_percent >= 10 and prob_implicita >= 40:
                        relatorio += "✅ RECOMENDAÇÃO: APOSTA FORTE!\n"
                        relatorio += "🔥 Value >= 10% com probabilidade Bet365 >= 40%\n"
                    elif value_percent >= 10 and prob_implicita >= 30:
                        relatorio += "🟡 RECOMENDAÇÃO: APOSTA MODERADA!\n"
                        relatorio += "� Value >= 10% com probabilidade Bet365 >= 30%\n"
                    elif value_percent >= 10 and prob_implicita >= 15 and prob_implicita < 30:
                        relatorio += "⚠️ RECOMENDAÇÃO: APOSTA ARRISCADA!\n"
                        relatorio += "🟡 Value >= 10% com probabilidade Bet365 entre 15% e 30%\n"
                    elif value_percent >= 30 and prob_implicita >= 5 and prob_implicita < 15:
                        relatorio += "🚨 RECOMENDAÇÃO: APOSTA MUITO ARRISCADA!\n"
                        relatorio += "🔴 Value >= 30% com probabilidade Bet365 entre 5% e 15%\n"
                    else:
                        relatorio += "❌ NÃO RECOMENDADO - Não atende aos critérios\n"
                else:
                    # NOVAS Regras para Over/Under: 
                    # Forte: Prob. Bet365 >= 40%, value >= 10%
                    # Moderada: Prob. Bet365 >= 30%, value >= 10%
                    # Arriscada: Prob. Bet365 >= 15% E < 30%, value >= 10%
                    # Muito Arriscada: Prob. Bet365 >= 5% E < 15%, value >= 30%
                    if value_percent >= 10 and prob_implicita >= 40:
                        relatorio += "✅ RECOMENDAÇÃO: APOSTA FORTE!\n"
                        relatorio += "🔥 Probabilidade Bet365 >= 40% com value >= 10%\n"
                    elif value_percent >= 10 and prob_implicita >= 30:
                        relatorio += "🟡 RECOMENDAÇÃO: APOSTA MODERADA!\n"
                        relatorio += "� Probabilidade Bet365 >= 30% com value >= 10%\n"
                    elif value_percent >= 10 and prob_implicita >= 15 and prob_implicita < 30:
                        relatorio += "⚠️ RECOMENDAÇÃO: APOSTA ARRISCADA!\n"
                        relatorio += "🟡 Probabilidade Bet365 entre 15% e 30% com value >= 10%\n"
                    elif value_percent >= 30 and prob_implicita >= 5 and prob_implicita < 15:
                        relatorio += "🚨 RECOMENDAÇÃO: APOSTA MUITO ARRISCADA!\n"
                        relatorio += "🔴 Probabilidade Bet365 entre 5% e 15% com value >= 30%\n"
                    else:
                        relatorio += "❌ NÃO RECOMENDADO - Não atende aos critérios\n"
        
        relatorio += f"""
═══════════════════════════════════════
⏰ Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        
        return relatorio

    # ==========================================
    # FUNÇÕES DE DICAS E BILHETES AUTOMÁTICOS
    # ==========================================
    
    def mostrar_dicas_apostas(self):
        """Mostra janela com dicas de apostas baseadas no arquivo recomendacao_apostas.txt"""
        try:
            # Ler o arquivo de recomendações
            docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'recomendacao_apostas.txt')
            
            if not os.path.exists(docs_path):
                messagebox.showerror("Erro", "Arquivo de recomendações não encontrado!")
                return
                
            with open(docs_path, 'r', encoding='utf-8') as f:
                conteudo_dicas = f.read()
            
            # Criar janela de dicas
            janela_dicas = tk.Toplevel(self.root)
            janela_dicas.title("💡 Dicas de Apostas - Bet Booster")
            janela_dicas.geometry("600x500")
            janela_dicas.configure(bg=self.cores['bg_principal'])
            
            # Frame principal
            main_frame = tk.Frame(janela_dicas, bg=self.cores['bg_principal'])
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Título
            titulo = tk.Label(main_frame, text="💡 DICAS DE APOSTAS", 
                             font=('Arial', 18, 'bold'), bg=self.cores['bg_principal'], fg='#1e40af')
            titulo.pack(pady=(0, 20))
            
            # Área de texto com scroll
            texto_frame = tk.Frame(main_frame, bg=self.cores['bg_principal'])
            texto_frame.pack(fill='both', expand=True)
            
            # ScrolledText para as dicas
            texto_dicas = scrolledtext.ScrolledText(texto_frame, wrap=tk.WORD, 
                                                   font=('Arial', 11), 
                                                   bg=self.cores['bg_secundario'], fg=self.cores['fg_normal'],
                                                   insertbackground=self.cores['fg_normal'],
                                                   relief='flat', borderwidth=1)
            texto_dicas.pack(fill='both', expand=True)
            
            # Formatar o conteúdo das dicas
            conteudo_formatado = self.formatar_dicas_apostas(conteudo_dicas)
            texto_dicas.insert('1.0', conteudo_formatado)
            texto_dicas.config(state='disabled')
            
            # Botão fechar
            tk.Button(main_frame, text="Fechar", command=janela_dicas.destroy,
                     font=('Arial', 12), bg='#ef4444', fg='white',
                     padx=30, pady=8).pack(pady=20)
                     
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao mostrar dicas: {str(e)}")
    
    def formatar_dicas_apostas(self, conteudo):
        """Formata o conteúdo das dicas para melhor visualização"""
        linhas = conteudo.split('\n')
        conteudo_formatado = ""
        
        for linha in linhas:
            linha = linha.strip()
            if not linha:
                conteudo_formatado += "\n"
                continue
                
            if linha.startswith("Dica de Aposta segura:"):
                conteudo_formatado += f"🛡️ {linha.upper()}\n"
                conteudo_formatado += "─" * 50 + "\n"
            elif linha.startswith("Bilhete"):
                conteudo_formatado += f"\n🎯 {linha.upper()}\n"
                conteudo_formatado += "─" * 30 + "\n"
            elif linha.startswith("Time em casa"):
                conteudo_formatado += f"• {linha}\n"
            elif linha.startswith("Mínimo"):
                conteudo_formatado += f"• {linha}\n"
            elif linha.startswith("Mais de"):
                conteudo_formatado += f"• {linha}\n"
            elif linha.startswith("Time de"):
                conteudo_formatado += f"• {linha}\n"
            elif any(x in linha for x in ["aposta forte", "aposta moderada", "apostas moderadas", "aposta arriscada"]):
                conteudo_formatado += f"  → {linha}\n"
            else:
                conteudo_formatado += f"{linha}\n"
        
        return conteudo_formatado
    
    def classificar_aposta_por_criterios(self, aposta):
        """
        Classifica uma aposta baseada nos critérios das dicas:
        - Time em casa
        - Mínimo 3 vitórias nos últimos 5
        - Mais de 0.5 de diferença de gols esperados
        - Time de mesma liga
        """
        try:
            # Verificar se é time da casa (primeira parte do jogo)
            jogo_partes = aposta['jogo'].split(' vs ')
            if len(jogo_partes) != 2:
                return "moderada"  # Default se não conseguir identificar
            
            time_casa = jogo_partes[0].strip()
            
            # Por enquanto, vamos usar a classificação existente do sistema
            # que já está baseada em probabilidade e value
            if "Vitória" in aposta.get('aposta', ''):
                if "FORTE" in aposta.get('tipo', ''):
                    return "forte"
                elif "MODERADA" in aposta.get('tipo', ''):
                    return "moderada"
                elif "ARRISCADA" in aposta.get('tipo', '') and "MUITO" not in aposta.get('tipo', ''):
                    return "arriscada"
                elif "MUITO_ARRISCADA" in aposta.get('tipo', ''):
                    return "muito_arriscada"
                else:
                    # Classificar baseado em probabilidade e value como fallback
                    prob_implicita = aposta.get('prob_implicita', 0)
                    value = aposta.get('value', 1)
                    value_percent = (value - 1) * 100
                    
                    if value_percent >= 10 and prob_implicita >= 45:
                        return "forte"
                    elif value_percent >= 10 and prob_implicita >= 35:
                        return "moderada"
                    elif value_percent >= 10 and prob_implicita >= 25:
                        return "arriscada"
                    elif value_percent >= 30 and prob_implicita >= 15:
                        return "muito_arriscada"
                    else:
                        return None
            else:
                return None
                    
        except Exception as e:
            print(f"Erro ao classificar aposta: {e}")
            return None

    def mostrar_menu_bilhetes(self):
        """Mostra menu com opções de bilhetes com preview das apostas"""
        try:
            # Verificar se temos apostas hot disponíveis
            if not hasattr(self, 'apostas_hot') or not self.apostas_hot:
                messagebox.showwarning("Aviso", "Nenhuma aposta hot disponível. Carregue as apostas primeiro.")
                return
            
            # Criar janela do menu
            menu_window = tk.Toplevel(self.root)
            menu_window.title("🎫 Bilhetes Automáticos")
            
            # Obter dimensões da tela
            screen_width = menu_window.winfo_screenwidth()
            screen_height = menu_window.winfo_screenheight()
            
            # Definir tamanho da janela (maior para exibir 4 bilhetes lado a lado)
            window_width = int(screen_width * 0.80)  # 95% da largura da tela
            window_height = int(screen_height * 0.80)  # 90% da altura da tela
            
            # Calcular posição para centralizar
            x = (screen_width - window_width) // 2
            y = int(screen_height * 0.02)  # 2% do topo da tela
            
            menu_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            menu_window.transient(self.root)
            menu_window.configure(bg=self.cores['bg_principal'])
            
            # Título
            titulo_frame = tk.Frame(menu_window, bg=self.cores['bg_principal'])
            titulo_frame.pack(fill='x', pady=10)
            
            tk.Label(titulo_frame, text="🎫 BILHETES AUTOMÁTICOS", 
                    font=('Arial', 18, 'bold'), bg=self.cores['bg_principal'], fg='#1e40af').pack()
            tk.Label(titulo_frame, text="Visualize e escolha os bilhetes ou apostas individuais", 
                    font=('Arial', 11), bg=self.cores['bg_principal'], fg=self.cores['fg_normal']).pack(pady=2)
            
            # Canvas com scrollbar para os bilhetes
            canvas_frame = tk.Frame(menu_window, bg=self.cores['bg_principal'])
            canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            canvas = tk.Canvas(canvas_frame, bg=self.cores['bg_principal'], highlightthickness=0)
            scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.cores['bg_principal'])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Função para scroll com mouse
            def on_mouse_wheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            # Função para ativar scroll quando mouse entra na janela
            def on_enter(event):
                canvas.bind_all("<MouseWheel>", on_mouse_wheel)
            
            # Função para desativar scroll quando mouse sai da janela
            def on_leave(event):
                canvas.unbind_all("<MouseWheel>")
            
            # Bind de entrada e saída do mouse
            menu_window.bind("<Enter>", on_enter)
            canvas.bind("<Enter>", on_enter)
            scrollable_frame.bind("<Enter>", on_enter)
            
            # Unbind quando fechar a janela
            def on_close():
                canvas.unbind_all("<MouseWheel>")
                menu_window.destroy()
            
            menu_window.protocol("WM_DELETE_WINDOW", on_close)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Função para verificar se é aposta de vitória (não é over/under)
            def eh_aposta_vitoria(aposta):
                aposta_texto = aposta.get('aposta', '').lower()
                # Excluir apostas de gols (over/under)
                if 'mais de' in aposta_texto or 'menos de' in aposta_texto:
                    return False
                if 'over' in aposta_texto or 'under' in aposta_texto:
                    return False
                if 'gol' in aposta_texto:
                    return False
                # Incluir apenas apostas de vitória ou empate
                return True
            
            # Obter apostas filtradas - APENAS APOSTAS DE VITÓRIA
            apostas_fortes = [a for a in self.apostas_hot if a.get('tipo', '').upper() == 'FORTE' and eh_aposta_vitoria(a)]
            apostas_moderadas = [a for a in self.apostas_hot if a.get('tipo', '').upper() == 'MODERADA' and eh_aposta_vitoria(a)]
            apostas_arriscadas = [a for a in self.apostas_hot if a.get('tipo', '').upper() == 'ARRISCADA' and eh_aposta_vitoria(a)]
            apostas_muito_arriscadas = [a for a in self.apostas_hot if a.get('tipo', '').upper() == 'MUITO_ARRISCADA' and eh_aposta_vitoria(a)]
            
            # Ordenar apostas
            apostas_fortes.sort(key=lambda x: x.get('prob_media', 0), reverse=True)
            apostas_moderadas.sort(key=lambda x: x.get('prob_media', 0), reverse=True)
            apostas_arriscadas.sort(key=lambda x: x.get('prob_media', 0), reverse=True)
            apostas_muito_arriscadas.sort(key=lambda x: x.get('prob_media', 0), reverse=True)
            
            # Configurações dos bilhetes
            bilhetes_config = [
                ('🛡️ Bilhete Seguro 1', 'seguro_1', '#22c55e', 'green'),
                ('🛡️ Bilhete Seguro 2', 'seguro_2', '#22c55e', 'green'),
                ('⚡ Bilhete Arriscado 1', 'arriscado_1', '#f97316', 'orange'),
                ('⚡ Bilhete Arriscado 2', 'arriscado_2', '#f97316', 'orange'),
                ('🔥 Bilhete Muito Arriscado 1', 'muito_arriscado_1', '#ef4444', 'red'),
                ('🔥 Bilhete Muito Arriscado 2', 'muito_arriscado_2', '#ef4444', 'red'),
                ('🎰 Bilhete Mega Sena 1', 'mega_sena_1', '#8b5cf6', 'purple'),
                ('🎰 Bilhete Mega Sena 2', 'mega_sena_2', '#8b5cf6', 'purple')
            ]
            
            # Criar bilhetes em layout de grid (4 por linha)
            row = 0
            col = 0
            
            for nome_bilhete, tipo_bilhete, cor_bg, cor_fg in bilhetes_config:
                apostas_bilhete = self.obter_apostas_bilhete(tipo_bilhete, apostas_fortes, apostas_moderadas, 
                                                             apostas_arriscadas, apostas_muito_arriscadas)
                
                if apostas_bilhete:
                    self.criar_card_bilhete(scrollable_frame, nome_bilhete, tipo_bilhete, 
                                          apostas_bilhete, cor_bg, cor_fg, menu_window, row, col)
                    
                    # Avançar para próxima posição
                    col += 1
                    if col >= 4:  # 4 bilhetes por linha
                        col = 0
                        row += 1
            
            # Botão fechar
            btn_fechar = tk.Button(menu_window, text="❌ Fechar", command=on_close,
                     font=('Arial', 12, 'bold'), bg='#6b7280', fg='white',
                     padx=30, pady=10)
            btn_fechar.pack(pady=15)
                     
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao mostrar menu de bilhetes: {str(e)}")
    
    def obter_apostas_bilhete(self, tipo_bilhete, apostas_fortes, apostas_moderadas, 
                              apostas_arriscadas, apostas_muito_arriscadas):
        """Retorna as apostas para um tipo de bilhete específico com preenchimento automático"""
        apostas_selecionadas = []
        apostas_backup = []  # Backup de apostas fortes e moderadas para preencher faltantes
        
        # Criar lista de backup com todas fortes e moderadas
        apostas_backup.extend(apostas_fortes)
        apostas_backup.extend(apostas_moderadas)
        
        # Índice para o backup
        backup_idx = 0
        
        if tipo_bilhete == 'seguro_1':
            # primeira forte + segunda forte
            if len(apostas_fortes) >= 1:
                apostas_selecionadas.append(apostas_fortes[0])
                backup_idx = 1
            if len(apostas_fortes) >= 2:
                apostas_selecionadas.append(apostas_fortes[1])
                backup_idx = 2
                
        elif tipo_bilhete == 'seguro_2':
            # terceira forte + primeira moderada
            if len(apostas_fortes) >= 3:
                apostas_selecionadas.append(apostas_fortes[2])
                backup_idx = 3
            if len(apostas_moderadas) >= 1:
                apostas_selecionadas.append(apostas_moderadas[0])
                
                
        elif tipo_bilhete == 'arriscado_1':
            # primeira forte + segunda forte + primeira moderada
            if len(apostas_fortes) >= 1:
                apostas_selecionadas.append(apostas_fortes[0])
                backup_idx = 1
            if len(apostas_fortes) >= 2:
                apostas_selecionadas.append(apostas_fortes[1])
                backup_idx = 2
            if len(apostas_moderadas) >= 1:
                apostas_selecionadas.append(apostas_moderadas[0])
                
        elif tipo_bilhete == 'arriscado_2':
            # terceira forte + quarta forte + segunda moderada
            if len(apostas_fortes) >= 3:
                apostas_selecionadas.append(apostas_fortes[2])
                backup_idx = 3
            if len(apostas_fortes) >= 4:
                apostas_selecionadas.append(apostas_fortes[3])
                backup_idx = 4
            if len(apostas_moderadas) >= 2:
                apostas_selecionadas.append(apostas_moderadas[1])
                
        elif tipo_bilhete == 'muito_arriscado_1':
            # primeira moderada + segunda moderada + primeira arriscada
            if len(apostas_moderadas) >= 1:
                apostas_selecionadas.append(apostas_moderadas[0])
            if len(apostas_moderadas) >= 2:
                apostas_selecionadas.append(apostas_moderadas[1])
            if len(apostas_arriscadas) >= 1:
                apostas_selecionadas.append(apostas_arriscadas[0])
                
        elif tipo_bilhete == 'muito_arriscado_2':
            # terceira moderada + quarta moderada + segunda arriscada
            if len(apostas_moderadas) >= 3:
                apostas_selecionadas.append(apostas_moderadas[2])
            if len(apostas_moderadas) >= 4:
                apostas_selecionadas.append(apostas_moderadas[3])
            if len(apostas_arriscadas) >= 2:
                apostas_selecionadas.append(apostas_arriscadas[1])
                
        elif tipo_bilhete == 'mega_sena_1':
            # primeira forte + segunda forte + primeira moderada + segunda moderada + primeira arriscada
            if len(apostas_fortes) >= 1:
                apostas_selecionadas.append(apostas_fortes[0])
                backup_idx = 1
            if len(apostas_fortes) >= 2:
                apostas_selecionadas.append(apostas_fortes[1])
                backup_idx = 2
            if len(apostas_moderadas) >= 1:
                apostas_selecionadas.append(apostas_moderadas[0])
            if len(apostas_moderadas) >= 2:
                apostas_selecionadas.append(apostas_moderadas[1])
            if len(apostas_arriscadas) >= 1:
                apostas_selecionadas.append(apostas_arriscadas[0])
                
        elif tipo_bilhete == 'mega_sena_2':
            # terceira forte + quarta forte + terceira moderada + quarta moderada + segunda arriscada
            if len(apostas_fortes) >= 3:
                apostas_selecionadas.append(apostas_fortes[2])
                backup_idx = 3
            if len(apostas_fortes) >= 4:
                apostas_selecionadas.append(apostas_fortes[3])
                backup_idx = 4
            if len(apostas_moderadas) >= 3:
                apostas_selecionadas.append(apostas_moderadas[2])
            if len(apostas_moderadas) >= 4:
                apostas_selecionadas.append(apostas_moderadas[3])
            if len(apostas_arriscadas) >= 2:
                apostas_selecionadas.append(apostas_arriscadas[1])
        
        # Preencher apostas faltantes com backup (se necessário)
        # Determinar quantas apostas devem ter cada bilhete
        apostas_esperadas = {
            'seguro_1': 2, 'seguro_2': 2,
            'arriscado_1': 3, 'arriscado_2': 3,
            'muito_arriscado_1': 3, 'muito_arriscado_2': 3,
            'mega_sena_1': 5, 'mega_sena_2': 5
        }
        
        num_esperado = apostas_esperadas.get(tipo_bilhete, 2)
        
        # Se faltam apostas, preencher com backup
        while len(apostas_selecionadas) < num_esperado and backup_idx < len(apostas_backup):
            # Verificar se a aposta já não está na lista
            aposta_backup = apostas_backup[backup_idx]
            ja_existe = False
            for ap in apostas_selecionadas:
                if ap['jogo'] == aposta_backup['jogo'] and ap['aposta'] == aposta_backup['aposta']:
                    ja_existe = True
                    break
            
            if not ja_existe:
                apostas_selecionadas.append(aposta_backup)
            
            backup_idx += 1
        
        return apostas_selecionadas
    
    def criar_card_bilhete(self, parent, nome_bilhete, tipo_bilhete, apostas, cor_bg, cor_fg, menu_window, row, col):
        """Cria um card visual para um bilhete com preview das apostas em layout grid"""
        # Frame principal do card
        card_frame = tk.Frame(parent, bg=self.cores['bg_card'], relief='ridge', borderwidth=2)
        card_frame.grid(row=row, column=col, sticky='nsew', pady=8, padx=8)
        
        # Configurar peso das colunas para expansão uniforme (4 colunas)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)
        parent.grid_columnconfigure(3, weight=1)
        
        # Header do bilhete
        header_frame = tk.Frame(card_frame, bg=cor_bg)
        header_frame.pack(fill='x')
        
        # Calcular odd total
        odd_total = 1.0
        for aposta in apostas:
            odd_total *= aposta.get('odd', 1.0)
        
        # Nome e odd total
        tk.Label(header_frame, text=nome_bilhete, 
                font=('Arial', 12, 'bold'), bg=cor_bg, fg='white').pack(side='left', padx=12, pady=6)
        
        tk.Label(header_frame, text=f"ODD: {odd_total:.2f}x", 
                font=('Arial', 11, 'bold'), bg=cor_bg, fg='white').pack(side='right', padx=12, pady=6)
        
        # Lista de apostas
        apostas_frame = tk.Frame(card_frame, bg=self.cores['bg_card'])
        apostas_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        for idx, aposta in enumerate(apostas, 1):
            # Frame para cada aposta
            aposta_frame = tk.Frame(apostas_frame, bg=self.cores['bg_secundario'], relief='solid', borderwidth=1)
            aposta_frame.pack(fill='x', pady=2)
            
            # Info da aposta
            info_frame = tk.Frame(aposta_frame, bg=self.cores['bg_secundario'])
            info_frame.pack(side='left', fill='both', expand=True, padx=8, pady=4)
            
            # Jogo
            jogo_text = aposta['jogo']
            if len(jogo_text) > 40:
                jogo_text = jogo_text[:37] + "..."
            tk.Label(info_frame, text=f"{idx}. {jogo_text}", 
                    font=('Arial', 9, 'bold'), bg=self.cores['bg_secundario'], 
                    fg=self.cores['fg_titulo'], anchor='w').pack(fill='x')
            
            # Aposta e tipo
            aposta_info = f"{aposta['aposta']} - {aposta['tipo']}"
            tk.Label(info_frame, text=aposta_info, 
                    font=('Arial', 8), bg=self.cores['bg_secundario'], 
                    fg=self.cores['fg_normal'], anchor='w').pack(fill='x')
            
            # Odd e probabilidade
            odd_prob_text = f"ODD: {aposta.get('odd', 0):.2f} | Prob: {aposta.get('nossa_prob', 0):.1f}%"
            tk.Label(info_frame, text=odd_prob_text, 
                    font=('Arial', 8), bg=self.cores['bg_secundario'], 
                    fg=self.cores['fg_secundario'], anchor='w').pack(fill='x')
            
            # Botão adicionar individual
            btn_frame = tk.Frame(aposta_frame, bg=self.cores['bg_secundario'])
            btn_frame.pack(side='right', padx=4, pady=4)
            
            tk.Button(btn_frame, text="+ Add", 
                     font=('Arial', 8), bg='#3b82f6', fg='white',
                     command=lambda a=aposta: self.adicionar_aposta_individual(a, menu_window),
                     padx=6, pady=2).pack()
        
        # Botão adicionar bilhete completo
        btn_completo_frame = tk.Frame(card_frame, bg=self.cores['bg_card'])
        btn_completo_frame.pack(fill='x', padx=8, pady=8)
        
        tk.Button(btn_completo_frame, text=f"✅ Adicionar Completo (ODD: {odd_total:.2f}x)", 
                 font=('Arial', 10, 'bold'), bg=cor_bg, fg='white',
                 command=lambda: self.adicionar_bilhete_completo(tipo_bilhete, apostas, nome_bilhete, menu_window),
                 padx=15, pady=8).pack(fill='x')
    
    def adicionar_aposta_individual(self, aposta, menu_window):
        """Adiciona uma aposta individual à múltipla"""
        try:
            # Verificar se a aposta já está na múltipla
            for ap in self.apostas_multipla:
                if ap['jogo'] == aposta['jogo'] and ap['aposta'] == aposta['aposta']:
                    messagebox.showinfo("Aviso", "Esta aposta já está na múltipla!")
                    return
            
            # Adicionar aposta
            self.apostas_multipla.append({
                'jogo': aposta['jogo'],
                'aposta': aposta['aposta'],
                'tipo': aposta['tipo'],
                'odd': aposta['odd'],
                'nossa_prob': aposta.get('nossa_prob', aposta.get('prob_calculada', 0)),
                'prob_calculada': aposta.get('prob_calculada', aposta.get('nossa_prob', 0)),
                'prob_implicita': aposta.get('prob_implicita', 0),
                'match_id': aposta.get('match_id', ''),
                'liga': aposta.get('liga', ''),
                'horario': aposta.get('horario', '')
            })
            
            # Atualizar interface
            self.atualizar_multipla()
            
            # Mudar para aba de múltiplas
            self.notebook.select(4)
            
            messagebox.showinfo("Sucesso", f"Aposta adicionada!\n\n{aposta['jogo']}\n{aposta['aposta']}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar aposta: {str(e)}")
    
    def adicionar_bilhete_completo(self, tipo_bilhete, apostas, nome_bilhete, menu_window):
        """Adiciona todas as apostas de um bilhete à múltipla"""
        try:
            # Limpar múltipla atual
            self.apostas_multipla.clear()
            
            # Adicionar todas as apostas
            for aposta in apostas:
                self.apostas_multipla.append({
                    'jogo': aposta['jogo'],
                    'aposta': aposta['aposta'],
                    'tipo': aposta['tipo'],
                    'odd': aposta['odd'],
                    'nossa_prob': aposta.get('nossa_prob', aposta.get('prob_calculada', 0)),
                    'prob_calculada': aposta.get('prob_calculada', aposta.get('nossa_prob', 0)),
                    'prob_implicita': aposta.get('prob_implicita', 0),
                    'match_id': aposta.get('match_id', ''),
                    'liga': aposta.get('liga', ''),
                    'horario': aposta.get('horario', '')
                })
            
            # Atualizar interface
            self.atualizar_multipla()
            
            # Mudar para aba de múltiplas
            self.notebook.select(4)
            
            # Calcular odd total
            odd_total = 1.0
            for aposta in apostas:
                odd_total *= aposta.get('odd', 1.0)
            
            menu_window.destroy()
            
            messagebox.showinfo("Sucesso", 
                              f"{nome_bilhete} adicionado com sucesso!\n\n"
                              f"{len(apostas)} apostas adicionadas\n"
                              f"ODD Total: {odd_total:.2f}x")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar bilhete: {str(e)}")

    def criar_bilhete_personalizado(self, tipo_bilhete, menu_window):
        """Cria bilhete personalizado baseado no tipo especificado"""
        try:
            menu_window.destroy()  # Fechar menu
            
            # Mapear nomes dos bilhetes
            nomes_bilhetes = {
                'seguro_1': 'Bilhete Seguro 1',
                'seguro_2': 'Bilhete Seguro 2',
                'arriscado_1': 'Bilhete Arriscado 1',
                'arriscado_2': 'Bilhete Arriscado 2',
                'muito_arriscado_1': 'Bilhete Muito Arriscado 1',
                'muito_arriscado_2': 'Bilhete Muito Arriscado 2',
                'mega_sena_1': 'Bilhete Mega Sena 1',
                'mega_sena_2': 'Bilhete Mega Sena 2'
            }
            
            if tipo_bilhete not in nomes_bilhetes:
                messagebox.showerror("Erro", "Tipo de bilhete não encontrado")
                return
                
            nome_bilhete = nomes_bilhetes[tipo_bilhete]
            
            # Verificar se temos apostas hot disponíveis
            if not hasattr(self, 'apostas_hot') or not self.apostas_hot:
                messagebox.showwarning("Aviso", "Nenhuma aposta hot disponível. Carregue as apostas primeiro.")
                return
            
            # Filtrar apostas por tipo
            apostas_fortes = [a for a in self.apostas_hot if a.get('tipo', '').upper() == 'FORTE']
            apostas_moderadas = [a for a in self.apostas_hot if a.get('tipo', '').upper() == 'MODERADA']
            apostas_arriscadas = [a for a in self.apostas_hot if a.get('tipo', '').upper() == 'ARRISCADA']
            apostas_muito_arriscadas = [a for a in self.apostas_hot if a.get('tipo', '').upper() == 'MUITO_ARRISCADA']
            
            # Ordenar apostas por probabilidade (melhor para pior)
            apostas_fortes.sort(key=lambda x: x.get('prob_media', 0), reverse=True)
            apostas_moderadas.sort(key=lambda x: x.get('prob_media', 0), reverse=True)
            apostas_arriscadas.sort(key=lambda x: x.get('prob_media', 0), reverse=True)
            apostas_muito_arriscadas.sort(key=lambda x: x.get('prob_media', 0), reverse=True)
            
            # Usar a função obter_apostas_bilhete para montar o bilhete
            apostas_selecionadas = self.obter_apostas_bilhete(
                tipo_bilhete, apostas_fortes, apostas_moderadas, 
                apostas_arriscadas, apostas_muito_arriscadas
            )
            
            if not apostas_selecionadas:
                messagebox.showwarning("Aviso", f"Não há apostas suficientes para criar o {nome_bilhete}")
                return
            
            # Limpar múltipla atual e adicionar apostas selecionadas
            self.apostas_multipla.clear()
            
            for aposta in apostas_selecionadas:
                self.apostas_multipla.append({
                    'jogo': aposta['jogo'],
                    'aposta': aposta['aposta'],
                    'tipo': aposta['tipo'],
                    'odd': aposta['odd'],
                    'nossa_prob': aposta.get('nossa_prob', aposta.get('prob_calculada', 0)),
                    'prob_calculada': aposta.get('prob_calculada', aposta.get('nossa_prob', 0)),
                    'prob_implicita': aposta.get('prob_implicita', 0),
                    'match_id': aposta.get('match_id', ''),
                    'liga': aposta.get('liga', ''),
                    'horario': aposta.get('horario', '')
                })
            
            # Atualizar interface
            self.atualizar_multipla()
            
            # Mudar para aba de múltiplas
            self.notebook.select(4)  # Índice da aba múltiplas
            
            # Gerar lista dos jogos adicionados para a descrição com posições
            jogos_adicionados = []
            
            for aposta in apostas_selecionadas:
                tipo_aposta = aposta['tipo'].upper()
               
                jogo_nome = aposta['jogo']
                # Extrair apenas os nomes dos times (remover "vs")
                if " vs " in jogo_nome:
                    times = jogo_nome.split(" vs ")
                    jogo_resumido = f"{times[0][:20]}{'...' if len(times[0]) > 20 else ''} vs {times[1][:20]}{'...' if len(times[1]) > 20 else ''}"
                else:
                    jogo_resumido = jogo_nome[:40] + ("..." if len(jogo_nome) > 40 else "")
                
                jogos_adicionados.append(f"• {jogo_resumido} ({aposta['aposta']})")
            
            # Não limitar jogos, mostrar todos com suas posições
            jogos_texto = "\n".join(jogos_adicionados)
            
            messagebox.showinfo("Sucesso", 
                              f"{nome_bilhete} criado com sucesso!\n\n"
                              f"Jogos adicionados:\n{jogos_texto}")
                              
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar bilhete: {str(e)}")

    def obter_apostas_por_classificacao(self, tipo_classificacao):
        """Obtém apostas filtradas por classificação"""
        if not hasattr(self, 'apostas_hot') or not self.apostas_hot:
            return []
        
        apostas_classificadas = []

        for aposta in self.apostas_hot:
            classificacao = self.classificar_aposta_por_criterios(aposta)
            if classificacao == tipo_classificacao:
                apostas_classificadas.append(aposta)

        # Ordenar por apostas que tenham a maior diferença de gols esperados
        apostas_classificadas.sort(key=lambda x: x.get('prob_media', 0), reverse=True)
        return apostas_classificadas


def main():
    """Função principal"""
    root = tk.Tk()
    app = BetBoosterV2(root)
    
    # Configurar fechamento
    def on_closing():
        app.salvar_dados()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
