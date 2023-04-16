from flask import Flask, request, jsonify
import hashlib
import json
import secrets

app = Flask(__name__)



@app.route('/register', methods=['POST'])
def register():
    # 解析请求的JSON数据
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    salt = generate_salt()

    # 加密密码
    hashed_password = hash_password(password,salt)

    # 检查用户名是否已经存在
    if is_username_exists(username):
        return jsonify({'message': '用户名已存在'}), 400

    # 注册用户
    user = {'username': username, 'password': hashed_password, 'salt': salt}
    write_user_to_file(user)
    return jsonify({'message': '注册成功'}), 200


@app.route('/login', methods=['POST'])
def login():
    # 解析请求的JSON数据
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 获取用户信息
    user = get_user_from_file(username)

    if user is not None:
        hashed_password = hash_password(password,user['salt'])
        if user['password'] == hashed_password:
            return jsonify({'message': '登录成功'}), 200

    return jsonify({'message': '用户名或密码错误'}), 401

def generate_salt():
    """生成加密盐值"""
    salt = secrets.token_hex(16)
    return salt


def hash_password(password,salt):
    """对密码进行加盐哈希处理"""
    salted_password = salt + password
    hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
    return hashed_password


def is_username_exists(username):
    """检查用户名是否已经存在"""
    with open('users.txt', 'r') as f:
        for line in f:
            user = json.loads(line)
            if user['username'] == username:
                return True
    return False


def write_user_to_file(user):
    """将用户信息写入文件"""
    with open('users.txt', 'a') as f:
        json.dump(user, f)
        f.write('\n')


def get_user_from_file(username):
    """从文件中获取用户信息"""
    with open('users.txt', 'r') as f:
        for line in f:
            user = json.loads(line)
            if user['username'] == username:
                return user


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

