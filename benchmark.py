"""
Benchmark: Comparação entre Processamento Serial e Distribuído
Avalia em que ponto o processamento distribuído começa a valer a pena
"""
import socket
import pickle
import numpy as np
import time
import sys
from tabulate import tabulate


class BenchmarkClient:
    def __init__(self, load_balancer_host='load_balancer', load_balancer_port=5000):
        self.load_balancer_host = load_balancer_host
        self.load_balancer_port = load_balancer_port
    
    def serial_multiplication(self, matrix_a, matrix_b):
        """
        Executa multiplicação serial (tudo em um único servidor)
        """
        try:
            # Conecta ao load balancer (que encaminhará para apenas 1 servidor)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(120)
            client_socket.connect((self.load_balancer_host, self.load_balancer_port))
            
            # Prepara dados para envio (matriz completa)
            data = {
                'submatrix_a': matrix_a,  # Envia matriz completa
                'matrix_b': matrix_b,
                'task_id': 'SERIAL'
            }
            
            # Serializa e envia
            serialized_data = pickle.dumps(data)
            client_socket.sendall(serialized_data + b'END_OF_DATA')
            
            # Recebe resultado
            response_data = b''
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b'END_OF_DATA' in response_data:
                    response_data = response_data.replace(b'END_OF_DATA', b'')
                    break
            
            result = pickle.loads(response_data)
            client_socket.close()
            
            return result['result']
            
        except Exception as e:
            print(f"[BENCHMARK] Erro na multiplicação serial: {e}")
            raise
    
    def split_matrix(self, matrix, num_parts):
        """
        Divide a matriz A em submatrizes (linhas) para distribuição
        """
        rows = matrix.shape[0]
        rows_per_part = rows // num_parts
        
        submatrices = []
        for i in range(num_parts):
            start_row = i * rows_per_part
            if i == num_parts - 1:
                end_row = rows
            else:
                end_row = (i + 1) * rows_per_part
            
            submatrices.append(matrix[start_row:end_row])
        
        return submatrices
    
    def send_to_load_balancer(self, submatrix_a, matrix_b, task_id):
        """
        Envia submatriz para o load balancer e recebe o resultado
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(120)
            client_socket.connect((self.load_balancer_host, self.load_balancer_port))
            
            data = {
                'submatrix_a': submatrix_a,
                'matrix_b': matrix_b,
                'task_id': task_id
            }
            
            serialized_data = pickle.dumps(data)
            client_socket.sendall(serialized_data + b'END_OF_DATA')
            
            response_data = b''
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b'END_OF_DATA' in response_data:
                    response_data = response_data.replace(b'END_OF_DATA', b'')
                    break
            
            result = pickle.loads(response_data)
            client_socket.close()
            
            return result
            
        except Exception as e:
            print(f"[BENCHMARK] Erro ao enviar tarefa {task_id}: {e}")
            raise
    
    def distributed_multiplication(self, matrix_a, matrix_b, num_servers=2):
        """
        Executa multiplicação distribuída entre múltiplos servidores
        """
        submatrices = self.split_matrix(matrix_a, num_servers)
        
        results = []
        for i, submatrix in enumerate(submatrices):
            task_id = f"DIST-{i+1}"
            result = self.send_to_load_balancer(submatrix, matrix_b, task_id)
            results.append(result)
        
        final_result = np.vstack([r['result'] for r in results])
        return final_result


def run_benchmark():
    """
    Executa benchmark com 15 casos de teste de tamanhos variados
    """
    print("="*80)
    print("BENCHMARK: PROCESSAMENTO SERIAL vs DISTRIBUÍDO")
    print("Análise de Performance com Multiplicação de Matrizes")
    print("="*80)
    
    # Aguarda servidores iniciarem
    print("\n[BENCHMARK] Aguardando servidores iniciarem...")
    time.sleep(5)
    
    client = BenchmarkClient()
    
    # Define 15 casos de teste com tamanhos crescentes
    test_cases = [
        (10, 10, 10),      # Caso 1: Muito pequeno
        (20, 20, 20),      # Caso 2
        (30, 30, 30),      # Caso 3
        (50, 50, 50),      # Caso 4
        (75, 75, 75),      # Caso 5
        (100, 100, 100),   # Caso 6
        (150, 150, 150),   # Caso 7
        (200, 200, 200),   # Caso 8
        (300, 300, 300),   # Caso 9
        (400, 400, 400),   # Caso 10
        (500, 500, 500),   # Caso 11
        (600, 600, 600),   # Caso 12
        (700, 700, 700),   # Caso 13
        (800, 800, 800),   # Caso 14
        (1000, 1000, 1000) # Caso 15: Muito grande
    ]
    
    results = []
    parallel_wins_from = None
    
    print(f"\n[BENCHMARK] Executando {len(test_cases)} casos de teste...")
    print(f"[BENCHMARK] Cada caso será executado 3 vezes para média de tempo\n")
    
    for idx, (rows_a, cols_a, cols_b) in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"CASO {idx}/15: Matriz A({rows_a}×{cols_a}) × Matriz B({cols_a}×{cols_b})")
        print(f"{'='*80}")
        
        # Gera matrizes para este caso
        matrix_a = np.random.randint(1, 10, size=(rows_a, cols_a))
        matrix_b = np.random.randint(1, 10, size=(cols_a, cols_b))
        
        # ========== TESTE SERIAL (3 execuções) ==========
        print(f"\n[SERIAL] Executando processamento serial (1 servidor)...")
        serial_times = []
        
        for run in range(3):
            start_time = time.time()
            result_serial = client.serial_multiplication(matrix_a, matrix_b)
            end_time = time.time()
            serial_time = end_time - start_time
            serial_times.append(serial_time)
            print(f"  Execução {run+1}/3: {serial_time:.4f}s")
        
        avg_serial_time = np.mean(serial_times)
        print(f"[SERIAL] Tempo médio: {avg_serial_time:.4f}s")
        
        # ========== TESTE DISTRIBUÍDO (3 execuções) ==========
        print(f"\n[DISTRIBUÍDO] Executando processamento distribuído (2 servidores)...")
        distributed_times = []
        
        for run in range(3):
            start_time = time.time()
            result_distributed = client.distributed_multiplication(matrix_a, matrix_b, num_servers=2)
            end_time = time.time()
            distributed_time = end_time - start_time
            distributed_times.append(distributed_time)
            print(f"  Execução {run+1}/3: {distributed_time:.4f}s")
        
        avg_distributed_time = np.mean(distributed_times)
        print(f"[DISTRIBUÍDO] Tempo médio: {avg_distributed_time:.4f}s")
        
        # ========== ANÁLISE ==========
        speedup = avg_serial_time / avg_distributed_time
        improvement = ((avg_serial_time - avg_distributed_time) / avg_serial_time) * 100
        
        winner = "DISTRIBUÍDO" if avg_distributed_time < avg_serial_time else "SERIAL"
        
        if winner == "DISTRIBUÍDO" and parallel_wins_from is None:
            parallel_wins_from = idx
        
        print(f"\n[ANÁLISE]")
        print(f"  Vencedor: {winner}")
        print(f"  Speedup: {speedup:.2f}x")
        if improvement > 0:
            print(f"  Melhoria: {improvement:.2f}% mais rápido")
        else:
            print(f"  Overhead: {abs(improvement):.2f}% mais lento")
        
        # Validação
        if np.array_equal(result_serial, result_distributed):
            print(f"  ✓ Resultados validados (iguais)")
        else:
            print(f"  ✗ ERRO: Resultados diferentes!")
        
        # Armazena resultados
        results.append({
            'Caso': idx,
            'Dimensões': f"{rows_a}×{cols_a}×{cols_b}",
            'Serial (s)': f"{avg_serial_time:.4f}",
            'Distribuído (s)': f"{avg_distributed_time:.4f}",
            'Speedup': f"{speedup:.2f}x",
            'Melhoria (%)': f"{improvement:+.2f}%",
            'Vencedor': winner
        })
    
    # ========== RELATÓRIO FINAL ==========
    print(f"\n\n{'='*80}")
    print("RELATÓRIO FINAL - COMPARAÇÃO DE PERFORMANCE")
    print(f"{'='*80}\n")
    
    # Tabela de resultados
    print(tabulate(results, headers='keys', tablefmt='grid'))
    
    # Conclusões
    print(f"\n{'='*80}")
    print("CONCLUSÕES")
    print(f"{'='*80}\n")
    
    if parallel_wins_from:
        winning_case = results[parallel_wins_from - 1]
        print(f"✅ O processamento DISTRIBUÍDO começa a valer a pena a partir do:")
        print(f"   CASO {parallel_wins_from}: {winning_case['Dimensões']}")
        print(f"   Speedup: {winning_case['Speedup']}")
        print(f"   Melhoria: {winning_case['Melhoria (%)']}")
    else:
        print(f"⚠️  O processamento SERIAL foi mais rápido em todos os casos testados.")
        print(f"   Isso pode indicar que o overhead de rede supera os benefícios")
        print(f"   do paralelismo para os tamanhos testados.")
    
    # Estatísticas gerais
    serial_wins = sum(1 for r in results if r['Vencedor'] == 'SERIAL')
    distributed_wins = sum(1 for r in results if r['Vencedor'] == 'DISTRIBUÍDO')
    
    print(f"\n📊 ESTATÍSTICAS GERAIS:")
    print(f"   • Total de casos: {len(results)}")
    print(f"   • Vitórias SERIAL: {serial_wins}")
    print(f"   • Vitórias DISTRIBUÍDO: {distributed_wins}")
    
    # Salva resultados em arquivo
    print(f"\n💾 Salvando resultados em 'benchmark_results.txt'...")
    with open('/app/benchmark_results.txt', 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("BENCHMARK: PROCESSAMENTO SERIAL vs DISTRIBUÍDO\n")
        f.write("="*80 + "\n\n")
        f.write(tabulate(results, headers='keys', tablefmt='grid'))
        f.write("\n\n" + "="*80 + "\n")
        f.write("CONCLUSÕES\n")
        f.write("="*80 + "\n\n")
        if parallel_wins_from:
            f.write(f"✅ Processamento DISTRIBUÍDO vale a pena a partir do CASO {parallel_wins_from}\n")
            f.write(f"   Dimensões: {results[parallel_wins_from-1]['Dimensões']}\n")
        else:
            f.write("⚠️  Processamento SERIAL foi mais rápido em todos os casos.\n")
        f.write(f"\n📊 ESTATÍSTICAS:\n")
        f.write(f"   • Vitórias SERIAL: {serial_wins}\n")
        f.write(f"   • Vitórias DISTRIBUÍDO: {distributed_wins}\n")
    
    print(f"✅ Resultados salvos com sucesso!")
    
    print(f"\n{'='*80}")
    print("BENCHMARK CONCLUÍDO!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    try:
        run_benchmark()
    except KeyboardInterrupt:
        print("\n\n[BENCHMARK] Interrompido pelo usuário.")
    except Exception as e:
        print(f"\n[BENCHMARK] Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
