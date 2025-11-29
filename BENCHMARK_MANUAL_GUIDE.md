# Guia Completo - Benchmark Manual

## 📋 Visão Geral

O **Benchmark Manual** permite que você defina manualmente as dimensões das matrizes e o número de execuções para comparar o desempenho entre processamento serial e distribuído de forma personalizada.

---

## 🚀 Como Executar

### Passo 1: Iniciar os servidores e load balancer

```bash
docker compose up -d server1 server2 load_balancer
```

Aguarde alguns segundos para garantir que todos os serviços estejam prontos.

### Passo 2: Executar o benchmark manual

```bash
docker compose run --rm benchmark_manual
```

O sistema iniciará de forma interativa e você poderá configurar cada teste.

---

## 🎯 Funcionalidades

### ✅ Validação Automática (Demonstração Inicial)

Antes de começar seus testes, o sistema executa uma validação com matriz 2×2 conhecida:

```
Matriz A:        Matriz B:        Resultado Esperado:
[1  2]           [5  6]           [19  22]
[3  4]           [7  8]           [43  50]
```

Isso garante que o servidor está calculando corretamente antes de prosseguir.

---

### ✅ Dimensões Personalizadas

Você define completamente as dimensões de ambas as matrizes:

```
Digite o número de LINHAS da Matriz A: 100
Digite o número de COLUNAS da Matriz A: 50
Digite o número de LINHAS da Matriz B: 50
Digite o número de COLUNAS da Matriz B: 200
```

**Validações automáticas:**
- ✓ Todas as dimensões devem ser > 0
- ✓ Colunas de A = Linhas de B (compatibilidade para multiplicação)
- ✓ Confirmação antes de prosseguir

**Resultado:**
- Matriz A: 100×50
- Matriz B: 50×200
- Matriz Resultado: 100×200

---

### ✅ Input Manual para Matrizes Pequenas (até 4×4)

Para matrizes de dimensão **até 4×4**, você pode escolher:

#### Opção 1: Preencher Manualmente

```
Como deseja definir a Matriz A (2×2)?
  1 - Preencher manualmente (valor por valor)
  2 - Gerar aleatoriamente (valores entre 1 e 9)
Escolha (1 ou 2): 1

Linha 1/2 (digite 2 valores separados por espaço):
  Valores: 1 2

Linha 2/2 (digite 2 valores separados por espaço):
  Valores: 3 4
```

**Formato de entrada:**
- Digite os valores **separados por espaço**
- Apenas **números inteiros**
- Número exato de valores por linha

**Exemplo de preenchimento 3×3:**
```
Linha 1/3: 1 2 3
Linha 2/3: 4 5 6
Linha 3/3: 7 8 9
```

#### Opção 2: Gerar Aleatoriamente

```
Como deseja definir a Matriz A (2×2)?
  1 - Preencher manualmente (valor por valor)
  2 - Gerar aleatoriamente (valores entre 1 e 9)
Escolha (1 ou 2): 2

[BENCHMARK] Gerando Matriz A aleatoriamente...
[BENCHMARK] Matriz A gerada!
```

Gera valores aleatórios entre 1 e 9.

---

### ✅ Matrizes Maiores que 4×4

Para matrizes grandes, o sistema **gera automaticamente** valores aleatórios:

```
Digite o número de LINHAS da Matriz A: 100
...
[BENCHMARK] Gerando Matriz A aleatoriamente...
[BENCHMARK] Gerando Matriz B aleatoriamente...
```

Não há opção de input manual (seria impraticável).

---

### ✅ Número de Execuções Personalizável

```
Quantas execuções para calcular a média? (recomendado: 3): 5
```

O sistema executará o teste **5 vezes** e calculará a **média** dos tempos para maior precisão estatística.

**Recomendações:**
- **3 execuções**: Boa precisão, rápido
- **5 execuções**: Maior confiabilidade
- **10+ execuções**: Análise estatística rigorosa (mais demorado)

---

### ✅ Visualização das Matrizes

O sistema exibe as **primeiras 10×10** de cada matriz gerada:

```
[MATRIZES] Primeiras 10x10 - Matriz A:
[[1 2 3 4 5 6 7 8 9 1]
 [2 3 4 5 6 7 8 9 1 2]
 [3 4 5 6 7 8 9 1 2 3]
 ...]

[MATRIZES] Primeiras 10x10 - Matriz B:
[[5 6 7 8 9 1 2 3 4 5]
 [6 7 8 9 1 2 3 4 5 6]
 ...]

[RESULTADO] Primeiras 10x10 - Matriz Resultado:
[[234 256 278 301 323 345 367 389 411 234]
 [256 278 301 323 345 367 389 411 234 256]
 ...]
```

