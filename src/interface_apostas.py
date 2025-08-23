#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Gráfica para Análise de Apostas Esportivas
Sistema completo para cálculo de probabilidades baseado em estatísticas de gols
Integrado com API SofaScore para busca automática de times
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import math
from datetime import datetime
import os
import sys
import threading

# Adicionar pasta api ao path para importar módulos
pasta_atual = os.path.dirname(os.path.abspath(__file__))
pasta_pai = os.path.dirname(pasta_atual)
pasta_api = os.path.join(pasta_pai, 'api')
if pasta_api not in sys.path:
    sys.path.insert(0, pasta_api)

from api.sofascore_api import SofaScoreAPI

class CalculadoraApostasGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Análise de Apostas - Calculadora Avançada")
        self.root.geometry("1000x700")
        
        # Dados dos times e apostas
        self.times_database = {}
        self.apostas_ativas = []
        
        # Integração com API SofaScore
        self.api = SofaScoreAPI()
        
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
        
        # Aba 1: Busca de Times (API)
        self.create_busca_api_tab()
        
        # Aba 2: Cadastro de Times
        self.create_cadastro_tab()
        
        # Aba 3: Análise de Confrontos
        self.create_analise_tab()
        
        # Aba 4: Apostas e Múltiplas
        self.create_apostas_tab()
        
        # Aba 5: Histórico e Estatísticas
        self.create_historico_tab()
    
    def create_busca_api_tab(self):
        """Cria a aba de busca de times via API SofaScore"""
        self.tab_busca_api = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_busca_api, text="🔍 Buscar Times (API)")
        
        # Título
        ttk.Label(self.tab_busca_api, text="Busca de Times via SofaScore API", style='Title.TLabel').pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(self.tab_busca_api)
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # Frame de busca
        busca_frame = ttk.LabelFrame(main_frame, text="Buscar Time", padding=15)
        busca_frame.pack(fill='x', pady=10)
        
        # Campo de busca
        ttk.Label(busca_frame, text="Nome do Time:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_busca_time = ttk.Entry(busca_frame, width=30, font=('Arial', 12))
        self.entry_busca_time.grid(row=0, column=1, padx=5, pady=5)
        self.entry_busca_time.bind('<Return>', lambda event: self.buscar_times_api())
        
        # Botões de ação
        btn_frame = ttk.Frame(busca_frame)
        btn_frame.grid(row=0, column=2, padx=10, pady=5)
        
        self.btn_buscar = ttk.Button(btn_frame, text="🔍 Buscar", command=self.buscar_times_api)
        self.btn_buscar.pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🔄 Limpar", command=self.limpar_busca).pack(side='left', padx=5)
        
        # Label de status
        self.label_status_busca = ttk.Label(busca_frame, text="Digite o nome de um time e clique em Buscar", 
                                           style='Subtitle.TLabel')
        self.label_status_busca.grid(row=1, column=0, columnspan=3, pady=10)
        
        # Frame de resultados
        resultados_frame = ttk.LabelFrame(main_frame, text="Resultados da Busca", padding=10)
        resultados_frame.pack(fill='both', expand=True, pady=10)
        
        # Treeview para mostrar resultados
        columns = ('Nome', 'País', 'Liga', 'Gols/Partida', 'Gols Sofridos', 'Estádio', 'Popularidade')
        self.tree_busca = ttk.Treeview(resultados_frame, columns=columns, show='headings', height=12)
        
        # Configurar colunas
        column_widths = {'Nome': 150, 'País': 80, 'Liga': 120, 'Gols/Partida': 100, 
                        'Gols Sofridos': 100, 'Estádio': 150, 'Popularidade': 100}
        
        for col in columns:
            self.tree_busca.heading(col, text=col)
            self.tree_busca.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(resultados_frame, orient='vertical', command=self.tree_busca.yview)
        scrollbar_h = ttk.Scrollbar(resultados_frame, orient='horizontal', command=self.tree_busca.xview)
        self.tree_busca.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Grid layout para scrollbars
        self.tree_busca.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        resultados_frame.grid_rowconfigure(0, weight=1)
        resultados_frame.grid_columnconfigure(0, weight=1)
        
        # Botões de ação para resultados
        acoes_frame = ttk.Frame(resultados_frame)
        acoes_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='ew')
        
        self.btn_adicionar_selecionado = ttk.Button(acoes_frame, text="➕ Adicionar Time Selecionado", 
                                                   command=self.adicionar_time_da_busca, state='disabled')
        self.btn_adicionar_selecionado.pack(side='left', padx=5)
        
        ttk.Button(acoes_frame, text="📋 Ver Detalhes", command=self.ver_detalhes_time).pack(side='left', padx=5)
        
        # Bind para seleção
        self.tree_busca.bind('<<TreeviewSelect>>', self.on_selecao_busca)
        
        # Frame de informações da API
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Informações", padding=10)
        info_frame.pack(fill='x', pady=5)
        
        info_text = """
🌐 Esta funcionalidade busca times reais da base de dados do SofaScore
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
        
        # Treeview para mostrar times
        columns = ('Nome', 'Gols/Partida', 'Gols Sofridos/Partida', 'Liga', 'Força Ofensiva', 'Força Defensiva')
        self.tree_times = ttk.Treeview(lista_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_times.heading(col, text=col)
            self.tree_times.column(col, width=120, anchor='center')
        
        # Scrollbar para a tabela
        scrollbar_times = ttk.Scrollbar(lista_frame, orient='vertical', command=self.tree_times.yview)
        self.tree_times.configure(yscrollcommand=scrollbar_times.set)
        
        self.tree_times.pack(side='left', fill='both', expand=True)
        scrollbar_times.pack(side='right', fill='y')
        
        # Botões de ação
        btn_actions_frame = ttk.Frame(lista_frame)
        btn_actions_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_actions_frame, text="Remover Time Selecionado", 
                  command=self.remover_time).pack(side='left', padx=5)
        ttk.Button(btn_actions_frame, text="Editar Time", 
                  command=self.editar_time).pack(side='left', padx=5)
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
        
        # Fator casa (checkbox) com callback para atualizar indicador
        self.var_fator_casa = tk.BooleanVar()
        self.var_fator_casa.set(True)  # Ativado por padrão
        self.check_fator_casa = ttk.Checkbutton(
            selecao_frame, 
            text="Aplicar Vantagem de Casa (15%)", 
            variable=self.var_fator_casa,
            command=self.atualizar_indicador_fator_casa
        )
        self.check_fator_casa.grid(row=2, column=2, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Indicador visual do status do fator casa
        self.label_status_casa = ttk.Label(selecao_frame, text="✅ Vantagem de casa ATIVADA", 
                                          style='Success.TLabel')
        self.label_status_casa.grid(row=3, column=2, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Botão calcular
        ttk.Button(selecao_frame, text="Calcular Probabilidades", 
                  command=self.calcular_confronto).grid(row=4, column=1, columnspan=2, pady=15)
        
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
        
        # Botões
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=15)
        
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
        
        # Adicionar times
        for nome, dados in self.times_database.items():
            self.tree_times.insert('', 'end', values=(
                nome,
                f"{dados['gols_marcados']:.2f}",
                f"{dados['gols_sofridos']:.2f}",
                dados['liga'],
                f"{dados['forca_ofensiva']:.2f}",
                f"{dados['forca_defensiva']:.2f}"
            ))
    
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
        
        # Forças já calculadas
        forca_of_a = time_a_dados['forca_ofensiva']
        forca_def_a = time_a_dados['forca_defensiva']
        forca_of_b = time_b_dados['forca_ofensiva']
        forca_def_b = time_b_dados['forca_defensiva']
        
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
            dados_a = self.times_database[time_a]
            dados_b = self.times_database[time_b]
            
            # Obter configuração do fator casa
            aplicar_fator_casa = self.var_fator_casa.get()
            
            # Calcular gols esperados
            gols_esp_a, gols_esp_b = self.calcular_gols_esperados(dados_a, dados_b, aplicar_fator_casa)
            
            # Calcular probabilidades
            prob_a, prob_empate, prob_b = self.calcular_probabilidades_poisson(gols_esp_a, gols_esp_b)
            
            # Análise de odds (se fornecidas)
            resultado_texto = f"""
{'='*80}
ANÁLISE COMPLETA DO CONFRONTO
{'='*80}

