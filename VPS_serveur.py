import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 12345

ADMIN_TOKEN = "ADMIN_SECRET"

clients = {}   # client_id -> socket
admins = []    # sockets admin

ALLOWED_ACTIONS = {
    "ping",
    "get_info"
}

def send(sock, data):
    sock.sendall((json.dumps(data) + "\n").encode())

def handle_connection(conn, addr):
    print(f"[VPS] Connexion de {addr}")
    buffer = ""

    role = None
    client_id = None

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                msg = json.loads(line)

                # ---------- AUTH ----------
                if msg["type"] == "auth":
                    if msg["role"] == "admin":
                        if msg.get("token") == ADMIN_TOKEN:
                            role = "admin"
                            admins.append(conn)
                            print("[VPS] Admin connecté")
                        else:
                            conn.close()
                            return

                    elif msg["role"] == "client":
                        role = "client"
                        client_id = msg["client_id"]
                        clients[client_id] = conn
                        print(f"[VPS] Client enregistré: {client_id}")

                        # informer les admins
                        for a in admins:
                            send(a, {
                                "type": "client_join",
                                "client_id": client_id
                            })

                # ---------- ADMIN ----------
                elif role == "admin" and msg["type"] == "command_request":
                    target = msg["target"]
                    action = msg["action"]

                    if action not in ALLOWED_ACTIONS:
                        continue

                    if target in clients:
                        send(clients[target], {
                            "type": "command",
                            "action": action
                        })

                # ---------- CLIENT ----------
                elif role == "client" and msg["type"] == "command_result":
                    for a in admins:
                        send(a, {
                            "type": "client_response",
                            "client_id": client_id,
                            "action": msg["action"],
                            "result": msg["result"]
                        })

    except Exception as e:
        print("[VPS] Erreur:", e)

    finally:
        if role == "client" and client_id in clients:
            del clients[client_id]
        if conn in admins:
            admins.remove(conn)

        conn.close()
        print("[VPS] Déconnexion", addr)

def main():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()
    print(f"[VPS] Écoute sur {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_connection, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
