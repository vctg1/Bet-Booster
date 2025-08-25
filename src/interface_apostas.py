#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Gráfica para Análise de Apostas Esportivas
Sistema completo para cálculo de probabilidades baseado em estatísticas de gols
Integrado com API Radar Esportivo para busca automática de times e estatísticas reais
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import math
from datetime import datetime
import os
import sys
import threading
import time

# Importar API Radar Esportivo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.radar_esportivo_api import RadarEsportivoAPI

class CalculadoraApostasGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Análise de Apostas - Calculadora Avançada")
        self.root.geometry("1000x700")
        
        # Dados dos times e apostas
        self.times_database = {}
        self.apostas_ativas = []
        
        # Integração com API Radar Esportivo
        self.api = RadarEsportivoAPI()
        
        # Configurar estilo
        self.setup_styles()
        
        # Criar interface
        self.create_widgets()
        
        # Carregar dados salvos
        self.carregar_dados()
    
    def setup_styles(self):
        """Configura estilos da interface"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Success.TLabel', foreground='green', font=('Arial', 10, 'bold'))
        style.configure('Warning.TLabel', foreground='red', font=('Arial', 10, 'bold'))
    
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba 1: Jogos do Dia
        self.create_jogos_do_dia_tab()
        
        # Aba 2: Cadastro de Times
        self.create_cadastro_tab()
        
        # Aba 3: Análise de Confrontos
        self.create_analise_tab()
        
        # Aba 4: Apostas e Múltiplas
        self.create_apostas_tab()
        
        # Aba 5: Histórico e Estatísticas
        self.create_historico_tab()
    
    def create_jogos_do_dia_tab(self):
        """Cria a aba de jogos do dia via Radar Esportivo API"""
        self.tab_jogos_dia = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_jogos_dia, text="⚽ Jogos do Dia")
        
        # Título
        ttk.Label(self.tab_jogos_dia, text="Jogos do Dia - Radar Esportivo", style='Title.TLabel').pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(self.tab_jogos_dia)
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # Frame de controles
        controles_frame = ttk.LabelFrame(main_frame, text="Controles", padding=15)
        controles_frame.pack(fill='x', pady=10)
        
        # Frame de seleção de data
        data_frame = ttk.Frame(controles_frame)
        data_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(data_frame, text="📅 Data:").pack(side='left', padx=(0, 5))
        
        # Campo de data (formato DD/MM/AAAA)
        self.entry_data = ttk.Entry(data_frame, width=12)
        self.entry_data.pack(side='left', padx=(0, 5))
        
        # Preencher com a data de hoje
        data_hoje = datetime.now().strftime('%d/%m/%Y')
        self.entry_data.insert(0, data_hoje)
        
        # Botões de data rápida
        ttk.Button(data_frame, text="Hoje", 
                  command=self.definir_data_hoje).pack(side='left', padx=2)
        ttk.Button(data_frame, text="Ontem", 
                  command=self.definir_data_ontem).pack(side='left', padx=2)
        ttk.Button(data_frame, text="Amanhã", 
                  command=self.definir_data_amanha).pack(side='left', padx=2)
        
        # Label de ajuda
        ttk.Label(data_frame, text="(formato: DD/MM/AAAA)", 
                 style='Subtitle.TLabel').pack(side='left', padx=(10, 0))
        
        # Botões de ação
        btn_frame = ttk.Frame(controles_frame)
        btn_frame.pack(fill='x')
        
        self.btn_carregar_jogos = ttk.Button(btn_frame, text="🔄 Carregar Jogos da Data", 
                                           command=self.carregar_jogos_da_data)
        self.btn_carregar_jogos.pack(side='left', padx=5)
        
        self.btn_simular_selecionados = ttk.Button(btn_frame, text="⚽ Simular Selecionados", 
                                                 command=self.simular_jogos_selecionados, state='disabled')
        self.btn_simular_selecionados.pack(side='left', padx=5)
        
        self.btn_cadastrar_times = ttk.Button(btn_frame, text="📋 Cadastrar Times (10 últimas)", 
                                            command=self.cadastrar_times_selecionados, state='disabled')
        self.btn_cadastrar_times.pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="�️ Limpar Lista", command=self.limpar_jogos_dia).pack(side='left', padx=5)
        
        # Label de status
        self.label_status_jogos = ttk.Label(controles_frame, text="Selecione uma data e clique em 'Carregar Jogos da Data' para buscar as partidas", 
                                          style='Subtitle.TLabel')
        self.label_status_jogos.pack(pady=10)
        
        # Frame de resultados
        resultados_frame = ttk.LabelFrame(main_frame, text="Jogos Disponíveis", padding=10)
        resultados_frame.pack(fill='both', expand=True, pady=10)
        
        # Frame de pesquisa para jogos
        pesquisa_jogos_frame = ttk.Frame(resultados_frame)
        pesquisa_jogos_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(pesquisa_jogos_frame, text="🔍 Pesquisar:").pack(side='left', padx=(0, 5))
        self.entry_pesquisa_jogos = ttk.Entry(pesquisa_jogos_frame, width=30)
        self.entry_pesquisa_jogos.pack(side='left', padx=(0, 10))
        self.entry_pesquisa_jogos.bind('<KeyRelease>', self.filtrar_jogos)
        
        ttk.Button(pesquisa_jogos_frame, text="Limpar Pesquisa", 
                  command=self.limpar_pesquisa_jogos).pack(side='left', padx=5)
        
        # Label de contagem de jogos
        self.label_contagem_jogos = ttk.Label(pesquisa_jogos_frame, text="")
        self.label_contagem_jogos.pack(side='right')
        
        # Treeview para mostrar jogos
        columns = ('Liga', 'Casa', 'Visitante', 'Horário', 'Status')
        self.tree_jogos = ttk.Treeview(resultados_frame, columns=columns, show='tree headings', height=15)
        
        # Configurar colunas
        self.tree_jogos.heading('#0', text='Selecionar')
        self.tree_jogos.column('#0', width=80, minwidth=80)
        
        for col in columns:
            self.tree_jogos.heading(col, text=col)
            if col == 'Liga':
                self.tree_jogos.column(col, width=200, minwidth=150)
            elif col in ['Casa', 'Visitante']:
                self.tree_jogos.column(col, width=150, minwidth=120)
            elif col == 'Horário':
                self.tree_jogos.column(col, width=100, minwidth=80)
            else:  # Status
                self.tree_jogos.column(col, width=100, minwidth=80)
        
        # Scrollbar para o Treeview
        scrollbar_jogos = ttk.Scrollbar(resultados_frame, orient='vertical', command=self.tree_jogos.yview)
        self.tree_jogos.configure(yscrollcommand=scrollbar_jogos.set)
        
        # Pack do Treeview e Scrollbar
        self.tree_jogos.pack(side='left', fill='both', expand=True)
        scrollbar_jogos.pack(side='right', fill='y')
        
        # Bind para seleção de itens
        self.tree_jogos.bind('<Button-1>', self.toggle_jogo_selecao)
        
        # Frame de informações do jogo selecionado
        info_frame = ttk.LabelFrame(main_frame, text="Informações do Jogo", padding=10)
        info_frame.pack(fill='x', pady=10)
        
        self.text_info_jogo = tk.Text(info_frame, height=4, wrap='word', font=('Arial', 10))
        self.text_info_jogo.pack(fill='x')
        
        # Inicializar dados
        self.jogos_do_dia = []
        self.jogos_selecionados = set()
        
        # Opções para estatísticas reais
        self.var_usar_dados_reais = tk.BooleanVar()
        self.var_usar_dados_reais.set(True)
        self.var_mesmo_campo = tk.BooleanVar()
        self.var_mesmo_campo.set(True)
        
        # Frame de informações da API
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Informações", padding=10)
        info_frame.pack(fill='x', pady=5)
        
        info_text = """
