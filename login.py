import tkinter as tk
import requests

registered_name = ""

def start():
    SERVER_URL = 'http://localhost:8080'  # 服务器端URL


    def register():
        global registered_name
        username = entry_username.get()
        password = entry_password.get()

        # 发送注册请求到服务器
        response = requests.post(f'{SERVER_URL}/register', json={'username': username, 'password': password})
        if response.status_code == 200:
            label_result.config(text='注册成功', fg='green')
            registered_name = username
            root.destroy()
        else:
            label_result.config(text='注册失败', fg='red')


    def login():
        global registered_name
        username = entry_username.get()
        password = entry_password.get()

        # 发送登录请求到服务器
        response = requests.post(f'{SERVER_URL}/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            label_result.config(text='登录成功', fg='green')
            registered_name = username
            root.destroy()
        else:
            label_result.config(text='登录失败', fg='red')


    # 创建窗口
    root = tk.Tk()
    root.title('注册和登录')
    root.geometry('300x200')

    # 用户名输入框
    label_username = tk.Label(root, text='用户名:')
    label_username.pack()
    entry_username = tk.Entry(root)
    entry_username.pack()

    # 密码输入框
    label_password = tk.Label(root, text='密码:')
    label_password.pack()
    entry_password = tk.Entry(root, show='*')
    entry_password.pack()

    # 注册按钮
    btn_register = tk.Button(root, text='注册', command=register)
    btn_register.pack()

    # 登录按钮
    btn_login = tk.Button(root, text='登录', command=login)
    btn_login.pack()

    # 结果显示标签
    label_result = tk.Label(root, text='')
    label_result.pack()

    root.mainloop()