Permite verificar visualmente os dados sendo processados.

---

### ✅ Comparação Serial vs Distribuído

Para cada teste, o sistema executa **ambos os modos**:

#### Processamento Serial (1 servidor)
```
[SERIAL] Executando processamento serial (1 servidor)...
  Execução 1/3... 0.0234s
  Execução 2/3... 0.0245s
  Execução 3/3... 0.0239s
[SERIAL] Tempo médio: 0.0239s
```

#### Processamento Distribuído (2 servidores)
```
[DISTRIBUÍDO] Executando processamento distribuído (2 servidores)...
  Execução 1/3... 0.0456s
  Execução 2/3... 0.0467s
  Execução 3/3... 0.0461s
[DISTRIBUÍDO] Tempo médio: 0.0461s
```

---

### ✅ Análise de Resultados

Após cada teste, recebe análise completa:

```
================================================================================
RESULTADO DA ANÁLISE
================================================================================
  Vencedor: SERIAL
  Speedup: 0.52x
  Overhead: 92.84% mais lento
  ✓ Resultados validados (iguais)
```

**Métricas:**
- **Vencedor**: Qual abordagem foi mais rápida
- **Speedup**: Razão entre tempo serial e distribuído
  - `> 1.0x` = Distribuído mais rápido
  - `< 1.0x` = Serial mais rápido
- **Melhoria/Overhead**: Percentual de ganho ou perda
  - `+36.5%` = Distribuído 36.5% mais rápido
  - `-92.8%` = Distribuído 92.8% mais lento
- **Validação**: Confirma que ambos os resultados são idênticos

---

### ✅ Múltiplos Testes em Sequência

Após cada teste, você pode executar outro:

```
Deseja testar outro tamanho de matriz? (s/n): s
```

**Responda:**
- `s` = Novo teste (volta ao menu de dimensões)
- `n` = Finalizar e ver histórico completo

---

### ✅ Histórico Completo

Ao finalizar, recebe tabela com **todos os testes** realizados:

```
================================================================================
HISTÓRICO DE TESTES REALIZADOS
================================================================================

╔════════════════════════╦════════════╦════════════╦═════════════════╦══════════╦══════════════╦═════════════╗
║ Dimensões              ║ Execuções  ║ Serial (s) ║ Distribuído (s) ║ Speedup  ║ Melhoria (%) ║ Vencedor    ║
╠════════════════════════╬════════════╬════════════╬═════════════════╬══════════╬══════════════╬═════════════╣
║ (2×2) × (2×2)          ║          3 ║ 0.0026     ║ 0.0049          ║ 0.52x    ║ -92.84%      ║ SERIAL      ║
║ (10×10) × (10×10)      ║          3 ║ 0.0034     ║ 0.0056          ║ 0.61x    ║ -64.71%      ║ SERIAL      ║
║ (100×100) × (100×100)  ║          3 ║ 0.0234     ║ 0.0189          ║ 1.24x    ║ +19.23%      ║ DISTRIBUÍDO ║
║ (500×500) × (500×500)  ║          5 ║ 2.4567     ║ 1.3456          ║ 1.83x    ║ +45.23%      ║ DISTRIBUÍDO ║
╚════════════════════════╩════════════╩════════════╩═════════════════╩══════════╩══════════════╩═════════════╝

📊 ESTATÍSTICAS GERAIS:
   • Total de testes: 4
   • Vitórias SERIAL: 2
   • Vitórias DISTRIBUÍDO: 2
```

**Estatísticas:**
- Total de testes realizados na sessão
- Quantos casos o serial venceu
- Quantos casos o distribuído venceu

---

## 📊 Exemplos de Uso

### Exemplo 1: Teste Simples 2×2 com Input Manual

```bash
docker compose run --rm benchmark_manual
```

**Entrada:**
```
Digite o número de LINHAS da Matriz A: 2
Digite o número de COLUNAS da Matriz A: 2
Digite o número de LINHAS da Matriz B: 2
Digite o número de COLUNAS da Matriz B: 2
Confirma estas dimensões? (s/n): s

Como deseja definir a Matriz A (2×2)? 1
Linha 1/2: 1 2
Linha 2/2: 3 4

Como deseja definir a Matriz B (2×2)? 1
Linha 1/2: 5 6
Linha 2/2: 7 8

Quantas execuções para calcular a média? 3
```

**Resultado:**
```
Vencedor: SERIAL
Speedup: 0.52x
Overhead: 92.84% mais lento
```

**Por quê?** Overhead de rede >> Benefício do paralelismo para matrizes tão pequenas.

---

### Exemplo 2: Matrizes Médias (Aleatórias)