🏟️  CONFRONTO: {time_a} (Casa) vs {time_b} (Visitante)
📅  Data da Análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}

📊 ESTATÍSTICAS DOS TIMES:
┌─────────────────────────────────────────────────────────────┐
│ {time_a:<25} │ {time_b:<25} │
├─────────────────────────────────────────────────────────────┤
│ Gols/Partida: {dados_a['gols_marcados']:<13.2f} │ Gols/Partida: {dados_b['gols_marcados']:<13.2f} │
│ Gols Sofridos: {dados_a['gols_sofridos']:<12.2f} │ Gols Sofridos: {dados_b['gols_sofridos']:<12.2f} │
│ Força Ofensiva: {dados_a['forca_ofensiva']:<11.2f} │ Força Ofensiva: {dados_b['forca_ofensiva']:<11.2f} │
│ Força Defensiva: {dados_a['forca_defensiva']:<10.2f} │ Força Defensiva: {dados_b['forca_defensiva']:<10.2f} │
│ Liga: {dados_a['liga']:<19} │ Liga: {dados_b['liga']:<19} │
└─────────────────────────────────────────────────────────────┘

⚽ GOLS ESPERADOS (Modelo de Poisson):
• {time_a}: {gols_esp_a:.2f} gols
• {time_b}: {gols_esp_b:.2f} gols
• Total de gols esperados: {gols_esp_a + gols_esp_b:.2f}
• Vantagem de casa: {'Aplicada (+15%)' if aplicar_fator_casa else 'Não aplicada'}

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
                
                # Recomendações
                resultado_texto += "🎯 RECOMENDAÇÕES:\n"
                
                recomendacoes = []
                if prob_a > prob_impl_a and (prob_a - prob_impl_a) / prob_impl_a > 0.05:
                    vantagem = (prob_a - prob_impl_a) / prob_impl_a * 100
                    recomendacoes.append(f"🔥 FORTE: Apostar em vitória do {time_a} (Vantagem: {vantagem:.1f}%)")
                
                if prob_empate > prob_impl_empate and (prob_empate - prob_impl_empate) / prob_impl_empate > 0.05:
                    vantagem = (prob_empate - prob_impl_empate) / prob_impl_empate * 100
                    recomendacoes.append(f"🔥 FORTE: Apostar em empate (Vantagem: {vantagem:.1f}%)")
                
                if prob_b > prob_impl_b and (prob_b - prob_impl_b) / prob_impl_b > 0.05:
                    vantagem = (prob_b - prob_impl_b) / prob_impl_b * 100
                    recomendacoes.append(f"🔥 FORTE: Apostar em vitória do {time_b} (Vantagem: {vantagem:.1f}%)")
                
                if not recomendacoes:
                    resultado_texto += "⚠️  Não foram encontradas apostas com value significativo (>5%)\n"
                    resultado_texto += "   Recomenda-se aguardar melhores oportunidades\n"
                else:
                    for rec in recomendacoes:
                        resultado_texto += f"{rec}\n"
                
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
            
            # Calcular probabilidades usando a configuração atual do fator casa
            dados_a = self.times_database[time_a]
            dados_b = self.times_database[time_b]
            aplicar_fator_casa = self.var_fator_casa.get()
            
            gols_esp_a, gols_esp_b = self.calcular_gols_esperados(dados_a, dados_b, aplicar_fator_casa)
            prob_a, prob_empate, prob_b = self.calcular_probabilidades_poisson(gols_esp_a, gols_esp_b)
            
            # Mapear probabilidade
            prob_map = {
                "Vitória A": prob_a,
                "Empate": prob_empate,
                "Vitória B": prob_b
            }
            
            probabilidade = prob_map[tipo_aposta]
            retorno_potencial = valor * odd
            lucro_potencial = retorno_potencial - valor
            
            # Análise de value
            prob_implicita = 1 / odd
            e_value = probabilidade > prob_implicita
            vantagem = (probabilidade - prob_implicita) / prob_implicita * 100
            
            resultado = f"""
ANÁLISE DA APOSTA SIMPLES
{'='*50}

🎮 Confronto: {time_a} vs {time_b}
🎯 Aposta: {tipo_aposta}
💰 Valor apostado: R$ {valor:.2f}
📊 Odd: {odd:.2f}
🏟️ Vantagem de casa: {'Aplicada (+15%)' if aplicar_fator_casa else 'Não aplicada'}

📈 PROBABILIDADES:
• Nossa probabilidade: {probabilidade:.1%}
• Probabilidade implícita: {prob_implicita:.1%}
• {"✅ VALUE BET" if e_value else "❌ SEM VALUE"}: {vantagem:+.1f}%

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
            dados_a = self.times_database[time_a]
            dados_b = self.times_database[time_b]
            aplicar_fator_casa = self.var_fator_casa.get()
            
            gols_esp_a, gols_esp_b = self.calcular_gols_esperados(dados_a, dados_b, aplicar_fator_casa)
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
                'probabilidade': probabilidade
            }
            
            self.apostas_ativas.append(aposta)
            
            # Atualizar tree
            self.tree_apostas.insert('', 'end', values=(
                aposta['confronto'],
                aposta['tipo'],
                f"{aposta['odd']:.2f}",
                f"{aposta['probabilidade']:.1%}"
            ))
            
            messagebox.showinfo("Sucesso", "Aposta adicionada à múltipla!")
            
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
            aplicar_fator_casa = self.var_fator_casa.get()
            resultado_texto = f"""
