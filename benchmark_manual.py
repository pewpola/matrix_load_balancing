"""
Benchmark Manual: Comparação entre Processamento Serial e Distribuído
O usuário define os tamanhos de matrizes que deseja testar
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


def get_matrix_dimensions():
    """
    Solicita ao usuário as dimensões das matrizes
    """
    print("\n" + "="*80)
    print("CONFIGURAÇÃO DAS MATRIZES")
    print("="*80)
    print("\nPara multiplicar Matriz A × Matriz B:")
    print("  • Matriz A deve ter dimensões: linhas × colunas")
    print("  • Matriz B deve ter dimensões: linhas × colunas")
    print("  • O número de COLUNAS de A deve ser igual ao número de LINHAS de B")
    
    while True:
        try:
            print("\n" + "-"*80)
            rows_a = int(input("Digite o número de LINHAS da Matriz A: ").strip())
            cols_a = int(input("Digite o número de COLUNAS da Matriz A: ").strip())
            rows_b = int(input("Digite o número de LINHAS da Matriz B: ").strip())
            cols_b = int(input("Digite o número de COLUNAS da Matriz B: ").strip())
            
            if rows_a <= 0 or cols_a <= 0 or rows_b <= 0 or cols_b <= 0:
                print("\n❌ Erro: Todas as dimensões devem ser maiores que zero!")
                continue
            
            if cols_a != rows_b:
                print(f"\n❌ Erro: Número de COLUNAS de A ({cols_a}) deve ser igual ao número de LINHAS de B ({rows_b})!")
                continue
            
            print(f"\n✓ Configuração:")
            print(f"  • Matriz A: {rows_a}×{cols_a}")
            print(f"  • Matriz B: {rows_b}×{cols_b}")
            print(f"  • Resultado: {rows_a}×{cols_b}")
            
            confirm = input("\nConfirma estas dimensões? (s/n): ").strip().lower()
            if confirm == 's':
                return rows_a, cols_a, rows_b, cols_b
            
        except ValueError:
            print("\n❌ Erro: Digite apenas números inteiros!")
        except KeyboardInterrupt:
            print("\n\n[BENCHMARK] Cancelado pelo usuário.")
            sys.exit(0)


def get_num_executions():
    """
    Solicita ao usuário quantas execuções realizar para média
    """
    while True:
        try:
            num_exec = int(input("\nQuantas execuções para calcular a média? (recomendado: 3): ").strip())
            if num_exec <= 0:
                print("❌ Erro: Número de execuções deve ser maior que zero!")
                continue
            return num_exec
        except ValueError:
            print("❌ Erro: Digite um número inteiro!")
        except KeyboardInterrupt:
            print("\n\n[BENCHMARK] Cancelado pelo usuário.")
            sys.exit(0)


def input_matrix_manually(rows, cols, matrix_name):
    """
    Permite ao usuário inserir manualmente os valores de uma matriz linha por linha
    """
    print(f"\n[INPUT] Insira os valores da Matriz {matrix_name} ({rows}×{cols})")
    print(f"[INPUT] Digite os valores separados por espaço para cada linha")
    
    matrix = []
    for i in range(rows):
        while True:
            try:
                print(f"\nLinha {i+1}/{rows} (digite {cols} valores separados por espaço):")
                line_input = input(f"  Valores: ").strip()
                values = [int(x) for x in line_input.split()]
                
                if len(values) != cols:
                    print(f"❌ Erro: Esperado {cols} valores, mas recebeu {len(values)}. Tente novamente.")
                    continue
                
                matrix.append(values)
                break
            except ValueError:
                print("❌ Erro: Digite apenas números inteiros válidos separados por espaço!")
            except KeyboardInterrupt:
                print("\n\n[BENCHMARK] Cancelado pelo usuário.")
                sys.exit(0)
    
    return np.array(matrix, dtype=int)


def get_matrix_input_mode(rows, cols, matrix_name):
    """
    Pergunta ao usuário se deseja preencher manualmente ou gerar aleatoriamente
    """
    if rows > 4 or cols > 4:
        return 'random'
    
    print(f"\n[INPUT] Como deseja definir a Matriz {matrix_name} ({rows}×{cols})?")
    print("  1 - Preencher manualmente (valor por valor)")
    print("  2 - Gerar aleatoriamente (valores entre 1 e 9)")
    
    while True:
        try:
            choice = input("\nEscolha (1 ou 2): ").strip()
            if choice == '1':
                return 'manual'
            elif choice == '2':
                return 'random'
            else:
                print("❌ Erro: Digite 1 ou 2!")
        except KeyboardInterrupt:
            print("\n\n[BENCHMARK] Cancelado pelo usuário.")
            sys.exit(0)


def run_manual_benchmark():
    """
    Executa benchmark manual com dimensões definidas pelo usuário
    """
    print("="*80)
    print("BENCHMARK MANUAL: PROCESSAMENTO SERIAL vs DISTRIBUÍDO")
    print("Análise de Performance Personalizada")
    print("="*80)
    
    # Aguarda servidores iniciarem
    print("\n[BENCHMARK] Aguardando servidores iniciarem...")
    time.sleep(5)
    
    client = BenchmarkClient()
    
    # ========== DEMONSTRAÇÃO: Validação com Matriz 2x2 ==========
    print("\n" + "="*80)
    print("DEMONSTRAÇÃO: VALIDAÇÃO DA MULTIPLICAÇÃO COM MATRIZ 2x2")
    print("="*80)
    
    # Define matrizes 2x2 simples
    demo_a = np.array([[1, 2],
                       [3, 4]])
    
    demo_b = np.array([[5, 6],
                       [7, 8]])
    
    print("\n[DEMO] Matriz A (2×2):")
    print(demo_a)
    print("\n[DEMO] Matriz B (2×2):")
    print(demo_b)
    print("\n[DEMO] Primeiras 10x10 - Matriz A:")
    print(demo_a[:10, :10])
    print("\n[DEMO] Primeiras 10x10 - Matriz B:")
    print(demo_b[:10, :10])
    
    # Cálculo manual esperado
    print("\n[DEMO] Cálculo manual esperado:")
    print("  Resultado[0,0] = (1×5) + (2×7) = 5 + 14 = 19")
    print("  Resultado[0,1] = (1×6) + (2×8) = 6 + 16 = 22")
    print("  Resultado[1,0] = (3×5) + (4×7) = 15 + 28 = 43")
    print("  Resultado[1,1] = (3×6) + (4×8) = 18 + 32 = 50")
    
    # Executa multiplicação via servidor
    print("\n[DEMO] Enviando para multiplicação distribuída...")
    demo_result = client.serial_multiplication(demo_a, demo_b)
    
    # Resultado esperado com NumPy
    demo_expected = np.dot(demo_a, demo_b)
    
    print("\n[DEMO] Resultado obtido do servidor:")
    print(demo_result)
    
    print("\n[DEMO] Resultado esperado (NumPy local):")
    print(demo_expected)
    
    print("\n[DEMO] Primeiras 10x10 - Resultado:")
    print(demo_result[:10, :10])
    
    # Validação
    if np.array_equal(demo_result, demo_expected):
        print("\n[DEMO] ✅ VALIDAÇÃO CONFIRMADA!")
        print("[DEMO] O servidor está calculando corretamente a multiplicação de matrizes.")
    else:
        print("\n[DEMO] ❌ ERRO NA VALIDAÇÃO!")
        print("[DEMO] Os resultados não coincidem. Verifique a implementação.")
        return
    
    # Loop para permitir múltiplos testes
    results_history = []
    
    while True:
        # Solicita dimensões ao usuário
        rows_a, cols_a, rows_b, cols_b = get_matrix_dimensions()
        
        # Solicita número de execuções
        num_executions = get_num_executions()
        
        print("\n" + "="*80)
        print(f"TESTE: Matriz A({rows_a}×{cols_a}) × Matriz B({rows_b}×{cols_b})")
        print(f"Execuções por teste: {num_executions}")
        print("="*80)
        
        # Gera ou solicita input das matrizes
        mode_a = get_matrix_input_mode(rows_a, cols_a, 'A')
        if mode_a == 'manual':
            matrix_a = input_matrix_manually(rows_a, cols_a, 'A')
            print(f"\n[BENCHMARK] Matriz A preenchida manualmente!")
        else:
            print("\n[BENCHMARK] Gerando Matriz A aleatoriamente...")
            matrix_a = np.random.randint(1, 10, size=(rows_a, cols_a))
            print("[BENCHMARK] Matriz A gerada!")
        
        mode_b = get_matrix_input_mode(rows_b, cols_b, 'B')
        if mode_b == 'manual':
            matrix_b = input_matrix_manually(rows_b, cols_b, 'B')
            print(f"\n[BENCHMARK] Matriz B preenchida manualmente!")
        else:
            print("\n[BENCHMARK] Gerando Matriz B aleatoriamente...")
            matrix_b = np.random.randint(1, 10, size=(rows_b, cols_b))
            print("[BENCHMARK] Matriz B gerada!")
        
        # Exibe primeiras 10x10 das matrizes
        print(f"\n[MATRIZES] Primeiras 10x10 - Matriz A:")
        print(matrix_a[:10, :10])
        print(f"\n[MATRIZES] Primeiras 10x10 - Matriz B:")
        print(matrix_b[:10, :10])
        
        # ========== TESTE SERIAL ==========
        print(f"\n[SERIAL] Executando processamento serial (1 servidor)...")
        serial_times = []
        
        for run in range(num_executions):
            print(f"  Execução {run+1}/{num_executions}...", end=" ", flush=True)
            start_time = time.time()
            result_serial = client.serial_multiplication(matrix_a, matrix_b)
            end_time = time.time()
            serial_time = end_time - start_time
            serial_times.append(serial_time)
            print(f"{serial_time:.4f}s")
        
        avg_serial_time = np.mean(serial_times)
        print(f"[SERIAL] Tempo médio: {avg_serial_time:.4f}s")
        
        # ========== TESTE DISTRIBUÍDO ==========
        print(f"\n[DISTRIBUÍDO] Executando processamento distribuído (2 servidores)...")
        distributed_times = []
        
        for run in range(num_executions):
            print(f"  Execução {run+1}/{num_executions}...", end=" ", flush=True)
            start_time = time.time()
            result_distributed = client.distributed_multiplication(matrix_a, matrix_b, num_servers=2)
            end_time = time.time()
            distributed_time = end_time - start_time
            distributed_times.append(distributed_time)
            print(f"{distributed_time:.4f}s")
        
        avg_distributed_time = np.mean(distributed_times)
        print(f"[DISTRIBUÍDO] Tempo médio: {avg_distributed_time:.4f}s")
        
        # ========== ANÁLISE ==========
        speedup = avg_serial_time / avg_distributed_time
        improvement = ((avg_serial_time - avg_distributed_time) / avg_serial_time) * 100
        
        winner = "DISTRIBUÍDO" if avg_distributed_time < avg_serial_time else "SERIAL"
        
        print(f"\n" + "="*80)
        print("RESULTADO DA ANÁLISE")
        print("="*80)
        print(f"  Vencedor: {winner}")
        print(f"  Speedup: {speedup:.2f}x")
        if improvement > 0:
            print(f"  Melhoria: {improvement:.2f}% mais rápido")
        else:
            print(f"  Overhead: {abs(improvement):.2f}% mais lento")
        
        # Exibe primeiras 10x10 do resultado
        print(f"\n[RESULTADO] Primeiras 10x10 - Matriz Resultado:")
        print(result_distributed[:10, :10])
        
        # Validação
        if np.array_equal(result_serial, result_distributed):
            print(f"  ✓ Resultados validados (iguais)")
        else:
            print(f"  ✗ ERRO: Resultados diferentes!")
        
        # Armazena no histórico
        results_history.append({
            'Dimensões': f"({rows_a}×{cols_a}) × ({rows_b}×{cols_b})",
            'Execuções': num_executions,
            'Serial (s)': f"{avg_serial_time:.4f}",
            'Distribuído (s)': f"{avg_distributed_time:.4f}",
            'Speedup': f"{speedup:.2f}x",
            'Melhoria (%)': f"{improvement:+.2f}%",
            'Vencedor': winner
        })
        
        # Pergunta se quer fazer outro teste
        print("\n" + "="*80)
        try:
            another = input("\nDeseja testar outro tamanho de matriz? (s/n): ").strip().lower()
            if another != 's':
                break
        except KeyboardInterrupt:
            print("\n")
            break
    
    # ========== RELATÓRIO FINAL ==========
    if results_history:
        print("\n\n" + "="*80)
        print("HISTÓRICO DE TESTES REALIZADOS")
        print("="*80 + "\n")
        
        print(tabulate(results_history, headers='keys', tablefmt='grid'))
        
        # Estatísticas gerais
        serial_wins = sum(1 for r in results_history if r['Vencedor'] == 'SERIAL')
        distributed_wins = sum(1 for r in results_history if r['Vencedor'] == 'DISTRIBUÍDO')
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   • Total de testes: {len(results_history)}")
        print(f"   • Vitórias SERIAL: {serial_wins}")
        print(f"   • Vitórias DISTRIBUÍDO: {distributed_wins}")
    
    print(f"\n{'='*80}")
    print("BENCHMARK MANUAL CONCLUÍDO!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    try:
        run_manual_benchmark()
    except KeyboardInterrupt:
        print("\n\n[BENCHMARK] Interrompido pelo usuário.")
    except Exception as e:
        print(f"\n[BENCHMARK] Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
