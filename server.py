import json
import socket
from threading import Thread


class Server:
    def __init__(self):
        self.port = 5000
        # host change to your own ip, the same in client.py
        def get_host_ip():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
            finally:
                s.close()
            return ip
        self.host = get_host_ip()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players_data = {}

    def start(self):
        self.get_socket_ready()
        self.handle_connection()

    def get_socket_ready(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print("The server is ready to accept client connections")

    def handle_connection(self):
        while True:
            conn, addr = self.sock.accept()
            print(f"Received connection from {addr}")
            conn.send(str(id(conn)).encode("utf-8"))
            Thread(target=self.handle_message, args=(conn, )).start()





    def handle_message(self, conn):
        while True:
            try:
                data = conn.recv(2048)
                if not data:
                    print("No data received, close the connection")
                    self.players_data.pop(str(id(conn)))
                    conn.close()
                    break
                else:
                    data = json.loads(data.decode("utf-8"))
                    name = data["name"]  # 提取用户名
                    pwd = data["pwd"]  # 提取密码
                    if self.validate_user(name, pwd):  # 验证用户名和密码
                        self.update_one_player_data(data)
                        conn.sendall(json.dumps(self.get_other_players_data(data["id"])).encode("utf-8"))
                    else:
                        conn.sendall("wrong username or password".encode("utf-8"))  # 发送错误信息
            except Exception as e:
                print(repr(e))
                break

    def validate_user(self, username, password):
        # 在这里添加用户名和密码验证的逻辑，例如：
        # 可以将用户名和密码与预先设置的值进行比较，或者查询数据库进行验证
        if username == "admin" and password == "123456":
            return True
        else:
            return False

    def update_one_player_data(self, data):
        key = data["id"]
        pos = data["pos"]
        color = data["color"]
        name = data["name"]
        pwd = data["pwd"]
        self.players_data[key] = {"pos": pos, "color": color, "name": name}

    def get_other_players_data(self, current_player_id):
        data = {}
        for key, value in self.players_data.items():
            if key != current_player_id:
                data[key] = value
        return data


if __name__ == '__main__':
    server = Server()
    server.start()

