# Guia Rápido - Benchmark Serial vs Distribuído

## 🚀 Como Executar

### 1. Reconstruir as imagens (apenas primeira vez ou após mudanças)
```bash
docker compose build
```

### 2. Subir os servidores e load balancer
```bash
docker compose up -d server1 server2 load_balancer
```

### 3. Executar o benchmark
```bash
docker compose run --rm benchmark
```

### 4. Ver resultados em tempo real
```bash
docker compose logs -f benchmark
```

### 5. Copiar arquivo de resultados
```bash
docker cp matrix_benchmark:/app/benchmark_results.txt .
```

## 📊 O Que o Benchmark Faz

- **15 casos de teste** com matrizes crescentes (10×10 até 1000×1000)
- **3 execuções por caso** para média confiável
- Compara **SERIAL** (1 servidor) vs **DISTRIBUÍDO** (2 servidores)
- Identifica **quando o processamento distribuído vale a pena**
- Calcula **speedup** e **porcentagem de melhoria**

## 📈 Métricas Analisadas

- **Tempo de execução médio** (serial vs distribuído)
- **Speedup**: quanto mais rápido fica (ex: 1.5x = 50% mais rápido)
- **Melhoria percentual**: +36% = 36% mais rápido, -20% = 20% mais lento
- **Ponto de virada**: caso onde distribuído passa a ser mais rápido

## 🎯 Objetivo Acadêmico

Demonstrar que:
- Para **matrizes pequenas**: overhead de rede > benefício do paralelismo
- Para **matrizes grandes**: benefício do paralelismo > overhead de rede
- Existe um **ponto de equilíbrio** onde vale a pena distribuir

## 📝 Para o Relatório

O benchmark gera:
1. **Tabela completa** com todos os 15 casos
2. **Identificação clara** do ponto onde distribuído vence
3. **Estatísticas** de vitórias serial vs distribuído
4. **Arquivo texto** `benchmark_results.txt` para anexar ao trabalho

## 🔧 Ajustes Opcionais

Para modificar os casos de teste, edite `benchmark.py`:

```python
test_cases = [
    (10, 10, 10),      # Caso 1
    (20, 20, 20),      # Caso 2
    # ... adicione mais casos conforme necessário
]
```

## ⏱️ Tempo Estimado

- Casos pequenos (10×10 a 100×100): ~5-10 segundos cada
- Casos médios (200×200 a 500×500): ~15-30 segundos cada
- Casos grandes (600×600 a 1000×1000): ~30-60 segundos cada

**Tempo total estimado**: 15-25 minutos para completar todos os 15 casos
