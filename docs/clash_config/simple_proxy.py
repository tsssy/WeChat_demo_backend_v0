#!/usr/bin/env python3
"""
简单代理服务器
直接转发到你的代理节点
"""

import socket
import threading
import time
import sys
import os
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/simple_proxy.log'),
        logging.StreamHandler()
    ]
)

# 代理配置
PROXY_HOST = "y3apx-g04.hk01-ae5.entry.v50708.dev"
PROXY_PORT = 19274

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

def create_proxy_connection():
    """创建到代理服务器的连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((PROXY_HOST, PROXY_PORT))
        log_info(f"连接到代理服务器: {PROXY_HOST}:{PROXY_PORT}")
        return sock
    except Exception as e:
        log_error(f"连接代理服务器失败: {e}")
        return None

def handle_client(client_socket):
    """处理客户端连接"""
    try:
        # 连接到代理服务器
        proxy_socket = create_proxy_connection()
        if not proxy_socket:
            client_socket.close()
            return
        
        # 简单的数据转发
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
        t1 = threading.Thread(target=forward_data, args=(client_socket, proxy_socket, "client->proxy"))
        t2 = threading.Thread(target=forward_data, args=(proxy_socket, client_socket, "proxy->client"))
        
        t1.daemon = True
        t2.daemon = True
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
    except Exception as e:
        log_error(f"处理客户端连接失败: {e}")
        client_socket.close()

def start_proxy_server():
    """启动代理服务器"""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((LOCAL_HOST, LOCAL_PORT))
        server.listen(5)
        
        log_info(f"简单代理服务器启动在 {LOCAL_HOST}:{LOCAL_PORT}")
        log_info("按 Ctrl+C 停止服务器")
        
        while True:
            client_socket, addr = server.accept()
            log_info(f"接受连接: {addr}")
            
            # 为每个连接创建新线程
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        log_info("正在停止代理服务器...")
        server.close()
    except Exception as e:
        log_error(f"启动代理服务器失败: {e}")

if __name__ == "__main__":
    start_proxy_server() 