MÚLTIPLA: {len(self.apostas_ativas)} apostas
🏟️ Vantagem de casa: {'Aplicada (+15%)' if aplicar_fator_casa else 'Não aplicada'}
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
        media_gols_marcados = sum(dados['gols_marcados'] for dados in self.times_database.values()) / total_times
        media_gols_sofridos = sum(dados['gols_sofridos'] for dados in self.times_database.values()) / total_times
        
        # Times mais ofensivos e defensivos
        time_mais_ofensivo = max(self.times_database.items(), key=lambda x: x[1]['gols_marcados'])
        time_mais_defensivo = min(self.times_database.items(), key=lambda x: x[1]['gols_sofridos'])
        
        # Ligas representadas
        ligas = set(dados['liga'] for dados in self.times_database.values())
        
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
            estatisticas += f"""
{nome}:
  📈 Gols marcados: {dados['gols_marcados']:.2f}/jogo
  📉 Gols sofridos: {dados['gols_sofridos']:.2f}/jogo
  ⚔️  Força ofensiva: {dados['forca_ofensiva']:.2f}
  🛡️  Força defensiva: {dados['forca_defensiva']:.2f}
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
    
    # ========== MÉTODOS DA API SOFASCORE ==========
    
    def buscar_times_api(self):
        """Busca times via API SofaScore em thread separada"""
        nome_time = self.entry_busca_time.get().strip()
        
        if not nome_time:
            messagebox.showwarning("Aviso", "Digite o nome de um time para buscar!")
            return
        
        if len(nome_time) < 3:
            messagebox.showwarning("Aviso", "Digite pelo menos 3 caracteres!")
            return
        
        # Desabilitar botão e mostrar status
        self.btn_buscar.config(state='disabled', text="🔄 Buscando...")
        self.label_status_busca.config(text=f"Buscando '{nome_time}' na API SofaScore...")
        
        # Limpar resultados anteriores
        for item in self.tree_busca.get_children():
            self.tree_busca.delete(item)
        
        # Executar busca em thread separada para não travar a interface
        thread = threading.Thread(target=self._executar_busca_api, args=(nome_time,))
        thread.daemon = True
        thread.start()
    
    def _executar_busca_api(self, nome_time):
        """Executa a busca na API em thread separada"""
        try:
            # Buscar times na API
            times_encontrados = self.api.buscar_e_processar_time(nome_time)
            
            # Atualizar interface na thread principal
            self.root.after(0, self._atualizar_resultados_busca, times_encontrados, nome_time)
            
        except Exception as e:
            # Mostrar erro na thread principal
            self.root.after(0, self._mostrar_erro_busca, str(e))
    
    def _atualizar_resultados_busca(self, times_encontrados, nome_time):
        """Atualiza a interface com os resultados da busca"""
        # Reabilitar botão
        self.btn_buscar.config(state='normal', text="🔍 Buscar")
        
        if not times_encontrados:
            self.label_status_busca.config(text=f"Nenhum time encontrado para '{nome_time}'")
            return
        
        # Adicionar resultados à tabela
        for time in times_encontrados:
            popularidade_formatada = f"{time['popularidade']:,}".replace(',', '.')
            
            self.tree_busca.insert('', 'end', values=(
                time['nome'],
                time['pais'],
                time['liga'],
                f"{time['gols_marcados']:.2f}",
                f"{time['gols_sofridos']:.2f}",
                time['estadio'] or 'N/A',
                popularidade_formatada
            ), tags=(str(time['id_sofascore']),))
        
        # Atualizar status
        total = len(times_encontrados)
        self.label_status_busca.config(text=f"✅ {total} time(s) encontrado(s) para '{nome_time}'")
    
    def _mostrar_erro_busca(self, erro):
        """Mostra erro da busca na interface"""
        self.btn_buscar.config(state='normal', text="🔍 Buscar")
        self.label_status_busca.config(text=f"❌ Erro na busca: {erro}")
        messagebox.showerror("Erro na API", f"Erro ao buscar times:\n{erro}")
    
    def limpar_busca(self):
        """Limpa os campos e resultados da busca"""
        self.entry_busca_time.delete(0, tk.END)
        
        for item in self.tree_busca.get_children():
            self.tree_busca.delete(item)
        
        self.label_status_busca.config(text="Digite o nome de um time e clique em Buscar")
        self.btn_adicionar_selecionado.config(state='disabled')
    
    def on_selecao_busca(self, event):
        """Callback quando um time é selecionado na busca"""
        selecao = self.tree_busca.selection()
        if selecao:
            self.btn_adicionar_selecionado.config(state='normal')
        else:
            self.btn_adicionar_selecionado.config(state='disabled')
    
    def adicionar_time_da_busca(self):
        """Adiciona o time selecionado da busca ao banco de dados"""
        selecao = self.tree_busca.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um time da lista!")
            return
        
        item = self.tree_busca.item(selecao[0])
        valores = item['values']
        
        nome_time = valores[0]
        
        # Verificar se já existe
        if nome_time in self.times_database:
            resposta = messagebox.askyesno(
                "Time já existe", 
                f"O time '{nome_time}' já está cadastrado.\nDeseja atualizar os dados?"
            )
            if not resposta:
                return
        
        # Buscar dados completos do time selecionado
        id_sofascore = item['tags'][0] if item['tags'] else None
        
        if not id_sofascore:
            messagebox.showerror("Erro", "Não foi possível obter ID do time!")
            return
        
        try:
            # Mostrar progresso
            self.label_status_busca.config(text=f"⏳ Adicionando '{nome_time}'...")
            
            # Obter dados completos
            dados_completos = self.api.buscar_e_processar_time(nome_time)
            
            if not dados_completos:
                messagebox.showerror("Erro", "Não foi possível obter dados completos do time!")
                return
            
            # Encontrar o time correto na lista
            time_selecionado = None
            for time in dados_completos:
                if str(time['id_sofascore']) == id_sofascore:
                    time_selecionado = time
                    break
            
            if not time_selecionado:
                messagebox.showerror("Erro", "Time não encontrado nos dados detalhados!")
                return
            
            # Adicionar ao banco de dados
            self.times_database[nome_time] = {
                'gols_marcados': time_selecionado['gols_marcados'],
                'gols_sofridos': time_selecionado['gols_sofridos'],
                'liga': time_selecionado['liga'],
                'forca_ofensiva': time_selecionado['forca_ofensiva'],
                'forca_defensiva': time_selecionado['forca_defensiva'],
                'data_cadastro': datetime.now().isoformat(),
                'fonte': 'SofaScore API',
                'id_sofascore': time_selecionado['id_sofascore'],
                'pais': time_selecionado['pais'],
                'estadio': time_selecionado['estadio'],
                'tecnico': time_selecionado['tecnico'],
                'popularidade': time_selecionado['popularidade']
            }
            
            # Atualizar interfaces
            self.atualizar_lista_times()
            self.atualizar_comboboxes()
            self.salvar_dados()
            
            # Feedback
            self.label_status_busca.config(text=f"✅ '{nome_time}' adicionado com sucesso!")
            messagebox.showinfo("Sucesso", f"Time '{nome_time}' adicionado com dados da API SofaScore!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar time:\n{str(e)}")
            self.label_status_busca.config(text="❌ Erro ao adicionar time")
    
    def ver_detalhes_time(self):
        """Mostra detalhes completos do time selecionado"""
        selecao = self.tree_busca.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um time da lista!")
            return
        
        item = self.tree_busca.item(selecao[0])
        valores = item['values']
        id_sofascore = item['tags'][0] if item['tags'] else None
        
        if not id_sofascore:
            messagebox.showerror("Erro", "Não foi possível obter ID do time!")
            return
        
        try:
            # Buscar dados detalhados
            dados_detalhados = self.api.obter_dados_time(int(id_sofascore))
            estatisticas = self.api.obter_estatisticas_time(int(id_sofascore))
            
            if not dados_detalhados or not estatisticas:
                messagebox.showerror("Erro", "Não foi possível obter detalhes do time!")
                return
            
            # Criar janela de detalhes
            janela_detalhes = tk.Toplevel(self.root)
            janela_detalhes.title(f"Detalhes - {dados_detalhados['nome']}")
            janela_detalhes.geometry("600x500")
            janela_detalhes.resizable(False, False)
            
            # Texto com detalhes
            texto_detalhes = f"""