🌐 Esta funcionalidade busca times reais da base de dados do Radar Esportivo
📊 Os dados incluem estatísticas estimadas baseadas na liga do time
🔄 As informações são atualizadas automaticamente durante a busca
⚡ Use esta opção para adicionar times rapidamente com dados precisos
        """
        ttk.Label(info_frame, text=info_text.strip(), justify='left').pack(anchor='w')
    
    def create_cadastro_tab(self):
        """Cria a aba de cadastro de times"""
        self.tab_cadastro = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cadastro, text="Cadastro de Times")
        
        # Título
        ttk.Label(self.tab_cadastro, text="Cadastro de Times", style='Title.TLabel').pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(self.tab_cadastro)
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # Frame de entrada
        entrada_frame = ttk.LabelFrame(main_frame, text="Adicionar Novo Time", padding=15)
        entrada_frame.pack(fill='x', pady=10)
        
        # Grid para organizar campos
        ttk.Label(entrada_frame, text="Nome do Time:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_nome = ttk.Entry(entrada_frame, width=25)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(entrada_frame, text="Gols por Partida:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.entry_gols_marcados = ttk.Entry(entrada_frame, width=15)
        self.entry_gols_marcados.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(entrada_frame, text="Gols Sofridos por Partida:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_gols_sofridos = ttk.Entry(entrada_frame, width=15)
        self.entry_gols_sofridos.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(entrada_frame, text="Liga/Campeonato:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.entry_liga = ttk.Entry(entrada_frame, width=20)
        self.entry_liga.grid(row=1, column=3, padx=5, pady=5)
        
        # Botões
        btn_frame = ttk.Frame(entrada_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        ttk.Button(btn_frame, text="Adicionar Time", 
                  command=self.adicionar_time).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Limpar Campos", 
                  command=self.limpar_campos_cadastro).pack(side='left', padx=5)
        
        # Lista de times cadastrados
        lista_frame = ttk.LabelFrame(main_frame, text="Times Cadastrados", padding=10)
        lista_frame.pack(fill='both', expand=True, pady=10)
        
        # Frame de pesquisa
        pesquisa_frame = ttk.Frame(lista_frame)
        pesquisa_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(pesquisa_frame, text="🔍 Pesquisar:").pack(side='left', padx=(0, 5))
        self.entry_pesquisa = ttk.Entry(pesquisa_frame, width=30)
        self.entry_pesquisa.pack(side='left', padx=(0, 10))
        self.entry_pesquisa.bind('<KeyRelease>', self.filtrar_times)
        
        ttk.Button(pesquisa_frame, text="Limpar Pesquisa", 
                  command=self.limpar_pesquisa).pack(side='left', padx=5)
        
        # Label de contagem
        self.label_contagem = ttk.Label(pesquisa_frame, text="")
        self.label_contagem.pack(side='right')
        
        # Frame para a tabela
        table_frame = ttk.Frame(lista_frame)
        table_frame.pack(fill='both', expand=True)
        
        # Treeview para mostrar times (com seleção múltipla)
        columns = ('Nome', 'Gols/Partida', 'Gols Sofridos/Partida', 'Liga', 'Força Ofensiva', 'Força Defensiva')
        self.tree_times = ttk.Treeview(table_frame, columns=columns, show='headings', height=15, selectmode='extended')
        
        for col in columns:
            self.tree_times.heading(col, text=col)
            self.tree_times.column(col, width=120, anchor='center')
        
        # Scrollbar para a tabela
        scrollbar_times = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree_times.yview)
        self.tree_times.configure(yscrollcommand=scrollbar_times.set)
        
        self.tree_times.pack(side='left', fill='both', expand=True)
        scrollbar_times.pack(side='right', fill='y')
        
        # Botões de ação
        btn_actions_frame = ttk.Frame(lista_frame)
        btn_actions_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_actions_frame, text="Remover Selecionados", 
                  command=self.remover_times_selecionados).pack(side='left', padx=5)
        ttk.Button(btn_actions_frame, text="Editar Time", 
                  command=self.editar_time).pack(side='left', padx=5)
        ttk.Button(btn_actions_frame, text="Selecionar Todos", 
                  command=self.selecionar_todos_times).pack(side='left', padx=5)
        ttk.Button(btn_actions_frame, text="Exportar Dados", 
                  command=self.exportar_dados).pack(side='right', padx=5)
    
    def create_analise_tab(self):
        """Cria a aba de análise de confrontos"""
        self.tab_analise = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analise, text="Análise de Confrontos")
        
        ttk.Label(self.tab_analise, text="Análise de Confrontos", style='Title.TLabel').pack(pady=10)
        
        main_frame = ttk.Frame(self.tab_analise)
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # Frame de seleção
        selecao_frame = ttk.LabelFrame(main_frame, text="Selecionar Confronto", padding=15)
        selecao_frame.pack(fill='x', pady=10)
        
        # Comboboxes para seleção de times
        ttk.Label(selecao_frame, text="Time A (Casa):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.combo_time_a = ttk.Combobox(selecao_frame, width=25, state="readonly")
        self.combo_time_a.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(selecao_frame, text="Time B (Visitante):").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.combo_time_b = ttk.Combobox(selecao_frame, width=25, state="readonly")
        self.combo_time_b.grid(row=0, column=3, padx=5, pady=5)
        
        # Odds
        ttk.Label(selecao_frame, text="Odd Vitória A:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_odd_a = ttk.Entry(selecao_frame, width=15)
        self.entry_odd_a.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(selecao_frame, text="Odd Empate:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.entry_odd_empate = ttk.Entry(selecao_frame, width=15)
        self.entry_odd_empate.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(selecao_frame, text="Odd Vitória B:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_odd_b = ttk.Entry(selecao_frame, width=15)
        self.entry_odd_b.grid(row=2, column=1, padx=5, pady=5)
        
        # Opção para escolher tipo de dados
        ttk.Label(selecao_frame, text="Tipo de Dados:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.var_tipo_dados = tk.StringVar()
        self.var_tipo_dados.set("geral")  # Padrão: geral
        self.combo_tipo_dados = ttk.Combobox(selecao_frame, textvariable=self.var_tipo_dados, 
                                           values=["geral", "casa_fora"], state="readonly", width=15)
        self.combo_tipo_dados.grid(row=2, column=3, padx=5, pady=5)
        
        # Labels explicativas para os tipos de dados
        ttk.Label(selecao_frame, text="• casa_fora: Time A (casa) vs Time B (fora)", 
                 font=('Arial', 8)).grid(row=3, column=2, columnspan=2, sticky='w', padx=5)
        ttk.Label(selecao_frame, text="• geral: Estatísticas gerais dos times", 
                 font=('Arial', 8)).grid(row=4, column=2, columnspan=2, sticky='w', padx=5)
        
        # Fator casa (checkbox) com callback para atualizar indicador
        self.var_fator_casa = tk.BooleanVar()
        self.var_fator_casa.set(False)  # Desativado por padrão
        self.check_fator_casa = ttk.Checkbutton(
            selecao_frame, 
            text="Aplicar Vantagem de Casa (15%)", 
            variable=self.var_fator_casa,
            command=self.atualizar_indicador_fator_casa
        )
        self.check_fator_casa.grid(row=5, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Indicador visual do status do fator casa
        self.label_status_casa = ttk.Label(selecao_frame, text="❌ Vantagem de casa DESATIVADA", 
                                            style='Warning.TLabel')
        self.label_status_casa.grid(row=5, column=2, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Placar ao vivo (opcional)
        placar_frame = ttk.LabelFrame(selecao_frame, text="📺 Placar Ao Vivo (Opcional)")
        placar_frame.grid(row=6, column=0, columnspan=4, sticky='ew', padx=5, pady=10)
        
        self.var_placar_ativo = tk.BooleanVar()
        self.check_placar_ativo = ttk.Checkbutton(
            placar_frame, 
            text="Ativar Placar Ao Vivo", 
            variable=self.var_placar_ativo,
            command=self.atualizar_estado_placar
        )
        self.check_placar_ativo.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        ttk.Label(placar_frame, text="Gols Time A:").grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.entry_gols_time_a = ttk.Entry(placar_frame, width=5, state='disabled')
        self.entry_gols_time_a.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(placar_frame, text="Gols Time B:").grid(row=0, column=3, sticky='w', padx=5, pady=5)
        self.entry_gols_time_b = ttk.Entry(placar_frame, width=5, state='disabled')
        self.entry_gols_time_b.grid(row=0, column=4, padx=5, pady=5)
        
        ttk.Label(placar_frame, text="Tempo (min):").grid(row=0, column=5, sticky='w', padx=5, pady=5)
        self.entry_tempo_partida = ttk.Entry(placar_frame, width=5, state='disabled')
        self.entry_tempo_partida.grid(row=0, column=6, padx=5, pady=5)
        
        # Status do placar
        self.label_status_placar = ttk.Label(placar_frame, text="❌ Placar ao vivo DESATIVADO", 
                                           style='Warning.TLabel')
        self.label_status_placar.grid(row=1, column=0, columnspan=7, pady=5)
        
        # Botão calcular (movido para linha 7 para não sobrepor)
        ttk.Button(selecao_frame, text="Calcular Probabilidades", 
                  command=self.calcular_confronto).grid(row=7, column=1, columnspan=2, pady=15)
        
        # Frame de resultados
        resultados_frame = ttk.LabelFrame(main_frame, text="Resultados da Análise", padding=15)
        resultados_frame.pack(fill='both', expand=True, pady=10)
        
        # Área de texto para resultados
        self.text_resultados = scrolledtext.ScrolledText(resultados_frame, height=20, width=100)
        self.text_resultados.pack(fill='both', expand=True)
    
    def create_apostas_tab(self):
        """Cria a aba de apostas e múltiplas"""
        self.tab_apostas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_apostas, text="Apostas e Múltiplas")
        
        ttk.Label(self.tab_apostas, text="Sistema de Apostas", style='Title.TLabel').pack(pady=10)
        
        main_frame = ttk.Frame(self.tab_apostas)
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # Frame esquerdo - Adicionar apostas
        left_frame = ttk.LabelFrame(main_frame, text="Adicionar Aposta", padding=15)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Seleção do confronto
        ttk.Label(left_frame, text="Time A:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.combo_aposta_time_a = ttk.Combobox(left_frame, width=20, state="readonly")
        self.combo_aposta_time_a.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Time B:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.combo_aposta_time_b = ttk.Combobox(left_frame, width=20, state="readonly")
        self.combo_aposta_time_b.grid(row=0, column=3, padx=5, pady=5)
        
        # Tipo de aposta
        ttk.Label(left_frame, text="Tipo de Aposta:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.combo_tipo_aposta = ttk.Combobox(left_frame, values=["Vitória A", "Empate", "Vitória B"], 
                                             state="readonly", width=15)
        self.combo_tipo_aposta.grid(row=1, column=1, padx=5, pady=5)
        
        # Odd da aposta
        ttk.Label(left_frame, text="Odd:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.entry_aposta_odd = ttk.Entry(left_frame, width=15)
        self.entry_aposta_odd.grid(row=1, column=3, padx=5, pady=5)
        
        # Valor da aposta
        ttk.Label(left_frame, text="Valor da Aposta (R$):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_valor_aposta = ttk.Entry(left_frame, width=15)
        self.entry_valor_aposta.grid(row=2, column=1, padx=5, pady=5)
        
        # Tipo de dados
        ttk.Label(left_frame, text="Tipo de Dados:").grid(row=2, column=2, sticky='w', padx=5, pady=5)
        self.var_tipo_dados_aposta = tk.StringVar()
        self.var_tipo_dados_aposta.set("geral")  # Padrão: geral
        self.combo_tipo_dados_aposta = ttk.Combobox(left_frame, textvariable=self.var_tipo_dados_aposta, 
                                                   values=["geral", "casa_fora"], state="readonly", width=15)
        self.combo_tipo_dados_aposta.grid(row=2, column=3, padx=5, pady=5)
        
        # Vantagem de casa específica para apostas
        vantagem_casa_apostas_frame = ttk.Frame(left_frame)
        vantagem_casa_apostas_frame.grid(row=3, column=0, columnspan=4, sticky='ew', padx=5, pady=5)
        
        self.var_fator_casa_apostas = tk.BooleanVar()
        self.var_fator_casa_apostas.set(False)  # Padrão desativado
        self.check_fator_casa_apostas = ttk.Checkbutton(
            vantagem_casa_apostas_frame, 
            text="Aplicar Vantagem de Casa (15%)", 
            variable=self.var_fator_casa_apostas,
            command=self.atualizar_status_casa_apostas
        )
        self.check_fator_casa_apostas.pack(side='left', padx=5)
        
        self.label_status_casa_apostas = ttk.Label(vantagem_casa_apostas_frame, text="❌ Vantagem de casa DESATIVADA", 
                                                    style='Warning.TLabel')
        self.label_status_casa_apostas.pack(side='left', padx=10)
        
        # Placar ao vivo para apostas (opcional)
        placar_apostas_frame = ttk.LabelFrame(left_frame, text="📺 Placar Ao Vivo (Opcional)")
        placar_apostas_frame.grid(row=4, column=0, columnspan=4, sticky='ew', padx=5, pady=10)
        
        self.var_placar_apostas_ativo = tk.BooleanVar()
        self.check_placar_apostas_ativo = ttk.Checkbutton(
            placar_apostas_frame, 
            text="Ativar Placar Ao Vivo", 
            variable=self.var_placar_apostas_ativo,
            command=self.atualizar_estado_placar_apostas
        )
        self.check_placar_apostas_ativo.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        ttk.Label(placar_apostas_frame, text="Gols A:").grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.entry_gols_apostas_a = ttk.Entry(placar_apostas_frame, width=5, state='disabled')
        self.entry_gols_apostas_a.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(placar_apostas_frame, text="Gols B:").grid(row=0, column=3, sticky='w', padx=5, pady=5)
        self.entry_gols_apostas_b = ttk.Entry(placar_apostas_frame, width=5, state='disabled')
        self.entry_gols_apostas_b.grid(row=0, column=4, padx=5, pady=5)
        
        ttk.Label(placar_apostas_frame, text="Tempo:").grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.entry_tempo_apostas = ttk.Entry(placar_apostas_frame, width=5, state='disabled')
        self.entry_tempo_apostas.grid(row=1, column=2, padx=5, pady=5)
        
        # Status do placar nas apostas
        self.label_status_placar_apostas = ttk.Label(placar_apostas_frame, text="❌ Placar ao vivo DESATIVADO", 
                                                    style='Warning.TLabel')
        self.label_status_placar_apostas.grid(row=1, column=3, columnspan=2, pady=5)
        
        # Botões
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=15)
        
        ttk.Button(btn_frame, text="Calcular Aposta Simples", 
                  command=self.calcular_aposta_simples).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Adicionar à Múltipla", 
                  command=self.adicionar_multipla).pack(side='left', padx=5)
        
        # Frame direito - Apostas ativas
        right_frame = ttk.LabelFrame(main_frame, text="Apostas Ativas", padding=15)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Lista de apostas múltiplas
        columns_apostas = ('Confronto', 'Tipo', 'Odd', 'Probabilidade')
        self.tree_apostas = ttk.Treeview(right_frame, columns=columns_apostas, show='headings', height=10)
        
        for col in columns_apostas:
            self.tree_apostas.heading(col, text=col)
            self.tree_apostas.column(col, width=100, anchor='center')
        
        self.tree_apostas.pack(fill='both', expand=True)
        
        # Cálculo da múltipla
        multipla_frame = ttk.Frame(right_frame)
        multipla_frame.pack(fill='x', pady=10)
        
        ttk.Label(multipla_frame, text="Valor Total (R$):").pack(side='left')
        self.entry_valor_multipla = ttk.Entry(multipla_frame, width=15)
        self.entry_valor_multipla.pack(side='left', padx=5)
        
        ttk.Button(multipla_frame, text="Calcular Múltipla", 
                  command=self.calcular_multipla).pack(side='left', padx=5)
        ttk.Button(multipla_frame, text="Limpar Lista", 
                  command=self.limpar_apostas).pack(side='left', padx=5)
        
        # Resultados
        self.label_resultado_multipla = ttk.Label(right_frame, text="", style='Success.TLabel')
        self.label_resultado_multipla.pack(pady=10)
    
    def create_historico_tab(self):
        """Cria a aba de histórico e estatísticas"""
        self.tab_historico = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_historico, text="Histórico & Stats")
        
        ttk.Label(self.tab_historico, text="Histórico e Estatísticas", style='Title.TLabel').pack(pady=10)
        
        # Área de texto para estatísticas
        self.text_historico = scrolledtext.ScrolledText(self.tab_historico, height=30, width=120)
        self.text_historico.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Botões
        btn_frame = ttk.Frame(self.tab_historico)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Atualizar Estatísticas", 
                  command=self.atualizar_estatisticas).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Exportar Relatório", 
                  command=self.exportar_relatorio).pack(side='left', padx=5)
    
    def atualizar_comboboxes(self):
        """Atualiza as listas de times nos comboboxes"""
        times = list(self.times_database.keys())
        
        # Atualizar comboboxes da aba de análise
        self.combo_time_a['values'] = times
        self.combo_time_b['values'] = times
        
        # Atualizar comboboxes da aba de apostas
        self.combo_aposta_time_a['values'] = times
        self.combo_aposta_time_b['values'] = times
    
    def adicionar_time(self):
        """Adiciona um novo time ao banco de dados"""
        try:
            nome = self.entry_nome.get().strip()
            gols_marcados = float(self.entry_gols_marcados.get().replace(',', '.'))
            gols_sofridos = float(self.entry_gols_sofridos.get().replace(',', '.'))
            liga = self.entry_liga.get().strip() or "Não informado"
            
            if not nome:
                messagebox.showerror("Erro", "Nome do time é obrigatório!")
                return
            
            if nome in self.times_database:
                if not messagebox.askyesno("Confirmação", f"Time {nome} já existe. Deseja atualizar?"):
                    return
            
            # Calcular forças (assumindo média da liga = 1.2)
            media_liga = 1.2
            forca_ofensiva = gols_marcados / media_liga
            forca_defensiva = gols_sofridos / media_liga
            
            self.times_database[nome] = {
                'gols_marcados': gols_marcados,
                'gols_sofridos': gols_sofridos,
                'liga': liga,
                'forca_ofensiva': forca_ofensiva,
                'forca_defensiva': forca_defensiva,
                'data_cadastro': datetime.now().isoformat()
            }
            
            self.atualizar_lista_times()
            self.atualizar_comboboxes()
            self.limpar_campos_cadastro()
            self.salvar_dados()
            
            messagebox.showinfo("Sucesso", f"Time {nome} adicionado com sucesso!")
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos para os gols!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar time: {str(e)}")
    
    def atualizar_lista_times(self):
        """Atualiza a lista de times na interface"""
        # Limpar lista atual
        for item in self.tree_times.get_children():
            self.tree_times.delete(item)
        
        # Verificar se há filtro ativo
        termo_pesquisa = ""
        if hasattr(self, 'entry_pesquisa'):
            termo_pesquisa = self.entry_pesquisa.get().lower()
        
        # Adicionar times (filtrados se houver termo de pesquisa)
        times_mostrados = 0
        for nome, dados in self.times_database.items():
            # Aplicar filtro se houver termo de pesquisa
            if termo_pesquisa:
                if not (termo_pesquisa in nome.lower() or 
                       termo_pesquisa in dados.get('liga', '').lower()):
                    continue
            
            # Calcular força ofensiva e defensiva se não existirem
            forca_ofensiva = dados.get('forca_ofensiva', dados['gols_marcados'] / 1.2)
            forca_defensiva = dados.get('forca_defensiva', dados['gols_sofridos'] / 1.2)
            
            self.tree_times.insert('', 'end', values=(
                nome,
                f"{(dados['gols_marcados'] or 0):.2f}",
                f"{(dados['gols_sofridos'] or 0):.2f}",
                dados.get('liga', 'N/A'),
                f"{(forca_ofensiva or 0):.2f}",
                f"{(forca_defensiva or 0):.2f}"
            ))
            times_mostrados += 1
        
        # Atualizar contagem se o label existir
        if hasattr(self, 'label_contagem'):
            total_times = len(self.times_database)
            if termo_pesquisa:
                self.label_contagem.config(text=f"Mostrando {times_mostrados} de {total_times} times")
            else:
                self.label_contagem.config(text=f"Total: {total_times} times")
    
    def limpar_campos_cadastro(self):
        """Limpa os campos de cadastro"""
        self.entry_nome.delete(0, tk.END)
        self.entry_gols_marcados.delete(0, tk.END)
        self.entry_gols_sofridos.delete(0, tk.END)
        self.entry_liga.delete(0, tk.END)
    
    def atualizar_indicador_fator_casa(self):
        """Atualiza o indicador visual do status do fator casa"""
        if self.var_fator_casa.get():
            self.label_status_casa.config(
                text="✅ Vantagem de casa ATIVADA", 
                style='Success.TLabel'
            )
        else:
            self.label_status_casa.config(
                text="❌ Vantagem de casa DESATIVADA", 
                style='Warning.TLabel'
            )
    
    def atualizar_status_casa_apostas(self):
        """Atualiza o indicador visual do status do fator casa na aba apostas"""
        if self.var_fator_casa_apostas.get():
            self.label_status_casa_apostas.config(
                text="✅ Vantagem de casa ATIVADA", 
                style='Success.TLabel'
            )
        else:
            self.label_status_casa_apostas.config(
                text="❌ Vantagem de casa DESATIVADA", 
                style='Warning.TLabel'
            )
    
    def atualizar_estado_placar(self):
        """Atualiza o estado dos campos do placar ao vivo na aba de análise"""
        if self.var_placar_ativo.get():
            # Ativar campos
            self.entry_gols_time_a.config(state='normal')
            self.entry_gols_time_b.config(state='normal')
            self.entry_tempo_partida.config(state='normal')
            self.label_status_placar.config(
                text="✅ Placar ao vivo ATIVADO", 
                style='Success.TLabel'
            )
        else:
            # Desativar e limpar campos
            self.entry_gols_time_a.config(state='disabled')
            self.entry_gols_time_b.config(state='disabled')
            self.entry_tempo_partida.config(state='disabled')
            self.entry_gols_time_a.delete(0, tk.END)
            self.entry_gols_time_b.delete(0, tk.END)
            self.entry_tempo_partida.delete(0, tk.END)
            self.label_status_placar.config(
                text="❌ Placar ao vivo DESATIVADO", 
                style='Warning.TLabel'
            )
    
    def atualizar_estado_placar_apostas(self):
        """Atualiza o estado dos campos do placar ao vivo na aba de apostas"""
        if self.var_placar_apostas_ativo.get():
            # Ativar campos
            self.entry_gols_apostas_a.config(state='normal')
            self.entry_gols_apostas_b.config(state='normal')
            self.entry_tempo_apostas.config(state='normal')
            self.label_status_placar_apostas.config(
                text="✅ Placar ao vivo ATIVADO", 
                style='Success.TLabel'
            )
        else:
            # Desativar e limpar campos
            self.entry_gols_apostas_a.config(state='disabled')
            self.entry_gols_apostas_b.config(state='disabled')
            self.entry_tempo_apostas.config(state='disabled')
            self.entry_gols_apostas_a.delete(0, tk.END)
            self.entry_gols_apostas_b.delete(0, tk.END)
            self.entry_tempo_apostas.delete(0, tk.END)
            self.label_status_placar_apostas.config(
                text="❌ Placar ao vivo DESATIVADO", 
                style='Warning.TLabel'
            )
    
    def remover_time(self):
        """Remove o time selecionado"""
        selected = self.tree_times.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um time para remover!")
            return
        
        item = self.tree_times.item(selected[0])
        nome_time = item['values'][0]
        
        if messagebox.askyesno("Confirmação", f"Deseja remover o time {nome_time}?"):
            del self.times_database[nome_time]
            self.atualizar_lista_times()
            self.atualizar_comboboxes()
            self.salvar_dados()
            messagebox.showinfo("Sucesso", f"Time {nome_time} removido!")
    
    def remover_times_selecionados(self):
        """Remove múltiplos times selecionados"""
        selected = self.tree_times.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um ou mais times para remover!")
            return
        
        # Obter nomes dos times selecionados
        times_para_remover = []
        for item in selected:
            nome_time = self.tree_times.item(item)['values'][0]
            times_para_remover.append(nome_time)
        
        # Confirmação
        if len(times_para_remover) == 1:
            mensagem = f"Deseja remover o time {times_para_remover[0]}?"
        else:
            mensagem = f"Deseja remover {len(times_para_remover)} times selecionados?\n\n"
            mensagem += "Times a serem removidos:\n"
            for time in times_para_remover:
                mensagem += f"• {time}\n"
        
        if messagebox.askyesno("Confirmação", mensagem):
            # Remover times do banco de dados
            times_removidos = []
            for nome_time in times_para_remover:
                if nome_time in self.times_database:
                    del self.times_database[nome_time]
                    times_removidos.append(nome_time)
            
            # Atualizar interface
            self.atualizar_lista_times()
            self.atualizar_comboboxes()
            self.salvar_dados()
            
            # Mensagem de sucesso
            if len(times_removidos) == 1:
                messagebox.showinfo("Sucesso", f"Time {times_removidos[0]} removido!")
            else:
                messagebox.showinfo("Sucesso", f"{len(times_removidos)} times removidos com sucesso!")
    
    def selecionar_todos_times(self):
        """Seleciona todos os times visíveis na lista"""
        # Obter todos os itens na treeview
        all_items = self.tree_times.get_children()
        
        if not all_items:
            messagebox.showinfo("Info", "Nenhum time disponível para seleção!")
            return
        
        # Selecionar todos os itens
        self.tree_times.selection_set(all_items)
        messagebox.showinfo("Info", f"{len(all_items)} times selecionados!")
    
    def filtrar_times(self, event=None):
        """Filtra a lista de times baseado no texto de pesquisa"""
        termo_pesquisa = self.entry_pesquisa.get().lower()
        
        # Limpar lista atual
        for item in self.tree_times.get_children():
            self.tree_times.delete(item)
        
        # Adicionar apenas times que correspondem à pesquisa
        times_filtrados = 0
        for nome, dados in self.times_database.items():
            # Verificar se o termo está no nome do time ou na liga
            if (termo_pesquisa in nome.lower() or 
                termo_pesquisa in dados.get('liga', '').lower()):
                
                forca_ofensiva = dados.get('forca_ofensiva', dados['gols_marcados'] / 1.2)
                forca_defensiva = dados.get('forca_defensiva', dados['gols_sofridos'] / 1.2)
                
                self.tree_times.insert('', 'end', values=(
                    nome,
                    f"{(dados['gols_marcados'] or 0):.2f}",
                    f"{(dados['gols_sofridos'] or 0):.2f}",
                    dados.get('liga', 'N/A'),
                    f"{(forca_ofensiva or 0):.2f}",
                    f"{(forca_defensiva or 0):.2f}"
                ))
                times_filtrados += 1
        
        # Atualizar contagem
        total_times = len(self.times_database)
        if termo_pesquisa:
            self.label_contagem.config(text=f"Mostrando {times_filtrados} de {total_times} times")
        else:
            self.label_contagem.config(text=f"Total: {total_times} times")
    
    def limpar_pesquisa(self):
        """Limpa o campo de pesquisa e mostra todos os times"""
        self.entry_pesquisa.delete(0, tk.END)
        self.atualizar_lista_times()

    def _obter_dados_casa_fora(self, dados_time, tipo):
        """
        Obtém dados específicos para casa ou fora de um time
        
        Args:
            dados_time: Dados completos do time
            tipo: "casa" ou "fora"
        
        Returns:
            dict: Dados formatados para o tipo solicitado
        """
        try:
            if tipo == "casa":
                # Tentar usar dados específicos de casa
                if 'gols_marcados_casa' in dados_time and dados_time['gols_marcados_casa'] is not None:
                    gols_marcados = dados_time['gols_marcados_casa']
                    gols_sofridos = dados_time['gols_sofridos_casa']
                else:
                    # Fallback para dados gerais
                    gols_marcados = dados_time['gols_marcados']
                    gols_sofridos = dados_time['gols_sofridos']
            else:  # fora
                # Tentar usar dados específicos de fora
                if 'gols_marcados_fora' in dados_time and dados_time['gols_marcados_fora'] is not None:
                    gols_marcados = dados_time['gols_marcados_fora']
                    gols_sofridos = dados_time['gols_sofridos_fora']
                else:
                    # Fallback para dados gerais
                    gols_marcados = dados_time['gols_marcados']
                    gols_sofridos = dados_time['gols_sofridos']
            
            # Criar dados formatados
            dados_formatados = {
                'gols_marcados': gols_marcados,
                'gols_sofridos': gols_sofridos,
                'liga': dados_time.get('liga', 'N/A'),
                'forca_ofensiva': None,  # Será calculado no método de gols esperados
                'forca_defensiva': None  # Será calculado no método de gols esperados
            }
            
            return dados_formatados
            
        except Exception as e:
            print(f"❌ Erro ao obter dados casa/fora: {e}")
            # Fallback para dados gerais em caso de erro
            return {
                'gols_marcados': dados_time['gols_marcados'],
                'gols_sofridos': dados_time['gols_sofridos'],
                'liga': dados_time.get('liga', 'N/A'),
                'forca_ofensiva': None,
                'forca_defensiva': None
            }

    def calcular_gols_esperados(self, time_a_dados, time_b_dados, aplicar_fator_casa=True):
        """
        Calcula gols esperados usando o modelo melhorado
        
        Args:
            time_a_dados: Dados do time A (casa)
            time_b_dados: Dados do time B (visitante)
            aplicar_fator_casa: Boolean se deve aplicar vantagem de casa (15%)
        """
        media_liga = 1.2
        fator_casa = 1.15 if aplicar_fator_casa else 1.0
        
        # Verificar e garantir que os dados básicos não sejam None
        gols_marcados_a = time_a_dados.get('gols_marcados') or 0
        gols_sofridos_a = time_a_dados.get('gols_sofridos') or 0
        gols_marcados_b = time_b_dados.get('gols_marcados') or 0
        gols_sofridos_b = time_b_dados.get('gols_sofridos') or 0
        
        # Garantir valores mínimos para evitar divisão por zero
        gols_marcados_a = max(0.1, float(gols_marcados_a))
        gols_sofridos_a = max(0.1, float(gols_sofridos_a))
        gols_marcados_b = max(0.1, float(gols_marcados_b))
        gols_sofridos_b = max(0.1, float(gols_sofridos_b))
        
        # Forças já calculadas ou calcular se não existirem
        forca_of_a = time_a_dados.get('forca_ofensiva')
        if forca_of_a is None:
            forca_of_a = gols_marcados_a / media_liga
            
        forca_def_a = time_a_dados.get('forca_defensiva')
        if forca_def_a is None:
            forca_def_a = gols_sofridos_a / media_liga
            
        forca_of_b = time_b_dados.get('forca_ofensiva')
        if forca_of_b is None:
            forca_of_b = gols_marcados_b / media_liga
            
        forca_def_b = time_b_dados.get('forca_defensiva')
        if forca_def_b is None:
            forca_def_b = gols_sofridos_b / media_liga
        
        # Gols esperados com ou sem fator casa
        gols_esperados_a = forca_of_a * forca_def_b * media_liga * fator_casa
        gols_esperados_b = forca_of_b * forca_def_a * media_liga
        
        return gols_esperados_a, gols_esperados_b
    
    def calcular_probabilidades_poisson(self, gols_esperados_a, gols_esperados_b, max_gols=6):
        """Calcula probabilidades usando distribuição de Poisson"""
        prob_vitoria_a = 0
        prob_empate = 0
        prob_vitoria_b = 0
        
        for gols_a in range(max_gols + 1):
            for gols_b in range(max_gols + 1):
                # Fórmula de Poisson: P(X=k) = (λ^k * e^(-λ)) / k!
                prob_a = (gols_esperados_a ** gols_a * math.exp(-gols_esperados_a)) / math.factorial(gols_a)
                prob_b = (gols_esperados_b ** gols_b * math.exp(-gols_esperados_b)) / math.factorial(gols_b)
                prob_combinada = prob_a * prob_b
                
                if gols_a > gols_b:
                    prob_vitoria_a += prob_combinada
                elif gols_a == gols_b:
                    prob_empate += prob_combinada
                else:
                    prob_vitoria_b += prob_combinada
        
        return prob_vitoria_a, prob_empate, prob_vitoria_b
    
    def calcular_probabilidades_com_placar_ao_vivo(self, gols_esperados_a, gols_esperados_b, 
                                                  gols_atuais_a, gols_atuais_b, tempo_decorrido, max_gols=6):
        """
        Calcula probabilidades ajustadas considerando placar atual e tempo decorrido
        
        Args:
            gols_esperados_a: Gols esperados por time A no tempo restante
            gols_esperados_b: Gols esperados por time B no tempo restante  
            gols_atuais_a: Gols já marcados pelo time A
            gols_atuais_b: Gols já marcados pelo time B
            tempo_decorrido: Minutos já jogados
            max_gols: Máximo de gols a considerar no tempo restante
        """
        # Ajustar expectativa para o tempo restante
        tempo_restante = max(0, 90 - tempo_decorrido) / 90.0
        
        if tempo_restante <= 0:
            # Jogo acabou, probabilidades baseadas no resultado atual
            if gols_atuais_a > gols_atuais_b:
                return 1.0, 0.0, 0.0
            elif gols_atuais_a == gols_atuais_b:
                return 0.0, 1.0, 0.0
            else:
                return 0.0, 0.0, 1.0
        
        # Ajustar gols esperados para o tempo restante
        gols_esp_restante_a = gols_esperados_a * tempo_restante
        gols_esp_restante_b = gols_esperados_b * tempo_restante
        
        prob_vitoria_a = 0
        prob_empate = 0
        prob_vitoria_b = 0
        
        # Calcular probabilidades para gols adicionais no tempo restante
        for gols_add_a in range(max_gols + 1):
            for gols_add_b in range(max_gols + 1):
                # Probabilidade de marcar esses gols adicionais
                prob_a = (gols_esp_restante_a ** gols_add_a * math.exp(-gols_esp_restante_a)) / math.factorial(gols_add_a)
                prob_b = (gols_esp_restante_b ** gols_add_b * math.exp(-gols_esp_restante_b)) / math.factorial(gols_add_b)
                prob_combinada = prob_a * prob_b
                
                # Placar final
                gols_finais_a = gols_atuais_a + gols_add_a
                gols_finais_b = gols_atuais_b + gols_add_b
                
                if gols_finais_a > gols_finais_b:
                    prob_vitoria_a += prob_combinada
                elif gols_finais_a == gols_finais_b:
                    prob_empate += prob_combinada
                else:
                    prob_vitoria_b += prob_combinada
        
        return prob_vitoria_a, prob_empate, prob_vitoria_b
    
    def calcular_confronto(self):
        """Calcula e exibe a análise completa do confronto"""
        try:
            time_a = self.combo_time_a.get()
            time_b = self.combo_time_b.get()
            
            if not time_a or not time_b:
                messagebox.showwarning("Aviso", "Selecione ambos os times!")
                return
            
            if time_a == time_b:
                messagebox.showwarning("Aviso", "Selecione times diferentes!")
                return
            
            # Obter dados dos times
            dados_time_a = self.times_database[time_a]
            dados_time_b = self.times_database[time_b]
            
            # Verificar tipo de dados selecionado
            tipo_dados = self.var_tipo_dados.get()
            
            # Preparar dados baseado no tipo selecionado
            if tipo_dados == "casa_fora":
                # Usar dados específicos casa/fora
                dados_a = self._obter_dados_casa_fora(dados_time_a, "casa")
                dados_b = self._obter_dados_casa_fora(dados_time_b, "fora")
                
                # Verificar se os dados são válidos
                if any(v is None for v in [dados_a['gols_marcados'], dados_a['gols_sofridos'], 
                                         dados_b['gols_marcados'], dados_b['gols_sofridos']]):
                    messagebox.showwarning("Aviso", "Dados casa/fora indisponíveis. Usando dados gerais.")
                    dados_a = dados_time_a
                    dados_b = dados_time_b
                    info_tipo = "📊 Usando dados GERAIS dos times (fallback)"
                else:
                    info_tipo = "📊 Usando dados CASA/FORA (Time A em casa, Time B fora)"
            else:
                # Usar dados gerais
                dados_a = dados_time_a
                dados_b = dados_time_b
                info_tipo = "📊 Usando dados GERAIS dos times"
            
            # Obter configuração do fator casa
            aplicar_fator_casa = self.var_fator_casa.get()
            
            # Calcular gols esperados
            gols_esp_a, gols_esp_b = self.calcular_gols_esperados(dados_a, dados_b, aplicar_fator_casa)
            
            # Verificar se o placar ao vivo está ativo
            placar_ativo = self.var_placar_ativo.get()
            
            if placar_ativo:
                try:
                    gols_atuais_a = int(self.entry_gols_time_a.get() or 0)
                    gols_atuais_b = int(self.entry_gols_time_b.get() or 0)
                    tempo_atual = int(self.entry_tempo_partida.get() or 0)
                    
                    # Calcular probabilidades com placar ao vivo
                    prob_a, prob_empate, prob_b = self.calcular_probabilidades_com_placar_ao_vivo(
                        gols_esp_a, gols_esp_b, gols_atuais_a, gols_atuais_b, tempo_atual
                    )
                    
                    info_placar = f"📺 PLACAR AO VIVO: {gols_atuais_a} x {gols_atuais_b} ({tempo_atual}' min)"
                    
                except ValueError:
                    messagebox.showerror("Erro", "Por favor, insira valores válidos para o placar ao vivo!")
                    return
            else:
                # Calcular probabilidades normais
                prob_a, prob_empate, prob_b = self.calcular_probabilidades_poisson(gols_esp_a, gols_esp_b)
                info_placar = "📺 Placar ao vivo: DESATIVADO"
            
            # Análise de odds (se fornecidas)
            resultado_texto = f"""
{'='*80}
ANÁLISE COMPLETA DO CONFRONTO
{'='*80}

