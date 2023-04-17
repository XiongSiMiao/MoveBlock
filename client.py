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

    def draw(self):
        pygame.draw.rect(self.win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont(None, 20)
        text = font.render(self.name, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        self.win.blit(text, text_rect)

    def get_position(self):
        return [self.x, self.y]
    

 class Message:
    def __init__(self, win, text = "Can you see this message?"):
        self.win = win
        self.x = 0
        self.y = 0
        self.width = 200
        self.height = 200
        self.text = text

    def pass_message(self, message):
        self.text = message

    def draw(self):
        front = pygame.font.SysFont(None, 30)
        text = front.render(self.text, True, (0, 0, 0), (255, 255, 0))
        text_rect = text.get_rect()
        self.win.blit(text, text_rect)
        

class Input:
    def __init__(self, win):
        self.win = win
        self.x = 0
        self.y = 770
        self.width = 700
        self.height = 35
        self.color = (255, 255, 0)
        self.message = ""
        self.state = True
        
    def input_message(self):
        root = tk.Tk()
        root.title("Input Box")
        root.geometry ("400x200")
        enter_message = tk.Entry(root)
        enter_message.pack()
        btn1 = tk.Button(root)
        btn1["text"] = "Send"
        btn1.pack()
        
        def test(e):
            self.message = enter_message.get()
            messagebox.showinfo("Feedback", "Successfully send!")
            root.destroy()  # 关闭窗口
            
        btn1.bind("<Button-1>", test)  # 将按钮和方法进行绑定，也就是创建了一个事件
    
        root.mainloop()
        
    def get_message(self):
        return self.message
    
    
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
        
        self.message = Message(win = self.window, text = self.username + ":" )   #00000000000000
        self.input = Input(win = self.window)
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

        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.player.x - self.player.dis > 0:
            self.player.x -= self.player.dis

        elif keys[K_RIGHT] and self.player.x + self.player.dis < self.player.win.get_width() - self.player.width:
            self.player.x += self.player.dis

        elif keys[K_UP] and self.player.y - self.player.dis > 0:
            self.player.y -= self.player.dis

        elif keys[K_DOWN] and self.player.y + self.player.dis < self.player.win.get_height() - self.player.height:
            self.player.y += self.player.dis

        elif keys[K_RETURN]:
            self.input.input_message()

        self.player.draw()
        self.message.pass_message(self.username + ":" + self.input.get_message())
        self.message.draw()
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
