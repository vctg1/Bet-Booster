#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BET BOOSTER V2 - Sistema Completo de Análise de Apostas
Reestruturação completa com novas funcionalidades
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import math
from datetime import datetime, timedelta
import os
import sys
import threading
import time
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
        
        # API Integration
        self.api = RadarEsportivoAPI()
        
        # Mostrar tela de carregamento
        self.mostrar_tela_carregamento()
        
        # Configurar interface (será feito após carregamento)
        self.main_widgets_created = False
    
    def mostrar_tela_carregamento(self):
        """Mostra tela de carregamento inicial"""
        # Frame de carregamento
        self.loading_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.loading_frame.pack(fill='both', expand=True)
        
        # Logo/Título
        title_label = tk.Label(self.loading_frame, text="🎯 BET BOOSTER V2", 
                              font=('Arial', 24, 'bold'), fg='#1e40af', bg='#f0f0f0')
        title_label.pack(pady=(100, 20))
        
        subtitle_label = tk.Label(self.loading_frame, text="Sistema Avançado de Análise de Apostas", 
                                 font=('Arial', 14), fg='#374151', bg='#f0f0f0')
        subtitle_label.pack(pady=(0, 50))
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.loading_frame, 
                                          variable=self.progress_var, 
                                          maximum=100, 
                                          length=400, 
                                          mode='determinate')
        self.progress_bar.pack(pady=20)
        
        # Status do carregamento
        self.loading_status = tk.Label(self.loading_frame, text="Inicializando sistema...", 
                                      font=('Arial', 11), fg='#6b7280', bg='#f0f0f0')
        self.loading_status.pack(pady=10)
        
        # Iniciar carregamento
        self.root.after(500, self.iniciar_carregamento)
    
    def iniciar_carregamento(self):
        """Inicia o processo de carregamento"""
        threading.Thread(target=self.executar_carregamento, daemon=True).start()
    
    def executar_carregamento(self):
        """Executa o carregamento completo"""
        try:
            # Etapa 1: Carregar database
            self.atualizar_loading(10, "Carregando database de times...")
            self.carregar_dados()
            time.sleep(0.5)
            
            # Etapa 2: Configurar estilos
            self.atualizar_loading(20, "Configurando interface...")
            self.setup_styles()
            time.sleep(0.3)
            
            # Etapa 3: Buscar jogos de hoje
            self.atualizar_loading(30, "Buscando jogos de hoje...")
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            jogos_hoje = self.api.buscar_jogos_do_dia(data_hoje)
            print(f"✅ {len(jogos_hoje) if jogos_hoje else 0} jogos encontrados hoje")
            time.sleep(0.3)
            
            # Etapa 4: Buscar jogos de amanhã
            self.atualizar_loading(40, "Buscando jogos de amanhã...")
            data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            jogos_amanha = self.api.buscar_jogos_do_dia(data_amanha)
            print(f"✅ {len(jogos_amanha) if jogos_amanha else 0} jogos encontrados amanhã")
            time.sleep(0.3)
            
            # Etapa 5: Filtrar e preparar jogos para análise
            self.atualizar_loading(50, "Preparando jogos para análise...")
            jogos_validos_hoje = self.filtrar_jogos_validos(jogos_hoje or [])
            jogos_validos_amanha = jogos_amanha[:7] if jogos_amanha else []
            
            # Armazenar para uso posterior
            self.jogos_para_hot = {
                'hoje': jogos_validos_hoje[:8],
                'amanha': jogos_validos_amanha
            }
            total_jogos = len(self.jogos_para_hot['hoje']) + len(self.jogos_para_hot['amanha'])
            print(f"✅ {total_jogos} jogos selecionados para análise hot")
            time.sleep(0.5)
            
            # Etapa 6: CARREGAR E ANALISAR APOSTAS HOT COMPLETAMENTE
            self.atualizar_loading(60, "Analisando apostas hot de hoje...")
            apostas_hot_hoje = self.analisar_jogos_completo(self.jogos_para_hot['hoje'], 'Hoje')
            
            self.atualizar_loading(80, "Analisando apostas hot de amanhã...")
            apostas_hot_amanha = self.analisar_jogos_completo(self.jogos_para_hot['amanha'], 'Amanhã')
            
            # Combinar e ordenar apostas
            self.apostas_hot_carregadas = apostas_hot_hoje + apostas_hot_amanha
            self.apostas_hot_carregadas.sort(key=lambda x: (
                0 if x.get('periodo') == 'Hoje' else 1,
                -x['forca_recomendacao']
            ))
            
            print(f"✅ {len(self.apostas_hot_carregadas)} apostas hot analisadas e prontas")
            
            # Etapa 7: Finalizar
            self.atualizar_loading(100, "Finalizando inicialização...")
            time.sleep(0.5)
            
            # Criar interface principal
            self.root.after(100, self.finalizar_carregamento)
            
        except Exception as e:
            print(f"Erro no carregamento: {e}")
            self.apostas_hot_carregadas = []
            self.root.after(100, self.finalizar_carregamento)
    
    def filtrar_jogos_validos(self, jogos):
        """Filtra jogos de hoje que ainda não encerraram"""
        jogos_validos = []
        agora = datetime.now()
        
        for jogo in jogos:
            try:
                # Verificar se jogo é uma string (ID) ao invés de dicionário
                if isinstance(jogo, str):
                    # Se for apenas ID, considerá-lo válido
                    jogos_validos.append({'id': jogo})
                    continue
                
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
                                jogos_validos.append(jogo)
                        except:
                            # Se não conseguir parsear a data, incluir mesmo assim
                            jogos_validos.append(jogo)
                    else:
                        # Se não tem horário, incluir
                        jogos_validos.append(jogo)
                else:
                    # Se tem status mas não é válido, pular
                    continue
                    
            except Exception as e:
                print(f"Erro ao filtrar jogo: {e}")
                # Em caso de erro, incluir o jogo se for um dicionário válido
                if isinstance(jogo, dict) or isinstance(jogo, str):
                    if isinstance(jogo, str):
                        jogos_validos.append({'id': jogo})
                    else:
                        jogos_validos.append(jogo)
        
        return jogos_validos
    
    def analisar_jogos_completo(self, jogos, periodo):
        """Analisa completamente uma lista de jogos para apostas hot"""
        apostas_analisadas = []
        
        for i, jogo in enumerate(jogos):
            try:
                # Atualizar status de progresso
                progresso_base = 60 if periodo == 'Hoje' else 80
                progresso_atual = progresso_base + (i / len(jogos)) * 15  # 15% para cada período
                self.atualizar_loading(progresso_atual, f"Analisando {jogo.get('home_team', 'Time')} vs {jogo.get('away_team', 'Time')}...")
                
                jogo['periodo'] = periodo
                recomendacoes = self.processar_jogo_para_hot(jogo)
                apostas_analisadas.extend(recomendacoes)
                
                print(f"✅ {len(recomendacoes)} apostas encontradas para {jogo.get('home_team', '')} vs {jogo.get('away_team', '')}")
                
            except Exception as e:
                print(f"Erro ao analisar jogo {jogo.get('home_team', '')} vs {jogo.get('away_team', '')}: {e}")
                continue
        
        return apostas_analisadas
    
    def atualizar_loading(self, progresso, status):
        """Atualiza barra de progresso e status"""
        def update():
            self.progress_var.set(progresso)
            self.loading_status.config(text=status)
        
        self.root.after(0, update)
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
                apostas_hoje = len([a for a in self.apostas_hot_carregadas if a.get('periodo') == 'Hoje'])
                apostas_amanha = len([a for a in self.apostas_hot_carregadas if a.get('periodo') == 'Amanhã'])
                
                self.status_hot.config(
                    text=f"✅ {total_apostas} apostas hot carregadas ({apostas_hoje} hoje, {apostas_amanha} amanhã)", 
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
        style.configure('Hot.TLabel', foreground='orange', font=('Arial', 10, 'bold'))
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
        controles_frame = ttk.LabelFrame(self.tab_apostas_hot, text="Configurações", padding=10)
        controles_frame.pack(fill='x', padx=20, pady=10)
        
        buttons_frame = ttk.Frame(controles_frame)
        buttons_frame.pack(fill='x')
        
        ttk.Button(buttons_frame, text="📊 Configurar Filtros", 
                  command=self.configurar_filtros_hot).pack(side='left', padx=5)
        
        # Status
        self.status_hot = ttk.Label(controles_frame, text="Pronto para análise", style='Success.TLabel')
        self.status_hot.pack(pady=5)
        
        # Frame principal com scrollbar
        main_frame = ttk.Frame(self.tab_apostas_hot)
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.apostas_hot_frame = ttk.Frame(canvas)
        
        self.apostas_hot_frame.bind("<Configure>", 
                                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.apostas_hot_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
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
        self.entry_data = ttk.Entry(linha1, width=12)
        self.entry_data.pack(side='left', padx=(0, 10))
        self.entry_data.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        ttk.Button(linha1, text="🔍 Buscar Jogos", 
                  command=self.buscar_jogos_do_dia).pack(side='left', padx=5)
        ttk.Button(linha1, text="🔄 Atualizar Status", 
                  command=self.atualizar_status_jogos).pack(side='left', padx=5)
        
        # Linha 2: Opções de análise
        linha2 = ttk.Frame(controles_frame)
        linha2.pack(fill='x', pady=5)
        
        ttk.Label(linha2, text="Modo:").pack(side='left', padx=(0, 5))
        self.modo_analise = ttk.Combobox(linha2, values=["Dados Gerais", "Casa/Fora"], 
                                        state="readonly", width=15)
        self.modo_analise.pack(side='left', padx=(0, 10))
        self.modo_analise.set("Dados Gerais")
        
        # Status
        self.status_jogos = ttk.Label(controles_frame, text="Pronto", style='Success.TLabel')
        self.status_jogos.pack(pady=5)
        
        # Frame da lista de jogos
        lista_frame = ttk.LabelFrame(self.tab_jogos_dia, text="Lista de Jogos", padding=10)
        lista_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Treeview para jogos
        columns = ('Horário', 'Status', 'Casa', 'Visitante', 'Liga', 'Odds H/E/A')
        self.tree_jogos = ttk.Treeview(lista_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_jogos.heading(col, text=col)
            if col == 'Horário':
                self.tree_jogos.column(col, width=80, anchor='center')
            elif col == 'Status':
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
        self.tree_jogos.bind('<Double-1>', self.on_jogo_selecionado)
        
        # Frame de ações
        acoes_frame = ttk.LabelFrame(self.tab_jogos_dia, text="Ações do Jogo Selecionado", padding=10)
        acoes_frame.pack(fill='x', padx=20, pady=10)
        
        # Botões de ação
        acoes_buttons = ttk.Frame(acoes_frame)
        acoes_buttons.pack(fill='x')
        
        ttk.Button(acoes_buttons, text="📊 Calcular Probabilidades", 
                  command=self.calcular_prob_jogo_selecionado).pack(side='left', padx=5)
        ttk.Button(acoes_buttons, text="💰 Aposta Simples", 
                  command=self.aposta_simples_jogo).pack(side='left', padx=5)
        ttk.Button(acoes_buttons, text="📋 Adicionar à Múltipla", 
                  command=self.adicionar_multipla_jogo).pack(side='left', padx=5)
        ttk.Button(acoes_buttons, text="⚡ Editar Jogo Ao Vivo", 
                  command=self.editar_jogo_ao_vivo).pack(side='left', padx=5)
    
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
        
        # Frame de estatísticas casa
        stats_casa_frame = ttk.LabelFrame(cadastro_frame, text="Estatísticas em Casa", padding=10)
        stats_casa_frame.pack(fill='x', pady=10)
        
        # Linha casa 1: Gols
        linha_casa1 = ttk.Frame(stats_casa_frame)
        linha_casa1.pack(fill='x', pady=2)
        
        ttk.Label(linha_casa1, text="Gols Marcados Casa:").pack(side='left')
        self.entry_gols_marcados_casa = ttk.Entry(linha_casa1, width=10)
        self.entry_gols_marcados_casa.pack(side='left', padx=(10, 20))
        
        ttk.Label(linha_casa1, text="Gols Sofridos Casa:").pack(side='left')
        self.entry_gols_sofridos_casa = ttk.Entry(linha_casa1, width=10)
        self.entry_gols_sofridos_casa.pack(side='left', padx=10)
        
        # Frame de estatísticas fora
        stats_fora_frame = ttk.LabelFrame(cadastro_frame, text="Estatísticas Fora de Casa", padding=10)
        stats_fora_frame.pack(fill='x', pady=10)
        
        # Linha fora 1: Gols
        linha_fora1 = ttk.Frame(stats_fora_frame)
        linha_fora1.pack(fill='x', pady=2)
        
        ttk.Label(linha_fora1, text="Gols Marcados Fora:").pack(side='left')
        self.entry_gols_marcados_fora = ttk.Entry(linha_fora1, width=10)
        self.entry_gols_marcados_fora.pack(side='left', padx=(10, 20))
        
        ttk.Label(linha_fora1, text="Gols Sofridos Fora:").pack(side='left')
        self.entry_gols_sofridos_fora = ttk.Entry(linha_fora1, width=10)
        self.entry_gols_sofridos_fora.pack(side='left', padx=10)
        
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
        self.combo_modo_analise = ttk.Combobox(linha_config, values=["Dados Gerais", "Casa/Fora"], 
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
        
        self.texto_analise = scrolledtext.ScrolledText(resultado_frame, height=25, width=80)
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
                
                gols_marcados_casa = float(self.entry_gols_marcados_casa.get() or "0")
                gols_sofridos_casa = float(self.entry_gols_sofridos_casa.get() or "0")
                gols_marcados_fora = float(self.entry_gols_marcados_fora.get() or "0")
                gols_sofridos_fora = float(self.entry_gols_sofridos_fora.get() or "0")
                
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
                'gols_marcados_casa': gols_marcados_casa,
                'gols_sofridos_casa': gols_sofridos_casa,
                'gols_marcados_fora': gols_marcados_fora,
                'gols_sofridos_fora': gols_sofridos_fora,
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
            self.entry_gols_marcados_casa, self.entry_gols_sofridos_casa,
            self.entry_gols_marcados_fora, self.entry_gols_sofridos_fora,
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

🏠 EM CASA:
⚽ Gols Marcados: {dados.get('gols_marcados_casa', 0):.2f}
🥅 Gols Sofridos: {dados.get('gols_sofridos_casa', 0):.2f}

✈️ FORA DE CASA:
⚽ Gols Marcados: {dados.get('gols_marcados_fora', 0):.2f}
🥅 Gols Sofridos: {dados.get('gols_sofridos_fora', 0):.2f}

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
        
        # Selecionar dados baseado no modo
        if modo == "Casa/Fora":
            gols_casa = dados_casa.get('gols_marcados_casa', dados_casa.get('gols_marcados', 0))
            gols_sofridos_casa = dados_casa.get('gols_sofridos_casa', dados_casa.get('gols_sofridos', 0))
            gols_visitante = dados_visitante.get('gols_marcados_fora', dados_visitante.get('gols_marcados', 0))
            gols_sofridos_visitante = dados_visitante.get('gols_sofridos_fora', dados_visitante.get('gols_sofridos', 0))
            modo_texto = "DADOS CASA/FORA"
        else:
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
📊 Over 1.5 gols: {probabilidades['over_15']:.1f}%
📊 Under 1.5 gols: {probabilidades['under_15']:.1f}%
📊 Over 2.5 gols: {probabilidades['over_25']:.1f}%
📊 Under 2.5 gols: {probabilidades['under_25']:.1f}%
📊 Over 3.5 gols: {probabilidades['over_35']:.1f}%
📊 Under 3.5 gols: {probabilidades['under_35']:.1f}%

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
        elif probabilidades['empate'] == maior_prob and maior_prob >= 35:
            recomendacoes += f"🟢 FORTE: Empate ({maior_prob:.1f}%)\n"
        
        # Recomendações para gols
        if probabilidades['over_25'] >= 60:
            recomendacoes += f"🟢 FORTE: Over 2.5 gols ({probabilidades['over_25']:.1f}%)\n"
        elif probabilidades['under_25'] >= 60:
            recomendacoes += f"🟢 FORTE: Under 2.5 gols ({probabilidades['under_25']:.1f}%)\n"
        
        if probabilidades['over_15'] >= 75:
            recomendacoes += f"🟡 ARRISCADA: Over 1.5 gols ({probabilidades['over_15']:.1f}%)\n"
        
        if probabilidades['over_35'] >= 30:
            recomendacoes += f"🟡 ARRISCADA: Over 3.5 gols ({probabilidades['over_35']:.1f}%)\n"
        
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
    
    def create_multiplas_tab(self):
        """Nova aba: Gestão de Múltiplas"""
        self.tab_multiplas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_multiplas, text="🎯 Múltiplas")
        
        ttk.Label(self.tab_multiplas, text="🎯 GESTÃO DE APOSTAS MÚLTIPLAS", 
                 style='Title.TLabel').pack(pady=10)
        
        # Frame da múltipla atual
        multipla_frame = ttk.LabelFrame(self.tab_multiplas, text="Múltipla Atual", padding=15)
        multipla_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Lista de apostas na múltipla
        columns_multipla = ('Jogo', 'Aposta', 'Odd', 'Prob. Implícita', 'Status')
        self.tree_multipla = ttk.Treeview(multipla_frame, columns=columns_multipla, show='headings', height=10)
        
        for col in columns_multipla:
            self.tree_multipla.heading(col, text=col)
            self.tree_multipla.column(col, width=150)
        
        self.tree_multipla.pack(fill='both', expand=True)
        
        # Informações da múltipla
        info_frame = ttk.Frame(multipla_frame)
        info_frame.pack(fill='x', pady=10)
        
        self.label_odd_total = ttk.Label(info_frame, text="Odd Total: 1.00", style='Subtitle.TLabel')
        self.label_odd_total.pack(side='left', padx=10)
        
        self.label_prob_total = ttk.Label(info_frame, text="Probabilidade: 100%", style='Subtitle.TLabel')
        self.label_prob_total.pack(side='left', padx=10)
        
        # Botões de controle
        controle_frame = ttk.Frame(multipla_frame)
        controle_frame.pack(fill='x', pady=10)
        
        ttk.Button(controle_frame, text="🗑️ Limpar Múltipla", 
                  command=self.limpar_multipla).pack(side='left', padx=5)
        ttk.Button(controle_frame, text="💾 Salvar Múltipla", 
                  command=self.salvar_multipla).pack(side='left', padx=5)
        ttk.Button(controle_frame, text="📊 Calcular Retorno", 
                  command=self.calcular_retorno_multipla).pack(side='left', padx=5)
    
    # Métodos para Apostas Hot
    def auto_carregar_apostas_hot(self):
        """Carrega apostas hot apenas se não foram carregadas na inicialização"""
        if hasattr(self, 'apostas_hot_carregadas') and self.apostas_hot_carregadas:
            # Já foram carregadas, apenas exibir
            self.exibir_apostas_hot_prontas()
        else:
            # Carregar pela primeira vez
            threading.Thread(target=self.carregar_apostas_hot, daemon=True).start()
    
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
            
            # Ordenar por força da recomendação (hoje primeiro)
            apostas_recomendadas.sort(key=lambda x: (
                0 if x.get('periodo') == 'Hoje' else 1,  # Hoje primeiro
                -x['forca_recomendacao']  # Depois por força
            ))
            
            # Exibir apostas hot
            self.exibir_apostas_hot(apostas_recomendadas)
            
            self.status_hot.config(text=f"✅ {len(apostas_recomendadas)} apostas analisadas (Hoje e Amanhã)", 
                                 style='Success.TLabel')
            
        except Exception as e:
            self.status_hot.config(text=f"❌ Erro: {str(e)}", style='Warning.TLabel')
    
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
            
            # Calcular probabilidades
            modo = self.modo_analise.get() if hasattr(self, 'modo_analise') else "detalhado"
            probabilidades = self.calcular_probabilidades_jogo(stats, modo)
            
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
            odds = odds_detalhadas['odds']
            
            # 1. Analisar Resultado Final (1X2)
            if 'resultFt' in odds:
                result_odds = odds['resultFt']
                
                # Calcular probabilidades implícitas
                prob_casa_implicita = 1 / result_odds['home'] * 100
                prob_empate_implicita = 1 / result_odds['draw'] * 100
                prob_fora_implicita = 1 / result_odds['away'] * 100
                
                # Comparar com nossas probabilidades calculadas
                prob_casa_calc = probabilidades.get('vitoria_casa', 0)
                prob_empate_calc = probabilidades.get('empate', 0)
                prob_fora_calc = probabilidades.get('vitoria_visitante', 0)
                
                # Identificar value bets
                value_casa = (prob_casa_calc / prob_casa_implicita) if prob_casa_implicita > 0 else 0
                value_empate = (prob_empate_calc / prob_empate_implicita) if prob_empate_implicita > 0 else 0
                value_fora = (prob_fora_calc / prob_fora_implicita) if prob_fora_implicita > 0 else 0
                
                # Recomendações baseadas nos critérios
                apostas_resultado = [
                    ('Vitória Casa', value_casa, prob_casa_calc, prob_casa_implicita, result_odds['home']),
                    ('Empate', value_empate, prob_empate_calc, prob_empate_implicita, result_odds['draw']),
                    ('Vitória Fora', value_fora, prob_fora_calc, prob_fora_implicita, result_odds['away'])
                ]
                
                for aposta, value, prob_calc, prob_impl, odd in apostas_resultado:
                    # Converter value para porcentagem
                    value_percent = (value - 1) * 100
                    
                    # Aplicar regras para apostas de vencedor:
                    # Forte: value >= 5% E probabilidade IMPLÍCITA >= 35%
                    # Arriscada: value >= 15% E probabilidade IMPLÍCITA < 35%
                    tipo_recomendacao = None
                    
                    if value_percent >= 5 and prob_impl >= 35:
                        tipo_recomendacao = "FORTE"
                    elif value_percent >= 15 and prob_impl < 35:
                        tipo_recomendacao = "ARRISCADA"
                    
                    if tipo_recomendacao and prob_calc >= 15:  # Mínimo de confiança na nossa probabilidade
                        
                        forca = value * (prob_calc / 100)  # Força baseada em value e probabilidade
                        
                        recomendacoes.append({
                            'jogo': f"{odds_detalhadas['home_team']} vs {odds_detalhadas['away_team']}",
                            'aposta': aposta,
                            'tipo': tipo_recomendacao,
                            'odd': odd,
                            'value': value,
                            'value_percent': value_percent,
                            'prob_calculada': prob_calc,
                            'prob_implicita': prob_impl,
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
                
                # Probabilidades implícitas
                prob_over25_impl = 1 / gols_odds['over'] * 100
                prob_under25_impl = 1 / gols_odds['under'] * 100
                
                # Value bets
                value_over = (prob_over25_calc / prob_over25_impl) if prob_over25_impl > 0 else 0
                value_under = (prob_under25_calc / prob_under25_impl) if prob_under25_impl > 0 else 0
                
                apostas_gols = [
                    ('Over 2.5 gols', value_over, prob_over25_calc, prob_over25_impl, gols_odds['over']),
                    ('Under 2.5 gols', value_under, prob_under25_calc, prob_under25_impl, gols_odds['under'])
                ]
                
                for aposta, value, prob_calc, prob_impl, odd in apostas_gols:
                    # Converter value para porcentagem
                    value_percent = (value - 1) * 100
                    
                    # Aplicar regras para apostas Over/Under:
                    # Forte: probabilidade IMPLÍCITA >= 35% E Value bet >= 5%
                    # Arriscada: probabilidade IMPLÍCITA < 35% E Value bet >= 15%
                    tipo_recomendacao = None
                    
                    if prob_impl >= 35 and value_percent >= 5:
                        tipo_recomendacao = "FORTE"
                    elif prob_impl < 35 and value_percent >= 15:
                        tipo_recomendacao = "ARRISCADA"
                    
                    if tipo_recomendacao and prob_calc >= 15:  # Mínimo de confiança na nossa probabilidade
                        
                        forca = value * (prob_calc / 100)
                        
                        recomendacoes.append({
                            'jogo': f"{odds_detalhadas['home_team']} vs {odds_detalhadas['away_team']}",
                            'aposta': aposta,
                            'tipo': tipo_recomendacao,
                            'odd': odd,
                            'value': value,
                            'value_percent': value_percent,
                            'prob_calculada': prob_calc,
                            'prob_implicita': prob_impl,
                            'forca_recomendacao': forca,
                            'match_id': odds_detalhadas['match_id'],
                            'liga': odds_detalhadas['league'],
                            'horario': self.formatar_horario(odds_detalhadas['start_time'])
                        })
            
        except Exception as e:
            print(f"Erro ao analisar recomendações: {e}")
        
        return recomendacoes
    
    def exibir_apostas_hot(self, apostas):
        """Exibe as apostas hot na interface"""
        # Limpar frame atual
        for widget in self.apostas_hot_frame.winfo_children():
            widget.destroy()
        
        if not apostas:
            ttk.Label(self.apostas_hot_frame, text="Nenhuma aposta recomendada encontrada", 
                     style='Warning.TLabel').pack(pady=20)
            return
        
        # Separar por tipo
        apostas_fortes = [a for a in apostas if a['tipo'] == 'FORTE']
        apostas_arriscadas = [a for a in apostas if a['tipo'] == 'ARRISCADA']
        
        # Exibir apostas fortes primeiro
        if apostas_fortes:
            titulo_forte = ttk.Label(self.apostas_hot_frame, text="🟢 APOSTAS FORTES", 
                                   style='Success.TLabel', font=('Arial', 14, 'bold'))
            titulo_forte.pack(pady=10)
            
            for aposta in apostas_fortes:
                self.criar_card_aposta(aposta)
        
        # Linha separadora
        if apostas_fortes and apostas_arriscadas:
            separator = ttk.Separator(self.apostas_hot_frame, orient='horizontal')
            separator.pack(fill='x', pady=20)
        
        # Exibir apostas arriscadas
        if apostas_arriscadas:
            titulo_arriscada = ttk.Label(self.apostas_hot_frame, text="🟡 APOSTAS ARRISCADAS", 
                                       style='Hot.TLabel', font=('Arial', 14, 'bold'))
            titulo_arriscada.pack(pady=10)
            
            for aposta in apostas_arriscadas:
                self.criar_card_aposta(aposta)
    
    def criar_card_aposta(self, aposta):
        """Cria um card visual para uma aposta recomendada"""
        # Frame do card
        card_frame = ttk.LabelFrame(self.apostas_hot_frame, text="", padding=15)
        card_frame.pack(fill='x', pady=5, padx=10)
        
        # Linha 1: Jogo e horário
        linha1 = ttk.Frame(card_frame)
        linha1.pack(fill='x')
        
        jogo_label = ttk.Label(linha1, text=aposta['jogo'], 
                              style='Subtitle.TLabel', font=('Arial', 12, 'bold'))
        jogo_label.pack(side='left')
        
        # Mostrar período (Hoje/Amanhã)
        periodo = aposta.get('periodo', 'Hoje')
        periodo_color = 'red' if periodo == 'Hoje' else 'blue'
        periodo_label = ttk.Label(linha1, text=f"📅 {periodo}", 
                                 font=('Arial', 10, 'bold'))
        periodo_label.pack(side='right')
        
        # Configurar cor do período
        if periodo == 'Hoje':
            periodo_label.configure(foreground='red')
        else:
            periodo_label.configure(foreground='blue')
        
        horario_label = ttk.Label(linha1, text=f"⏰ {aposta['horario']}", 
                                 style='Success.TLabel')
        horario_label.pack(side='right')
        
        # Linha 2: Liga
        liga_label = ttk.Label(card_frame, text=f"🏆 {aposta['liga']}", 
                              font=('Arial', 9))
        liga_label.pack(anchor='w')
        
        # Linha 3: Aposta e tipo
        linha3 = ttk.Frame(card_frame)
        linha3.pack(fill='x', pady=5)
        
        tipo_color = 'Success.TLabel' if aposta['tipo'] == 'FORTE' else 'Hot.TLabel'
        tipo_emoji = '🟢' if aposta['tipo'] == 'FORTE' else '🟡'
        
        aposta_label = ttk.Label(linha3, text=f"{tipo_emoji} {aposta['aposta']}", 
                                style=tipo_color, font=('Arial', 11, 'bold'))
        aposta_label.pack(side='left')
        
        odd_label = ttk.Label(linha3, text=f"Odd: {aposta['odd']:.2f}", 
                             style='Subtitle.TLabel')
        odd_label.pack(side='right')
        
        # Linha 4: Probabilidades e value
        linha4 = ttk.Frame(card_frame)
        linha4.pack(fill='x')
        
        prob_calc_label = ttk.Label(linha4, text=f"📊 Nossa prob: {aposta['prob_calculada']:.1f}%")
        prob_calc_label.pack(side='left')
        
        prob_impl_label = ttk.Label(linha4, text=f"🎯 Prob. implícita: {aposta['prob_implicita']:.1f}%")
        prob_impl_label.pack(side='left', padx=20)
        
        value_label = ttk.Label(linha4, text=f"💎 Value: {((aposta['value'] - 1) * 100):.1f}%", 
                               style='Success.TLabel')
        value_label.pack(side='right')
        
        # Botões de ação
        acoes_frame = ttk.Frame(card_frame)
        acoes_frame.pack(fill='x', pady=10)
        
        ttk.Button(acoes_frame, text="📋 Adicionar à Múltipla", 
                  command=lambda: self.adicionar_aposta_multipla(aposta)).pack(side='left', padx=5)
        ttk.Button(acoes_frame, text="📊 Ver Análise Completa", 
                  command=lambda: self.ver_analise_completa(aposta)).pack(side='left', padx=5)
    
    # Métodos para Jogos do Dia
    def buscar_jogos_do_dia(self):
        """Busca jogos do dia selecionado"""
        try:
            self.status_jogos.config(text="🔄 Buscando jogos...", style='Warning.TLabel')
            self.root.update()
            
            # Converter data do formato DD/MM/YYYY para YYYY-MM-DD
            data_input = self.entry_data.get()
            data_obj = datetime.strptime(data_input, '%d/%m/%Y')
            data_api = data_obj.strftime('%Y-%m-%d')
            
            # Buscar jogos
            jogos = self.api.buscar_jogos_do_dia(data_api)
            
            if not jogos:
                self.status_jogos.config(text="❌ Nenhum jogo encontrado", style='Warning.TLabel')
                return
            
            # Buscar odds para cada jogo
            self.jogos_do_dia = []
            
            for jogo in jogos:
                try:
                    odds_detalhadas = self.buscar_odds_detalhadas(jogo['id'])
                    if odds_detalhadas:
                        jogo_completo = {**jogo, **odds_detalhadas}
                        # Determinar status do jogo
                        jogo_completo['status_calculado'] = self.determinar_status_jogo(odds_detalhadas['start_time'])
                        self.jogos_do_dia.append(jogo_completo)
                    else:
                        jogo['odds'] = None
                        jogo['status_calculado'] = self.determinar_status_jogo('')
                        self.jogos_do_dia.append(jogo)
                except Exception as e:
                    print(f"Erro ao processar jogo: {e}")
                    jogo['odds'] = None
                    jogo['status_calculado'] = 'Agendado'
                    self.jogos_do_dia.append(jogo)
            
            # Atualizar lista visual
            self.atualizar_lista_jogos()
            
            self.status_jogos.config(text=f"✅ {len(self.jogos_do_dia)} jogos carregados", 
                                   style='Success.TLabel')
            
        except Exception as e:
            self.status_jogos.config(text=f"❌ Erro: {str(e)}", style='Warning.TLabel')
    
    def determinar_status_jogo(self, start_time):
        """Determina o status atual do jogo baseado no horário"""
        if not start_time:
            return "Agendado"
        
        try:
            # Converter para datetime (assumindo UTC e ajustando para GMT-3)
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            start_dt_local = start_dt - timedelta(hours=3)  # Ajustar para GMT-3
            
            agora = datetime.now()
            
            if agora < start_dt_local:
                return "Agendado"
            elif agora >= start_dt_local and agora <= start_dt_local + timedelta(minutes=120):
                return "🔴 AO VIVO"
            else:
                return "Encerrado"
                
        except Exception:
            return "Agendado"
    
    def atualizar_lista_jogos(self):
        """Atualiza a lista visual de jogos"""
        # Limpar árvore
        for item in self.tree_jogos.get_children():
            self.tree_jogos.delete(item)
        
        # Adicionar jogos
        for jogo in self.jogos_do_dia:
            horario = self.formatar_horario(jogo.get('start_time', ''))
            status = jogo.get('status_calculado', 'Agendado')
            casa = jogo.get('home_team', jogo.get('time_casa', ''))
            visitante = jogo.get('away_team', jogo.get('time_visitante', ''))
            liga = jogo.get('league', jogo.get('liga', ''))
            
            # Formatear odds
            odds_text = "N/A"
            if jogo.get('odds') and 'resultFt' in jogo['odds']:
                result_odds = jogo['odds']['resultFt']
                odds_text = f"{result_odds['home']:.2f} / {result_odds['draw']:.2f} / {result_odds['away']:.2f}"
            
            # Inserir na árvore
            item_id = self.tree_jogos.insert('', 'end', values=(
                horario, status, casa, visitante, liga, odds_text
            ))
            
            # Colorir linhas de jogos ao vivo
            if "AO VIVO" in status:
                self.tree_jogos.set(item_id, 'Status', status)
    
    def atualizar_status_jogos(self):
        """Atualiza o status de todos os jogos carregados"""
        if not self.jogos_do_dia:
            return
        
        for jogo in self.jogos_do_dia:
            jogo['status_calculado'] = self.determinar_status_jogo(jogo.get('start_time', ''))
        
        self.atualizar_lista_jogos()
        self.status_jogos.config(text="✅ Status atualizado", style='Success.TLabel')
    
    def on_jogo_selecionado(self, event):
        """Callback quando um jogo é selecionado"""
        selection = self.tree_jogos.selection()
        if not selection:
            return
        
        # Obter índice do jogo selecionado
        item = self.tree_jogos.item(selection[0])
        values = item['values']
        
        # Encontrar jogo correspondente
        casa = values[2]
        visitante = values[3]
        
        for i, jogo in enumerate(self.jogos_do_dia):
            jogo_casa = jogo.get('home_team', jogo.get('time_casa', ''))
            jogo_visitante = jogo.get('away_team', jogo.get('time_visitante', ''))
            
            if jogo_casa == casa and jogo_visitante == visitante:
                self.jogo_selecionado_index = i
                break
    
    def calcular_prob_jogo_selecionado(self):
        """Calcula probabilidades do jogo selecionado"""
        if not hasattr(self, 'jogo_selecionado_index'):
            messagebox.showwarning("Aviso", "Selecione um jogo primeiro")
            return
        
        jogo = self.jogos_do_dia[self.jogo_selecionado_index]
        
        # Implementar cálculo de probabilidades
        # (será adaptado dos métodos existentes)
        messagebox.showinfo("Info", f"Calculando probabilidades para {jogo.get('home_team', '')} vs {jogo.get('away_team', '')}")
    
    # Métodos auxiliares
    def formatar_horario(self, start_time):
        """Formata horário de UTC para local"""
        if not start_time:
            return ""
        
        try:
            dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            dt_local = dt - timedelta(hours=3)  # GMT-3
            return dt_local.strftime('%H:%M')
        except:
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
    
    def calcular_probabilidades_jogo(self, stats, modo):
        """Calcula probabilidades de um jogo baseado nas estatísticas"""
        # Implementação será adaptada dos métodos existentes
        # Por agora, retorna valores de exemplo
        return {
            'vitoria_casa': 40.0,
            'empate': 30.0,
            'vitoria_visitante': 30.0,
            'gols_esperados_total': 2.5
        }
    
    def configurar_filtros_hot(self):
        """Configura filtros para apostas hot"""
        messagebox.showinfo("Info", "Funcionalidade de filtros será implementada")
    
    def adicionar_aposta_multipla(self, aposta):
        """Adiciona aposta à múltipla"""
        self.apostas_multipla.append(aposta)
        self.atualizar_multipla()
        messagebox.showinfo("Sucesso", f"Aposta adicionada à múltipla: {aposta['aposta']}")
    
    def ver_analise_completa(self, aposta):
        """Mostra análise completa de uma aposta"""
        messagebox.showinfo("Análise", f"Análise completa de: {aposta['aposta']}")
    
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
                f"{aposta['prob_implicita']:.1f}%",
                aposta['tipo']
            ))
            odd_total *= aposta['odd']
        
        # Atualizar labels
        prob_total = (1 / odd_total * 100) if odd_total > 0 else 0
        self.label_odd_total.config(text=f"Odd Total: {odd_total:.2f}")
        self.label_prob_total.config(text=f"Probabilidade: {prob_total:.1f}%")
    
    def limpar_multipla(self):
        """Limpa a múltipla atual"""
        self.apostas_multipla.clear()
        self.atualizar_multipla()
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
        window.geometry("500x600")
        window.transient(self.root)
        window.grab_set()
        
        # Título
        ttk.Label(window, text="📊 CÁLCULO DE RETORNO - MÚLTIPLA", 
                 style='Title.TLabel').pack(pady=10)
        
        # Resumo da múltipla
        resumo_frame = ttk.LabelFrame(window, text="Resumo da Múltipla", padding=15)
        resumo_frame.pack(fill='x', padx=20, pady=10)
        
        # Calcular odd total
        odd_total = 1.0
        for aposta in self.apostas_multipla:
            odd_total *= aposta['odd']
        
        prob_total = (1 / odd_total * 100) if odd_total > 0 else 0
        
        ttk.Label(resumo_frame, text=f"📋 Apostas: {len(self.apostas_multipla)}", 
                 style='Subtitle.TLabel').pack(anchor='w')
        ttk.Label(resumo_frame, text=f"🎯 Odd Total: {odd_total:.2f}", 
                 style='Subtitle.TLabel').pack(anchor='w')
        ttk.Label(resumo_frame, text=f"📊 Probabilidade: {prob_total:.1f}%", 
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
        
        resultado_text = scrolledtext.ScrolledText(resultado_frame, height=15, width=50)
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
                    relatorio += f"""
{i}. {aposta['jogo']}
   💰 Aposta: {aposta['aposta']}
   🎯 Odd: {aposta['odd']:.2f}
   📊 Prob. Implícita: {aposta['prob_implicita']:.1f}%
"""
                
                relatorio += f"""
═══════════════════════════════════════
📊 CÁLCULOS FINANCEIROS:
═══════════════════════════════════════

💵 Valor Apostado: R$ {valor:.2f}
🎯 Odd Total: {odd_total:.2f}
📊 Probabilidade Total: {prob_total:.1f}%

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
    def calcular_prob_jogo_selecionado(self):
        """Calcula probabilidades do jogo selecionado"""
        if not hasattr(self, 'jogo_selecionado_index'):
            messagebox.showwarning("Aviso", "Selecione um jogo primeiro")
            return
        
        jogo = self.jogos_do_dia[self.jogo_selecionado_index]
        
        try:
            # Buscar estatísticas
            stats = self.api.buscar_estatisticas_detalhadas_time(jogo['id'])
            if not stats:
                messagebox.showerror("Erro", "Não foi possível obter estatísticas")
                return
            
            # Calcular probabilidades
            probabilidades = self.calcular_probabilidades_completas(stats, self.modo_analise.get())
            
            # Exibir resultado
            casa = jogo.get('home_team', jogo.get('time_casa', ''))
            visitante = jogo.get('away_team', jogo.get('time_visitante', ''))
            
            resultado = f"""
🎲 PROBABILIDADES CALCULADAS
═══════════════════════════════════════

🏠 {casa} vs ✈️ {visitante}

📊 RESULTADOS:
🏠 Vitória Casa: {probabilidades['vitoria_casa']:.1f}%
🤝 Empate: {probabilidades['empate']:.1f}%
✈️ Vitória Visitante: {probabilidades['vitoria_visitante']:.1f}%

⚽ GOLS ESPERADOS:
🏠 Casa: {probabilidades['gols_esperados_casa']:.2f}
✈️ Visitante: {probabilidades['gols_esperados_visitante']:.2f}
🎯 Total: {probabilidades['gols_esperados_total']:.2f}

📈 MERCADOS DE GOLS:
Over 2.5: {self.calcular_prob_over_under(probabilidades['gols_esperados_total'], 2.5, 'over'):.1f}%
Under 2.5: {self.calcular_prob_over_under(probabilidades['gols_esperados_total'], 2.5, 'under'):.1f}%
"""
            
            messagebox.showinfo("Probabilidades", resultado)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular probabilidades: {str(e)}")
    
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
            print(f"💾 Database salvo: {len(self.times_database)} times")
        except Exception as e:
            print(f"❌ Erro ao salvar dados: {e}")
    
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
    
    def editar_jogo_ao_vivo(self):
        """Edita informações de jogo ao vivo"""
        if not hasattr(self, 'jogo_selecionado_index'):
            messagebox.showwarning("Aviso", "Selecione um jogo primeiro")
            return
        
        jogo = self.jogos_do_dia[self.jogo_selecionado_index]
        
        if jogo.get('status_calculado') != "🔴 AO VIVO":
            messagebox.showwarning("Aviso", "Este jogo não está ao vivo")
            return
        
        # Abrir janela de edição ao vivo
        self.abrir_janela_edicao_ao_vivo(jogo)
    
    def abrir_janela_aposta_simples(self, jogo):
        """Abre janela para calcular aposta simples"""
        window = tk.Toplevel(self.root)
        window.title("💰 Aposta Simples")
        window.geometry("500x600")
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
        ttk.Label(aposta_frame, text="Tipo de Aposta:").pack(anchor='w')
        tipo_aposta = ttk.Combobox(aposta_frame, values=[
            "Vitória Casa", "Empate", "Vitória Visitante",
            "Over 2.5 gols", "Under 2.5 gols", "Ambos Marcam",
            "Over 1.5 gols", "Under 1.5 gols"
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
        
        resultado_text = scrolledtext.ScrolledText(resultado_frame, height=10, width=50)
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
        window.geometry("400x400")
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
                    (f"Vitória {casa}", result_odds['home'], 'Vitória Casa'),
                    ("Empate", result_odds['draw'], 'Empate'),
                    (f"Vitória {visitante}", result_odds['away'], 'Vitória Visitante')
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
                    ("Over 2.5 gols", gols_odds['over'], 'Over 2.5'),
                    ("Under 2.5 gols", gols_odds['under'], 'Under 2.5')
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
        window.geometry("400x500")
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
        
        # Calcular probabilidade implícita
        prob_implicita = (1 / odd * 100) if odd > 0 else 0
        
        # Determinar se é arriscada (seria necessário comparar com outras odds)
        tipo_recomendacao = "FORTE"  # Simplificado por agora
        
        aposta_detalhada = {
            'jogo': f"{casa} vs {visitante}",
            'aposta': tipo_aposta,
            'tipo': tipo_recomendacao,
            'odd': odd,
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
        """Calcula probabilidades completas baseado nas estatísticas"""
        try:
            if modo == "Casa/Fora":
                # Usar estatísticas específicas de casa/fora
                gols_casa = stats['time_casa']['casa']['gols_marcados']
                gols_sofridos_casa = stats['time_casa']['casa']['gols_sofridos']
                gols_visitante = stats['time_visitante']['fora']['gols_marcados']
                gols_sofridos_visitante = stats['time_visitante']['fora']['gols_sofridos']
            else:
                # Usar estatísticas gerais
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
            
            return {
                'vitoria_casa': prob_vitoria_casa,
                'empate': prob_empate,
                'vitoria_visitante': prob_vitoria_visitante,
                'gols_esperados_casa': gols_esperados_casa,
                'gols_esperados_visitante': gols_esperados_visitante,
                'gols_esperados_total': gols_esperados_casa + gols_esperados_visitante
            }
            
        except Exception as e:
            print(f"Erro ao calcular probabilidades: {e}")
            return {
                'vitoria_casa': 33.33,
                'empate': 33.33,
                'vitoria_visitante': 33.33,
                'gols_esperados_total': 2.5
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
🏠 Vitória Casa: {probabilidades['vitoria_casa']:.1f}%
🤝 Empate: {probabilidades['empate']:.1f}%
✈️ Vitória Visitante: {probabilidades['vitoria_visitante']:.1f}%

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
            
            if tipo_aposta == "Vitória Casa" and 'resultFt' in odds:
                odd_aposta = odds['resultFt']['home']
                prob_nossa = probabilidades['vitoria_casa']
            elif tipo_aposta == "Empate" and 'resultFt' in odds:
                odd_aposta = odds['resultFt']['draw']
                prob_nossa = probabilidades['empate']
            elif tipo_aposta == "Vitória Visitante" and 'resultFt' in odds:
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
📊 Nossa Probabilidade: {prob_nossa:.1f}%
🏠 Prob. Implícita: {prob_implicita:.1f}%
💎 Value Bet: {value_bet:.3f} ({((value_bet - 1) * 100):+.1f}%)

💵 Retorno Potencial: R$ {retorno_potencial:.2f}
💰 Lucro Potencial: R$ {lucro_potencial:.2f}

"""
                
                # Aplicar novas regras de classificação
                value_percent = (value_bet - 1) * 100
                
                # Determinar tipo de aposta para aplicar regra correta
                is_vencedor = tipo_aposta in ["Vitória Casa", "Empate", "Vitória Visitante"]
                
                if is_vencedor:
                    # Regras para vencedor: Forte: value >= 5% E prob_impl >= 35%
                    # Arriscada: value >= 15% E prob_impl < 35%
                    if value_percent >= 5 and prob_implicita >= 35:
                        relatorio += "✅ RECOMENDAÇÃO: APOSTA FORTE!\n"
                        relatorio += "🔥 Value >= 5% com probabilidade implícita >= 35%\n"
                    elif value_percent >= 15 and prob_implicita < 35:
                        relatorio += "⚠️ RECOMENDAÇÃO: APOSTA ARRISCADA!\n"
                        relatorio += "🟡 Value >= 15% com probabilidade implícita < 35%\n"
                    else:
                        relatorio += "❌ NÃO RECOMENDADO - Não atende aos critérios\n"
                else:
                    # Regras para Over/Under: Forte: prob_impl >= 35% E value >= 5%
                    # Arriscada: prob_impl < 35% E value >= 15%
                    if prob_implicita >= 35 and value_percent >= 5:
                        relatorio += "✅ RECOMENDAÇÃO: APOSTA FORTE!\n"
                        relatorio += "🔥 Probabilidade implícita >= 35% com value >= 5%\n"
                    elif prob_implicita < 35 and value_percent >= 15:
                        relatorio += "⚠️ RECOMENDAÇÃO: APOSTA ARRISCADA!\n"
                        relatorio += "🟡 Probabilidade implícita < 35% com value >= 15%\n"
                    else:
                        relatorio += "❌ NÃO RECOMENDADO - Não atende aos critérios\n"
        
        relatorio += f"""
═══════════════════════════════════════
⏰ Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        
        return relatorio

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
