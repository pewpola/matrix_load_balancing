"""
Cliente para Sistema de Multiplicação Distribuída de Matrizes
Gera matrizes, divide em submatrizes e distribui para servidores via load balancer
"""
import socket
import pickle
import numpy as np
import time
import os
import threading


class MatrixClient:
    def __init__(self, load_balancer_host='load_balancer', load_balancer_port=5000):
        self.load_balancer_host = load_balancer_host
        self.load_balancer_port = load_balancer_port
    
    def generate_matrices(self, rows_a, cols_a, cols_b):
        """
        Gera duas matrizes aleatórias para multiplicação
        Matriz A: rows_a x cols_a
        Matriz B: cols_a x cols_b
        """
        print(f"\n[CLIENT] Gerando matrizes...")
        print(f"[CLIENT] Matriz A: {rows_a}x{cols_a}")
        print(f"[CLIENT] Matriz B: {cols_a}x{cols_b}")
        
        matrix_a = np.random.randint(1, 10, size=(rows_a, cols_a))
        matrix_b = np.random.randint(1, 10, size=(cols_a, cols_b))
        
        print(f"[CLIENT] Matrizes geradas com sucesso!")
        return matrix_a, matrix_b
    
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
                # Última parte pega o resto das linhas
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
            # Conecta ao load balancer
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(60)
            client_socket.connect((self.load_balancer_host, self.load_balancer_port))
            
            # Prepara dados para envio
            data = {
                'submatrix_a': submatrix_a,
                'matrix_b': matrix_b,
                'task_id': task_id
            }
            
            # Serializa e envia
            serialized_data = pickle.dumps(data)
            client_socket.sendall(serialized_data + b'END_OF_DATA')
            
            print(f"[CLIENT] Tarefa {task_id} enviada ao load balancer")
            
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
            
            print(f"[CLIENT] Resultado da tarefa {task_id} recebido de {result['server_id']}")
            
            client_socket.close()
            return result
            
        except Exception as e:
            print(f"[CLIENT] Erro ao enviar tarefa {task_id}: {e}")
            raise
    
    def multiply_distributed(self, matrix_a, matrix_b, num_servers=2):
        """
        Realiza a multiplicação distribuída de matrizes EM PARALELO
        Usa threading para enviar todas as tarefas simultaneamente aos servidores
        """
        print(f"\n[CLIENT] Iniciando multiplicação distribuída...")
        print(f"[CLIENT] Dividindo trabalho entre {num_servers} servidores")
        
        # Divide a matriz A em submatrizes
        submatrices = self.split_matrix(matrix_a, num_servers)
        
        print(f"[CLIENT] Matriz A dividida em {len(submatrices)} partes:")
        for i, sub in enumerate(submatrices):
            print(f"  - Parte {i+1}: {sub.shape}")
        
        # Lista para armazenar resultados na ordem correta
        results = [None] * num_servers
        threads = []
        
        def process_task(index, submatrix):
            """Função executada por cada thread para processar uma submatriz"""
            task_id = f"TASK-{index+1}"
            print(f"\n[CLIENT] Enviando {task_id}...")
            result = self.send_to_load_balancer(submatrix, matrix_b, task_id)
            results[index] = result  # Armazena na posição correta
        
        start_time = time.time()
        
        # Cria e inicia todas as threads simultaneamente (PROCESSAMENTO PARALELO!)
        print(f"\n[CLIENT] 🚀 Disparando {num_servers} requisições SIMULTANEAMENTE...")
        for i, submatrix in enumerate(submatrices):
            thread = threading.Thread(target=process_task, args=(i, submatrix))
            threads.append(thread)
            thread.start()
        
        # Aguarda todas as threads completarem
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Concatena os resultados parciais
        print(f"\n[CLIENT] Concatenando resultados parciais...")
        final_result = np.vstack([r['result'] for r in results])
        
        print(f"[CLIENT] Multiplicação distribuída concluída!")
        print(f"[CLIENT] Tempo total: {end_time - start_time:.2f} segundos")
        print(f"[CLIENT] Resultado final shape: {final_result.shape}")
        
        # Mostra estatísticas de distribuição
        print(f"\n[CLIENT] Estatísticas de distribuição:")
        for result in results:
            print(f"  - {result['task_id']} processada por {result['server_id']}")
        
        return final_result
    
    def verify_result(self, matrix_a, matrix_b, distributed_result):
        """
        Verifica se o resultado distribuído está correto comparando com NumPy
        """
        print(f"\n[CLIENT] Verificando resultado...")
        expected_result = np.dot(matrix_a, matrix_b)
        
        if np.array_equal(distributed_result, expected_result):
            print(f"[CLIENT] ✓ Resultado CORRETO! A multiplicação distribuída funcionou perfeitamente.")
            return True
        else:
            print(f"[CLIENT] ✗ Erro! O resultado distribuído difere do esperado.")
            return False
    
    def display_matrices(self, matrix_a, matrix_b, result):
        """
        Exibe as matrizes se forem pequenas o suficiente
        """
        if matrix_a.shape[0] <= 10 and matrix_a.shape[1] <= 10:
            print(f"\n[CLIENT] Matriz A:")
            print(matrix_a)
            print(f"\n[CLIENT] Matriz B:")
            print(matrix_b)
            print(f"\n[CLIENT] Resultado (A × B):")
            print(result)
        else:
            print(f"\n[CLIENT] Matrizes muito grandes para exibir completamente.")
            print(f"[CLIENT] Primeiras linhas do resultado:")
            print(result[:5, :5])