🏟️  CONFRONTO: {time_a} (Casa) vs {time_b} (Visitante)
📅  Data da Análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}
{info_tipo}

📊 ESTATÍSTICAS DOS TIMES:
┌─────────────────────────────────────────────────────────────┐
│ {time_a:<25} │ {time_b:<25} │
├─────────────────────────────────────────────────────────────┤
│ Gols/Partida: {(dados_a['gols_marcados'] or 0):<13.2f} │ Gols/Partida: {(dados_b['gols_marcados'] or 0):<13.2f} │
│ Gols Sofridos: {(dados_a['gols_sofridos'] or 0):<12.2f} │ Gols Sofridos: {(dados_b['gols_sofridos'] or 0):<12.2f} │
│ Força Ofensiva: {(dados_a.get('forca_ofensiva') or (dados_a['gols_marcados'] or 0)/1.2):<11.2f} │ Força Ofensiva: {(dados_b.get('forca_ofensiva') or (dados_b['gols_marcados'] or 0)/1.2):<11.2f} │
│ Força Defensiva: {(dados_a.get('forca_defensiva') or (dados_a['gols_sofridos'] or 0)/1.2):<10.2f} │ Força Defensiva: {(dados_b.get('forca_defensiva') or (dados_b['gols_sofridos'] or 0)/1.2):<10.2f} │
│ Liga: {dados_a.get('liga', 'N/A'):<19} │ Liga: {dados_b.get('liga', 'N/A'):<19} │
└─────────────────────────────────────────────────────────────┘

