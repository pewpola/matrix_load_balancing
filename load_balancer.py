"""
Load Balancer para Distribuição de Tarefas de Multiplicação de Matrizes
Implementa algoritmo Round-Robin para balanceamento de carga entre servidores
"""
import socket
import pickle
import threading
import time
from queue import Queue


class LoadBalancer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.servers = [
            {'host': 'server1', 'port': 5001, 'id': 'SERVER-1'},
            {'host': 'server2', 'port': 5002, 'id': 'SERVER-2'}
        ]
        self.current_server_index = 0
        self.lock = threading.Lock()
        self.stats = {
            'total_requests': 0,
            'server_requests': {'SERVER-1': 0, 'SERVER-2': 0}
        }
    
    def get_next_server(self):
        """
        Implementa Round-Robin para seleção do próximo servidor
        """
        with self.lock:
            server = self.servers[self.current_server_index]
            self.current_server_index = (self.current_server_index + 1) % len(self.servers)
            self.stats['total_requests'] += 1
            self.stats['server_requests'][server['id']] += 1
            return server
    
    def forward_to_server(self, server, data):
        """
        Encaminha a requisição para o servidor selecionado
        """
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"[LOAD BALANCER] Encaminhando para {server['id']} ({server['host']}:{server['port']}) - Tentativa {attempt + 1}")
                
                # Conecta ao servidor
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.settimeout(30)
                server_socket.connect((server['host'], server['port']))
                
                # Envia os dados
                server_socket.sendall(data + b'END_OF_DATA')
                
                # Recebe a resposta
                response_data = b''
                while True:
                    chunk = server_socket.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    if b'END_OF_DATA' in response_data:
                        response_data = response_data.replace(b'END_OF_DATA', b'')
                        break
                
                server_socket.close()
                
                print(f"[LOAD BALANCER] Resposta recebida de {server['id']}")
                return response_data
                
            except Exception as e:
                print(f"[LOAD BALANCER] Erro ao conectar com {server['id']}: {e}")
                if attempt < max_retries - 1:
                    print(f"[LOAD BALANCER] Aguardando {retry_delay}s antes de tentar novamente...")
                    time.sleep(retry_delay)
                else:
                    print(f"[LOAD BALANCER] Falha após {max_retries} tentativas")
                    raise
        
        raise Exception(f"Não foi possível conectar ao servidor {server['id']}")
    
    def handle_client(self, client_socket, address):
        """
        Processa requisições do cliente e distribui entre os servidores
        """
        try:
            print(f"[LOAD BALANCER] Conexão recebida de {address}")
            
            # Recebe dados do cliente
            data = b''
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b'END_OF_DATA' in data:
                    data = data.replace(b'END_OF_DATA', b'')
                    break
            
            if not data:
                print(f"[LOAD BALANCER] Nenhum dado recebido de {address}")
                return
            
            # Seleciona o servidor usando Round-Robin
            server = self.get_next_server()
            
            print(f"[LOAD BALANCER] Servidor selecionado: {server['id']}")
            print(f"[LOAD BALANCER] Estatísticas - Total: {self.stats['total_requests']}, "
                  f"SERVER-1: {self.stats['server_requests']['SERVER-1']}, "
                  f"SERVER-2: {self.stats['server_requests']['SERVER-2']}")
            
            # Encaminha para o servidor selecionado
            response_data = self.forward_to_server(server, data)
            
            # Envia resposta de volta ao cliente
            client_socket.sendall(response_data + b'END_OF_DATA')
            
            print(f"[LOAD BALANCER] Resposta enviada para {address}")
            
        except Exception as e:
            print(f"[LOAD BALANCER] Erro ao processar requisição: {e}")
            import traceback
            traceback.print_exc()
        finally:
            client_socket.close()
    
    def start(self):
        """
        Inicia o load balancer
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)
        
        print(f"[LOAD BALANCER] Iniciado em {self.host}:{self.port}")
        print(f"[LOAD BALANCER] Servidores disponíveis:")
        for server in self.servers:
            print(f"  - {server['id']}: {server['host']}:{server['port']}")
        print(f"[LOAD BALANCER] Aguardando conexões...")
        
        try:
            while True:
                client_socket, address = server_socket.accept()
                # Processa cada cliente em uma thread separada
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print(f"\n[LOAD BALANCER] Encerrando...")
        finally:
            server_socket.close()


if __name__ == "__main__":
    load_balancer = LoadBalancer()
    load_balancer.start()
