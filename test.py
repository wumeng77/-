import time
from flask import Flask, render_template, request, session, redirect, url_for,jsonify
from flask_socketio import SocketIO, emit
import paramiko
import os
from to_db import get_hosts,insert_host
from to_redis import init_redis_session

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)
init_redis_session(app)
sessions = {}

@app.route('/')
def index():
    try:
        session['key'] = 'value'  # 尝试保存数据到会话中
    except Exception as e:
        return f"Session error: {e}"

    return render_template('index.html')

@app.route('/terminal')
def terminal():
    return render_template('/connect/terminal.html')

@app.route('/connection')
def connection():
    return render_template('/connect/choose_connect.html',hosts =get_hosts())




############
# ssh连接模块
@app.route('/connect_to_host', methods=['POST'])
def connect():
    ip_address = request.form['ip']
    username = request.form['username']
    password = request.form['password']

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip_address, username=username, password=password)

        # 创建交互式 SSH 通道
        ssh_channel = ssh_client.invoke_shell()

        # 保存会话和 SSH 通道
        session_id = os.urandom(24).hex()
        session['session_id'] = session_id
        sessions[session_id] = {'ssh_client': ssh_client, 'ssh_channel': ssh_channel}

        return redirect(url_for('terminal'))
    except Exception as e:
        return f"Connection failed: {str(e)}"
    
@socketio.on('execute_command')
def handle_command(data):
    command = data['command'] + '\n'
    session_id = session.get('session_id', None)

    if session_id and session_id in sessions:
        ssh_channel = sessions[session_id]['ssh_channel']
        ssh_channel.send(command)

        output = ""
        time.sleep(0.5)  # 给命令足够时间执行
        while ssh_channel.recv_ready():
            part = ssh_channel.recv(4096).decode('utf-8')
            output += part

        # 过滤掉输入命令行的回显部分，只显示命令执行的输出
        command_echo = command.strip()  # 移除命令行回显
        filtered_output = output.replace(command_echo, '', 1).strip()

        # 发送过滤后的输出
        emit('response', {'result': filtered_output})
    else:
        emit('response', {'result': 'SSH channel not established'})

# 主机存活状态探测
def is_host_alive(ip_address):
    response = os.system(f"ping -c 1 {ip_address}")
    return response == 0
@app.route('/alive_hosts', methods=['GET'])
def alive_hosts():
    alive_hosts_list = []
    
    # 从数据库获取主机 IP 地址
    hosts = get_hosts()  # 这应该返回一个 (IPADDR, USERNAME) 的列表

    for host in hosts:
        ip_address = host[0]  # 假设 host[0] 是 IP 地址
        if is_host_alive(ip_address):
            alive_hosts_list.append({'ip': ip_address, 'status': 'Online'})
        else:
            alive_hosts_list.append({'ip': ip_address, 'status': 'Offline'})

    return jsonify(alive_hosts_list)


# 添加主机到数据库中
@app.route('/add_host', methods=['GET'])
def add_host_page():
    return render_template('add_host.html')

# 处理表单提交，将主机信息插入数据库
@app.route('/add_host', methods=['POST'])
def add_host():
    ip_address = request.form['ip']
    username = request.form['username']
    password = request.form['password']

    # 插入主机信息到数据库
    if insert_host((ip_address, username, password)):
        return redirect(url_for('index'))  # 插入成功后返回首页
    else:
        return "Failed to add host."

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0',port=5000, debug=True,allow_unsafe_werkzeug=True)
