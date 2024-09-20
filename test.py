import time

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
import paramiko
import os
from to_db import get_hosts

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)

sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/terminal')
def terminal():
    return render_template('/connect/terminal.html')

@app.route('/connection')
def connection():
    return render_template('/connect/choose_connect.html',hosts =get_hosts())

# 接收前端命令并执行

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

if __name__ == '__main__':
    socketio.run(app, debug=True,allow_unsafe_werkzeug=True)
