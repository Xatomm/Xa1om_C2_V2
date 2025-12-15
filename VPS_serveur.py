import socket, threading, json

SERVER_HOST = "0.0.0.0"
SERVER_PORT_CLIENTS = 5000  # port pour clients
SERVER_PORT_GUI = 5001      # port pour le GUI/admin

clients = {}  # client_id -> socket
gui_socket = None

def handle_client(sock, addr):
    global clients, gui_socket
    buffer = ""
    client_id = None
    try:
        while True:
            data = sock.recv(4096).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                msg = json.loads(line)

                # Auth client
                if msg.get("type") == "auth" and msg.get("role") == "client":
                    client_id = msg.get("client_id")
                    clients[client_id] = sock
                    print(f"[+] Client connecté : {client_id}")

                    if gui_socket:
                        gui_socket.sendall((json.dumps({
                            "type": "client_join",
                            "client_id": client_id
                        }) + "\n").encode())

                # Command response
                elif msg.get("type") == "command_result" and gui_socket:
                    gui_socket.sendall((json.dumps({
                        "type": "client_response",
                        "client_id": client_id,
                        "action": msg["action"],
                        "result": msg["result"]
                    }) + "\n").encode())
    except:
        pass
    finally:
        if client_id and client_id in clients:
            del clients[client_id]
            print(f"[-] Client déconnecté : {client_id}")
            if gui_socket:
                gui_socket.sendall((json.dumps({
                    "type": "client_left",
                    "client_id": client_id
                }) + "\n").encode())
        sock.close()

def handle_gui(sock, addr):
    global gui_socket
    gui_socket = sock
    print("[+] GUI connecté")
    buffer = ""
    try:
        while True:
            data = sock.recv(4096).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                msg = json.loads(line)

                # Command request from GUI
                if msg.get("type") == "command_request":
                    target = msg.get("target")
                    action = msg.get("action")
                    if target in clients:
                        clients[target].sendall((json.dumps({
                            "type": "command",
                            "action": action
                        }) + "\n").encode())
    except:
        pass
    finally:
        gui_socket = None
        sock.close()
        print("[-] GUI déconnecté")

# -------------------
# Lancement du serveur
# -------------------
def main():
    # Thread clients
    threading.Thread(target=lambda: accept_connections(SERVER_PORT_CLIENTS, handle_client), daemon=True).start()
    # Thread GUI
    threading.Thread(target=lambda: accept_connections(SERVER_PORT_GUI, handle_gui), daemon=True).start()

    print(f"Serveur VPS démarré. Ports clients: {SERVER_PORT_CLIENTS}, GUI: {SERVER_PORT_GUI}")
    while True:
        pass

def accept_connections(port, handler):
    sock = socket.socket()
    sock.bind((SERVER_HOST, port))
    sock.listen(5)
    while True:
        client_sock, addr = sock.accept()
        threading.Thread(target=handler, args=(client_sock, addr), daemon=True).start()

if __name__ == "__main__":
    main()
