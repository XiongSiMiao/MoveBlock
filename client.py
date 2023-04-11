import sys
import json
import pygame
# remember download this package
import socket
import tkinter as tk
import tkinter.messagebox
from random import randint


class Player:
    def __init__(self, win, p_id, x, y, color, name):
        self.win = win
        self.id = p_id
        self.dis = 3
        self.x = x
        self.y = y
        self.width = 80
        self.height = 80
        self.color = color
        self.name = name

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.x -= self.dis
        elif keys[pygame.K_RIGHT]:
            self.x += self.dis
        elif keys[pygame.K_UP]:
            self.y -= self.dis
        elif keys[pygame.K_DOWN]:
            self.y += self.dis

    def draw(self):
        pygame.draw.rect(self.win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont(None, 20)
        text = font.render(self.name, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        self.win.blit(text, text_rect)


class GameWindow:
    def __init__(self, Name, Password):
        self.width = 1200
        self.height = 800
        self.window = self.init_window()
        self.username, self.password = Name, Password

        self.player = Player(win=self.window,
                             p_id=None,
                             x=randint(0, self.width - 100),
                             y=randint(0, self.height - 100),
                             color=(randint(0, 200), randint(0, 200), randint(0, 200)),
                             name=self.username)

        self.port = 5000

        # change to your own ip
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

        self.connect()
        self.other_players_dict = {}

    def init_window(self):
        pygame.init()
        pygame.display.set_caption('移动方块')
        return pygame.display.set_mode((self.width, self.height))

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.player.id = self.sock.recv(2048).decode("utf-8")

    def send_player_data(self):
        data = {
            "id": self.player.id,
            "pos": [self.player.x, self.player.y],
            "color": self.player.color,
            "name": self.player.name,
            "pwd": self.password,
        }
        self.sock.send(json.dumps(data).encode("utf-8"))
        return self.sock.recv(2048).decode("utf-8")

    def update_window(self):
        self.window.fill((255, 255, 255))

        self.player.move()
        self.player.draw()

        other_players_data = json.loads(self.send_player_data())
        self.update_other_players_data(other_players_data)
        self.delete_offline_players(other_players_data)

        pygame.display.update()

    def update_other_players_data(self, data):
        for key, value in data.items():
            if not self.other_players_dict.get(key):
                self.add_one_player(key, value)
            else:
                pos = value["pos"]
                self.other_players_dict[key].x = pos[0]
                self.other_players_dict[key].y = pos[1]
                self.other_players_dict[key].draw()

    def add_one_player(self, player_id, value):
        pos = value["pos"]
        color = value["color"]
        self.other_players_dict[player_id] = Player(self.window, player_id, pos[0], pos[1], color, name=value["name"])

    def delete_offline_players(self, data):
        new_dict = {}
        for key in self.other_players_dict.keys():
            if data.get(key):
                new_dict[key] = self.other_players_dict[key]
        self.other_players_dict = new_dict

    def start(self):
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)
            # 60 fps

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.update_window()


def Login():
    # 创建应用程序窗口
    root = tkinter.Tk()
    # 设置窗口标题
    root.title('Login Window')
    varName = tkinter.StringVar()
    varName.set('')
    varPwd = tkinter.StringVar()
    varPwd.set('')
    # 创建标签
    labelName = tkinter.Label(root, text='Username:', justify=tkinter.RIGHT, width=80)
    # 将标签放到窗口上
    labelName.place(x=10, y=5, width=80, height=20)
    # 创建文本框，同时设置关联的变量
    entryName = tkinter.Entry(root, width=80, textvariable=varName)
    entryName.place(x=100, y=5, width=80, height=20)

    labelPwd = tkinter.Label(root, text='Password:', justify=tkinter.RIGHT, width=80)
    labelPwd.place(x=10, y=30, width=80, height=20)
    # 创建密码文本框
    entryPwd = tkinter.Entry(root, show='*', width=80, textvariable=varPwd)
    entryPwd.place(x=100, y=30, width=80, height=20)

    def login():
        # 获取用户名和密码
        name = entryName.get()
        pwd = entryPwd.get()
        if is_logined(name, pwd):
            root.destroy()
            game = GameWindow(name, pwd)
            game.start()
        else:
            tkinter.messagebox.showerror('MoveBlock', message='Wrong username or password!')

    def is_logined(name, pwd):
        # 向server发送用户名和密码
        # 接收server返回的信息
        def connect():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            return sock

        def get_host():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
            finally:
                s.close()
            return ip

        host = get_host()
        port = 5000
        sock = connect()
        data = {
            "name": name,
            "pwd": pwd,
        }
        sock.send(json.dumps(data).encode("utf-8"))
        result = sock.recv(2048).decode("utf-8")
        return result != "wrong username or password"

    # 创建按钮组件，同时设置按钮事件处理函数
    buttonOk = tkinter.Button(root, text='Login', command=login)
    buttonOk.place(x=30, y=70, width=50, height=20)

    def cancel():
        # 清空用户输入的用户名和密码
        varName.set('')
        varPwd.set('')

    buttonCancel = tkinter.Button(root, text='Cancel', command=cancel)
    buttonCancel.place(x=90, y=70, width=50, height=20)

    # 启动消息循环
    root.mainloop()


if __name__ == '__main__':
    Login()