```bash
docker compose run --rm benchmark_manual
```

**Entrada:**
```
Digite o número de LINHAS da Matriz A: 200
Digite o número de COLUNAS da Matriz A: 200
Digite o número de LINHAS da Matriz B: 200
Digite o número de COLUNAS da Matriz B: 200
Confirma estas dimensões? (s/n): s

Quantas execuções para calcular a média? 5
```

**Resultado:**
```
Vencedor: DISTRIBUÍDO
Speedup: 1.56x
Melhoria: +36.05% mais rápido
```

**Por quê?** Custo computacional O(n³) domina o overhead de comunicação O(n²).

---

### Exemplo 3: Matrizes Retangulares

```bash
docker compose run --rm benchmark_manual
```

**Entrada:**
```
Digite o número de LINHAS da Matriz A: 500
Digite o número de COLUNAS da Matriz A: 100
Digite o número de LINHAS da Matriz B: 100
Digite o número de COLUNAS da Matriz B: 300
Confirma estas dimensões? (s/n): s

Quantas execuções para calcular a média? 3
```

**Resultado:**
```
Matriz A: 500×100
Matriz B: 100×300
Resultado: 500×300

Vencedor: DISTRIBUÍDO
Speedup: 1.72x
Melhoria: +41.86% mais rápido
```

---

### Exemplo 4: Múltiplos Testes para Encontrar Ponto de Virada

Teste várias dimensões crescentes para identificar o ponto exato onde distribuído começa a vencer:

1. **Teste 1:** 50×50 → Serial vence
2. **Teste 2:** 100×100 → Serial vence
3. **Teste 3:** 150×150 → Empate técnico (~1.0x)
4. **Teste 4:** 200×200 → **Distribuído vence!** 🎯
5. **Teste 5:** 500×500 → Distribuído vence (maior vantagem)

**Conclusão:** Ponto de virada em ~200×200 neste ambiente.

---

## 🎯 Casos de Uso Práticos

### 1. Validar Implementação
```
Objetivo: Verificar se o sistema está funcionando corretamente
Dimensões: 2×2 ou 3×3
Input: Manual (valores conhecidos)
Execuções: 1
Validação: Conferir resultado manualmente
```

### 2. Encontrar Ponto de Virada
```
Objetivo: Descobrir quando distribuído compensa
Dimensões: Crescentes (10, 50, 100, 150, 200, 300, 500...)
Input: Aleatório
Execuções: 3-5
Análise: Identificar primeiro Speedup > 1.0x
```

### 3. Análise de Performance
```
Objetivo: Medir performance em caso específico
Dimensões: As do seu problema real
Input: Aleatório
Execuções: 10+ (estatística rigorosa)
Análise: Média, desvio padrão, intervalo de confiança
```

### 4. Comparação de Abordagens
```
Objetivo: Testar diferentes estratégias de particionamento
Dimensões: Fixas (ex: 1000×1000)
Testes: Variar número de execuções
Análise: Consistência dos resultados
```

### 5. Demonstração Didática
```
Objetivo: Mostrar conceitos de computação distribuída
Dimensões: 2×2 (manual) + 100×100 + 500×500
Input: Manual para 2×2, aleatório para resto
Execuções: 3
Análise: Mostrar overhead pequeno vs grande
```

---

## 💡 Dicas e Boas Práticas

### ✅ Escolha de Dimensões

**Para matrizes pequenas (< 100×100):**
- Espere que serial vença (overhead de rede)
- Use para validação manual

**Para matrizes médias (100×100 - 500×500):**
- Zona de transição
- Encontre o ponto de virada

**Para matrizes grandes (> 500×500):**
- Espere que distribuído vença
- Speedup aumenta com tamanho

### ✅ Número de Execuções

- **1 execução**: Teste rápido, baixa precisão
- **3 execuções**: Recomendado, boa precisão
- **5-10 execuções**: Análise confiável
- **30+ execuções**: Análise estatística formal

### ✅ Input Manual vs Aleatório

**Use input manual quando:**
- Validar com valores conhecidos
- Demonstração didática
- Matrizes muito pequenas (2×2, 3×3)

**Use aleatório quando:**
- Benchmark de performance real
- Matrizes médias/grandes
- Múltiplos testes em sequência

### ✅ Interpretação de Resultados

**Speedup < 1.0x (Serial vence):**
- Normal para matrizes pequenas
- Overhead > Benefício
- Comunicação é o gargalo

**Speedup ≈ 1.0x (Empate):**
- Ponto de virada
- Overhead ≈ Benefício
- Zona crítica de decisão

