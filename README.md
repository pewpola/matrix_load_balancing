# Sistema de Multiplicação Distribuída de Matrizes

## 📋 Descrição

Sistema de **computação distribuída** que implementa multiplicação de matrizes usando arquitetura cliente-servidor com **load balancer**. O sistema distribui o processamento entre 2 servidores utilizando algoritmo **Round-Robin** para balanceamento de carga.

## 🏗️ Arquitetura

```
┌─────────┐
│ Cliente │
└────┬────┘
     │
     ▼
┌──────────────┐
│Load Balancer │ (Round-Robin)
└──────┬───────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌────────┐ ┌────────┐
│Server 1│ │Server 2│
└────────┘ └────────┘
```

### Componentes:

1. **Cliente (`client.py`)**
   - Gera matrizes A e B aleatórias
   - Divide matriz A em submatrizes
   - Envia tarefas para o load balancer
   - Recebe e concatena resultados parciais
   - Valida resultado final

2. **Load Balancer (`load_balancer.py`)**
   - Recebe requisições do cliente
   - Distribui tarefas usando Round-Robin
   - Encaminha para servidores disponíveis
   - Retorna resultados ao cliente
   - Coleta estatísticas de uso

3. **Servidores (`server.py`)**
   - Recebem submatrizes do load balancer
   - Realizam multiplicação de matrizes
   - Retornam resultados parciais
   - 2 instâncias rodando em paralelo

## 🚀 Como Executar com Docker

### Pré-requisitos
- Docker
- Docker Compose

### Passo 1: Build das imagens
```bash
docker compose build
```

### Passo 2: Executar o sistema
```bash
docker compose up
```

**Nota:** Use `docker compose up` (sem `-d`) para ver os logs de todos os componentes em tempo real. Os servidores e load balancer permanecerão rodando continuamente.

### Passo 3: Ver os logs
Se executou com `-d` (em background), para acompanhar os logs de cada componente:
```bash
# Todos os componentes
docker compose logs -f

# Apenas o cliente
docker compose logs -f client

# Apenas o load balancer
docker compose logs -f load_balancer

# Apenas os servidores
docker compose logs -f server1 server2
```

**Dica:** Para executar múltiplas requisições, você pode executar manualmente o cliente em outro terminal:
```bash
docker compose exec client python client.py
```

### Parar o sistema
```bash
docker compose down
```

## 📊 Executar Benchmark (Serial vs Distribuído)

O projeto inclui um sistema de benchmark que compara o desempenho entre processamento serial (1 servidor) e distribuído (2 servidores) em 15 casos de teste com tamanhos crescentes de matrizes.

### Executar o benchmark:

```bash
# 1. Certifique-se de que os servidores e load balancer estão rodando
docker compose up -d server1 server2 load_balancer

# 2. Execute o benchmark
docker compose run --rm benchmark

# 3. Ver resultados em tempo real nos logs
docker compose logs -f benchmark
```

### O que o benchmark faz:

1. **Testa 15 casos** com matrizes de tamanhos crescentes (10×10 até 1000×1000)
2. **Executa cada caso 3 vezes** e calcula a média para maior precisão
3. **Compara tempos** de execução serial vs distribuído
4. **Calcula speedup** e porcentagem de melhoria
5. **Identifica o ponto de virada** onde o processamento distribuído passa a valer a pena
6. **Gera relatório completo** em formato de tabela

### Exemplo de saída:

```
╔══════╦═════════════════╦═════════════╦═════════════════╦══════════╦══════════════╦═════════════╗
║ Caso ║ Dimensões       ║ Serial (s)  ║ Distribuído (s) ║ Speedup  ║ Melhoria (%) ║ Vencedor    ║
╠══════╬═════════════════╬═════════════╬═════════════════╬══════════╬══════════════╬═════════════╣
║    1 ║ 10×10×10        ║ 0.0234      ║ 0.0456          ║ 0.51x    ║ -95.12%      ║ SERIAL      ║
║    2 ║ 20×20×20        ║ 0.0245      ║ 0.0467          ║ 0.52x    ║ -90.61%      ║ SERIAL      ║
║  ... ║ ...             ║ ...         ║ ...             ║ ...      ║ ...          ║ ...         ║
║    8 ║ 200×200×200     ║ 0.1234      ║ 0.0789          ║ 1.56x    ║ +36.05%      ║ DISTRIBUÍDO ║
╚══════╩═════════════════╩═════════════╩═════════════════╩══════════╩══════════════╩═════════════╝

✅ O processamento DISTRIBUÍDO começa a valer a pena a partir do:
   CASO 8: 200×200×200
   Speedup: 1.56x
   Melhoria: +36.05%
```