🏆 INFORMAÇÕES DETALHADAS DO TIME
{'='*60}

📝 DADOS BÁSICOS:
• Nome: {dados_detalhados['nome']}
• Nome Completo: {dados_detalhados['nome_completo']}
• País: {dados_detalhados['pais']}
• Liga Principal: {dados_detalhados['liga_principal']}
• Liga Atual: {dados_detalhados['liga_atual']}

🏟️ ESTRUTURA:
• Estádio: {dados_detalhados['estadio']}
• Capacidade: {dados_detalhados['capacidade_estadio']:,} lugares
• Técnico: {dados_detalhados['tecnico']}

📊 ESTATÍSTICAS (Temporada 2024/25):
• Gols por Partida: {estatisticas['gols_marcados']:.2f}
• Gols Sofridos por Partida: {estatisticas['gols_sofridos']:.2f}
• Força Ofensiva: {estatisticas['gols_marcados']/estatisticas['media_liga']:.3f}
• Força Defensiva: {estatisticas['gols_sofridos']/estatisticas['media_liga']:.3f}
• Média da Liga: {estatisticas['media_liga']:.2f} gols/time/jogo

🌐 DADOS ADICIONAIS:
• Popularidade: {dados_detalhados['popularidade']:,} seguidores
• ID SofaScore: {dados_detalhados['id']}
• Última Atualização: {estatisticas['ultima_atualizacao']}

💡 OBSERVAÇÕES:
• Os dados estatísticos são estimados baseados na liga
• Para dados mais precisos, consulte o site oficial do SofaScore
• As estatísticas são atualizadas regularmente
            """
            
            # Widget de texto com scroll
            text_widget = scrolledtext.ScrolledText(janela_detalhes, wrap=tk.WORD, 
                                                   font=('Consolas', 10), padx=10, pady=10)
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', texto_detalhes.strip())
            text_widget.config(state='disabled')
            
            # Botão fechar
            ttk.Button(janela_detalhes, text="Fechar", 
                      command=janela_detalhes.destroy).pack(pady=10)
            
            # Centralizar janela
            janela_detalhes.transient(self.root)
            janela_detalhes.grab_set()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter detalhes:\n{str(e)}")

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