**Speedup > 1.0x (Distribuído vence):**
- Normal para matrizes grandes
- Benefício > Overhead
- Computação é o gargalo

**Speedup próximo a 2.0x (Máximo teórico com 2 servidores):**
- Excelente paralelização
- Overhead mínimo
- Lei de Amdahl sendo respeitada

---

## ⚠️ Solução de Problemas

### Erro: "Número de COLUNAS de A deve ser igual ao número de LINHAS de B"

**Causa:** Dimensões incompatíveis para multiplicação de matrizes.

**Solução:**
```
Se A é (m × n) e B é (p × q)
Então n deve ser igual a p
```

**Exemplo correto:**
- A: 100×**50**
- B: **50**×200
- ✓ Compatível (50 = 50)

### Erro: "Digite apenas números inteiros válidos"

**Causa:** Tentou inserir números decimais ou caracteres inválidos.

**Solução:** Use apenas números inteiros separados por espaço:
```
Correto:   1 2 3 4 5
Incorreto: 1.5 2.3 abc
```

### Erro: "Esperado X valores, mas recebeu Y"

**Causa:** Número errado de valores em uma linha.

**Solução:** Digite exatamente o número de valores solicitado:
```
Para matriz 3×3:
Linha 1/3: 1 2 3  ← Exatamente 3 valores
```

### Sistema trava durante execução

**Causa:** Matrizes muito grandes (memória insuficiente).

**Solução:** 
- Reduza as dimensões
- Aumente recursos do Docker
- Execute em máquina mais potente

### Resultados inconsistentes

**Causa:** Poucos testes, variação de rede/CPU.

**Solução:**
- Aumente número de execuções (5-10)
- Feche outros processos
- Execute múltiplas vezes

---

## 🔬 Análise Científica

### Complexidade Computacional

**Multiplicação de Matrizes:**
- Complexidade: **O(n³)** (algoritmo ingênuo)
- Para n×n × n×n = n³ operações

**Comunicação de Rede:**
- Enviar matriz A: **O(n²)** bytes
- Enviar matriz B: **O(n²)** bytes
- Receber resultado: **O(n²)** bytes
- Total: **3·O(n²)**

**Trade-off:**
```
Para n pequeno: O(n²) dominante → Serial vence
Para n grande:  O(n³) dominante → Distribuído vence
Ponto de virada: Quando O(n³) ≈ k·O(n²)
```

### Lei de Amdahl

Com 2 servidores ideais:
```
Speedup máximo = 1 / ((1-p) + p/2)

Onde p = fração paralelizável

Se p = 0.95 (95% paralelizável):
Speedup = 1 / (0.05 + 0.475) = 1.90x
```

**Por isso nunca vemos speedup = 2.0x exato!**

Fração sequencial inclui:
- Particionamento inicial
- Agregação final
- Overhead de comunicação

---

## 📈 Padrões Esperados

### Pequenas (< 100×100)
```
Serial:      0.001 - 0.050s
Distribuído: 0.003 - 0.080s
Speedup:     0.3x - 0.8x
Vencedor:    SERIAL (overhead domina)
```

### Médias (100×100 - 500×500)
```
Serial:      0.050 - 3.000s
Distribuído: 0.040 - 2.000s
Speedup:     0.8x - 1.8x
Vencedor:    TRANSIÇÃO (depende da dimensão)
```

### Grandes (> 500×500)
```
Serial:      3.000 - 30.000s
Distribuído: 1.500 - 16.000s
Speedup:     1.6x - 2.0x
Vencedor:    DISTRIBUÍDO (computação domina)
```

---

## 🎓 Conceitos Demonstrados

✅ **Particionamento de Dados**
- Divisão horizontal da matriz A

✅ **Replicação de Dados**
- Matriz B replicada para todos servidores

✅ **Balanceamento de Carga**
- Round-Robin automático

✅ **Processamento Paralelo**
- 2 servidores trabalhando simultaneamente

✅ **Agregação de Resultados**
- Concatenação vertical (numpy.vstack)

✅ **Validação de Correção**
- Comparação com resultado serial

✅ **Análise de Performance**
- Speedup, overhead, ponto de virada

✅ **Trade-off Comunicação vs Computação**
- Demonstração empírica do equilíbrio

---

## 📚 Referências e Leitura Adicional

- **Lei de Amdahl**: Limite teórico de speedup paralelo
- **Complexidade O(n³)**: Custo da multiplicação de matrizes
- **Algoritmo de Strassen**: Multiplicação O(n^2.807)
- **MapReduce**: Paradigma de processamento distribuído
- **Load Balancing**: Estratégias Round-Robin, Least Connections, Weighted

---

**Pronto para começar! Execute e explore diferentes cenários! 🚀**
