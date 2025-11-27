"""
Servidor de Computação Distribuída para Multiplicação de Matrizes
Recebe submatrizes do load balancer e realiza a multiplicação
"""
import socket
import pickle
import numpy as np
import sys
import os


class MatrixServer:
    def __init__(self, host='0.0.0.0', port=5001):
        self.host = host
        self.port = port
        self.server_id = os.getenv('SERVER_ID', 'SERVER-1')
        
    def multiply_matrices(self, submatrix_a, matrix_b):
        """
        Realiza a multiplicação de uma submatriz de A com a matriz B completa
        """
        print(f"[{self.server_id}] Realizando multiplicação de matrizes...")
        print(f"[{self.server_id}] Submatriz A shape: {submatrix_a.shape}")
        print(f"[{self.server_id}] Matriz B shape: {matrix_b.shape}")
        
        result = np.dot(submatrix_a, matrix_b)
        
        print(f"[{self.server_id}] Multiplicação concluída. Resultado shape: {result.shape}")
        return result
    
    def handle_client(self, client_socket):
        """
        Processa requisições de multiplicação de matrizes
        """
        try:
            # Recebe os dados do cliente
            data = b''
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                # Verifica se recebeu todos os dados (termina com END_OF_DATA)
                if b'END_OF_DATA' in data:
                    data = data.replace(b'END_OF_DATA', b'')
                    break
            
            if not data:
                print(f"[{self.server_id}] Nenhum dado recebido")
                return
            
            # Desserializa os dados recebidos
            received_data = pickle.loads(data)
            submatrix_a = received_data['submatrix_a']
            matrix_b = received_data['matrix_b']
            task_id = received_data.get('task_id', 'unknown')
            
            print(f"[{self.server_id}] Recebida tarefa {task_id}")
            
            # Realiza a multiplicação
            result = self.multiply_matrices(submatrix_a, matrix_b)
            
            # Prepara a resposta
            response = {
                'result': result,
                'task_id': task_id,
                'server_id': self.server_id
            }
            
            # Serializa e envia o resultado
            result_data = pickle.dumps(response)
            client_socket.sendall(result_data + b'END_OF_DATA')
            
            print(f"[{self.server_id}] Resultado enviado para tarefa {task_id}")
            
        except Exception as e:
            print(f"[{self.server_id}] Erro ao processar requisição: {e}")
            import traceback
            traceback.print_exc()
        finally:
            client_socket.close()
    
    def start(self):
        """
        Inicia o servidor e aguarda conexões
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"[{self.server_id}] Servidor iniciado em {self.host}:{self.port}")
        print(f"[{self.server_id}] Aguardando conexões...")
        
        try:
            while True:
                client_socket, address = server_socket.accept()
                print(f"[{self.server_id}] Conexão recebida de {address}")
                self.handle_client(client_socket)
        except KeyboardInterrupt:
            print(f"\n[{self.server_id}] Servidor encerrado")
        finally:
            server_socket.close()


if __name__ == "__main__":
    # Permite configurar a porta via argumentos ou variável de ambiente
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.getenv('PORT', 5001))
    
    server = MatrixServer(port=port)
    server.start()
