# BET BOOSTER V2 - Documentação Completa

## 🚀 VISÃO GERAL

O **BET BOOSTER V2** é uma reestruturação completa do sistema de análise de apostas esportivas, implementando funcionalidades avançadas para identificação de value bets, análise automática de jogos e gestão de apostas múltiplas.

## ✨ NOVAS FUNCIONALIDADES V2

### 1. 🔥 APOSTAS HOT - Recomendações Automáticas
- **Análise automática** dos jogos do dia
- **Identificação de value bets** com probabilidades implícitas
- **Classificação inteligente**: FORTE vs ARRISCADA
- **Critérios de recomendação**:
  - **FORTE**: Maior probabilidade implícita + value ≥ 20%
  - **ARRISCADA**: Menor probabilidade implícita + value ≥ 10% + prob ≥ 15%

### 2. ⚽ JOGOS DO DIA - Integração Completa
- **100% integrado** com outras funcionalidades
- **Odds em tempo real** via API Radar Esportivo
- **Status automático**: Agendado / AO VIVO / Encerrado
- **Ações integradas**:
  - Calcular probabilidades
  - Aposta simples
  - Adicionar à múltipla
  - Editar jogo ao vivo

### 3. ⏰ SISTEMA DE STATUS INTELIGENTE
- **Detecção automática** baseada em `startTime`
- **Jogo ao vivo**: quando hora atual > startTime
- **Jogo encerrado**: após 120 minutos do início
- **Desconsideração** do campo `status` (não confiável)

### 4. ⚡ EDIÇÃO AO VIVO
- **Placar em tempo real** para jogos ao vivo
- **Tempo de partida** atual
- **Estatísticas adicionais**: cartões, escanteios
- **Recálculo automático** das probabilidades

### 5. 📊 PROBABILIDADE IMPLÍCITA
- **Cálculo automático** das odds da casa
- **Comparação** com probabilidades calculadas
- **Identificação de value bets**
- **Recomendação baseada** na maior probabilidade implícita

### 6. 🎯 GESTÃO DE MÚLTIPLAS
- **Interface dedicada** para múltiplas
- **Cálculo automático** de odd total
- **Análise de risco** baseada em probabilidades
- **Relatórios detalhados** de retorno

### 7. 💾 PERSISTÊNCIA DE DADOS
- **Integração com database** existente
- **Suporte a odds** (`marketOdds.resultFt`)
- **Horário de partida** (`startTime`)
- **Compatibilidade** com cadastro manual

## 📋 ESTRUTURA DE DADOS

### Jogo Completo
```json
{
  "match_id": "262115",
  "home_team": "Avai",
  "away_team": "Amazonas FC",
  "start_time": "2025-08-26T00:30:00.000Z",
  "league": "Brazil Serie B",
  "status_calculado": "Agendado",
  "odds": {
    "resultFt": {
      "home": 1.615,
      "draw": 3.7,
      "away": 5.75
    },
    "goalsOu25": {
      "over": 2.2,
      "under": 1.65
    }
  }
}
```

### Aposta Hot
```json
{
  "jogo": "Avai vs Amazonas FC",
  "aposta": "Vitória Casa",
  "tipo": "FORTE",
  "odd": 1.615,
  "value": 1.247,
  "prob_calculada": 62.0,
  "prob_implicita": 61.9,
  "forca_recomendacao": 0.772
}
```

## 🔧 FUNCIONAMENTO TÉCNICO

### Algoritmo de Recomendações
1. **Busca automática** dos jogos do dia
2. **Obtenção de odds** via API prepRadar
3. **Cálculo de estatísticas** detalhadas por time
4. **Aplicação de distribuição de Poisson** para probabilidades
5. **Cálculo de probabilidades implícitas**: `1/odd * 100`
6. **Identificação de value**: `prob_calculada / prob_implicita`
7. **Classificação FORTE/ARRISCADA** baseada na maior prob. implícita

### Cálculo de Status
```python
def determinar_status_jogo(start_time):
    agora = datetime.now()
    start_dt_local = start_dt - timedelta(hours=3)  # GMT-3
    
    if agora < start_dt_local:
        return "Agendado"
    elif agora <= start_dt_local + timedelta(minutes=120):
        return "🔴 AO VIVO"
    else:
        return "Encerrado"
```

### Distribuição de Poisson
```python
prob_resultado = (gols_esperados ** gols * exp(-gols_esperados)) / factorial(gols)
```

## 🎮 GUIA DE USO

