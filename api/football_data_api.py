#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Alternativa usando Football-Data.org (API Gratuita)
Solução para contornar limitações do SofaScore
"""

import urllib.request
import urllib.parse
import urllib.error
import json
from typing import Dict, List, Optional
import time

class FootballDataAPI:
    """
    Integração com Football-Data.org - API gratuita para dados de futebol
    """
    
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        
        # API Key gratuita (30 requests/minute)
        # Registre-se em: https://www.football-data.org/client/register
        self.api_key = "YOUR_API_KEY_HERE"  # Substitua pela sua chave
        
        self.headers = {
            'X-Auth-Token': self.api_key,
            'Accept': 'application/json'
        }
        
        self.timeout = 10  # Timeout padrão para requisições
    
    def buscar_times_por_liga(self, liga_id: int) -> List[Dict]:
        """
        Busca times de uma liga específica
        
        Args:
            liga_id: ID da liga (ex: 2013 = Brasileirão, 2014 = La Liga)
            
        Returns:
            Lista de times da liga
        """
        try:
            url = f"{self.base_url}/competitions/{liga_id}/teams"
            
            # Criar requisição com urllib
            req = urllib.request.Request(url)
            for key, value in self.headers.items():
                req.add_header(key, value)
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data.get('teams', [])
                else:
                    print(f"Erro na API: {response.getcode()}")
                    return []
                
        except urllib.error.HTTPError as e:
            print(f"Erro HTTP {e.code}: {e.reason}")
            return []
        except urllib.error.URLError as e:
            print(f"Erro de conexão: {e.reason}")
            return []
        except Exception as e:
            print(f"Erro ao buscar times: {e}")
            return []
    
    def obter_ligas_disponiveis(self) -> List[Dict]:
        """Obtém lista de ligas disponíveis"""
        try:
            url = f"{self.base_url}/competitions"
            
            # Criar requisição com urllib
            req = urllib.request.Request(url)
            for key, value in self.headers.items():
                req.add_header(key, value)
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data.get('competitions', [])
                else:
                    return []
                
        except Exception as e:
            print(f"Erro ao obter ligas: {e}")
            return []

# IDs das principais ligas na Football-Data.org
LIGAS_PRINCIPAIS = {
    'Premier League': 2021,
    'La Liga': 2014,
    'Serie A': 2019,
    'Bundesliga': 2002,
    'Ligue 1': 2015,
    'Eredivisie': 2003,
    'Liga Portugal': 2017,
    'Championship': 2016,
    'Copa do Mundo': 2000,
    'Euros': 2018
}

def demonstrar_api():
    """Demonstra o uso da API Football-Data"""
    api = FootballDataAPI()
    
    print("🔍 Demonstrando Football-Data.org API...")
    print("\n📋 Ligas Principais Disponíveis:")
    
    for liga, id_liga in LIGAS_PRINCIPAIS.items():
        print(f"   • {liga}: ID {id_liga}")
    
    print(f"\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 Buscando times da Premier League...")
    times_pl = api.buscar_times_por_liga(2021)
    
    if times_pl:
        print(f"✅ Encontrados {len(times_pl)} times:")
        for time in times_pl[:5]:  # Mostrar apenas 5
            print(f"   • {time.get('name')} - {time.get('area', {}).get('name')}")
    else:
        print("❌ Não foi possível obter dados da API")
        print("💡 Verifique se você registrou uma API key em:")
        print("   https://www.football-data.org/client/register")

if __name__ == "__main__":
    demonstrar_api()
