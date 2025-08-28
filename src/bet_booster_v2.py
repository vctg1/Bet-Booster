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
        """Limpa todos os arquivos de cache quando a data muda"""
        try:
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
            if not os.path.exists(cache_dir):
                return
            
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            arquivos_removidos = 0
            tem_cache_hoje = False
            
            # Verificar se existe cache de hoje
            for arquivo in os.listdir(cache_dir):
                if arquivo.startswith('jogos_') and arquivo.endswith('.json'):
                    if data_hoje in arquivo:
                        tem_cache_hoje = True
                        break
            
            # Se não tem cache de hoje, limpar todos os caches antigos
            if not tem_cache_hoje:
                for arquivo in os.listdir(cache_dir):
                    if arquivo.startswith('jogos_') and arquivo.endswith('.json'):
                        # Extrair data do nome do arquivo
                        try:
                            data_str = arquivo.replace('jogos_', '').replace('.json', '')
                            data_arquivo = datetime.strptime(data_str, '%Y-%m-%d')
                            
                            # Remover todos os caches de datas diferentes de hoje
                            if data_arquivo.strftime('%Y-%m-%d') != data_hoje:
                                arquivo_path = os.path.join(cache_dir, arquivo)
                                os.remove(arquivo_path)
                                arquivos_removidos += 1
                                print(f"🗑️ Cache de data anterior removido: {arquivo}")
                        except ValueError:
                            # Nome de arquivo inválido, ignorar
                            continue
            
            if arquivos_removidos > 0:
                print(f"✅ {arquivos_removidos} arquivos de cache de datas anteriores removidos")
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
            self.atualizar_loading(10, "Carregando database de times...")
            self.carregar_dados()
            time.sleep(0.5)
            
            # Etapa 2: Configurar estilos
            self.atualizar_loading(20, "Configurando interface...")
            self.setup_styles()
            time.sleep(0.3)
            
            # Etapa 3: Limpar cache antigo
            self.atualizar_loading(25, "Limpando cache antigo...")
            self.limpar_cache_antigo()
            time.sleep(0.2)
            
            # Etapa 4: Buscar jogos de hoje (com cache)
            self.atualizar_loading(30, "Verificando jogos de hoje...")
            data_hoje = datetime.now().strftime('%Y-%m-%d')
            
            # Tentar carregar do cache primeiro
            cache_hoje = self.carregar_jogos_cache(data_hoje)
            if cache_hoje:
                print(f"📁 Usando cache para hoje: {len(cache_hoje['jogos'])} jogos")
                jogos_hoje = cache_hoje['jogos']
                apostas_hot_hoje = cache_hoje['apostas_hot']
                
                # VERIFICAR E CORRIGIR PERÍODOS DAS APOSTAS HOT DE HOJE
                for aposta in apostas_hot_hoje:
                    if aposta.get('periodo') == 'Amanhã':
                        aposta['periodo'] = 'Hoje'
                        print(f"🔄 Período corrigido: {aposta.get('jogo', 'N/A')} - Amanhã -> Hoje")
            else:
                jogos_hoje = self.api.buscar_jogos_do_dia(data_hoje)
                print(f"🌐 {len(jogos_hoje) if jogos_hoje else 0} jogos encontrados hoje")
                apostas_hot_hoje = []
            
            time.sleep(0.3)
            
            # Etapa 5: Buscar jogos de amanhã (com cache)
            self.atualizar_loading(40, "Verificando jogos de amanhã...")
            data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Tentar carregar do cache primeiro
            cache_amanha = self.carregar_jogos_cache(data_amanha)
            if cache_amanha:
                print(f"📁 Usando cache para amanhã: {len(cache_amanha['jogos'])} jogos")
                jogos_amanha = cache_amanha['jogos']
                apostas_hot_amanha = cache_amanha['apostas_hot']
            else:
                jogos_amanha = self.api.buscar_jogos_do_dia(data_amanha)
                print(f"🌐 {len(jogos_amanha) if jogos_amanha else 0} jogos encontrados amanhã")
                apostas_hot_amanha = []
            
            time.sleep(0.3)
            
            # Etapa 5: Preparar os primeiros 50 jogos para análise
            self.atualizar_loading(50, "Preparando primeiros 50 jogos para análise...")
            
            # Se não há cache, processar os primeiros 50 jogos
            if not cache_hoje and jogos_hoje:
                jogos_validos_hoje = self.processar_todos_jogos(jogos_hoje[:50])
                print(f"📊 {len(jogos_validos_hoje)} jogos de hoje preparados para análise (limitado a 50)")
            else:
                jogos_validos_hoje = []
                
            if not cache_amanha and jogos_amanha:
                jogos_validos_amanha = self.processar_todos_jogos(jogos_amanha[:50])
                print(f"📊 {len(jogos_validos_amanha)} jogos de amanhã preparados para análise (limitado a 50)")
            else:
                jogos_validos_amanha = []
            
            total_para_analisar = len(jogos_validos_hoje) + len(jogos_validos_amanha)
            if total_para_analisar > 0:
                print(f"🔥 {total_para_analisar} jogos SELECIONADOS para análise completa (máximo 100)")
            time.sleep(0.5)
            
            # Etapa 6: CARREGAR E ANALISAR APOSTAS HOT COMPLETAMENTE
            apostas_todas = []
            
            # Se não há cache, analisar do zero
            if not cache_hoje and jogos_validos_hoje:
                self.atualizar_loading(60, "Analisando apostas hot de hoje...")
                apostas_hot_hoje, jogos_hoje_com_odds = self.analisar_jogos_completo(jogos_validos_hoje, 'Hoje')
                apostas_todas.extend(apostas_hot_hoje)
                
                # Salvar no cache com jogos enriquecidos com odds
                dados_cache_hoje = {
                    'jogos': jogos_hoje_com_odds,
                    'apostas_hot': apostas_hot_hoje
                }
                self.salvar_jogos_cache(data_hoje, dados_cache_hoje)
            else:
                apostas_todas.extend(apostas_hot_hoje)
            
            if not cache_amanha and jogos_validos_amanha:
                self.atualizar_loading(80, "Analisando apostas hot de amanhã...")
                apostas_hot_amanha, jogos_amanha_com_odds = self.analisar_jogos_completo(jogos_validos_amanha, 'Amanhã')
                apostas_todas.extend(apostas_hot_amanha)
                
                # Salvar no cache com jogos enriquecidos com odds
                dados_cache_amanha = {
                    'jogos': jogos_amanha_com_odds,
                    'apostas_hot': apostas_hot_amanha
                }
                self.salvar_jogos_cache(data_amanha, dados_cache_amanha)
            else:
                apostas_todas.extend(apostas_hot_amanha)
            
            # Combinar e ordenar apostas por prob. bet booster
            self.apostas_hot_carregadas = apostas_todas
            self.apostas_hot_carregadas.sort(key=lambda x: (
                0 if x.get('periodo') == 'Hoje' else 1,
                -x.get('nossa_prob', 0)  # Ordenar por prob. bet booster (maior para menor)
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
    
    def analisar_jogos_completo(self, jogos, periodo):
        """Analisa completamente os primeiros jogos de uma lista (limitado a 50) - VERSÃO PARALELA"""
        apostas_analisadas = []
        jogos_com_odds = []  # Lista para jogos enriquecidos com odds
        
        print(f"🔥 Iniciando análise completa PARALELA de {len(jogos)} jogos ({periodo}) - limitado a 50 primeiros")
        
        # Usar ThreadPoolExecutor para processamento paralelo
        max_workers = 10  # Máximo 10 threads simultâneas para não sobrecarregar API
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submeter todas as tarefas
            futures = []
            for i, jogo in enumerate(jogos):
                future = executor.submit(self.processar_jogo_para_hot_paralelo, jogo, periodo)
                futures.append(future)
            
            # Coletar resultados conforme completam
            for i, future in enumerate(as_completed(futures)):
                try:
                    # Atualizar status de progresso
                    progresso_base = 60 if periodo == 'Hoje' else 80
                    progresso_atual = progresso_base + (i / len(jogos)) * 15  # 15% para cada período
                    self.atualizar_loading(progresso_atual, f"[{i+1}/{len(jogos)}] Processando jogos...")
                    
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
        
        print(f"🎯 CONCLUÍDO PARALELO: {len(jogos_com_odds)} jogos processados, {len(apostas_analisadas)} apostas hot geradas ({periodo})")
        return apostas_analisadas, jogos_com_odds

    def analisar_jogos_completo_original(self, jogos, periodo):
        """Versão original - mantida como backup"""
        apostas_analisadas = []
        jogos_com_odds = []
        
        print(f"🔥 Iniciando análise completa de {len(jogos)} jogos ({periodo}) - limitado a 50 primeiros")
        
        for i, jogo in enumerate(jogos):
            try:
                # Atualizar status de progresso
                progresso_base = 60 if periodo == 'Hoje' else 80
                progresso_atual = progresso_base + (i / len(jogos)) * 15  # 15% para cada período
                
                # Garantir que temos um ID válido
                jogo_id = jogo.get('id') if isinstance(jogo, dict) else str(jogo)
                
                # Usar nomes dos times conforme estão no jogo original, ou N/A se não tiver
                time_casa = jogo.get('home_team', jogo.get('time_casa', 'N/A')) if isinstance(jogo, dict) else 'N/A'
                time_visitante = jogo.get('away_team', jogo.get('time_visitante', 'N/A')) if isinstance(jogo, dict) else 'N/A'
                
                self.atualizar_loading(progresso_atual, f"[{i+1}/{len(jogos)}] {time_casa} vs {time_visitante}")
                
                # Tentar buscar odds detalhadas para este jogo
                odds_detalhadas = None
                if jogo_id and jogo_id != 'N/A':
                    try:
                        odds_detalhadas = self.buscar_odds_detalhadas(jogo_id)
                    except Exception as e:
                        print(f"⚠️ Erro ao buscar odds para {jogo_id}: {e}")
                
                # Criar jogo completo sempre (com ou sem odds)
                if odds_detalhadas:
                    # Jogo COM odds
                    jogo_completo = {**jogo, **odds_detalhadas} if isinstance(jogo, dict) else {**odds_detalhadas, 'id': jogo_id}
                    jogo_completo['periodo'] = periodo
                    print(f"✅ Jogo {time_casa} vs {time_visitante} - COM odds")
                else:
                    # Jogo SEM odds - criar estrutura básica
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
                
                # Adicionar à lista de jogos processados
                jogos_com_odds.append(jogo_completo)
                
                # Tentar processar para apostas hot (só se tiver dados válidos)
                if isinstance(jogo, dict):
                    jogo['periodo'] = periodo
                    try:
                        recomendacoes = self.processar_jogo_para_hot(jogo)
                        apostas_analisadas.extend(recomendacoes)
                        print(f"📊 {len(recomendacoes)} apostas hot geradas")
                    except Exception as e:
                        print(f"⚠️ Erro ao processar apostas hot: {e}")
                
            except Exception as e:
                print(f"❌ ERRO ao processar jogo {i+1}: {e}")
                
                # SEMPRE adicionar jogo mesmo com erro total
                try:
                    jogo_erro = {
                        'id': jogo.get('id') if isinstance(jogo, dict) else str(jogo),
                        'home_team': 'Erro',
                        'away_team': 'Erro',
                        'periodo': periodo,
                        'odds': None,
                        'start_time': '',
                        'league': 'Erro'
                    }
                    jogos_com_odds.append(jogo_erro)
                    print(f"💾 Jogo com erro salvo como estrutura básica")
                except Exception as e2:
                    print(f"❌ Erro crítico ao salvar jogo com erro: {e2}")
        
        print(f"🎯 CONCLUÍDO: {len(jogos_com_odds)} jogos processados, {len(apostas_analisadas)} apostas hot geradas ({periodo})")
        return apostas_analisadas, jogos_com_odds
    
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
        
        # Filtro de Data
        ttk.Label(filtros_frame, text="📅 Data:").pack(side='left', padx=(0, 5))
        self.filtro_data = ttk.Combobox(filtros_frame, values=["Todos", "Hoje", "Amanhã"], 
                                       state="readonly", width=10)
        self.filtro_data.pack(side='left', padx=(0, 15))
        self.filtro_data.set("Todos")
        self.filtro_data.bind('<<ComboboxSelected>>', self.aplicar_filtros_hot)
        
        # Filtro de Risco
        ttk.Label(filtros_frame, text="🎯 Risco:").pack(side='left', padx=(0, 5))
        self.filtro_risco = ttk.Combobox(filtros_frame, values=["Todos", "Fortes", "Moderadas", "Arriscadas", "Muito Arriscadas"], 
                                        state="readonly", width=15)
        self.filtro_risco.pack(side='left', padx=(0, 15))
        self.filtro_risco.set("Todos")
        self.filtro_risco.bind('<<ComboboxSelected>>', self.aplicar_filtros_hot)
        
        # Filtro de Tipo de Aposta
        ttk.Label(filtros_frame, text="⚽ Tipo:").pack(side='left', padx=(0, 5))
        self.filtro_tipo = ttk.Combobox(filtros_frame, values=["Todos", "Resultado", "Outros"], 
                                       state="readonly", width=10)
        self.filtro_tipo.pack(side='left', padx=(0, 15))
        self.filtro_tipo.set("Todos")
        self.filtro_tipo.bind('<<ComboboxSelected>>', self.aplicar_filtros_hot)
        
        # Botão de limpeza de filtros
        ttk.Button(filtros_frame, text="🔄 Limpar Filtros", 
                  command=self.limpar_filtros_hot).pack(side='left', padx=15)
        
        # Linha 2: Botões de configuração
        buttons_frame = ttk.Frame(controles_frame)
        buttons_frame.pack(fill='x', pady=5)
        
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
    
    def aplicar_filtros_hot(self, event=None):
        """Aplica filtros nas apostas hot"""
        try:
            if not hasattr(self, 'apostas_hot') or not self.apostas_hot:
                return
            
            filtro_data = self.filtro_data.get()
            filtro_risco = self.filtro_risco.get()
            filtro_tipo = self.filtro_tipo.get()
            
            # Filtrar apostas
            apostas_filtradas = []
            
            for aposta in self.apostas_hot:
                # Filtro de data
                incluir_data = True
                if filtro_data == "Hoje":
                    incluir_data = aposta.get('periodo') == 'Hoje'
                elif filtro_data == "Amanhã":
                    incluir_data = aposta.get('periodo') == 'Amanhã'
                
                # Filtro de risco - usar o campo 'tipo' da aposta
                incluir_risco = True
                if filtro_risco == "Fortes":
                    incluir_risco = aposta.get('tipo') == 'FORTE'
                elif filtro_risco == "Moderadas":
                    incluir_risco = aposta.get('tipo') == 'MODERADA'
                elif filtro_risco == "Arriscadas":
                    incluir_risco = aposta.get('tipo') == 'ARRISCADA'
                elif filtro_risco == "Muito Arriscadas":
                    incluir_risco = aposta.get('tipo') == 'MUITO_ARRISCADA'
                
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
                
                if incluir_data and incluir_risco and incluir_tipo:
                    apostas_filtradas.append(aposta)
            
            # Atualizar interface com apostas filtradas
            self.atualizar_apostas_hot_interface(apostas_filtradas)
            
            # Atualizar status
            total_filtradas = len(apostas_filtradas)
            total_original = len(self.apostas_hot)
            
            status_text = f"✅ {total_filtradas} de {total_original} apostas"
            if filtro_data != "Todos":
                status_text += f" ({filtro_data})"
            if filtro_risco != "Todos":
                status_text += f" ({filtro_risco})"
            if filtro_tipo != "Todos":
                status_text += f" ({filtro_tipo})"
            
            self.status_hot.config(text=status_text, style='Success.TLabel')
            
        except Exception as e:
            self.status_hot.config(text=f"❌ Erro ao aplicar filtros: {str(e)}", style='Warning.TLabel')
    
    def limpar_filtros_hot(self):
        """Limpa todos os filtros das apostas hot"""
        self.filtro_data.set("Todos")
        self.filtro_risco.set("Todos")
        self.filtro_tipo.set("Todos")
        self.aplicar_filtros_hot()
    
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
    
    def atualizar_apostas_hot_interface(self, apostas_lista=None):
        """Atualiza a interface das apostas hot com a lista fornecida ou completa, ordenada por prob. bet booster"""
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
            
            # Ordenar apostas por prob. bet booster (do maior para o menor)
            apostas_ordenadas = sorted(apostas_para_mostrar, key=lambda x: x.get('nossa_prob', 0), reverse=True)
            
            # Adicionar apostas ordenadas
            for i, aposta in enumerate(apostas_ordenadas):
                self.criar_card_aposta_hot(aposta, i)
                
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
        self.entry_data = ttk.Entry(linha1, width=12)
        self.entry_data.pack(side='left', padx=(0, 10))
        self.entry_data.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
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
        elif probabilidades['empate'] == maior_prob and maior_prob >= 33:
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
        columns_multipla = ('Jogo', 'Aposta', 'Odd', 'Prob. Bet Booster', 'Prob. Bet365', 'Status')
        self.tree_multipla = ttk.Treeview(multipla_frame, columns=columns_multipla, show='headings', height=10)
        
        for col in columns_multipla:
            self.tree_multipla.heading(col, text=col)
            if col == 'Jogo':
                self.tree_multipla.column(col, width=200)
            elif col == 'Aposta':
                self.tree_multipla.column(col, width=120)
            elif col in ['Prob. Bet Booster', 'Prob. Bet365']:
                self.tree_multipla.column(col, width=100)
            else:
                self.tree_multipla.column(col, width=80)
        
        self.tree_multipla.pack(fill='both', expand=True)
        
        # Informações da múltipla
        info_frame = ttk.Frame(multipla_frame)
        info_frame.pack(fill='x', pady=10)
        
        self.label_odd_total = ttk.Label(info_frame, text="Odd Total: 1.00", style='Subtitle.TLabel')
        self.label_odd_total.pack(side='left', padx=10)
        
        self.label_prob_nossa = ttk.Label(info_frame, text="📊 Prob. Bet Booster: 100%", style='Success.TLabel')
        self.label_prob_nossa.pack(side='left', padx=10)
        
        self.label_prob_total = ttk.Label(info_frame, text="🎯 Prob. Bet365: 100%", style='Subtitle.TLabel')
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
            
            # Ordenar por prob. bet booster (maior para menor) como critério principal
            apostas_recomendadas.sort(key=lambda x: (
                0 if x.get('periodo') == 'Hoje' else 1,  # Hoje primeiro
                -x.get('nossa_prob', 0)  # Depois por prob. bet booster (maior para menor)
            ))
            
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
            odds = odds_detalhadas['odds']
            
            # 1. Analisar Resultado Final (1X2)
            if 'resultFt' in odds:
                result_odds = odds['resultFt']
                
                # Calcular probabilidades implícitas
                prob_casa_implicita = 1 / result_odds['home'] * 100
                prob_empate_implicita = 1 / result_odds['draw'] * 100
                prob_fora_implicita = 1 / result_odds['away'] * 100
                
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
                    (f'Vitória {home_team}', value_casa, prob_casa_calc, prob_casa_implicita, result_odds['home']),
                    ('Empate', value_empate, prob_empate_calc, prob_empate_implicita, result_odds['draw']),
                    (f'Vitória {away_team}', value_fora, prob_fora_calc, prob_fora_implicita, result_odds['away'])
                ]
                
                for aposta, value, prob_calc, prob_impl, odd in apostas_resultado:
                    # Converter value para porcentagem
                    value_percent = (value - 1) * 100
                    
                    # Aplicar NOVAS regras para apostas de vencedor:
                    # Forte: Prob. Bet365 >= 40%, value >= 10%
                    # Moderada: Prob. Bet365 >= 30%, value >= 10%
                    # Arriscada: Prob. Bet365 >= 15% E < 30%, value >= 10%
                    # Muito Arriscada: Prob. Bet365 >= 5% E < 15%, value >= 30%
                    tipo_recomendacao = None
                    
                    if value_percent >= 10 and prob_impl >= 40:
                        tipo_recomendacao = "FORTE"
                    elif value_percent >= 10 and prob_impl >= 30:
                        tipo_recomendacao = "MODERADA"
                    elif value_percent >= 10 and prob_impl >= 15 and prob_impl < 30:
                        tipo_recomendacao = "ARRISCADA"
                    elif value_percent >= 30 and prob_impl >= 5 and prob_impl < 15:
                        tipo_recomendacao = "MUITO_ARRISCADA"
                    
                    if tipo_recomendacao and prob_calc >= 15:  # Mínimo de confiança na probabilidade Bet Booster
                        
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
                    
                    # Aplicar NOVAS regras para apostas Over/Under:
                    # Forte: Prob. Bet365 >= 45%, value >= 15%
                    # Moderada: Prob. Bet365 >= 35%, value >= 15%
                    # Arriscada: Prob. Bet365 >= 20% E < 35%, value >= 15%
                    # Muito Arriscada: Prob. Bet365 >= 5% E < 20%, value >= 30%
                    tipo_recomendacao = None
                    
                    if value_percent >= 15 and prob_impl >= 45:
                        tipo_recomendacao = "FORTE"
                    elif value_percent >= 15 and prob_impl >= 35:
                        tipo_recomendacao = "MODERADA"
                    elif value_percent >= 15 and prob_impl >= 20 and prob_impl < 35:
                        tipo_recomendacao = "ARRISCADA"
                    elif value_percent >= 30 and prob_impl >= 5 and prob_impl < 20:
                        tipo_recomendacao = "MUITO_ARRISCADA"
                    
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
                            'forca_recomendacao': forca,
                            'match_id': odds_detalhadas['match_id'],
                            'liga': odds_detalhadas['league'],
                            'horario': self.formatar_horario(odds_detalhadas['start_time'])
                        })
            
        except Exception as e:
            print(f"Erro ao analisar recomendações: {e}")
        
        return recomendacoes
    
    def exibir_apostas_hot(self, apostas):
        """Exibe as apostas hot na interface ordenadas por prob. bet booster (maior para menor)"""
        # Ordenar apostas por prob. bet booster (do maior para o menor)
        apostas_ordenadas = sorted(apostas, key=lambda x: x.get('nossa_prob', 0), reverse=True)
        self.apostas_hot = apostas_ordenadas  # Armazenar para filtros
        self.atualizar_apostas_hot_interface()
        self.aplicar_filtros_hot()  # Aplicar filtros atuais
    
    def criar_card_aposta_hot(self, aposta, index):
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
        
        # Definir cor e emoji baseado no tipo
        if aposta['tipo'] == 'FORTE':
            tipo_color = 'Success.TLabel'
            tipo_emoji = '🟢'
        elif aposta['tipo'] == 'MODERADA':
            tipo_color = 'Moderate.TLabel'
            tipo_emoji = '🔵'
        elif aposta['tipo'] == 'MUITO_ARRISCADA':
            tipo_color = 'Danger.TLabel'
            tipo_emoji = '🔴'
        else:  # ARRISCADA
            tipo_color = 'Hot.TLabel'
            tipo_emoji = '🟡'
        
        aposta_label = ttk.Label(linha3, text=f"{tipo_emoji} {aposta['aposta']}", 
                                style=tipo_color, font=('Arial', 11, 'bold'))
        aposta_label.pack(side='left')
        
        odd_label = ttk.Label(linha3, text=f"Odd: {aposta['odd']:.2f}", 
                             style='Subtitle.TLabel')
        odd_label.pack(side='right')
        
        # Linha 4: Probabilidades e value
        linha4 = ttk.Frame(card_frame)
        linha4.pack(fill='x')
        
        prob_calc_label = ttk.Label(linha4, text=f"📊 Prob. Bet Booster: {aposta['prob_calculada']:.1f}%")
        prob_calc_label.pack(side='left')
        
        prob_impl_label = ttk.Label(linha4, text=f"🎯 Prob. Bet365: {aposta['prob_implicita']:.1f}%")
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
        """Busca jogos do dia selecionado com cache inteligente"""
        try:
            self.status_jogos.config(text="🔄 Verificando cache...", style='Warning.TLabel')
            self.root.update()
            
            # Converter data do formato DD/MM/YYYY para YYYY-MM-DD
            data_input = self.entry_data.get()
            data_obj = datetime.strptime(data_input, '%d/%m/%Y')
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
        """Calcula probabilidades do jogo selecionado"""
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
            
            # Exibir resultado
            casa = jogo.get('home_team', jogo.get('time_casa', ''))
            visitante = jogo.get('away_team', jogo.get('time_visitante', ''))
            
            resultado = f"""
🎲 PROBABILIDADES CALCULADAS
═══════════════════════════════════════

🏠 {casa} vs ✈️ {visitante}

📊 RESULTADOS:
🏠 Vitória {casa}: {probabilidades['vitoria_casa']:.1f}%
🤝 Empate: {probabilidades['empate']:.1f}%
✈️ Vitória {visitante}: {probabilidades['vitoria_visitante']:.1f}%

⚽ GOLS ESPERADOS:
🏠 {casa}: {probabilidades['gols_esperados_casa']:.2f}
✈️ {visitante}: {probabilidades['gols_esperados_visitante']:.2f}
🎯 Total: {probabilidades['gols_esperados_total']:.2f}

📈 MERCADOS DE GOLS:
Over 2.5: {self.calcular_prob_over_under(probabilidades['gols_esperados_total'], 2.5, 'over'):.1f}%
Under 2.5: {self.calcular_prob_over_under(probabilidades['gols_esperados_total'], 2.5, 'under'):.1f}%

🎯 Modo de Análise: {self.modo_analise.get()}
"""
            
            messagebox.showinfo("Probabilidades Calculadas", resultado)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular probabilidades:\n{str(e)}")
            print(f"Erro detalhado: {e}")
            import traceback
            traceback.print_exc()
    
    def forcar_atualizacao_jogos(self):
        """Atualiza apenas os jogos na aba sem mexer no cache"""
        try:
            # Converter data do formato DD/MM/YYYY para YYYY-MM-DD
            data_input = self.entry_data.get()
            data_obj = datetime.strptime(data_input, '%d/%m/%Y')
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
                f"{aposta.get('prob_calculada', 0):.1f}%",
                f"{aposta['prob_implicita']:.1f}%",
                aposta['tipo']
            ))
            odd_total *= aposta['odd']
        
        # Atualizar labels
        prob_total_implicita = (1 / odd_total * 100) if odd_total > 0 else 0
        
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
        
        prob_total = (1 / odd_total * 100) if odd_total > 0 else 0
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
        prob_implicita = (1 / odd * 100) if odd > 0 else 0
        
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
