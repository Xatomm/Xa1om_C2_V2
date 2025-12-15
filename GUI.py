import sys, socket, json, threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QListWidget,
    QPushButton, QVBoxLayout, QWidget, QTextEdit
)

VPS_HOST = "7.tcp.eu.ngrok.io"
VPS_PORT = 16420
ADMIN_TOKEN = "ADMIN_SECRET"

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin GUI")
        self.resize(600, 400)

        self.clients = []

        self.list = QListWidget()
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        btn_ping = QPushButton("Ping")
        btn_info = QPushButton("Get Info")

        btn_ping.clicked.connect(lambda: self.send_cmd("ping"))
        btn_info.clicked.connect(lambda: self.send_cmd("get_info"))

        layout = QVBoxLayout()
        layout.addWidget(self.list)
        layout.addWidget(btn_ping)
        layout.addWidget(btn_info)
        layout.addWidget(self.log)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        self.sock = socket.socket()
        self.sock.connect((VPS_HOST, VPS_PORT))

        self.send({
            "type": "auth",
            "role": "admin",
            "token": ADMIN_TOKEN
        })

        threading.Thread(target=self.listen, daemon=True).start()

    def send(self, msg):
        self.sock.sendall((json.dumps(msg) + "\n").encode())

    def listen(self):
        buffer = ""
        while True:
            data = self.sock.recv(4096)
            if not data:
                break

            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                msg = json.loads(line)
                self.handle(msg)

    def handle(self, msg):
        if msg["type"] == "client_join":
            cid = msg["client_id"]
            self.clients.append(cid)
            self.list.addItem(cid)

        elif msg["type"] == "client_response":
            self.log.append(
                f"[{msg['client_id']}] {msg['action']} → {msg['result']}"
            )

    def send_cmd(self, action):
        item = self.list.currentItem()
        if not item:
            return

        self.send({
            "type": "command_request",
            "target": item.text(),
            "action": action
        })

app = QApplication(sys.argv)
win = GUI()
win.show()
sys.exit(app.exec())
