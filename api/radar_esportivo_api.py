#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API para integração com Radar Esportivo
Busca jogos do dia e dados de times/partidas
"""

import requests
import json
from datetime import datetime, timedelta
import time

class RadarEsportivoAPI:
    def __init__(self):
        self.base_url = "https://api.radaresportivo.com/public"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache'
        })
    
    def buscar_jogos_do_dia(self, data=None, timezone_offset=-180):
        """
        Busca jogos de uma data específica
        
        Args:
            data: Data no formato YYYY-MM-DD (padrão: hoje)
            timezone_offset: Offset do timezone em minutos (padrão: -180 para UTC-3)
        
        Returns:
            dict: Dados dos jogos do dia
        """
        try:
            if data is None:
                data = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/dailyRadar/{data}"
            params = {'mOffset': timezone_offset}
            
            print(f"🔍 Buscando jogos para {data}...")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data_response = response.json()
            
            if 'dailyRadar' not in data_response:
                print("❌ Resposta da API não contém dados esperados")
                return None
            
            # Processar dados
            jogos_processados = self.processar_jogos(data_response['dailyRadar'])
            
            print(f"✅ {len(jogos_processados)} jogos encontrados")
            return jogos_processados
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")
            return None
    
    def processar_jogos(self, daily_radar_data):
        """
        Processa os dados brutos da API e extrai informações relevantes
        
        Args:
            daily_radar_data: Dados brutos da API
        
        Returns:
            list: Lista de jogos processados
        """
        jogos = []
        
        try:
            for region_data in daily_radar_data:
                if not isinstance(region_data, dict) or 'seasons' not in region_data:
                    continue
                
                region = region_data.get('region', {})
                region_name = region.get('name', 'Desconhecido')
                region_code = region.get('code', 'XX')
                
                for season_data in region_data['seasons']:
                    if not isinstance(season_data, dict):
                        continue
                    
                    league = season_data.get('league', {})
                    season = season_data.get('season', {})
                    matches = season_data.get('matches', [])
                    
                    if not league or not matches:
                        continue
                    
                    league_name = league.get('name', 'Liga Desconhecida')
                    league_relevance = league.get('relevance', 'low')
                    season_name = season.get('name', 'Temporada Desconhecida')
                    
                    for match in matches:
                        if not isinstance(match, dict):
                            continue
                        
                        jogo_processado = self.processar_partida_individual(
                            match, region_name, region_code, league_name, 
                            league_relevance, season_name
                        )
                        
                        if jogo_processado:
                            jogos.append(jogo_processado)
            
            # Ordenar por relevância e horário
            jogos.sort(key=lambda x: (
                self.get_relevance_priority(x['relevancia_liga']),
                x['horario'] if x['horario'] else '99:99'
            ))
            
            return jogos
            
        except Exception as e:
            print(f"❌ Erro ao processar jogos: {str(e)}")
            return []
    
    def processar_partida_individual(self, match, region_name, region_code, 
                                   league_name, league_relevance, season_name):
        """
        Processa uma partida individual
        
        Args:
            match: Dados da partida
            region_name: Nome da região
            region_code: Código da região
            league_name: Nome da liga
            league_relevance: Relevância da liga
            season_name: Nome da temporada
        
        Returns:
            dict: Dados processados da partida ou None
        """
        try:
            # Extrair dados básicos
            match_id = match.get('id', 'unknown')
            home_team = match.get('homeTeam', {})
            away_team = match.get('awayTeam', {})
            
            if not home_team or not away_team:
                return None
            
            # Nomes dos times
            home_name = home_team.get('name', 'Time Casa')
            away_name = away_team.get('name', 'Time Visitante')
            
            # Horário da partida
            match_time = match.get('matchTime', '')
            status = match.get('status', 'scheduled')
            
            # Estatísticas estimadas baseadas na liga
            stats_casa = self.estimar_estatisticas_time(home_team, league_relevance)
            stats_visitante = self.estimar_estatisticas_time(away_team, league_relevance)
            
            # Placar (se jogo em andamento ou finalizado)
            home_score = match.get('homeScore', 0)
            away_score = match.get('awayScore', 0)
            
            return {
                'id': match_id,
                'time_casa': home_name,
                'time_visitante': away_name,
                'horario': self.formatar_horario(match_time),
                'status': self.traduzir_status(status),
                'placar_casa': home_score,
                'placar_visitante': away_score,
                'regiao': region_name,
                'codigo_regiao': region_code,
                'liga': league_name,
                'relevancia_liga': league_relevance,
                'temporada': season_name,
                'stats_casa': stats_casa,
                'stats_visitante': stats_visitante,
                'atualizado_em': match.get('updatedAt', ''),
            }
            
        except Exception as e:
            print(f"❌ Erro ao processar partida individual: {str(e)}")
            return None
    
    def estimar_estatisticas_time(self, team_data, league_relevance):
        """
        Estima estatísticas do time baseado na liga e dados disponíveis
        
        Args:
            team_data: Dados do time
            league_relevance: Relevância da liga (high, medium, low)
        
        Returns:
            dict: Estatísticas estimadas
        """
        # Médias base por relevância da liga
        medias_base = {
            'high': {'gols_marcados': 1.4, 'gols_sofridos': 1.2},
            'medium': {'gols_marcados': 1.2, 'gols_sofridos': 1.1},
            'low': {'gols_marcados': 1.0, 'gols_sofridos': 1.0}
        }
        
        base = medias_base.get(league_relevance, medias_base['medium'])
        
        # Variação aleatória pequena para simular diferenças entre times
        import random
        variacao = random.uniform(0.85, 1.15)
        
        gols_marcados = round(base['gols_marcados'] * variacao, 2)
        gols_sofridos = round(base['gols_sofridos'] * (2 - variacao), 2)  # Inverso para defesa
        
        media_liga = base['gols_marcados']
        forca_ofensiva = round(gols_marcados / media_liga, 3)
        forca_defensiva = round(gols_sofridos / media_liga, 3)
        
        return {
            'gols_marcados': gols_marcados,
            'gols_sofridos': gols_sofridos,
            'forca_ofensiva': forca_ofensiva,
            'forca_defensiva': forca_defensiva,
            'media_liga': media_liga
        }
    
    def formatar_horario(self, match_time):
        """
        Formata o horário da partida
        
        Args:
            match_time: Horário bruto da API
        
        Returns:
            str: Horário formatado
        """
        try:
            if not match_time:
                return ''
            
            # Tentar diferentes formatos de data
            formatos = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S',
                '%H:%M'
            ]
            
            for formato in formatos:
                try:
                    dt = datetime.strptime(match_time, formato)
                    return dt.strftime('%H:%M')
                except ValueError:
                    continue
            
            # Se não conseguir converter, retornar original
            return str(match_time)[:5]
            
        except Exception:
            return ''
    
    def traduzir_status(self, status):
        """
        Traduz o status da partida
        
        Args:
            status: Status em inglês
        
        Returns:
            str: Status traduzido
        """
        traducoes = {
            'scheduled': 'Agendado',
            'live': 'Ao Vivo',
            'finished': 'Finalizado',
            'postponed': 'Adiado',
            'cancelled': 'Cancelado',
            'interrupted': 'Interrompido'
        }
        
        return traducoes.get(status, status.capitalize())
    
    def buscar_partidas_hoje(self):
        """
        Busca partidas que estão acontecendo hoje
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            url = f"{self.base_url}/public/results/{today}"
            print(f"📅 Buscando partidas de hoje...")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success' and 'data' in data:
                partidas = data['data']
                print(f"✅ Encontradas {len(partidas)} partidas hoje")
                
                # Filtrar apenas partidas que têm match_id
                partidas_validas = []
                for partida in partidas:
                    if 'matchId' in partida and partida['matchId']:
                        partidas_validas.append({
                            'match_id': partida['matchId'],
                            'home_team': partida.get('homeTeam', 'Time Casa'),
                            'away_team': partida.get('awayTeam', 'Time Visitante'),
                            'league': partida.get('league', 'Liga'),
                            'status': partida.get('status', 'Agendado'),
                            'time': partida.get('time', '')
                        })
                
                return partidas_validas
            else:
                print("❌ Nenhuma partida encontrada para hoje")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão ao buscar partidas: {e}")
            return []
        except Exception as e:
            print(f"❌ Erro inesperado ao buscar partidas: {e}")
            return []

    def buscar_estatisticas_time(self, match_id, field='home', window='last10'):
        """
        Busca estatísticas reais de um time baseado no match ID
        
        Args:
            match_id: ID da partida
            field: 'home' ou 'away' 
            window: 'last10' para últimos 10 jogos
        
        Returns:
            dict: Estatísticas calculadas do time
        """
        try:
            url = f"{self.base_url}/goalRadar/{match_id}"
            
            params = {
                'field': field,
                'window': window,
                'mode': 'anyField'
            }
            
            print(f"🔍 Buscando estatísticas do time {field} - Match ID: {match_id} (modo: anyField)")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data:
                print(f"❌ Dados não encontrados para match ID {match_id}")
                return None
            
            # Extrair estatísticas dos dados
            estatisticas = self.processar_estatisticas_time(data, field, 'anyField')
            
            print(f"✅ Estatísticas obtidas: {estatisticas['media_gols_marcados']:.2f} gols/jogo (marcados), {estatisticas['media_gols_sofridos']:.2f} gols/jogo (sofridos)")
            
            return estatisticas
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão ao buscar estatísticas: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas: {str(e)}")
            return None
    
    def processar_estatisticas_time(self, data, field, mode):
        """
        Processa os dados estatísticos retornados pela API
        
        Args:
            data: Dados da API goalRadar
            field: Campo do time (home/away)
            mode: Modo da busca (anyField)
        
        Returns:
            dict: Estatísticas processadas
        """
        try:
            dados_api = data['data']
            match_count = data.get('matchCount', 10)
            
            # Extrair somas de gols
            gols_marcados_total = dados_api['sums']['goalsScored']['fullTime']
            gols_sofridos_total = dados_api['sums']['goalsConceded']['fullTime']
            
            # Calcular médias
            media_gols_marcados = gols_marcados_total / match_count if match_count > 0 else 0
            media_gols_sofridos = gols_sofridos_total / match_count if match_count > 0 else 0
            
            # Estatísticas adicionais dos counts
            counts = dados_api.get('counts', {})
            
            # Análise de desempenho
            vitorias = counts.get('won', {}).get('fullTime', 0)
            empates = counts.get('drew', {}).get('fullTime', 0)
            derrotas = counts.get('lost', {}).get('fullTime', 0)
            
            # Percentuais
            perc_vitorias = (vitorias / match_count * 100) if match_count > 0 else 0
            perc_empates = (empates / match_count * 100) if match_count > 0 else 0
            perc_derrotas = (derrotas / match_count * 100) if match_count > 0 else 0
            
            # Análise de gols
            jogos_sem_marcar = counts.get('failToScore', {}).get('fullTime', 0)
            jogos_sem_sofrer = counts.get('cleanSheet', {}).get('fullTime', 0)
            
            # Mercados de gols (para análise adicional)
            markets = counts.get('markets', {}).get('matchGoals', {})
            over15 = markets.get('over15', 0)
            over25 = markets.get('over25', 0)
            btts = markets.get('btts', 0)  # Both Teams To Score
            
            # Forma recente (últimos jogos)
            forma = dados_api.get('race', [])
            
            # Calcular força ofensiva e defensiva baseada na média da liga
            media_liga_estimada = 1.2  # Estimativa padrão
            forca_ofensiva = media_gols_marcados / media_liga_estimada if media_liga_estimada > 0 else 1
            forca_defensiva = media_gols_sofridos / media_liga_estimada if media_liga_estimada > 0 else 1
            
            estatisticas = {
                'match_id': data.get('matchId'),
                'field': field,
                'mode': mode,
                'match_count': match_count,
                'media_gols_marcados': round(media_gols_marcados, 2),
                'media_gols_sofridos': round(media_gols_sofridos, 2),
                'gols_marcados_total': gols_marcados_total,
                'gols_sofridos_total': gols_sofridos_total,
                'forca_ofensiva': round(forca_ofensiva, 3),
                'forca_defensiva': round(forca_defensiva, 3),
                'vitorias': vitorias,
                'empates': empates,
                'derrotas': derrotas,
                'perc_vitorias': round(perc_vitorias, 1),
                'perc_empates': round(perc_empates, 1),
                'perc_derrotas': round(perc_derrotas, 1),
                'jogos_sem_marcar': jogos_sem_marcar,
                'jogos_sem_sofrer': jogos_sem_sofrer,
                'over15_jogos': over15,
                'over25_jogos': over25,
                'btts_jogos': btts,
                'forma_recente': forma[:5],  # Últimos 5 resultados
                'updated_at': data.get('updatedAt')
            }
            
            return estatisticas
            
        except Exception as e:
            print(f"❌ Erro ao processar estatísticas: {str(e)}")
            return None
    
    def buscar_estatisticas_detalhadas_time(self, match_id):
        """
        Busca estatísticas detalhadas de ambos os times de um jogo específico
        USA APENAS DADOS GERAIS (anyField) - sem separação casa/fora
        
        Args:
            match_id: ID da partida
        
        Returns:
            dict: Estatísticas detalhadas dos times
        """
        try:
            print(f"📊 Buscando estatísticas detalhadas para Match ID: {match_id}")
            
            # Buscar APENAS estatísticas gerais (anyField) - sem delay
            stats_casa_geral = self.buscar_estatisticas_time(match_id, 'home')  # Casa geral
            stats_visitante_geral = self.buscar_estatisticas_time(match_id, 'away')  # Visitante geral
            
            if not all([stats_casa_geral, stats_visitante_geral]):
                print("❌ Não foi possível obter estatísticas gerais")
                return None
            
            estatisticas_detalhadas = {
                'match_id': match_id,
                'time_casa': {
                    'nome': stats_casa_geral.get('nome', 'Time Casa'),
                    'geral': {
                        'gols_marcados': stats_casa_geral['media_gols_marcados'],
                        'gols_sofridos': stats_casa_geral['media_gols_sofridos'],
                        'vitorias': stats_casa_geral['vitorias'],
                        'empates': stats_casa_geral['empates'],
                        'derrotas': stats_casa_geral['derrotas'],
                        'btts': stats_casa_geral['btts_jogos'],
                        'over15': stats_casa_geral['over15_jogos'],
                        'over25': stats_casa_geral['over25_jogos'],
                        'forma': stats_casa_geral['forma_recente']
                    }
                },
                'time_visitante': {
                    'nome': stats_visitante_geral.get('nome', 'Time Visitante'),
                    'geral': {
                        'gols_marcados': stats_visitante_geral['media_gols_marcados'],
                        'gols_sofridos': stats_visitante_geral['media_gols_sofridos'],
                        'vitorias': stats_visitante_geral['vitorias'],
                        'empates': stats_visitante_geral['empates'],
                        'derrotas': stats_visitante_geral['derrotas'],
                        'btts': stats_visitante_geral['btts_jogos'],
                        'over15': stats_visitante_geral['over15_jogos'],
                        'over25': stats_visitante_geral['over25_jogos'],
                        'forma': stats_visitante_geral['forma_recente']
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ Estatísticas detalhadas obtidas com sucesso")
            return estatisticas_detalhadas
            
        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas detalhadas: {str(e)}")
            return None
    
    def buscar_estatisticas_confronto(self, match_id):
        """
        Busca estatísticas de ambos os times de um confronto
        USA APENAS DADOS GERAIS (anyField)
        
        Args:
            match_id: ID da partida
        
        Returns:
            dict: Estatísticas de ambos os times
        """
        try:
            print(f"📊 Buscando estatísticas completas do confronto - Match ID: {match_id}")
            
            # Buscar APENAS dados gerais (anyField) - sem delay
            stats_casa = self.buscar_estatisticas_time(match_id, 'home')
            
            # Buscar dados do time visitante
            stats_visitante = self.buscar_estatisticas_time(match_id, 'away')
            
            if not stats_casa or not stats_visitante:
                print("❌ Não foi possível obter estatísticas completas")
                return None
            
            confronto = {
                'match_id': match_id,
                'mode': 'anyField',
                'time_casa': stats_casa,
                'time_visitante': stats_visitante,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ Estatísticas do confronto obtidas com sucesso")
            return confronto
            
        except Exception as e:
            print(f"❌ Erro ao buscar estatísticas do confronto: {str(e)}")
            return None
    
    def buscar_varias_datas(self, data_inicio, data_fim):
        """
        Busca jogos em um intervalo de datas
        
        Args:
            data_inicio: Data de início (YYYY-MM-DD)
            data_fim: Data de fim (YYYY-MM-DD)
        
        Returns:
            dict: Jogos organizados por data
        """
        try:
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            fim = datetime.strptime(data_fim, '%Y-%m-%d')
            
            jogos_por_data = {}
            data_atual = inicio
            
            while data_atual <= fim:
                data_str = data_atual.strftime('%Y-%m-%d')
                jogos = self.buscar_jogos_do_dia(data_str)
                
                if jogos:
                    jogos_por_data[data_str] = jogos
                
                data_atual += timedelta(days=1)
                time.sleep(0.5)  # Pausa entre requisições
            
            return jogos_por_data
            
        except Exception as e:
            print(f"❌ Erro ao buscar várias datas: {str(e)}")
            return {}
    
    def get_relevance_priority(self, relevance):
        """
        Converte relevância em prioridade numérica para ordenação
        
        Args:
            relevance: Relevância da liga
        
        Returns:
            int: Prioridade (menor = maior relevância)
        """
        priorities = {
            'high': 1,
            'medium': 2,
            'low': 3
        }
        
        return priorities.get(relevance, 4)
