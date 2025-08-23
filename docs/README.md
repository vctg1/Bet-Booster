# 🎯 Sistema de Análise de Apostas Esportivas

## 📋 Descrição

Sistema completo para análise de apostas esportivas baseado em **estatísticas de gols** e **distribuição de Poisson**. O sistema oferece uma interface gráfica intuitiva para cadastrar times, analisar confrontos e calcular probabilidades de vitória com base em dados estatísticos reais.

## 🚀 Funcionalidades Principais

### 1. 📊 Cadastro de Times
- Adicionar times com estatísticas de gols marcados e sofridos
- Cálculo automático de força ofensiva e defensiva
- Organização por ligas/campeonatos
- Edição e remoção de times

### 2. 🔍 Análise de Confrontos
- Cálculo de gols esperados usando modelo de Poisson
- Probabilidades de vitória baseadas em estatísticas
- Análise de value bets comparando com odds das casas
- Consideração do fator casa
- Recomendações automáticas de apostas

### 3. 💰 Sistema de Apostas
- **Apostas Simples**: Cálculo individual com retorno potencial
- **Apostas Múltiplas**: Combinação de várias apostas
- Análise de probabilidade e retorno financeiro
- Cálculo de value bets automático

### 4. 📈 Histórico e Estatísticas
- Estatísticas gerais do banco de dados
- Rankings de times mais ofensivos/defensivos
- Exportação de relatórios
- Backup automático dos dados

## 🛠️ Instalação e Execução

### Método 1: Execução Automática
```bash
python instalar_e_executar.py
```

### Método 2: Execução Manual
```bash
python interface_apostas.py
```

### Requisitos
- Python 3.6+
- tkinter (geralmente incluído com Python)
- Bibliotecas padrão: json, math, datetime

## 📊 Modelo Matemático

### Cálculo de Gols Esperados
```
Força Ofensiva = Gols Marcados / Média da Liga
Força Defensiva = Gols Sofridos / Média da Liga

Gols Esperados A = Força Ofensiva A × Força Defensiva B × Média Liga × Fator Casa
Gols Esperados B = Força Ofensiva B × Força Defensiva A × Média Liga
```

### Distribuição de Poisson
```
P(X gols) = (λ^X × e^(-λ)) / X!
onde λ = gols esperados
```

### Value Bet
```
Value Bet = Nossa Probabilidade > Probabilidade Implícita da Odd
Vantagem = (Nossa Prob - Prob Implícita) / Prob Implícita × 100%
```

## 📁 Estrutura de Arquivos

```
📦 Sistema de Apostas
├── 📜 interface_apostas.py          # Aplicação principal com GUI
├── 📜 instalar_e_executar.py        # Script de instalação/execução
├── 📜 calculadora_apostas_avancada.py # Versão linha de comando
├── 📜 calculo_excel.txt             # Fórmulas Excel melhoradas
├── 📜 Bet tabelas.json              # Dados dos times (formato atual)
├── 📜 times_database.json           # Base de dados da aplicação
└── 📜 README.md                     # Este arquivo
```

## 🎮 Como Usar

### 1. Cadastrar Times
1. Abra a aba **"Cadastro de Times"**
2. Preencha: Nome, Gols/Partida, Gols Sofridos/Partida, Liga
3. Clique em **"Adicionar Time"**
4. Os dados são salvos automaticamente

### 2. Analisar Confronto
1. Vá para a aba **"Análise de Confrontos"**
2. Selecione Time A (casa) e Time B (visitante)
3. Insira as odds da casa de apostas
4. Ajuste o fator casa (padrão: 1.15)
5. Clique em **"Calcular Probabilidades"**

### 3. Fazer Apostas
1. Na aba **"Apostas e Múltiplas"**:
   - **Aposta Simples**: Selecione confronto, tipo, odd e valor
   - **Múltipla**: Adicione várias apostas à lista e calcule o retorno combinado

### 4. Ver Estatísticas
1. Aba **"Histórico & Stats"**
2. Clique em **"Atualizar Estatísticas"**
3. Visualize rankings e dados gerais

## 📊 Exemplo Prático

### Dados de Entrada:
- **Cruzeiro**: 1.6 gols/jogo, 0.7 gols sofridos/jogo
- **Internacional**: 1.2 gols/jogo, 1.4 gols sofridos/jogo
- **Odds**: Cruzeiro 2.15, Empate 3.10, Internacional 3.75

### Resultado do Modelo:
- **Gols Esperados**: Cruzeiro 2.21, Internacional 1.03
- **Probabilidades**: Cruzeiro 59.2%, Empate 24.1%, Internacional 16.7%
- **Value Bet**: Cruzeiro (Nossa prob 59.2% vs Implícita 46.5%)

## 🔧 Configurações Avançadas

### Fator Casa
- **Padrão**: 1.15 (15% de vantagem para o mandante)
- **Conservador**: 1.10
- **Agressivo**: 1.20

### Média da Liga
- **Brasileirão**: ~1.2 gols por time por jogo
- **Premier League**: ~1.3 gols por time por jogo
- **Personalizável**: Ajuste conforme a liga

## 💡 Dicas de Uso

### ✅ Boas Práticas
1. **Cadastre dados recentes** (últimas 10-15 partidas)
2. **Considere o contexto** (lesões, motivação, etc.)
3. **Procure value bets** com vantagem >5%
4. **Diversifique apostas** não aposte tudo em um jogo
5. **Mantenha registros** para análise posterior

### ⚠️ Limitações
- Modelo baseado apenas em gols (não considera outros fatores)
- Não considera forma atual dos times
- Histórico direto entre times não é computado
- Condições externas (clima, arbitragem) não são consideradas

## 📈 Melhorias Futuras

### Versão 2.0 (Planejada)
- [ ] Integração com APIs de dados esportivos
- [ ] Consideração da forma atual dos times
- [ ] Histórico de confrontos diretos
- [ ] Machine Learning para ajuste de modelos
- [ ] Interface web
- [ ] Alertas automáticos de value bets
- [ ] Análise de mercados alternativos (over/under, etc.)

## 🆘 Solução de Problemas

### Erro: "tkinter não encontrado"
**Windows/macOS**: Geralmente já incluído
**Ubuntu/Debian**: `sudo apt-get install python3-tk`

### Erro: "Arquivo não encontrado"
Certifique-se de que todos os arquivos estão no mesmo diretório

### Interface não abre
Verifique se está usando Python 3.6+: `python --version`

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção de solução de problemas
2. Confira se todos os arquivos estão no diretório correto
3. Teste com o script `instalar_e_executar.py`

## 📄 Licença

Sistema desenvolvido para uso educacional e pessoal. 
**Importante**: Apostas envolvem riscos financeiros. Use com responsabilidade.

---

**🎯 Developed with ❤️ for smart betting analysis**