### Visualizar resultados salvos:

O benchmark salva automaticamente os resultados em `benchmark_results.txt`:

```bash
# Copiar arquivo de resultados do container para seu computador
docker cp matrix_benchmark:/app/benchmark_results.txt .

# Ou visualizar diretamente
docker compose run --rm benchmark cat /app/benchmark_results.txt
```

## 📊 Funcionamento

1. **Cliente** gera duas matrizes:
   - Matriz A (100x100)
   - Matriz B (100x100)

2. **Cliente** divide matriz A em 2 partes (uma para cada servidor)

3. **Load Balancer** distribui as tarefas:
   - TASK-1 → SERVER-1
   - TASK-2 → SERVER-2

4. **Servidores** processam em paralelo:
   - SERVER-1: calcula submatriz1 × B
   - SERVER-2: calcula submatriz2 × B

5. **Cliente** recebe e concatena os resultados

6. **Validação**: compara com numpy.dot() para verificar correção

## 🔧 Configuração

Você pode alterar o tamanho das matrizes editando `client.py`:

```python
# Configuração das matrizes (linha ~185)
rows_a = 100    # Linhas da matriz A
cols_a = 100    # Colunas da matriz A
cols_b = 100    # Colunas da matriz B
num_servers = 2 # Número de servidores
```

## 📈 Exemplo de Saída

```
======================================================================
SISTEMA DE MULTIPLICAÇÃO DISTRIBUÍDA DE MATRIZES
Arquitetura: Cliente -> Load Balancer -> Servidores (Round-Robin)
======================================================================

[CLIENT] Gerando matrizes...
[CLIENT] Matriz A: 100x100
[CLIENT] Matriz B: 100x100
[CLIENT] Matrizes geradas com sucesso!

[CLIENT] Iniciando multiplicação distribuída...
[CLIENT] Dividindo trabalho entre 2 servidores
[CLIENT] Matriz A dividida em 2 partes:
  - Parte 1: (50, 100)
  - Parte 2: (50, 100)

[LOAD BALANCER] Servidor selecionado: SERVER-1
[SERVER-1] Realizando multiplicação de matrizes...
[SERVER-1] Multiplicação concluída.

[LOAD BALANCER] Servidor selecionado: SERVER-2
[SERVER-2] Realizando multiplicação de matrizes...
[SERVER-2] Multiplicação concluída.

[CLIENT] Concatenando resultados parciais...
[CLIENT] Multiplicação distribuída concluída!
[CLIENT] Tempo total: 2.45 segundos
[CLIENT] Resultado final shape: (100, 100)

[CLIENT] Verificando resultado...
[CLIENT] ✓ Resultado CORRETO! A multiplicação distribuída funcionou perfeitamente.

======================================================================
PROCESSO CONCLUÍDO COM SUCESSO!
======================================================================
```

## 🧪 Executar sem Docker

Se preferir executar localmente sem Docker:

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar em terminais separados

**Terminal 1 - Servidor 1:**
```bash
python server.py 5001
```

**Terminal 2 - Servidor 2:**
```bash
python server.py 5002
```

**Terminal 3 - Load Balancer:**
```bash
python load_balancer.py
```

**Terminal 4 - Cliente:**
```bash
python client.py
```

**Nota:** Ao executar localmente, ajuste os hostnames em `client.py` e `load_balancer.py`:
- `load_balancer_host='localhost'` no client.py
- `'host': 'localhost'` para server1 e server2 no load_balancer.py

## 🎯 Características Técnicas

- **Protocolo**: TCP/IP com Sockets
- **Serialização**: Pickle
- **Balanceamento**: Round-Robin
- **Processamento**: NumPy para álgebra linear
- **Arquitetura**: Cliente-Servidor com Load Balancer
- **Containerização**: Docker + Docker Compose

## 📚 Conceitos de Computação Distribuída Aplicados

✅ **Divisão de Tarefas**: Matriz dividida em submatrizes  
✅ **Processamento Paralelo**: Múltiplos servidores processando simultaneamente  
✅ **Balanceamento de Carga**: Round-Robin entre servidores  
✅ **Agregação de Resultados**: Concatenação de resultados parciais  
✅ **Comunicação via Rede**: Socket programming  
✅ **Tolerância a Falhas**: Retry mechanism no load balancer  

## 👨‍💻 Autor

Sistema desenvolvido para demonstrar conceitos de computação distribuída e balanceamento de carga.
