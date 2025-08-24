# -*- coding: utf-8 -*-
"""
Teste para verificar cálculos casa/fora vs geral
"""

def teste_calculo_casa_fora():
    """Testa diferença entre cálculos casa/fora e geral"""
    
    print("🧪 Testando diferença Casa/Fora vs Geral...")
    
    # Dados do Oviedo (casa)
    oviedo_dados = {
        'gols_marcados': 0.8,  # dados gerais
        'gols_sofridos': 0.9,
        'gols_marcados_casa': 1.4,  # dados casa
        'gols_sofridos_casa': 0.6,
        'forca_ofensiva': None,
        'forca_defensiva': None
    }
    
    # Dados do Real Madrid (fora)
    real_dados = {
        'gols_marcados': 2.0,  # dados gerais
        'gols_sofridos': 0.8,
        'gols_marcados_fora': 1.8,  # dados fora
        'gols_sofridos_fora': 1.4,
        'forca_ofensiva': None,
        'forca_defensiva': None
    }
    
    # Função para obter dados casa/fora
    def obter_dados_casa_fora(dados_time, tipo):
        try:
            if tipo == "casa":
                if 'gols_marcados_casa' in dados_time and dados_time['gols_marcados_casa'] is not None:
                    gols_marcados = dados_time['gols_marcados_casa']
                    gols_sofridos = dados_time['gols_sofridos_casa']
                else:
                    gols_marcados = dados_time['gols_marcados']
                    gols_sofridos = dados_time['gols_sofridos']
            else:  # fora
                if 'gols_marcados_fora' in dados_time and dados_time['gols_marcados_fora'] is not None:
                    gols_marcados = dados_time['gols_marcados_fora']
                    gols_sofridos = dados_time['gols_sofridos_fora']
                else:
                    gols_marcados = dados_time['gols_marcados']
                    gols_sofridos = dados_time['gols_sofridos']
            
            return {
                'gols_marcados': gols_marcados,
                'gols_sofridos': gols_sofridos,
                'forca_ofensiva': None,
                'forca_defensiva': None
            }
        except Exception as e:
            print(f"Erro: {e}")
            return dados_time
    
    # Função para calcular gols esperados
    def calcular_gols_esperados(time_a_dados, time_b_dados):
        media_liga = 1.2
        fator_casa = 1.15
        
        # Verificar dados
        gols_marcados_a = max(0.1, float(time_a_dados.get('gols_marcados') or 0))
        gols_sofridos_a = max(0.1, float(time_a_dados.get('gols_sofridos') or 0))
        gols_marcados_b = max(0.1, float(time_b_dados.get('gols_marcados') or 0))
        gols_sofridos_b = max(0.1, float(time_b_dados.get('gols_sofridos') or 0))
        
        # Calcular forças
        forca_of_a = gols_marcados_a / media_liga
        forca_def_a = gols_sofridos_a / media_liga
        forca_of_b = gols_marcados_b / media_liga
        forca_def_b = gols_sofridos_b / media_liga
        
        # Gols esperados
        gols_esperados_a = forca_of_a * forca_def_b * media_liga * fator_casa
        gols_esperados_b = forca_of_b * forca_def_a * media_liga
        
        return gols_esperados_a, gols_esperados_b
    
    # Teste com dados GERAIS
    print("\n📊 DADOS GERAIS:")
    print(f"Oviedo: {oviedo_dados['gols_marcados']} gols marcados, {oviedo_dados['gols_sofridos']} gols sofridos")
    print(f"Real Madrid: {real_dados['gols_marcados']} gols marcados, {real_dados['gols_sofridos']} gols sofridos")
    
    gols_esp_a_geral, gols_esp_b_geral = calcular_gols_esperados(oviedo_dados, real_dados)
    print(f"Gols esperados - Oviedo: {gols_esp_a_geral:.2f}, Real Madrid: {gols_esp_b_geral:.2f}")
    
    # Teste com dados CASA/FORA
    print("\n🏠 DADOS CASA/FORA:")
    dados_oviedo_casa = obter_dados_casa_fora(oviedo_dados, "casa")
    dados_real_fora = obter_dados_casa_fora(real_dados, "fora")
    
    print(f"Oviedo (casa): {dados_oviedo_casa['gols_marcados']} gols marcados, {dados_oviedo_casa['gols_sofridos']} gols sofridos")
    print(f"Real Madrid (fora): {dados_real_fora['gols_marcados']} gols marcados, {dados_real_fora['gols_sofridos']} gols sofridos")
    
    gols_esp_a_casa_fora, gols_esp_b_casa_fora = calcular_gols_esperados(dados_oviedo_casa, dados_real_fora)
    print(f"Gols esperados - Oviedo: {gols_esp_a_casa_fora:.2f}, Real Madrid: {gols_esp_b_casa_fora:.2f}")
    
    # Comparação
    print(f"\n🔍 DIFERENÇA:")
    diff_oviedo = gols_esp_a_casa_fora - gols_esp_a_geral
    diff_real = gols_esp_b_casa_fora - gols_esp_b_geral
    print(f"Diferença Oviedo: {diff_oviedo:+.2f} gols")
    print(f"Diferença Real Madrid: {diff_real:+.2f} gols")
    
    if abs(diff_oviedo) > 0.01 or abs(diff_real) > 0.01:
        print("✅ Cálculos diferentes detectados - funcionando corretamente!")
    else:
        print("❌ Cálculos iguais - problema não resolvido!")

if __name__ == "__main__":
    teste_calculo_casa_fora()
    print("\n🎯 Teste concluído!")
