import sys
import json
import hashlib
import pygame
# remember download this package
import socket
import tkinter as tk
import tkinter.messagebox
from random import randint
import login


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

        if keys[pygame.K_LEFT] and self.x - self.dis > 0:
            self.x -= self.dis
        elif keys[pygame.K_RIGHT] and self.x + self.dis < self.win.get_width() - self.width:
            self.x += self.dis
        elif keys[pygame.K_UP] and self.y - self.dis > 0:
            self.y -= self.dis
        elif keys[pygame.K_DOWN] and self.y + self.dis < self.win.get_height() - self.height:
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




if __name__ == '__main__':
    login.start()
    game = GameWindow(login.registered_name,"NoMeaningPWD")
    game.start()
