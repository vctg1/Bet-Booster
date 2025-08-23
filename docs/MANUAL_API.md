# 🔍 Integração com API SofaScore - Manual do Usuário

## 📋 Visão Geral

O sistema agora conta com integração completa com a API do SofaScore, permitindo buscar times reais com estatísticas atualizadas automaticamente. Como fallback, também possui uma base de dados local com mais de 50 times populares do mundo todo.

## 🆕 Nova Aba: "🔍 Buscar Times (API)"

### Como Usar:

1. **Digite o nome do time** no campo de busca
2. **Clique em "🔍 Buscar"** ou pressione Enter
3. **Aguarde os resultados** aparecerem na tabela
4. **Selecione um time** da lista
5. **Clique em "➕ Adicionar Time Selecionado"** para adicionar ao sistema

### 📊 Informações Exibidas:

- **Nome do Time**: Nome oficial
- **País**: Nacionalidade do time
- **Liga**: Campeonato principal
- **Gols/Partida**: Média de gols marcados
- **Gols Sofridos**: Média de gols sofridos
- **Estádio**: Nome do estádio
- **Popularidade**: Número de seguidores

## 🌐 Fontes de Dados

### 1. API SofaScore (Principal)
- **Dados em tempo real** de times do mundo todo
- **Estatísticas oficiais** das principais ligas
- **Informações detalhadas** sobre estádios, técnicos, etc.

### 2. Base Local (Fallback)
Quando a API não está disponível, usa base curada com:

#### 🇧🇷 Brasil - Série A (13 times)
- Flamengo, Palmeiras, Corinthians, São Paulo
- Santos, Grêmio, Internacional, Cruzeiro
- Atlético-MG, Botafogo, Vasco, Fluminense, Bragantino

#### 🇪🇸 Espanha - La Liga (5 times)
- Barcelona, Real Madrid, Atlético Madrid
- Sevilla, Valencia

#### 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra - Premier League (6 times)
- Manchester City, Manchester United, Liverpool
- Arsenal, Chelsea, Tottenham

#### 🇮🇹 Itália - Serie A (5 times)
- Juventus, AC Milan, Inter Milan, Napoli, Roma

#### 🇩🇪 Alemanha - Bundesliga (4 times)
- Bayern Munich, Borussia Dortmund, RB Leipzig, Bayer Leverkusen

#### 🇫🇷 França - Ligue 1 (3 times)
- Paris Saint-Germain, Lyon, Marseille

#### 🇵🇹 Portugal - Primeira Liga (3 times)
- FC Porto, SL Benfica, Sporting CP

#### 🇦🇷 Argentina - Liga Profesional (2 times)
- Boca Juniors, River Plate

## 🎯 Funcionalidades Avançadas

### 📋 Ver Detalhes
- Clique em "📋 Ver Detalhes" para ver informações completas
- Janela popup com dados técnicos, histórico e estatísticas

### 🔄 Atualização Automática
- Times são adicionados automaticamente ao sistema
- Estatísticas calculadas com base na liga
- Forças ofensiva e defensiva calculadas automaticamente

### ⚡ Interface Inteligente
- **Busca em tempo real** sem travar a interface
- **Status visual** durante as operações
- **Feedback instantâneo** para cada ação

## 📈 Cálculo de Estatísticas

### Método API:
1. **Popularidade**: Times mais populares = melhores estatísticas
2. **Liga**: Cada liga tem média específica de gols
3. **Fator de ajuste**: Baseado em seguidores e histórico

### Método Local:
1. **Dados curados**: Estatísticas reais da temporada
2. **Forças calculadas**: Baseadas na média da liga
3. **Precisão alta**: Dados verificados manualmente

## 💡 Dicas de Uso

### ✅ Melhores Práticas:
- Use **nomes completos** para busca mais precisa
- Teste **variações do nome** se não encontrar
- **Barcelona**, **FC Barcelona**, **Barça** - todos funcionam
- Prefira a busca por API quando disponível

### ⚠️ Limitações:
- API pode estar indisponível ocasionalmente
- Alguns times menores podem não estar na base local
- Estatísticas são estimativas baseadas na liga

## 🔧 Solução de Problemas

### "Nenhum time encontrado"
- ✅ Verifique a grafia do nome
- ✅ Tente nomes alternativos
- ✅ Use apenas o nome principal (ex: "Inter" em vez de "Internacional")

### "Erro na API"
- ✅ Sistema automaticamente usa base local
- ✅ Tente novamente mais tarde
- ✅ Busca ainda funciona com times populares

### Interface Lenta
- ✅ Aguarde o processamento completar
- ✅ Não clique múltiplas vezes
- ✅ Verifique conexão com internet

## 📊 Exemplo de Uso Prático

```
1. Digite "Flamengo" na busca
2. Resultados aparecem instantaneamente
3. Selecione "Flamengo" da lista
4. Clique em "Ver Detalhes" para informações completas
5. Clique em "Adicionar Time" para usar no sistema
6. Time aparece automaticamente nas outras abas
```

## 🚀 Integração com Sistema Existente

- **Times adicionados** aparecem em todas as abas
- **Cálculos automáticos** de probabilidades
- **Compatibilidade total** com funcionalidades existentes
- **Backup automático** dos dados

---

*Esta funcionalidade torna o sistema muito mais poderoso, permitindo trabalhar com times reais e estatísticas atualizadas!*