def main():
    print("="*70)
    print("SISTEMA DE MULTIPLICAÇÃO DISTRIBUÍDA DE MATRIZES")
    print("Arquitetura: Cliente -> Load Balancer -> Servidores (Round-Robin)")
    print("="*70)
    
    # Aguarda um pouco para garantir que os servidores estejam prontos
    print("\n[CLIENT] Aguardando servidores iniciarem...")
    time.sleep(5)
    
    client = MatrixClient()
    
    # ========== EXEMPLO 1: Matrizes 2x2 (Manual) ==========
    print("\n" + "="*70)
    print("EXEMPLO 1: MULTIPLICAÇÃO COM MATRIZES 2x2 (VALORES FIXOS)")
    print("="*70)
    
    # Matrizes definidas manualmente
    matrix_a_small = np.array([[1, 2],
                                [3, 4]])
    
    matrix_b_small = np.array([[5, 6],
                                [7, 8]])
    
    print(f"\n[CLIENT] Matriz A (2x2):")
    print(matrix_a_small)
    print(f"\n[CLIENT] Matriz B (2x2):")
    print(matrix_b_small)
    
    # Executa multiplicação distribuída
    result_small = client.multiply_distributed(matrix_a_small, matrix_b_small, num_servers=2)
    
    # Verifica resultado
    client.verify_result(matrix_a_small, matrix_b_small, result_small)
    
    # Exibe resultado
    print(f"\n[CLIENT] Resultado (A × B):")
    print(result_small)
    
    print(f"\n[CLIENT] Cálculo manual para verificação:")
    print(f"  Linha 1: [1×5 + 2×7, 1×6 + 2×8] = [{1*5 + 2*7}, {1*6 + 2*8}]")
    print(f"  Linha 2: [3×5 + 4×7, 3×6 + 4×8] = [{3*5 + 4*7}, {3*6 + 4*8}]")
    
    # ========== EXEMPLO 2: Matrizes 100x100 (Aleatórias) ==========
    print("\n" + "="*70)
    print("EXEMPLO 2: MULTIPLICAÇÃO COM MATRIZES 100x100 (ALEATÓRIAS)")
    print("="*70)
    
    # Configuração das matrizes
    rows_a = 100
    cols_a = 100
    cols_b = 100
    num_servers = 2
    
    # Gera matrizes
    matrix_a, matrix_b = client.generate_matrices(rows_a, cols_a, cols_b)
    
    # Executa multiplicação distribuída
    result = client.multiply_distributed(matrix_a, matrix_b, num_servers)
    
    # Verifica resultado
    client.verify_result(matrix_a, matrix_b, result)
    
    # Exibe matrizes se forem pequenas
    client.display_matrices(matrix_a, matrix_b, result)
    
    print(f"\n{'='*70}")
    print("PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f"{'='*70}\n")
    
    # Mantém o container rodando para visualização dos logs
    print("[CLIENT] Container permanecerá ativo. Pressione Ctrl+C para encerrar.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[CLIENT] Encerrando...")


if __name__ == "__main__":
    main()
