#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstração dos Cálculos da Calculadora de Apostas
Exemplo prático: Cruzeiro vs Internacional
"""

import math

def calcular_exemplo_completo():
    """Demonstra os cálculos com dados reais"""
    
    print("="*80)
    print("DEMONSTRAÇÃO: CRUZEIRO vs INTERNACIONAL")
    print("="*80)
    
    # Dados dos times (do CSV fornecido)
    cruzeiro = {
        'nome': 'Cruzeiro',
        'gols_marcados': 1.6,
        'gols_sofridos': 0.7,
        'posicao': 'Casa'
    }
    
    internacional = {
        'nome': 'Internacional', 
        'gols_marcados': 1.2,
        'gols_sofridos': 1.4,
        'posicao': 'Visitante'
    }
    
    # Configurações
    media_liga = 1.2
    fator_casa = 1.15
    
    # Odds da casa
    odds = {
        'cruzeiro': 2.15,
        'empate': 3.10,
        'internacional': 3.75
    }
    
    print(f"📊 DADOS DOS TIMES:")
    print(f"• {cruzeiro['nome']} ({cruzeiro['posicao']}):")
    print(f"  - Gols marcados: {cruzeiro['gols_marcados']:.1f}/jogo")
    print(f"  - Gols sofridos: {cruzeiro['gols_sofridos']:.1f}/jogo")
    print(f"• {internacional['nome']} ({internacional['posicao']}):")
    print(f"  - Gols marcados: {internacional['gols_marcados']:.1f}/jogo") 
    print(f"  - Gols sofridos: {internacional['gols_sofridos']:.1f}/jogo")
    
    print(f"\n⚙️ CONFIGURAÇÕES:")
    print(f"• Média da liga: {media_liga} gols/time/jogo")
    print(f"• Fator casa: {fator_casa}")
    
    # Cálculo das forças
    print(f"\n🔢 CÁLCULO DAS FORÇAS:")
    
    forca_of_cru = cruzeiro['gols_marcados'] / media_liga
    forca_def_cru = cruzeiro['gols_sofridos'] / media_liga
    forca_of_int = internacional['gols_marcados'] / media_liga
    forca_def_int = internacional['gols_sofridos'] / media_liga
    
    print(f"• Cruzeiro - Força ofensiva: {forca_of_cru:.3f}")
    print(f"• Cruzeiro - Força defensiva: {forca_def_cru:.3f}")
    print(f"• Internacional - Força ofensiva: {forca_of_int:.3f}")
    print(f"• Internacional - Força defensiva: {forca_def_int:.3f}")
    
    # Gols esperados
    print(f"\n⚽ GOLS ESPERADOS (Modelo de Poisson):")
    
    gols_esp_cru = forca_of_cru * forca_def_int * media_liga * fator_casa
    gols_esp_int = forca_of_int * forca_def_cru * media_liga
    
    print(f"• Cruzeiro: {forca_of_cru:.3f} × {forca_def_int:.3f} × {media_liga} × {fator_casa} = {gols_esp_cru:.2f}")
    print(f"• Internacional: {forca_of_int:.3f} × {forca_def_cru:.3f} × {media_liga} = {gols_esp_int:.2f}")
    print(f"• Total esperado: {gols_esp_cru + gols_esp_int:.2f} gols")
    
    # Calcular probabilidades usando Poisson
    print(f"\n🎯 PROBABILIDADES (Distribuição de Poisson):")
    
    prob_vit_cru = 0
    prob_empate = 0
    prob_vit_int = 0
    
    # Simular até 6 gols para cada time (cobertura de ~99% dos casos)
    for gols_cru in range(7):
        for gols_int in range(7):
            # P(X=k) = (λ^k * e^(-λ)) / k!
            prob_cru = (gols_esp_cru ** gols_cru * math.exp(-gols_esp_cru)) / math.factorial(gols_cru)
            prob_int = (gols_esp_int ** gols_int * math.exp(-gols_esp_int)) / math.factorial(gols_int)
            prob_combinada = prob_cru * prob_int
            
            if gols_cru > gols_int:
                prob_vit_cru += prob_combinada
            elif gols_cru == gols_int:
                prob_empate += prob_combinada
            else:
                prob_vit_int += prob_combinada
    
    print(f"• Vitória Cruzeiro: {prob_vit_cru:.1%} ({prob_vit_cru:.4f})")
    print(f"• Empate: {prob_empate:.1%} ({prob_empate:.4f})")
    print(f"• Vitória Internacional: {prob_vit_int:.1%} ({prob_vit_int:.4f})")
    print(f"• Soma: {prob_vit_cru + prob_empate + prob_vit_int:.1%}")
    
    # Análise de odds
    print(f"\n💰 ANÁLISE DE ODDS:")
    
    prob_impl_cru = 1 / odds['cruzeiro']
    prob_impl_emp = 1 / odds['empate'] 
    prob_impl_int = 1 / odds['internacional']
    
    margem_casa = (prob_impl_cru + prob_impl_emp + prob_impl_int - 1) * 100
    
    print(f"┌─────────────────────────────────────────────────────────────────┐")
    print(f"│ Resultado     │ Nossa Prob │ Odd   │ Prob Impl │ Value Bet?    │")
    print(f"├─────────────────────────────────────────────────────────────────┤")
    print(f"│ Cruzeiro      │ {prob_vit_cru:>8.1%} │ {odds['cruzeiro']:>5.2f} │ {prob_impl_cru:>8.1%} │ {'✅ SIM' if prob_vit_cru > prob_impl_cru else '❌ NÃO':>11} │")
    print(f"│ Empate        │ {prob_empate:>8.1%} │ {odds['empate']:>5.2f} │ {prob_impl_emp:>8.1%} │ {'✅ SIM' if prob_empate > prob_impl_emp else '❌ NÃO':>11} │")
    print(f"│ Internacional │ {prob_vit_int:>8.1%} │ {odds['internacional']:>5.2f} │ {prob_impl_int:>8.1%} │ {'✅ SIM' if prob_vit_int > prob_impl_int else '❌ NÃO':>11} │")
    print(f"└─────────────────────────────────────────────────────────────────┘")
    
    print(f"\n📊 VANTAGENS PERCENTUAIS:")
    vant_cru = (prob_vit_cru - prob_impl_cru) / prob_impl_cru * 100
    vant_emp = (prob_empate - prob_impl_emp) / prob_impl_emp * 100
    vant_int = (prob_vit_int - prob_impl_int) / prob_impl_int * 100
    
    print(f"• Cruzeiro: {vant_cru:+.1f}%")
    print(f"• Empate: {vant_emp:+.1f}%") 
    print(f"• Internacional: {vant_int:+.1f}%")
    print(f"• Margem da casa: {margem_casa:.2f}%")
    
    # Recomendações
    print(f"\n🎯 RECOMENDAÇÕES:")
    
    recomendacoes = []
    if prob_vit_cru > prob_impl_cru and vant_cru > 5:
        recomendacoes.append(f"🔥 FORTE: Apostar em Cruzeiro (Vantagem: {vant_cru:.1f}%)")
    if prob_empate > prob_impl_emp and vant_emp > 5:
        recomendacoes.append(f"🔥 FORTE: Apostar em Empate (Vantagem: {vant_emp:.1f}%)")
    if prob_vit_int > prob_impl_int and vant_int > 5:
        recomendacoes.append(f"🔥 FORTE: Apostar em Internacional (Vantagem: {vant_int:.1f}%)")
    
    if recomendacoes:
        for rec in recomendacoes:
            print(f"{rec}")
    else:
        print("⚠️  Não foram encontrados value bets significativos (>5%)")
        print("   Aguarde melhores oportunidades ou odds mais favoráveis")
    
    # Exemplo de aposta
    print(f"\n💸 EXEMPLO DE APOSTA:")
    valor_aposta = 100
    
    if recomendacoes:
        # Pegar a melhor recomendação (maior vantagem)
        if vant_cru > max(vant_emp, vant_int) and vant_cru > 5:
            retorno = valor_aposta * odds['cruzeiro']
            lucro = retorno - valor_aposta
            print(f"• Apostar R$ {valor_aposta:.2f} em Cruzeiro")
            print(f"• Retorno potencial: R$ {retorno:.2f}")
            print(f"• Lucro potencial: R$ {lucro:.2f}")
            print(f"• Probabilidade de ganhar: {prob_vit_cru:.1%}")
        elif vant_emp > max(vant_cru, vant_int) and vant_emp > 5:
            retorno = valor_aposta * odds['empate']
            lucro = retorno - valor_aposta
            print(f"• Apostar R$ {valor_aposta:.2f} em Empate")
            print(f"• Retorno potencial: R$ {retorno:.2f}")
            print(f"• Lucro potencial: R$ {lucro:.2f}")
            print(f"• Probabilidade de ganhar: {prob_empate:.1%}")
        elif vant_int > 5:
            retorno = valor_aposta * odds['internacional']
            lucro = retorno - valor_aposta
            print(f"• Apostar R$ {valor_aposta:.2f} em Internacional")
            print(f"• Retorno potencial: R$ {retorno:.2f}")
            print(f"• Lucro potencial: R$ {lucro:.2f}")
            print(f"• Probabilidade de ganhar: {prob_vit_int:.1%}")
    else:
        print("• Não recomendado apostar neste confronto")
        print("• Aguarde odds mais favoráveis")
    
    print(f"\n{'='*80}")
    print("ANÁLISE CONCLUÍDA")
    print("Para usar a interface gráfica, execute: python interface_apostas.py")
    print(f"{'='*80}")

if __name__ == "__main__":
    calcular_exemplo_completo()