⚽ GOLS ESPERADOS (Modelo de Poisson):
• {time_a}: {gols_esp_a:.2f} gols
• {time_b}: {gols_esp_b:.2f} gols
• Total de gols esperados: {gols_esp_a + gols_esp_b:.2f}
• Vantagem de casa: {'Aplicada (+15%)' if aplicar_fator_casa else 'Não aplicada'}
• {info_placar}

🎯 PROBABILIDADES CALCULADAS:
• Vitória {time_a}: {prob_a:.1%} ({prob_a:.4f})
• Empate: {prob_empate:.1%} ({prob_empate:.4f})
• Vitória {time_b}: {prob_b:.1%} ({prob_b:.4f})

"""
            
            # Análise de odds se fornecidas
            try:
                odd_a = float(self.entry_odd_a.get().replace(',', '.'))
                odd_empate = float(self.entry_odd_empate.get().replace(',', '.'))
                odd_b = float(self.entry_odd_b.get().replace(',', '.'))
                
                # Probabilidades implícitas das odds
                prob_impl_a = 1 / odd_a
                prob_impl_empate = 1 / odd_empate
                prob_impl_b = 1 / odd_b
                
                margem_casa = (prob_impl_a + prob_impl_empate + prob_impl_b - 1) * 100
                
                resultado_texto += f"""
💰 ANÁLISE DE ODDS:
┌─────────────────────────────────────────────────────────────────────────┐
│ Resultado        │ Nossa Prob │ Odd    │ Prob Implícita │ Value Bet?     │
├─────────────────────────────────────────────────────────────────────────┤
│ Vitória {time_a:<8} │ {prob_a:>8.1%} │ {odd_a:>6.2f} │ {prob_impl_a:>13.1%} │ {"✅ SIM" if prob_a > prob_impl_a else "❌ NÃO":<14} │
│ Empate           │ {prob_empate:>8.1%} │ {odd_empate:>6.2f} │ {prob_impl_empate:>13.1%} │ {"✅ SIM" if prob_empate > prob_impl_empate else "❌ NÃO":<14} │
│ Vitória {time_b:<8} │ {prob_b:>8.1%} │ {odd_b:>6.2f} │ {prob_impl_b:>13.1%} │ {"✅ SIM" if prob_b > prob_impl_b else "❌ NÃO":<14} │
└─────────────────────────────────────────────────────────────────────────┘

📈 VANTAGENS PERCENTUAIS:
• {time_a}: {(prob_a - prob_impl_a) / prob_impl_a * 100:+.1f}%
• Empate: {(prob_empate - prob_impl_empate) / prob_impl_empate * 100:+.1f}%
• {time_b}: {(prob_b - prob_impl_b) / prob_impl_b * 100:+.1f}%

🏪 Margem da casa: {margem_casa:.2f}%

"""
                
                # Recomendações com três níveis
                resultado_texto += "🎯 RECOMENDAÇÕES:\n"
                
                recomendacoes_fortes = []
                recomendacoes_arriscadas = []
                
                # Analisar cada resultado
                for resultado, prob_nossa, prob_impl, nome_resultado in [
                    ("vitoria_a", prob_a, prob_impl_a, f"vitória do {time_a}"),
                    ("empate", prob_empate, prob_impl_empate, "empate"),
                    ("vitoria_b", prob_b, prob_impl_b, f"vitória do {time_b}")
                ]:
                    if prob_nossa > prob_impl:
                        vantagem = (prob_nossa - prob_impl) / prob_impl * 100
                        
                        # Recomendação FORTE: Value bet >= 10% E probabilidade >= 30%
                        if vantagem >= 10.0 and prob_nossa >= 0.30:
                            recomendacoes_fortes.append(
                                f"🔥 FORTE: Apostar em {nome_resultado} (Vantagem: {vantagem:.1f}%, Prob: {prob_nossa:.1%})"
                            )
                        
                        # Recomendação ARRISCADA: Value bet >= 20% E probabilidade < 30%
                        elif vantagem >= 20.0 and prob_nossa < 0.30:
                            recomendacoes_arriscadas.append(
                                f"⚡ ARRISCADA: Apostar em {nome_resultado} (Vantagem: {vantagem:.1f}%, Prob: {prob_nossa:.1%})"
                            )
                
                # Mostrar recomendações por prioridade
                if recomendacoes_fortes:
                    for rec in recomendacoes_fortes:
                        resultado_texto += f"{rec}\n"
                
                if recomendacoes_arriscadas:
                    if recomendacoes_fortes:
                        resultado_texto += "\n"
                    for rec in recomendacoes_arriscadas:
                        resultado_texto += f"{rec}\n"
                    resultado_texto += "   ⚠️  ATENÇÃO: Apostas arriscadas têm alta vantagem mas baixa probabilidade!\n"
                
                if not recomendacoes_fortes and not recomendacoes_arriscadas:
                    resultado_texto += "⚠️  Não foram encontradas apostas com vantagem significativa\n"
                    resultado_texto += "Recomenda-se aguardar melhores oportunidades"
                
            except ValueError:
                resultado_texto += "\n💡 Para análise de value bets, insira as odds da casa de apostas\n"
            
            resultado_texto += f"\n{'='*80}\n"
            
            # Exibir resultado
            self.text_resultados.delete(1.0, tk.END)
            self.text_resultados.insert(1.0, resultado_texto)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no cálculo: {str(e)}")
    
    def calcular_aposta_simples(self):
        """Calcula uma aposta simples"""
        try:
            time_a = self.combo_aposta_time_a.get()
            time_b = self.combo_aposta_time_b.get()
            tipo_aposta = self.combo_tipo_aposta.get()
            odd = float(self.entry_aposta_odd.get().replace(',', '.'))
            valor = float(self.entry_valor_aposta.get().replace(',', '.'))
            
            if not all([time_a, time_b, tipo_aposta]):
                messagebox.showwarning("Aviso", "Preencha todos os campos!")
                return
            
            # Obter dados dos times
            dados_time_a = self.times_database[time_a]
            dados_time_b = self.times_database[time_b]
            
            # Verificar tipo de dados selecionado
            tipo_dados = self.var_tipo_dados_aposta.get()
            
            # Preparar dados baseado no tipo selecionado
            if tipo_dados == "casa_fora":
                # Usar dados específicos casa/fora
                dados_a = self._obter_dados_casa_fora(dados_time_a, "casa")
                dados_b = self._obter_dados_casa_fora(dados_time_b, "fora")
                info_tipo_aposta = "📊 Dados: CASA/FORA"
                
                # Verificar se os dados são válidos
                if any(v is None for v in [dados_a['gols_marcados'], dados_a['gols_sofridos'], 
                                         dados_b['gols_marcados'], dados_b['gols_sofridos']]):
                    messagebox.showerror("Erro", "Dados casa/fora indisponíveis. Usando dados gerais.")
                    dados_a = dados_time_a
                    dados_b = dados_time_b
                    info_tipo_aposta = "📊 Dados: GERAIS (fallback)"
            else:
                # Usar dados gerais
                dados_a = dados_time_a
                dados_b = dados_time_b
                info_tipo_aposta = "📊 Dados: GERAIS"
            
            aplicar_fator_casa = self.var_fator_casa_apostas.get()
            
            gols_esp_a, gols_esp_b = self.calcular_gols_esperados(dados_a, dados_b, aplicar_fator_casa)
            
            # Verificar se o placar ao vivo está ativo nas apostas
            placar_apostas_ativo = self.var_placar_apostas_ativo.get()
            
            if placar_apostas_ativo:
                try:
                    gols_atuais_a = int(self.entry_gols_apostas_a.get() or 0)
                    gols_atuais_b = int(self.entry_gols_apostas_b.get() or 0)
                    tempo_atual = int(self.entry_tempo_apostas.get() or 0)
                    
                    # Calcular probabilidades com placar ao vivo
                    prob_a, prob_empate, prob_b = self.calcular_probabilidades_com_placar_ao_vivo(
                        gols_esp_a, gols_esp_b, gols_atuais_a, gols_atuais_b, tempo_atual
                    )
                    
                    info_placar_apostas = f"📺 Placar: {gols_atuais_a}x{gols_atuais_b} ({tempo_atual}')"
                    
                except ValueError:
                    messagebox.showerror("Erro", "Por favor, insira valores válidos para o placar ao vivo!")
                    return
            else:
                # Calcular probabilidades normais
                prob_a, prob_empate, prob_b = self.calcular_probabilidades_poisson(gols_esp_a, gols_esp_b)
                info_placar_apostas = "📺 Placar ao vivo: Não aplicado"
            
            # Mapear probabilidade
            prob_map = {
                "Vitória A": prob_a,
                "Empate": prob_empate,
                "Vitória B": prob_b
            }
            
            probabilidade = prob_map[tipo_aposta]
            retorno_potencial = valor * odd
            lucro_potencial = retorno_potencial - valor
            
            # Análise de value com três níveis de recomendação
            prob_implicita = 1 / odd
            vantagem = (probabilidade - prob_implicita) / prob_implicita * 100
            
            # Determinar tipo de recomendação
            recomendacao_tipo = ""
            recomendacao_icone = ""
            explicacao = ""
            
            if probabilidade > prob_implicita:
                if vantagem >= 10.0 and probabilidade >= 0.30:
                    # Recomendação FORTE
                    recomendacao_tipo = "VALUE BET FORTE RECOMENDADO"
                    recomendacao_icone = "🔥✅"
                    explicacao = "   (Value >= 10% + Prob >= 30%)"
                elif vantagem >= 20.0 and probabilidade < 0.30:
                    # Recomendação ARRISCADA
                    recomendacao_tipo = "VALUE BET ARRISCADO"
                    recomendacao_icone = "⚡⚠️"
                    explicacao = "   (Value >= 20% + Prob < 30% - RISCO ALTO!)"
                else:
                    # Não recomendado
                    recomendacao_tipo = "NÃO RECOMENDADO"
                    recomendacao_icone = "❌"
                    explicacao = "   (Precisa: Value >= 10% + Prob >= 30% OU Value >= 20%)"
            else:
                recomendacao_tipo = "NÃO RECOMENDADO"
                recomendacao_icone = "❌"
                explicacao = "   (Sem value bet positivo)"
            
            resultado = f"""
