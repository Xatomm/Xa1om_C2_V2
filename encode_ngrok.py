import base64

KEY = input("XOR KEY >>>")
DATA = input("NGROK TUNNEL ADR >>>")

def xor_encrypt(data, key):
    kb = key.encode()
    return bytes(data[i] ^ kb[i % len(kb)] for i in range(len(data)))

enc = xor_encrypt(DATA.encode(), KEY)
print(base64.b64encode(enc).decode())