### 1. Apostas Hot
1. Abra a aba **"🔥 Apostas Hot"**
2. Clique em **"🔄 Atualizar Apostas Hot"**
3. Aguarde a análise automática
4. Visualize recomendações **FORTES** (🟢) e **ARRISCADAS** (🟡)
5. Use **"📋 Adicionar à Múltipla"** para apostas interessantes

### 2. Jogos do Dia
1. Abra a aba **"⚽ Jogos do Dia"**
2. Selecione a data desejada
3. Clique em **"🔍 Buscar Jogos"**
4. Duplo-clique em um jogo para selecioná-lo
5. Use as ações disponíveis:
   - **📊 Calcular Probabilidades**
   - **💰 Aposta Simples**
   - **📋 Adicionar à Múltipla**
   - **⚡ Editar Jogo Ao Vivo** (se aplicável)

### 3. Cadastro Manual
1. Abra a aba **"➕ Cadastro Manual"**
2. Preencha as informações do time
3. Inclua estatísticas gerais, casa e fora
4. Adicione forma recente (V/E/D)
5. Clique em **"💾 Cadastrar Time"**

### 4. Análise de Confrontos
1. Abra a aba **"📊 Análise"**
2. Selecione o modo: **"Dados Gerais"** ou **"Casa/Fora"**
3. Escolha os times nos combos
4. Clique em **"📊 Analisar Confronto"**
5. Visualize o relatório detalhado

### 5. Múltiplas
1. Abra a aba **"🎯 Múltiplas"**
2. Adicione apostas via outras abas
3. Visualize odd total e probabilidade
4. Use **"📊 Calcular Retorno"** para análise financeira
5. **"💾 Salvar Múltipla"** para persistir

## ⚙️ CONFIGURAÇÕES E FILTROS

### Filtros de Apostas Hot
- **Probabilidade mínima**: 15%
- **Value mínimo**: 10% (1.10)
- **Value forte**: 20% (1.20)
- **Ligas suportadas**: Todas com odds disponíveis

### Modos de Análise
- **Dados Gerais**: Estatísticas completas do time
- **Casa/Fora**: Estatísticas específicas do mando de campo

## 🔍 TROUBLESHOOTING

### Problemas Comuns

**❌ "Nenhum jogo encontrado"**
- Verifique a data selecionada
- Confirme conexão com internet
- Tente uma data diferente

**❌ "Odds não disponíveis"**
- Nem todos os jogos têm odds
- Verifique se é um jogo importante
- Use cadastro manual como alternativa

**❌ "Erro ao buscar estatísticas"**
- API pode estar sobrecarregada
- Aguarde alguns segundos e tente novamente
- Verifique conexão com internet

**❌ "Status não atualiza"**
- Clique em **"🔄 Atualizar Status"**
- Verifique se o horário do sistema está correto
- Status é baseado em `startTime`, não em `status`

### Limitações Conhecidas

1. **Dependência de internet** para odds e estatísticas
2. **Rate limiting** da API (pause entre requisições)
3. **Odds limitadas** a jogos principais
4. **Status manual** necessário para alguns jogos

## 📊 MÉTRICAS E ANÁLISES

### Indicadores de Performance
- **Taxa de acerto** das recomendações FORTE: esperado > 60%
- **Value médio** identificado: 15-25%
- **Cobertura de jogos** com odds: 70-80%
- **Tempo de análise**: < 30 segundos por jogo

### Relatórios Disponíveis
- **Relatório de Aposta Simples**: análise completa individual
- **Relatório de Múltipla**: análise de risco e retorno
- **Estatísticas de Time**: detalhamento completo
- **Análise de Confronto**: probabilidades e recomendações

## 🔄 ATUALIZAÇÕES E MELHORIAS

### Próximas Funcionalidades
- [ ] Histórico de apostas realizadas
- [ ] Estatísticas de performance do usuário
- [ ] Alertas para jogos ao vivo
- [ ] Integração com mais casas de apostas
- [ ] Machine learning para recomendações

### Changelog V2
- ✅ Sistema de Apostas Hot implementado
- ✅ Integração completa Jogos do Dia
- ✅ Probabilidade implícita implementada
- ✅ Status automático de jogos
- ✅ Edição ao vivo implementada
- ✅ Gestão de múltiplas completa
- ✅ Interface renovada e otimizada

## 📞 SUPORTE

Para dúvidas, problemas ou sugestões:
- Verifique este manual primeiro
- Execute o teste completo: `teste_completo_v2.py`
- Consulte os logs de erro no console
- Verifique se todas as dependências estão instaladas

---

**BET BOOSTER V2** - Sistema Avançado de Análise de Apostas Esportivas
*Versão 2.0 - Reestruturação Completa*