ANÁLISE DA APOSTA SIMPLES
{'='*50}

🎮 Confronto: {time_a} vs {time_b}
{info_tipo_aposta}
🎯 Aposta: {tipo_aposta}
💰 Valor apostado: R$ {valor:.2f}
📊 Odd: {odd:.2f}
🏟️ Vantagem de casa: {'Aplicada (+15%)' if aplicar_fator_casa else 'Não aplicada'}
{info_placar_apostas}

📈 PROBABILIDADES:
• Nossa probabilidade: {probabilidade:.1%}
• Probabilidade implícita: {prob_implicita:.1%}
• {recomendacao_icone} {recomendacao_tipo}: {vantagem:+.1f}%
{explicacao}

💵 RETORNOS:
• Retorno total: R$ {retorno_potencial:.2f}
• Lucro potencial: R$ {lucro_potencial:.2f}
• Retorno sobre investimento: {(lucro_potencial/valor)*100:.1f}%

{'='*50}
"""
            
            messagebox.showinfo("Resultado da Aposta", resultado)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no cálculo: {str(e)}")
    
    def adicionar_multipla(self):
        """Adiciona aposta à lista de múltiplas"""
        try:
            time_a = self.combo_aposta_time_a.get()
            time_b = self.combo_aposta_time_b.get()
            tipo_aposta = self.combo_tipo_aposta.get()
            odd = float(self.entry_aposta_odd.get().replace(',', '.'))
            
            if not all([time_a, time_b, tipo_aposta]):
                messagebox.showwarning("Aviso", "Preencha todos os campos!")
                return
            
            # Calcular probabilidade usando configuração atual do fator casa
            dados_time_a = self.times_database[time_a]
            dados_time_b = self.times_database[time_b]
            
            # Verificar tipo de dados selecionado
            tipo_dados = self.var_tipo_dados_aposta.get()
            
            # Preparar dados baseado no tipo selecionado
            if tipo_dados == "casa_fora":
                # Usar dados específicos casa/fora
                dados_a = self._obter_dados_casa_fora(dados_time_a, "casa")
                dados_b = self._obter_dados_casa_fora(dados_time_b, "fora")
                info_tipo_aposta = "📊 Dados: CASA/FORA"
                
                # Verificar se os dados são válidos
                if any(v is None for v in [dados_a['gols_marcados'], dados_a['gols_sofridos'], 
                                         dados_b['gols_marcados'], dados_b['gols_sofridos']]):
                    messagebox.showwarning("Aviso", "Dados casa/fora indisponíveis. Usando dados gerais.")
                    dados_a = dados_time_a
                    dados_b = dados_time_b
                    info_tipo_aposta = "📊 Dados: GERAIS (fallback)"
            else:
                # Usar dados gerais
                dados_a = dados_time_a
                dados_b = dados_time_b
                info_tipo_aposta = "📊 Dados: GERAIS"
            
            aplicar_fator_casa = self.var_fator_casa_apostas.get()
            
            gols_esp_a, gols_esp_b = self.calcular_gols_esperados(dados_a, dados_b, aplicar_fator_casa)
            
            # Verificar se o placar ao vivo está ativo nas apostas
            placar_apostas_ativo = self.var_placar_apostas_ativo.get()
            
            if placar_apostas_ativo:
                try:
                    gols_atuais_a = int(self.entry_gols_apostas_a.get() or 0)
                    gols_atuais_b = int(self.entry_gols_apostas_b.get() or 0)
                    tempo_atual = int(self.entry_tempo_apostas.get() or 0)
                    
                    # Calcular probabilidades com placar ao vivo
                    prob_a, prob_empate, prob_b = self.calcular_probabilidades_com_placar_ao_vivo(
                        gols_esp_a, gols_esp_b, gols_atuais_a, gols_atuais_b, tempo_atual
                    )
                    
                except ValueError:
                    messagebox.showerror("Erro", "Por favor, insira valores válidos para o placar ao vivo!")
                    return
            else:
                # Calcular probabilidades normais
                prob_a, prob_empate, prob_b = self.calcular_probabilidades_poisson(gols_esp_a, gols_esp_b)
            
            prob_map = {
                "Vitória A": prob_a,
                "Empate": prob_empate,
                "Vitória B": prob_b
            }
            
            probabilidade = prob_map[tipo_aposta]
            
            # Adicionar à lista
            aposta = {
                'confronto': f"{time_a} vs {time_b}",
                'tipo': tipo_aposta,
                'odd': odd,
                'probabilidade': probabilidade,
                'tipo_dados': info_tipo_aposta
            }
            
            self.apostas_ativas.append(aposta)
            
            # Atualizar tree
            confronto_com_info = f"{aposta['confronto']} ({info_tipo_aposta.replace('📊 Dados: ', '')})"
            self.tree_apostas.insert('', 'end', values=(
                confronto_com_info,
                aposta['tipo'],
                f"{aposta['odd']:.2f}",
                f"{aposta['probabilidade']:.1%}"
            ))
            
            messagebox.showinfo("Sucesso", f"Aposta adicionada à múltipla!\n{info_tipo_aposta}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar aposta: {str(e)}")
    
    def calcular_multipla(self):
        """Calcula o resultado da aposta múltipla"""
        try:
            if not self.apostas_ativas:
                messagebox.showwarning("Aviso", "Adicione pelo menos uma aposta!")
                return
            
            valor_total = float(self.entry_valor_multipla.get().replace(',', '.'))
            
            # Calcular odd total e probabilidade combinada
            odd_total = 1
            prob_combinada = 1
            
            for aposta in self.apostas_ativas:
                odd_total *= aposta['odd']
                prob_combinada *= aposta['probabilidade']
            
            retorno_potencial = valor_total * odd_total
            lucro_potencial = retorno_potencial - valor_total
            
            # Exibir resultado
            aplicar_fator_casa = self.var_fator_casa_apostas.get()
            placar_apostas_ativo = self.var_placar_apostas_ativo.get()
            
            resultado_texto = f"""
