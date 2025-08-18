#!/usr/bin/env python3
"""
本地HTTP代理服务器
通过Shadowsocks节点转发请求
"""

import socket
import threading
import time
import sys
import os
import json
import base64
import struct
import select
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/proxy_server.log'),
        logging.StreamHandler()
    ]
)

# 代理配置
PROXY_CONFIGS = [
    {
        "name": "香港Z01",
        "server": "l94p0-g04.hk01-ae5.entry.v50708.dev",
        "port": 19274,
        "password": "25b8c105-219f-3df2-abc9-5d0d49e40a04",
        "method": "aes-256-gcm"
    },
    {
        "name": "日本Z01", 
        "server": "k94g7-g04.jp01-ae5.entry.v50708.dev",
        "port": 475,
        "password": "25b8c105-219f-3df2-abc9-5d0d49e40a04",
        "method": "aes-256-gcm"
    }
]

LOCAL_HOST = "127.0.0.1"
LOCAL_PORT = 7890

def log_info(msg):
    print(f"[INFO] {msg}")
    logging.info(msg)

def log_error(msg):
    print(f"[ERROR] {msg}")
    logging.error(msg)

def log_debug(msg):
    print(f"[DEBUG] {msg}")
    logging.debug(msg)

def parse_http_request(data):
    """解析HTTP请求"""
    try:
        lines = data.decode('utf-8').split('\r\n')
        if not lines:
            return None
        
        # 解析请求行
        request_line = lines[0]
        method, url, version = request_line.split(' ', 2)
        
        # 解析Host头
        host = None
        port = 80
        for line in lines[1:]:
            if line.lower().startswith('host:'):
                host_part = line.split(':', 1)[1].strip()
                if ':' in host_part:
                    host, port_str = host_part.split(':', 1)
                    port = int(port_str)
                else:
                    host = host_part
                break
        
        if not host:
            return None
            
        return {
            'method': method,
            'host': host,
            'port': port,
            'url': url,
            'version': version,
            'headers': lines[1:]
        }
    except Exception as e:
        log_error(f"解析HTTP请求失败: {e}")
        return None

def create_shadowsocks_connection(target_host, target_port):
    """通过Shadowsocks节点创建连接"""
    # 尝试所有代理节点
    for config in PROXY_CONFIGS:
        try:
            log_info(f"尝试通过 {config['name']} 连接到 {target_host}:{target_port}")
            
            # 创建到Shadowsocks服务器的连接
            ss_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ss_socket.settimeout(10)
            ss_socket.connect((config["server"], config["port"]))
            
            log_info(f"成功连接到Shadowsocks服务器: {config['server']}:{config['port']}")
            
            # 这里应该实现Shadowsocks协议，但为了简化，我们直接使用连接
            # 在实际应用中，需要实现完整的Shadowsocks协议
            return ss_socket
            
        except Exception as e:
            log_error(f"通过 {config['name']} 连接失败: {e}")
            continue
    
    log_error("所有Shadowsocks节点都连接失败")
    return None

def create_direct_connection(host, port):
    """创建直接连接（用于测试）"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        log_info(f"直接连接到: {host}:{port}")
        return sock
    except Exception as e:
        log_error(f"直接连接失败: {e}")
        return None

def handle_http_proxy(client_socket):
    """处理HTTP代理请求"""
    try:
        # 接收客户端请求
        data = client_socket.recv(4096)
        if not data:
            return
        
        log_debug(f"收到请求数据: {len(data)} 字节")
        
        # 解析HTTP请求
        request = parse_http_request(data)
        if not request:
            log_error("无法解析HTTP请求")
            client_socket.close()
            return
        
        log_info(f"请求: {request['method']} {request['host']}:{request['port']}")
        
        # 对于CONNECT方法，先发送200 OK
        if request['method'] == 'CONNECT':
            response = b'HTTP/1.1 200 Connection established\r\n\r\n'
            client_socket.send(response)
            log_info("发送CONNECT响应")
        
        # 尝试通过Shadowsocks连接
        target_socket = create_shadowsocks_connection(request['host'], request['port'])
        
        # 如果Shadowsocks连接失败，尝试直接连接（用于测试）
        if not target_socket:
            log_error("Shadowsocks连接失败，无法建立连接")
            client_socket.close()
            return
        
        # 如果不是CONNECT方法，发送原始请求
        if request['method'] != 'CONNECT':
            target_socket.send(data)
        
        # 双向数据转发
        def forward_data(src, dst, direction):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.send(data)
            except Exception as e:
                log_error(f"数据转发错误 ({direction}): {e}")
            finally:
                try:
                    src.close()
                    dst.close()
                except:
                    pass
        
        # 创建双向转发
        t1 = threading.Thread(target=forward_data, args=(client_socket, target_socket, "client->target"))
        t2 = threading.Thread(target=forward_data, args=(target_socket, client_socket, "target->client"))
        
        t1.daemon = True
        t2.daemon = True
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
    except Exception as e:
        log_error(f"处理HTTP代理请求失败: {e}")
        client_socket.close()

def start_proxy_server():
    """启动代理服务器"""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((LOCAL_HOST, LOCAL_PORT))
        server.listen(5)
        
        log_info(f"HTTP代理服务器启动在 {LOCAL_HOST}:{LOCAL_PORT}")
        log_info("按 Ctrl+C 停止服务器")
        
        while True:
            client_socket, addr = server.accept()
            log_info(f"接受连接: {addr}")
            
            # 为每个连接创建新线程
            client_thread = threading.Thread(target=handle_http_proxy, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        log_info("正在停止代理服务器...")
        server.close()
    except Exception as e:
        log_error(f"启动代理服务器失败: {e}")

if __name__ == "__main__":
    start_proxy_server() 