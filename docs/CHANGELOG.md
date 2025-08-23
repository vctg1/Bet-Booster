# Changelog - Sistema de Análise de Apostas

## Versão 2.0 - Melhorias no Fator Casa

### ✨ Novas Funcionalidades

#### 🏟️ Fator Casa Simplificado
- **ANTES**: Campo de entrada numérica para fator casa (ex: 1.15)
- **AGORA**: Checkbox simples "Aplicar Vantagem de Casa (15%)"
  - ✅ Marcado = Aplica vantagem de 15% ao time da casa
  - ❌ Desmarcado = Sem vantagem, cálculo neutro

#### 📊 Indicador Visual
- Novo indicador de status que mostra claramente se a vantagem está ativa:
  - ✅ **"Vantagem de casa ATIVADA"** (texto verde)
  - ❌ **"Vantagem de casa DESATIVADA"** (texto vermelho)

### 🔧 Melhorias Técnicas

#### Sincronização Global
- O status do fator casa é aplicado consistentemente em todas as funcionalidades:
  - ✅ Análise de confrontos
  - ✅ Apostas simples
  - ✅ Apostas múltiplas

#### Transparência nos Resultados
- Todos os relatórios agora mostram claramente se a vantagem foi aplicada:
  ```
  🏟️ Vantagem de casa: Aplicada (+15%)
  ```
  ou
  ```
  🏟️ Vantagem de casa: Não aplicada
  ```

### 📋 Como Usar

1. **Na aba "Análise de Confrontos"**:
   - Marque/desmarque o checkbox conforme desejado
   - O indicador visual mostra o status atual
   - Calcule normalmente - o fator será aplicado automaticamente

2. **Na aba "Apostas e Múltiplas"**:
   - O sistema usa automaticamente a configuração do fator casa
   - Não é necessário configurar novamente
   - Os resultados mostram se foi aplicado

### 🎯 Vantagens da Nova Implementação

- **Simplicidade**: ON/OFF em vez de valor numérico
- **Clareza**: Indicador visual sempre visível
- **Consistência**: Mesmo fator aplicado em todas as análises
- **Transparência**: Status sempre mostrado nos resultados

### 🔄 Migração da Versão Anterior

Se você estava usando a versão anterior:
- Substitua o valor "1.15" por marcar o checkbox
- Substitua o valor "1.0" por desmarcar o checkbox
- Todos os outros cálculos permanecem idênticos

### 📚 Detalhes Técnicos

O fator casa de 15% é baseado em estudos estatísticos do futebol:
- **Com fator**: `gols_esperados_casa = força_ofensiva × força_defensiva_adversário × 1.15`
- **Sem fator**: `gols_esperados_casa = força_ofensiva × força_defensiva_adversário × 1.0`

---

*Esta atualização torna o sistema mais intuitivo e elimina possíveis erros de digitação no fator casa.*