MÚLTIPLA: {len(self.apostas_ativas)} apostas
🏟️ Vantagem de casa: {'Aplicada (+15%)' if aplicar_fator_casa else 'Não aplicada'}
📺 Placar ao vivo: {'Ativado' if placar_apostas_ativo else 'Desativado'}
Odd total: {odd_total:.2f}
Probabilidade: {prob_combinada:.1%}
Retorno: R$ {retorno_potencial:.2f}
Lucro: R$ {lucro_potencial:.2f}
"""
            
            self.label_resultado_multipla.config(text=resultado_texto)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no cálculo: {str(e)}")
    
    def limpar_apostas(self):
        """Limpa a lista de apostas"""
        self.apostas_ativas = []
        for item in self.tree_apostas.get_children():
            self.tree_apostas.delete(item)
        self.label_resultado_multipla.config(text="")
    
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas gerais"""
        if not self.times_database:
            self.text_historico.delete(1.0, tk.END)
            self.text_historico.insert(1.0, "Nenhum time cadastrado ainda.")
            return
        
        # Calcular estatísticas
        total_times = len(self.times_database)
        
        # Filtrar valores válidos para cálculos
        gols_marcados_validos = [dados.get('gols_marcados', 0) or 0 for dados in self.times_database.values()]
        gols_sofridos_validos = [dados.get('gols_sofridos', 0) or 0 for dados in self.times_database.values()]
        
        media_gols_marcados = sum(gols_marcados_validos) / total_times if total_times > 0 else 0
        media_gols_sofridos = sum(gols_sofridos_validos) / total_times if total_times > 0 else 0
        
        # Times mais ofensivos e defensivos (com verificação de None)
        times_com_gols_validos = [(nome, dados) for nome, dados in self.times_database.items() 
                                if dados.get('gols_marcados') is not None]
        times_com_def_valida = [(nome, dados) for nome, dados in self.times_database.items() 
                               if dados.get('gols_sofridos') is not None]
        
        if times_com_gols_validos:
            time_mais_ofensivo = max(times_com_gols_validos, key=lambda x: x[1]['gols_marcados'])
        else:
            time_mais_ofensivo = ("N/A", {"gols_marcados": 0})
            
        if times_com_def_valida:
            time_mais_defensivo = min(times_com_def_valida, key=lambda x: x[1]['gols_sofridos'])
        else:
            time_mais_defensivo = ("N/A", {"gols_sofridos": 0})
        
        # Ligas representadas
        ligas = set(dados.get('liga', 'N/A') for dados in self.times_database.values() if dados.get('liga'))
        
        estatisticas = f"""
ESTATÍSTICAS GERAIS DO BANCO DE DADOS
{'='*60}

📊 RESUMO GERAL:
• Total de times cadastrados: {total_times}
• Média de gols marcados: {media_gols_marcados:.2f}
• Média de gols sofridos: {media_gols_sofridos:.2f}
• Ligas representadas: {len(ligas)}

🏆 DESTAQUES:
• Time mais ofensivo: {time_mais_ofensivo[0]} ({time_mais_ofensivo[1]['gols_marcados']:.2f} gols/jogo)
• Time mais defensivo: {time_mais_defensivo[0]} ({time_mais_defensivo[1]['gols_sofridos']:.2f} gols sofridos/jogo)

🏟️ LIGAS CADASTRADAS:
{chr(10).join(f"• {liga}" for liga in sorted(ligas))}

📋 TODOS OS TIMES:
{'─'*80}
"""
        
        # Lista detalhada dos times
        for nome, dados in sorted(self.times_database.items()):
            forca_ofensiva = dados.get('forca_ofensiva', dados['gols_marcados'] / 1.2)
            forca_defensiva = dados.get('forca_defensiva', dados['gols_sofridos'] / 1.2)
            estatisticas += f"""
{nome}:
  📈 Gols marcados: {dados['gols_marcados']:.2f}/jogo
  📉 Gols sofridos: {dados['gols_sofridos']:.2f}/jogo
  ⚔️  Força ofensiva: {forca_ofensiva:.2f}
  🛡️  Força defensiva: {forca_defensiva:.2f}
  🏆 Liga: {dados['liga']}
  📅 Cadastrado em: {dados.get('data_cadastro', 'N/A')[:10]}
"""
        
        self.text_historico.delete(1.0, tk.END)
        self.text_historico.insert(1.0, estatisticas)
    
    def salvar_dados(self):
        """Salva os dados em arquivo JSON"""
        try:
            # Determinar caminho da pasta data
            pasta_atual = os.path.dirname(os.path.abspath(__file__))
            pasta_pai = os.path.dirname(pasta_atual)
            pasta_data = os.path.join(pasta_pai, 'data')
            arquivo_times = os.path.join(pasta_data, 'times_database.json')
            
            with open(arquivo_times, 'w', encoding='utf-8') as f:
                json.dump(self.times_database, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
    
    def carregar_dados(self):
        """Carrega os dados do arquivo JSON"""
        try:
            # Determinar caminho da pasta data
            pasta_atual = os.path.dirname(os.path.abspath(__file__))
            pasta_pai = os.path.dirname(pasta_atual)
            pasta_data = os.path.join(pasta_pai, 'data')
            arquivo_times = os.path.join(pasta_data, 'times_database.json')
            
            if os.path.exists(arquivo_times):
                with open(arquivo_times, 'r', encoding='utf-8') as f:
                    self.times_database = json.load(f)
                self.atualizar_lista_times()
                self.atualizar_comboboxes()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
    
    def exportar_dados(self):
        """Exporta os dados para arquivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_times_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.times_database, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Sucesso", f"Dados exportados para {filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")
    
    def exportar_relatorio(self):
        """Exporta relatório completo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_completo_{timestamp}.txt"
            
            content = self.text_historico.get(1.0, tk.END)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("Sucesso", f"Relatório exportado para {filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar relatório: {str(e)}")
    
    def editar_time(self):
        """Edita o time selecionado"""
        selected = self.tree_times.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um time para editar!")
            return
        
        item = self.tree_times.item(selected[0])
        nome_time = item['values'][0]
        dados = self.times_database[nome_time]
        
        # Preencher campos com dados atuais
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, nome_time)
        
        self.entry_gols_marcados.delete(0, tk.END)
        self.entry_gols_marcados.insert(0, str(dados['gols_marcados']))
        
        self.entry_gols_sofridos.delete(0, tk.END)
        self.entry_gols_sofridos.insert(0, str(dados['gols_sofridos']))
        
        self.entry_liga.delete(0, tk.END)
        self.entry_liga.insert(0, dados['liga'])
    
    # ========== MÉTODOS DA API RADAR ESPORTIVO ==========
    
    def atualizar_opcoes_estatisticas(self):
        """Atualiza a disponibilidade das opções de estatísticas"""
        # Método placeholder para callback do checkbox
        pass
    
    def buscar_estatisticas_reais_jogo(self, match_id):
        """
        Busca estatísticas reais dos times de um jogo específico
        
        Args:
            match_id: ID da partida
        
        Returns:
            dict: Estatísticas dos times ou None
        """
        try:
            usar_mesmo_campo = self.var_mesmo_campo.get()
            
            print(f"📊 Buscando estatísticas reais para Match ID: {match_id}")
            print(f"Modo: {'Mesmo campo' if usar_mesmo_campo else 'Qualquer campo'}")
            
            # Buscar estatísticas usando a API
            stats = self.api.buscar_estatisticas_confronto(match_id, usar_mesmo_campo)
            
            if stats:
                return {
                    'stats_casa': {
                        'gols_marcados': stats['time_casa']['media_gols_marcados'],
                        'gols_sofridos': stats['time_casa']['media_gols_sofridos'],
                        'forca_ofensiva': stats['time_casa']['forca_ofensiva'],
                        'forca_defensiva': stats['time_casa']['forca_defensiva'],
                        'detalhes': stats['time_casa']
                    },
                    'stats_visitante': {
                        'gols_marcados': stats['time_visitante']['media_gols_marcados'],
                        'gols_sofridos': stats['time_visitante']['media_gols_sofridos'],
                        'forca_ofensiva': stats['time_visitante']['forca_ofensiva'],
                        'forca_defensiva': stats['time_visitante']['forca_defensiva'],
                        'detalhes': stats['time_visitante']
                    },
                    'modo': stats['mode'],
                    'usar_mesmo_campo': usar_mesmo_campo
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas reais: {str(e)}")
            return None
    
    def carregar_jogos_do_dia(self):
        """Carrega jogos do dia atual via Radar Esportivo API (método de compatibilidade)"""
        # Definir data de hoje no campo
        self.definir_data_hoje()
        # Chamar o método principal
        self.carregar_jogos_da_data()
    
    def _executar_carregamento_jogos(self):
        """Executa o carregamento dos jogos em thread separada"""
        try:
            # Buscar jogos na API
            jogos_encontrados = self.api.buscar_jogos_do_dia()
            
            # Atualizar interface na thread principal
            self.root.after(0, self._atualizar_jogos_do_dia, jogos_encontrados)
            
        except Exception as e:
            # Mostrar erro na thread principal
            self.root.after(0, self._mostrar_erro_jogos, str(e))
    
    def _atualizar_jogos_do_dia(self, jogos_encontrados):
        """Atualiza a interface com os jogos do dia"""
        # Reabilitar botão
        self.btn_carregar_jogos.config(state='normal', text="� Carregar Jogos do Dia")
        
        if not jogos_encontrados:
            self.label_status_jogos.config(text="Nenhum jogo encontrado para hoje")
            return
        
        # Armazenar jogos para uso posterior
        self.jogos_do_dia = jogos_encontrados
        
        # Limpar lista atual
        for item in self.tree_jogos.get_children():
            self.tree_jogos.delete(item)
        
        # Verificar se há filtro ativo
        termo_pesquisa = ""
        if hasattr(self, 'entry_pesquisa_jogos'):
            termo_pesquisa = self.entry_pesquisa_jogos.get().lower()
        
        # Adicionar jogos à tabela (filtrados se houver termo de pesquisa)
        jogos_mostrados = 0
        for jogo in jogos_encontrados:
            # Aplicar filtro se houver termo de pesquisa
            if termo_pesquisa:
                if not (termo_pesquisa in jogo['time_casa'].lower() or 
                       termo_pesquisa in jogo['time_visitante'].lower() or
                       termo_pesquisa in jogo['liga'].lower() or
                       termo_pesquisa in jogo['status'].lower()):
                    continue
            
            # Inserir jogo na árvore
            item_id = self.tree_jogos.insert('', 'end', text='☐', values=(
                jogo['liga'],
                jogo['time_casa'],
                jogo['time_visitante'],
                jogo['horario'],
                jogo['status']
            ))
            jogos_mostrados += 1
        
        # Atualizar status
        total = len(jogos_encontrados)
        self.label_status_jogos.config(text=f"✅ {total} jogo(s) encontrado(s) para hoje")
        
        # Atualizar contagem se o label existir
        if hasattr(self, 'label_contagem_jogos'):
            if termo_pesquisa:
                self.label_contagem_jogos.config(text=f"Mostrando {jogos_mostrados} de {total} jogos")
            else:
                self.label_contagem_jogos.config(text=f"Total: {total} jogos")
    
    def _mostrar_erro_jogos(self, erro):
        """Mostra erro do carregamento na interface"""
        self.btn_carregar_jogos.config(state='normal', text="🔄 Carregar Jogos do Dia")
        self.label_status_jogos.config(text=f"❌ Erro no carregamento: {erro}")
        messagebox.showerror("Erro na API", f"Erro ao carregar jogos:\n{erro}")
    
    def toggle_jogo_selecao(self, event):
        """Alterna seleção de um jogo na lista"""
        item = self.tree_jogos.identify('item', event.x, event.y)
        column = self.tree_jogos.identify('column', event.x, event.y)
        
        if item and column == '#0':  # Clicou na coluna de seleção
            current_text = self.tree_jogos.item(item, 'text')
            if item in self.jogos_selecionados:
                # Desmarcar
                self.jogos_selecionados.remove(item)
                self.tree_jogos.item(item, text='☐')
            else:
                # Marcar
                self.jogos_selecionados.add(item)
                self.tree_jogos.item(item, text='☑')
            
            # Atualizar botões
            if self.jogos_selecionados:
                self.btn_simular_selecionados.config(state='normal')
                self.btn_cadastrar_times.config(state='normal')
            else:
                self.btn_simular_selecionados.config(state='disabled')
                self.btn_cadastrar_times.config(state='disabled')
                
        elif item:  # Clicou em outra coluna - mostrar informações
            self._mostrar_info_jogo(item)
    
    def _mostrar_info_jogo(self, item):
        """Mostra informações detalhadas do jogo selecionado"""
        try:
            # Encontrar o jogo correspondente
            valores = self.tree_jogos.item(item)['values']
            if not valores:
                return
                
            liga, time_casa, time_visitante, horario, status = valores
            
            # Encontrar o jogo completo nos dados
            jogo_completo = None
            for jogo in self.jogos_do_dia:
                if (jogo['liga'] == liga and 
                    jogo['time_casa'] == time_casa and 
                    jogo['time_visitante'] == time_visitante):
                    jogo_completo = jogo
                    break
            
            if jogo_completo:
                info_text = f"""Liga: {jogo_completo['liga']}
Partida: {jogo_completo['time_casa']} vs {jogo_completo['time_visitante']}
Horário: {jogo_completo['horario']}
Status: {jogo_completo['status']}

Estatísticas estimadas:
• {jogo_completo['time_casa']}: {jogo_completo['stats_casa']['gols_marcados']:.2f} gols/jogo (marcados), {jogo_completo['stats_casa']['gols_sofridos']:.2f} gols/jogo (sofridos)
• {jogo_completo['time_visitante']}: {jogo_completo['stats_visitante']['gols_marcados']:.2f} gols/jogo (marcados), {jogo_completo['stats_visitante']['gols_sofridos']:.2f} gols/jogo (sofridos)"""
                
                self.text_info_jogo.delete(1.0, tk.END)
                self.text_info_jogo.insert(1.0, info_text)
            
        except Exception as e:
            self.text_info_jogo.delete(1.0, tk.END)
            self.text_info_jogo.insert(1.0, f"Erro ao carregar informações: {e}")
    
    def simular_jogos_selecionados(self):
        """Simula os jogos selecionados usando dados da API Radar Esportivo"""
        if not self.jogos_selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um jogo para simular!")
            return
        
        # Confirmar simulação
        if not messagebox.askyesno("Confirmação", 
                                  f"Simular {len(self.jogos_selecionados)} jogo(s) selecionado(s)?\n\n" +
                                  "A simulação usará os dados de gols esperados\n" +
                                  "fornecidos pela API do Radar Esportivo."):
            return
        
        jogos_para_simular = []
        
        # Coletar dados dos jogos selecionados
        for item_id in self.jogos_selecionados:
            valores = self.tree_jogos.item(item_id)['values']
            if valores:
                liga, time_casa, time_visitante, horario, status = valores
                
                # Encontrar o jogo completo
                jogo_encontrado = None
                for jogo in self.jogos_do_dia:
                    if (jogo['liga'] == liga and 
                        jogo['time_casa'] == time_casa and 
                        jogo['time_visitante'] == time_visitante):
                        jogo_encontrado = jogo
                        break
                
                if jogo_encontrado:
                    # Adicionar jogo para simulação com dados da API
                    jogo_processado = {
                        'id': jogo_encontrado['id'],
                        'time_casa': time_casa,
                        'time_visitante': time_visitante,
                        'liga': liga,
                        'horario': horario,
                        'status': status,
                        'stats_casa': jogo_encontrado['stats_casa'],
                        'stats_visitante': jogo_encontrado['stats_visitante'],
                        'fonte_dados': "Radar Esportivo API - Gols Esperados"
                    }
                    jogos_para_simular.append(jogo_processado)
        
        if not jogos_para_simular:
            messagebox.showerror("Erro", "Erro ao processar jogos selecionados!")
            return
        
        # Simular cada jogo usando dados da API
        resultados_simulacao = []
        for jogo in jogos_para_simular:
            try:
                # Realizar simulação baseada nos dados da API
                resultado = self._simular_confronto_radar_api(jogo)
                if resultado:
                    resultados_simulacao.append({
                        'jogo': f"{jogo['time_casa']} vs {jogo['time_visitante']}",
                        'resultado': resultado,
                        'fonte_dados': jogo['fonte_dados']
                    })
            except Exception as e:
                print(f"Erro ao simular {jogo['time_casa']} vs {jogo['time_visitante']}: {e}")
        
        # Mostrar resultados
        self._mostrar_resultados_simulacao_radar(resultados_simulacao)
    
    def _simular_confronto_radar_api(self, jogo):
        """Simula um confronto usando dados da API Radar Esportivo"""
        try:
            stats_casa = jogo['stats_casa']
            stats_visitante = jogo['stats_visitante']
            
            # Usar médias de gols da API com verificação de None
            media_casa = stats_casa['gols_marcados']
            media_visitante = stats_visitante['gols_marcados']
            
            # Verificar se os valores não são None
            if media_casa is None or media_visitante is None:
                print(f"⚠️ Dados inválidos para simulação: casa={media_casa}, visitante={media_visitante}")
                return None
                
            # Garantir que sejam valores numéricos positivos
            media_casa = max(0.1, float(media_casa))
            media_visitante = max(0.1, float(media_visitante))
            
            # Calcular probabilidades usando Poisson
            from math import factorial, exp
            
            def poisson_prob(k, lam):
                return (lam**k * exp(-lam)) / factorial(k)
            
            # Calcular probabilidades de resultado
            prob_casa = 0
            prob_empate = 0
            prob_visitante = 0
            
            for gols_casa in range(6):
                for gols_visitante in range(6):
                    prob = poisson_prob(gols_casa, media_casa) * poisson_prob(gols_visitante, media_visitante)
                    
                    if gols_casa > gols_visitante:
                        prob_casa += prob
                    elif gols_casa == gols_visitante:
                        prob_empate += prob
                    else:
                        prob_visitante += prob
            
            # Calcular probabilidades de mercados
            prob_over15 = 0
            prob_over25 = 0
            prob_btts = 0
            
            for gols_casa in range(8):
                for gols_visitante in range(8):
                    prob = poisson_prob(gols_casa, media_casa) * poisson_prob(gols_visitante, media_visitante)
                    total_gols = gols_casa + gols_visitante
                    
                    if total_gols > 1.5:
                        prob_over15 += prob
                    if total_gols > 2.5:
                        prob_over25 += prob
                    if gols_casa > 0 and gols_visitante > 0:
                        prob_btts += prob
            
            return {
                'media_gols_casa': media_casa,
                'media_gols_visitante': media_visitante,
                'media_gols_sofridos_casa': stats_casa['gols_sofridos'],
                'media_gols_sofridos_visitante': stats_visitante['gols_sofridos'],
                'prob_vitoria_casa': prob_casa,
                'prob_empate': prob_empate,
                'prob_vitoria_visitante': prob_visitante,
                'prob_over15': prob_over15,
                'prob_over25': prob_over25,
                'prob_btts': prob_btts,
                'total_gols_esperados': media_casa + media_visitante
            }
            
        except Exception as e:
            print(f"Erro na simulação da API: {e}")
            return None
    
    def _mostrar_resultados_simulacao_radar(self, resultados):
        """Mostra os resultados da simulação baseada na API Radar Esportivo"""
        janela = tk.Toplevel(self.root)
        janela.title("Simulação - Radar Esportivo API")
        janela.geometry("700x600")
        janela.transient(self.root)
        janela.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(janela)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="📊 Simulação - Dados Radar Esportivo", 
                 style='Title.TLabel').pack(pady=10)
        
        if not resultados:
            ttk.Label(main_frame, text="⚠️ Nenhum resultado obtido", 
                     style='Subtitle.TLabel').pack(pady=20)
            ttk.Button(main_frame, text="Fechar", command=janela.destroy).pack(pady=10)
            return
        
        # Informações gerais
        info_frame = ttk.LabelFrame(main_frame, text="Informações", padding=10)
        info_frame.pack(fill='x', pady=10)
        
        info_text = f"✅ {len(resultados)} jogo(s) simulado(s)\n"
        info_text += f"📊 Fonte: Dados de gols esperados da API Radar Esportivo\n"
        info_text += f"🧮 Método: Distribuição de Poisson"
        
        ttk.Label(info_frame, text=info_text).pack()
        
        # Resultados
        result_frame = ttk.LabelFrame(main_frame, text="Resultados das Simulações", padding=10)
        result_frame.pack(fill='both', expand=True, pady=10)
        
        # Text widget com scrollbar
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill='both', expand=True)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Arial', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Adicionar resultados
        for i, resultado in enumerate(resultados, 1):
            jogo_info = resultado['jogo']
            dados = resultado['resultado']
            fonte = resultado.get('fonte_dados', 'API')
            
            texto = f"🏆 {i}. {jogo_info}\n"
            texto += f"📊 Fonte: {fonte}\n\n"
            
            # Médias de gols
            texto += f"⚽ Gols Esperados:\n"
            texto += f"   • Casa: {dados['media_gols_casa']:.2f} gols\n"
            texto += f"   • Visitante: {dados['media_gols_visitante']:.2f} gols\n"
            texto += f"   • Total: {dados['total_gols_esperados']:.2f} gols\n\n"
            
            # Probabilidades de resultado
            texto += f"🎯 Probabilidades de Resultado:\n"
            texto += f"   • Vitória Casa: {dados['prob_vitoria_casa']:.1%}\n"
            texto += f"   • Empate: {dados['prob_empate']:.1%}\n"
            texto += f"   • Vitória Visitante: {dados['prob_vitoria_visitante']:.1%}\n\n"
            
            # Mercados populares
            texto += f"💰 Mercados Populares:\n"
            texto += f"   • Over 1.5 gols: {dados['prob_over15']:.1%}\n"
            texto += f"   • Over 2.5 gols: {dados['prob_over25']:.1%}\n"
            texto += f"   • Ambos marcam (BTTS): {dados['prob_btts']:.1%}\n\n"
            
            # Análise defensiva
            texto += f"🛡️ Análise Defensiva:\n"
            texto += f"   • Casa sofre em média: {dados['media_gols_sofridos_casa']:.2f} gols\n"
            texto += f"   • Visitante sofre em média: {dados['media_gols_sofridos_visitante']:.2f} gols\n"
            
            texto += f"{'-'*60}\n\n"
            
            text_widget.insert(tk.END, texto)
        
        text_widget.config(state='disabled')
        
        # Botão para fechar
        ttk.Button(main_frame, text="Fechar", command=janela.destroy).pack(pady=10)
    
    def _simular_confronto_automatico(self, time_casa, time_visitante):
        """Simula um confronto automaticamente usando as estatísticas dos times"""
        try:
            if time_casa not in self.times_database or time_visitante not in self.times_database:
                return None
            
            stats_casa = self.times_database[time_casa]
            stats_visitante = self.times_database[time_visitante]
            
            # Calcular probabilidades usando Poisson
            from math import factorial, exp
            
            def poisson_prob(k, lam):
                return (lam**k * exp(-lam)) / factorial(k)
            
            # Médias de gols esperadas com verificação de None
            gols_marcados_casa = stats_casa.get('gols_marcados', 0)
            gols_sofridos_visitante = stats_visitante.get('gols_sofridos', 0)
            gols_marcados_visitante = stats_visitante.get('gols_marcados', 0)
            gols_sofridos_casa = stats_casa.get('gols_sofridos', 0)
            
            # Verificar se os valores não são None
            if any(v is None for v in [gols_marcados_casa, gols_sofridos_visitante, gols_marcados_visitante, gols_sofridos_casa]):
                print(f"⚠️ Dados inválidos para simulação automática")
                return None
            
            # Garantir que sejam valores numéricos
            gols_marcados_casa = float(gols_marcados_casa)
            gols_sofridos_visitante = float(gols_sofridos_visitante)
            gols_marcados_visitante = float(gols_marcados_visitante)
            gols_sofridos_casa = float(gols_sofridos_casa)
            
            media_casa = (gols_marcados_casa + gols_sofridos_visitante) / 2
            media_visitante = (gols_marcados_visitante + gols_sofridos_casa) / 2
            
            # Garantir valores mínimos para evitar divisão por zero
            media_casa = max(0.1, media_casa)
            media_visitante = max(0.1, media_visitante)
            
            # Calcular probabilidades de vitória
            prob_casa = 0
            prob_empate = 0
            prob_visitante = 0
            
            for gols_casa in range(6):
                for gols_visitante in range(6):
                    prob = poisson_prob(gols_casa, media_casa) * poisson_prob(gols_visitante, media_visitante)
                    
                    if gols_casa > gols_visitante:
                        prob_casa += prob
                    elif gols_casa == gols_visitante:
                        prob_empate += prob
                    else:
                        prob_visitante += prob
            
            return {
                'media_gols_casa': media_casa,
                'media_gols_visitante': media_visitante,
                'prob_vitoria_casa': prob_casa,
                'prob_empate': prob_empate,
                'prob_vitoria_visitante': prob_visitante
            }
            
        except Exception as e:
            print(f"Erro na simulação automática: {e}")
            return None
    
    def _mostrar_resultados_simulacao(self, resultados, times_adicionados):
        """Mostra os resultados da simulação em uma janela"""
        janela = tk.Toplevel(self.root)
        janela.title("Resultados da Simulação")
        janela.geometry("600x500")
        janela.transient(self.root)
        janela.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(janela)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="Resultados da Simulação Automática", 
                 style='Title.TLabel').pack(pady=10)
        
        # Informações sobre times adicionados
        if times_adicionados:
            info_frame = ttk.LabelFrame(main_frame, text="Times Adicionados", padding=10)
            info_frame.pack(fill='x', pady=10)
            
            info_text = f"✅ {len(times_adicionados)} time(s) adicionado(s) automaticamente:\n"
            info_text += ", ".join(times_adicionados)
            info_text += "\n\n💡 As listas de times foram atualizadas automaticamente nas abas 'Confrontos' e 'Apostas'"
            
            info_label = ttk.Label(info_frame, text=info_text, wraplength=550)
            info_label.pack()
        
        # Resultados das simulações
        if resultados:
            result_frame = ttk.LabelFrame(main_frame, text="Análises dos Confrontos", padding=10)
            result_frame.pack(fill='both', expand=True, pady=10)
            
            # Text widget com scrollbar
            text_frame = ttk.Frame(result_frame)
            text_frame.pack(fill='both', expand=True)
            
            text_widget = tk.Text(text_frame, wrap='word', font=('Arial', 10))
            scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Adicionar resultados
            for resultado in resultados:
                jogo_info = resultado['jogo']
                dados = resultado['resultado']
                fonte = resultado.get('fonte_dados', 'Estimado')
                
                texto = f"🔥 {jogo_info}\n"
                texto += f"📊 Fonte dos dados: {fonte}\n"
                texto += f"Média de gols esperada - Casa: {dados['media_gols_casa']:.2f} | Visitante: {dados['media_gols_visitante']:.2f}\n"
                texto += f"Probabilidades:\n"
                texto += f"• Vitória Casa: {dados['prob_vitoria_casa']:.1%}\n"
                texto += f"• Empate: {dados['prob_empate']:.1%}\n"
                texto += f"• Vitória Visitante: {dados['prob_vitoria_visitante']:.1%}\n"
                
                # Adicionar detalhes extras se disponíveis
                if 'detalhes_extras' in resultado:
                    detalhes = resultado['detalhes_extras']
                    texto += f"\n📈 Detalhes adicionais:\n"
                    if 'casa' in detalhes:
                        casa_det = detalhes['casa']
                        texto += f"• Casa: {casa_det.get('vitorias', 0)}V {casa_det.get('empates', 0)}E {casa_det.get('derrotas', 0)}D "
                        texto += f"({casa_det.get('perc_vitorias', 0):.0f}% vitórias)\n"
                    if 'visitante' in detalhes:
                        vis_det = detalhes['visitante']
                        texto += f"• Visitante: {vis_det.get('vitorias', 0)}V {vis_det.get('empates', 0)}E {vis_det.get('derrotas', 0)}D "
                        texto += f"({vis_det.get('perc_vitorias', 0):.0f}% vitórias)\n"
                
                texto += f"{'-'*50}\n\n"
                
                text_widget.insert(tk.END, texto)
            
            text_widget.config(state='disabled')
        
        # Botão para fechar
        ttk.Button(main_frame, text="Fechar", command=janela.destroy).pack(pady=10)
    
    def cadastrar_times_selecionados(self):
        """Cadastra os times dos jogos selecionados usando estatísticas das últimas 10 partidas"""
        if not self.jogos_selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um jogo para cadastrar os times!")
            return
        
        # Confirmar a ação
        if not messagebox.askyesno("Confirmação", 
                                  f"Cadastrar times de {len(self.jogos_selecionados)} jogo(s) selecionado(s)?\n\n" +
                                  "Os times serão cadastrados com estatísticas das últimas 10 partidas,\n" +
                                  "incluindo dados separados para casa/fora e dados gerais."):
            return
        
        # Iniciar processo em thread separada para não travar a interface
        threading.Thread(target=self._executar_cadastro_times_detalhado, daemon=True).start()
    
    def _executar_cadastro_times_detalhado(self):
        """Executa o cadastro detalhado de times em thread separada"""
        try:
            times_processados = []
            times_com_erro = []
            
            for item_id in self.jogos_selecionados:
                valores = self.tree_jogos.item(item_id)['values']
                if valores:
                    liga, time_casa, time_visitante, horario, status = valores
                    
                    # Encontrar o jogo completo
                    jogo_encontrado = None
                    for jogo in self.jogos_do_dia:
                        if (jogo['liga'] == liga and 
                            jogo['time_casa'] == time_casa and 
                            jogo['time_visitante'] == time_visitante):
                            jogo_encontrado = jogo
                            break
                    
                    if jogo_encontrado:
                        match_id = jogo_encontrado['id']
                        
                        # Buscar estatísticas detalhadas
                        print(f"📊 Buscando estatísticas detalhadas para {time_casa} vs {time_visitante}")
                        stats_detalhadas = self.api.buscar_estatisticas_detalhadas_time(match_id)
                        
                        if stats_detalhadas:
                            # Processar time da casa
                            self._cadastrar_time_com_stats_detalhadas(
                                time_casa, 
                                stats_detalhadas['time_casa'], 
                                liga, 
                                'casa'
                            )
                            times_processados.append(f"{time_casa} (Casa)")
                            
                            # Processar time visitante
                            self._cadastrar_time_com_stats_detalhadas(
                                time_visitante,
                                stats_detalhadas['time_visitante'],
                                liga,
                                'visitante'
                            )
                            times_processados.append(f"{time_visitante} (Visitante)")
                            
                        else:
                            times_com_erro.append(f"{time_casa} vs {time_visitante}")
                        
                        # Pausa entre requisições
                        time.sleep(0.5)
            
            # Atualizar interface na thread principal
            self.root.after(0, self._finalizar_cadastro_times, times_processados, times_com_erro)
            
        except Exception as e:
            print(f"❌ Erro no cadastro de times: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro no cadastro de times: {e}"))
    
    def _cadastrar_time_com_stats_detalhadas(self, nome_time, stats_time, liga, tipo_time):
        """Cadastra um time com estatísticas detalhadas casa/fora"""
        try:
            # Verificar se time já existe
            if nome_time in self.times_database:
                # Atualizar dados existentes
                time_existente = self.times_database[nome_time]
                
                # Manter dados existentes se não tiver dados casa/fora
                if 'gols_marcados_casa' not in time_existente:
                    time_existente['gols_marcados_casa'] = 0.0
                    time_existente['gols_sofridos_casa'] = 0.0
                    time_existente['gols_marcados_fora'] = 0.0
                    time_existente['gols_sofridos_fora'] = 0.0
            else:
                # Criar novo time
                self.times_database[nome_time] = {
                    'nome': nome_time,
                    'liga': liga,
                    'origem': 'Radar Esportivo API - Estatísticas Detalhadas (10 últimas)',
                    'data_cadastro': datetime.now().isoformat(),
                    'gols_marcados_casa': 0.0,
                    'gols_sofridos_casa': 0.0,
                    'gols_marcados_fora': 0.0,
                    'gols_sofridos_fora': 0.0
                }
            
            # Atualizar estatísticas específicas
            time_data = self.times_database[nome_time]
            
            if tipo_time == 'casa':
                # Dados do time jogando em casa
                time_data['gols_marcados_casa'] = stats_time['casa']['gols_marcados']
                time_data['gols_sofridos_casa'] = stats_time['casa']['gols_sofridos']
                time_data['vitorias_casa'] = stats_time['casa']['vitorias']
                time_data['empates_casa'] = stats_time['casa']['empates']
                time_data['derrotas_casa'] = stats_time['casa']['derrotas']
                time_data['forma_casa'] = stats_time['casa']['forma']
            else:
                # Dados do time jogando fora
                time_data['gols_marcados_fora'] = stats_time['fora']['gols_marcados']
                time_data['gols_sofridos_fora'] = stats_time['fora']['gols_sofridos']
                time_data['vitorias_fora'] = stats_time['fora']['vitorias']
                time_data['empates_fora'] = stats_time['fora']['empates']
                time_data['derrotas_fora'] = stats_time['fora']['derrotas']
                time_data['forma_fora'] = stats_time['fora']['forma']
            
            # Dados gerais (sempre atualizar)
            time_data['gols_marcados'] = stats_time['geral']['gols_marcados']
            time_data['gols_sofridos'] = stats_time['geral']['gols_sofridos']
            time_data['vitorias'] = stats_time['geral']['vitorias']
            time_data['empates'] = stats_time['geral']['empates']
            time_data['derrotas'] = stats_time['geral']['derrotas']
            time_data['forma_geral'] = stats_time['geral']['forma']
            
            # Calcular forças (baseado em dados gerais)
            media_liga = 1.2
            time_data['forca_ofensiva'] = time_data['gols_marcados'] / media_liga
            time_data['forca_defensiva'] = time_data['gols_sofridos'] / media_liga
            
            # Adicionar estatísticas extras
            time_data['estatisticas_extras'] = {
                'btts_geral': stats_time['geral']['btts'],
                'over15_geral': stats_time['geral']['over15'],
                'over25_geral': stats_time['geral']['over25'],
                'partidas_analisadas': 10
            }
            
            # Adicionar dados casa/fora se disponíveis
            if tipo_time == 'casa':
                time_data['estatisticas_extras'].update({
                    'btts_casa': stats_time['casa']['btts'],
                    'over15_casa': stats_time['casa']['over15'],
                    'over25_casa': stats_time['casa']['over25']
                })
            else:
                time_data['estatisticas_extras'].update({
                    'btts_fora': stats_time['fora']['btts'],
                    'over15_fora': stats_time['fora']['over15'],
                    'over25_fora': stats_time['fora']['over25']
                })
            
            print(f"✅ {nome_time} cadastrado com estatísticas detalhadas ({tipo_time})")
            
        except Exception as e:
            print(f"❌ Erro ao cadastrar {nome_time}: {e}")
    
    def _finalizar_cadastro_times(self, times_processados, times_com_erro):
        """Finaliza o processo de cadastro de times"""
        try:
            # Salvar dados
            self.salvar_dados()
            
            # Atualizar listas
            self.atualizar_lista_times()
            self.atualizar_comboboxes()
            
            # Criar mensagem de resultado
            mensagem = f"Cadastro de times concluído!\n\n"
            
            if times_processados:
                mensagem += f"✅ {len(times_processados)} time(s) processado(s):\n"
                for time in times_processados[:10]:  # Mostrar apenas os primeiros 10
                    mensagem += f"• {time}\n"
                if len(times_processados) > 10:
                    mensagem += f"... e mais {len(times_processados) - 10} time(s)\n"
            
            if times_com_erro:
                mensagem += f"\n⚠️ {len(times_com_erro)} jogo(s) com erro:\n"
                for erro in times_com_erro[:5]:  # Mostrar apenas os primeiros 5
                    mensagem += f"• {erro}\n"
                if len(times_com_erro) > 5:
                    mensagem += f"... e mais {len(times_com_erro) - 5} erro(s)\n"
            
            mensagem += f"\n💡 Dados incluem estatísticas separadas para casa/fora e dados gerais"
            mensagem += f"\n🔄 Listas atualizadas automaticamente"
            
            messagebox.showinfo("Cadastro Concluído", mensagem)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao finalizar cadastro: {e}")
    
    def limpar_jogos_dia(self):
        """Limpa a lista de jogos do dia"""
        for item in self.tree_jogos.get_children():
            self.tree_jogos.delete(item)
        
        self.jogos_do_dia = []
        self.jogos_selecionados.clear()
        self.label_status_jogos.config(text="Selecione uma data e clique em 'Carregar Jogos' para buscar as partidas")
        self.btn_simular_selecionados.config(state='disabled')
        self.btn_cadastrar_times.config(state='disabled')
        
        # Limpar informações
        self.text_info_jogo.delete(1.0, tk.END)
        
        # Limpar campo de data se existir
        if hasattr(self, 'entry_data'):
            self.entry_data.delete(0, tk.END)
            self.label_contagem_jogos.config(text="")
    
    def filtrar_jogos(self, event=None):
        """Filtra a lista de jogos baseado no texto de pesquisa"""
        if not hasattr(self, 'jogos_do_dia') or not self.jogos_do_dia:
            return
            
        termo_pesquisa = self.entry_pesquisa_jogos.get().lower()
        
        # Limpar lista atual
        for item in self.tree_jogos.get_children():
            self.tree_jogos.delete(item)
        
        self.jogos_selecionados.clear()
        
        # Adicionar apenas jogos que correspondem à pesquisa
        jogos_filtrados = 0
        for jogo in self.jogos_do_dia:
            # Verificar se o termo está no nome dos times, liga ou status
            if (termo_pesquisa in jogo['time_casa'].lower() or 
                termo_pesquisa in jogo['time_visitante'].lower() or
                termo_pesquisa in jogo['liga'].lower() or
                termo_pesquisa in jogo['status'].lower()):
                
                # Inserir jogo na árvore
                item_id = self.tree_jogos.insert('', 'end', text='☐', values=(
                    jogo['liga'],
                    jogo['time_casa'],
                    jogo['time_visitante'],
                    jogo['horario'],
                    jogo['status']
                ))
                jogos_filtrados += 1
        
        # Atualizar contagem
        total_jogos = len(self.jogos_do_dia)
        if termo_pesquisa:
            self.label_contagem_jogos.config(text=f"Mostrando {jogos_filtrados} de {total_jogos} jogos")
        else:
            self.label_contagem_jogos.config(text=f"Total: {total_jogos} jogos")
        
        # Atualizar estado do botão de simulação
        self.btn_simular_selecionados.config(state='disabled')
    
    def limpar_pesquisa_jogos(self):
        """Limpa o campo de pesquisa de jogos e mostra todos os jogos"""
        self.entry_pesquisa_jogos.delete(0, tk.END)
        self._atualizar_jogos_do_dia(self.jogos_do_dia)
    
    def definir_data_hoje(self):
        """Define a data como hoje"""
        data_hoje = datetime.now().strftime('%d/%m/%Y')
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, data_hoje)
    
    def definir_data_ontem(self):
        """Define a data como ontem"""
        from datetime import timedelta
        data_ontem = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, data_ontem)
    
    def definir_data_amanha(self):
        """Define a data como amanhã"""
        from datetime import timedelta
        data_amanha = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, data_amanha)
    
    def validar_data(self, data_str):
        """Valida e converte string de data para formato da API (YYYY-MM-DD)"""
        try:
            # Tentar converter DD/MM/YYYY para YYYY-MM-DD
            data_obj = datetime.strptime(data_str, '%d/%m/%Y')
            return data_obj.strftime('%Y-%m-%d')
        except ValueError:
            try:
                # Tentar formato YYYY-MM-DD diretamente
                data_obj = datetime.strptime(data_str, '%Y-%m-%d')
                return data_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None
    
    def carregar_jogos_da_data(self):
        """Carrega jogos de uma data específica via Radar Esportivo API"""
        # Validar data
        data_str = self.entry_data.get().strip()
        if not data_str:
            messagebox.showwarning("Aviso", "Por favor, insira uma data!")
            return
        
        data_api = self.validar_data(data_str)
        if not data_api:
            messagebox.showerror("Erro", "Data inválida! Use o formato DD/MM/AAAA ou YYYY-MM-DD")
            return
        
        # Desabilitar botão e mostrar status
        self.btn_carregar_jogos.config(state='disabled', text="🔄 Carregando...")
        
        # Converter data para exibição
        try:
            data_obj = datetime.strptime(data_api, '%Y-%m-%d')
            data_exibicao = data_obj.strftime('%d/%m/%Y')
        except:
            data_exibicao = data_str
        
        self.label_status_jogos.config(text=f"Carregando jogos de {data_exibicao} da API Radar Esportivo...")
        
        # Limpar resultados anteriores
        for item in self.tree_jogos.get_children():
            self.tree_jogos.delete(item)
        self.jogos_selecionados.clear()
        self.btn_simular_selecionados.config(state='disabled')
        
        # Executar busca em thread separada para não travar a interface
        thread = threading.Thread(target=self._executar_carregamento_jogos_data, args=(data_api,))
        thread.daemon = True
        thread.start()
    
    def _executar_carregamento_jogos_data(self, data_api):
        """Executa o carregamento dos jogos de uma data específica em thread separada"""
        try:
            # Buscar jogos na API para a data específica
            jogos_encontrados = self.api.buscar_jogos_do_dia(data_api)
            
            # Atualizar interface na thread principal
            self.root.after(0, self._atualizar_jogos_da_data, jogos_encontrados, data_api)
            
        except Exception as e:
            # Mostrar erro na thread principal
            self.root.after(0, self._mostrar_erro_jogos_data, str(e), data_api)
    
    def _atualizar_jogos_da_data(self, jogos_encontrados, data_api):
        """Atualiza a interface com os jogos da data específica"""
        # Reabilitar botão
        self.btn_carregar_jogos.config(state='normal', text="🔄 Carregar Jogos da Data")
        
        # Converter data para exibição
        try:
            data_obj = datetime.strptime(data_api, '%Y-%m-%d')
            data_exibicao = data_obj.strftime('%d/%m/%Y')
        except:
            data_exibicao = data_api
        
        if not jogos_encontrados:
            self.label_status_jogos.config(text=f"Nenhum jogo encontrado para {data_exibicao}")
            if hasattr(self, 'label_contagem_jogos'):
                self.label_contagem_jogos.config(text="")
            return
        
        # Usar o método existente para atualizar a interface
        self._atualizar_jogos_do_dia(jogos_encontrados)
        
        # Atualizar status específico para a data
        total = len(jogos_encontrados)
        self.label_status_jogos.config(text=f"✅ {total} jogo(s) encontrado(s) para {data_exibicao}")
    
    def _mostrar_erro_jogos_data(self, erro, data_api):
        """Mostra erro do carregamento da data específica na interface"""
        self.btn_carregar_jogos.config(state='normal', text="🔄 Carregar Jogos da Data")
        
        # Converter data para exibição
        try:
            data_obj = datetime.strptime(data_api, '%Y-%m-%d')
            data_exibicao = data_obj.strftime('%d/%m/%Y')
        except:
            data_exibicao = data_api
            
        self.label_status_jogos.config(text=f"❌ Erro ao carregar jogos de {data_exibicao}: {erro}")
        messagebox.showerror("Erro na API", f"Erro ao carregar jogos de {data_exibicao}:\n{erro}")

