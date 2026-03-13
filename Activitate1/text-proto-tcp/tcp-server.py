import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024

class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            self.data[key] = value
        return f"{key} added"

    def get(self, key):
        with self.lock:
            return self.data.get(key, "Key not found")

    def remove(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                return f"{key} removed"
            return "Key not found"

state = State()

def process_command(command):
    parts = command.split()

    if len(parts) == 0:
        return "ERROR empty command"

    cmd = parts[0].upper()

    try:

        if cmd == "ADD":
            if len(parts) < 3:
                return "ERROR invalid format"

            key = parts[1]
            value = ' '.join(parts[2:])
            state.data[key] = value
            return "OK record added"

        elif cmd == "GET":
            if len(parts) != 2:
                return "ERROR invalid format"

            key = parts[1]

            if key not in state.data:
                return "ERROR invalid key"

            return f"DATA {state.data[key]}"

        elif cmd == "REMOVE":
            if len(parts) != 2:
                return "ERROR invalid format"

            key = parts[1]

            if key not in state.data:
                return "ERROR invalid key"

            del state.data[key]
            return "OK value deleted"

        elif cmd == "LIST":

            if not state.data:
                return "DATA|"

            items = ",".join([f"{k}={v}" for k, v in state.data.items()])
            return f"DATA|{items}"

        elif cmd == "COUNT":
            return f"DATA {len(state.data)}"

        elif cmd == "CLEAR":
            state.data.clear()
            return "all data deleted"

        elif cmd == "UPDATE":

            if len(parts) < 3:
                return "ERROR invalid format"

            key = parts[1]

            if key not in state.data:
                return "ERROR invalid key"

            value = ' '.join(parts[2:])
            state.data[key] = value

            return "Data updated"

        elif cmd == "POP":

            if len(parts) != 2:
                return "ERROR invalid format"

            key = parts[1]

            if key not in state.data:
                return "ERROR invalid key"

            value = state.data.pop(key)
            return f"DATA {value}"

        elif cmd == "QUIT":
            return "BYE"

        else:
            return "ERROR unknown command"

    except Exception as e:
        return f"ERROR {str(e)}"

def handle_client(client_socket):
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                command = data.decode('utf-8').strip()
                response = process_command(command)
                
                response_data = f"{len(response)} {response}".encode('utf-8')
                client_socket.sendall(response_data)

                if command.upper() == "QUIT":
                    print(f"[SERVER] Client {client_socket.getpeername()} disconnected with QUIT")
                    break

            except Exception as e:
                client_socket.sendall(f"Error: {str(e)}".encode('utf-8'))
                break

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"[SERVER] Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