def main():
    """Função principal"""
    root = tk.Tk()
    app = CalculadoraApostasGUI(root)
    
    # Carregar dados iniciais se existirem
    try:
        # Determinar caminho da pasta data
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        pasta_pai = os.path.dirname(pasta_atual)
        pasta_data = os.path.join(pasta_pai, 'data')
        arquivo_bet_tabelas = os.path.join(pasta_data, 'Bet tabelas.json')
        
        # Tentar carregar do JSON fornecido
        if os.path.exists(arquivo_bet_tabelas):
            with open(arquivo_bet_tabelas, 'r', encoding='utf-8') as f:
                dados_iniciais = json.load(f)
            
            # # Converter formato antigo para novo
            # if 'media_gols' in dados_iniciais:
            #     for i, jogo in enumerate(dados_iniciais['media_gols']):
            #         if 'TimeA' in jogo and 'TimeB' in jogo:
            #             # Adicionar TimeA
            #             nome_a = f"Time_A_{i+1}"
            #             dados_a = jogo['TimeA']
            #             app.times_database[nome_a] = {
            #                 'gols_marcados': dados_a['gols/partida'],
            #                 'gols_sofridos': dados_a['gols sof/partida'],
            #                 'liga': 'Importado',
            #                 'forca_ofensiva': dados_a['gols/partida'] / 1.2,
            #                 'forca_defensiva': dados_a['gols sof/partida'] / 1.2,
            #                 'data_cadastro': datetime.now().isoformat()
            #             }
                        
            #             # Adicionar TimeB
            #             nome_b = f"Time_B_{i+1}"
            #             dados_b = jogo['TimeB']
            #             app.times_database[nome_b] = {
            #                 'gols_marcados': dados_b['gols/partida'],
            #                 'gols_sofridos': dados_b['gols sof/partida'],
            #                 'liga': 'Importado',
            #                 'forca_ofensiva': dados_b['gols/partida'] / 1.2,
            #                 'forca_defensiva': dados_b['gols sof/partida'] / 1.2,
            #                 'data_cadastro': datetime.now().isoformat()
            #             }
                
                app.atualizar_lista_times()
                app.atualizar_comboboxes()
    except Exception as e:
        print(f"Erro ao carregar dados iniciais: {e}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
