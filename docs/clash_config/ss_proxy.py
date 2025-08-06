#!/usr/bin/env python3
"""
优化的Shadowsocks客户端实现
基于你的Clash配置文件
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
import hashlib
import hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/ss_proxy.log'),
        logging.StreamHandler()
    ]
)

# Shadowsocks配置
SS_CONFIGS = [
    {
        "name": "🇭🇰 香港Z01",
        "server": "y3apx-g04.hk01-ae5.entry.v50708.dev",
        "port": 19274,
        "password": "25b8c105-219f-3df2-abc9-5d0d49e40a04",
        "method": "aes-256-gcm"
    },
    {
        "name": "🇯🇵 日本Z01",
        "server": "6jdxn-g04.jp01-ae5.entry.v50708.dev",
        "port": 475,
        "password": "25b8c105-219f-3df2-abc9-5d0d49e40a04",
        "method": "aes-256-gcm"
    },
    {
        "name": "🇭🇰 香港Z02",
        "server": "tb3k2-g04.hk02-ae5.entry.v50708.dev",
        "port": 14562,
        "password": "25b8c105-219f-3df2-abc9-5d0d49e40a04",
        "method": "aes-256-gcm"
    },
    {
        "name": "🇯🇵 日本Z02",
        "server": "y0iob-g04.jp02-ae5.entry.v50708.dev",
        "port": 485,
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

class ShadowsocksClient:
    def __init__(self, config):
        self.config = config
        self.key = self._generate_key()
        
    def _generate_key(self):
        """生成加密密钥"""
        return hashlib.md5(self.config['password'].encode()).digest()
    
    def _encrypt(self, data):
        """加密数据"""
        try:
            # 生成随机IV
            iv = os.urandom(12)
            
            # 创建加密器
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # 加密数据
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # 返回IV + 密文 + 认证标签
            return iv + ciphertext + encryptor.tag
        except Exception as e:
            log_error(f"加密失败: {e}")
            return None
    
    def _decrypt(self, data):
        """解密数据"""
        try:
            if len(data) < 28:  # IV(12) + 最小密文(16)
                return None
                
            iv = data[:12]
            tag = data[-16:]
            ciphertext = data[12:-16]
            
            # 创建解密器
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # 解密数据
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext
        except Exception as e:
            log_error(f"解密失败: {e}")
            return None
    
    def _create_shadowsocks_header(self, addr_type, addr, port):
        """创建Shadowsocks请求头"""
        if addr_type == 1:  # IPv4
            addr_bytes = socket.inet_aton(addr)
            header = struct.pack('!B4sH', 1, addr_bytes, port)
        elif addr_type == 3:  # Domain
            addr_bytes = addr.encode()
            header = struct.pack('!BB', 3, len(addr_bytes)) + addr_bytes + struct.pack('!H', port)
        elif addr_type == 4:  # IPv6
            addr_bytes = socket.inet_pton(socket.AF_INET6, addr)
            header = struct.pack('!B16sH', 4, addr_bytes, port)
        else:
            return None
        return header
    
    def connect_to_target(self, target_host, target_port):
        """通过Shadowsocks连接到目标服务器"""
        try:
            # 连接到Shadowsocks服务器
            ss_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ss_socket.settimeout(10)
            ss_socket.connect((self.config['server'], self.config['port']))
            
            log_info(f"连接到Shadowsocks服务器: {self.config['name']}")
            
            # 解析目标地址
            try:
                # 尝试解析为IP地址
                ip = socket.gethostbyname(target_host)
                addr_type = 1  # IPv4
                addr = ip
            except:
                addr_type = 3  # Domain
                addr = target_host
            
            # 创建请求头
            header = self._create_shadowsocks_header(addr_type, addr, target_port)
            if not header:
                log_error("创建请求头失败")
                ss_socket.close()
                return None
            
            # 加密并发送请求
            encrypted_header = self._encrypt(header)
            if not encrypted_header:
                log_error("加密请求头失败")
                ss_socket.close()
                return None
            
            ss_socket.send(encrypted_header)
            log_info(f"发送请求到: {target_host}:{target_port}")
            
            return ss_socket
            
        except Exception as e:
            log_error(f"连接Shadowsocks服务器失败: {e}")
            return None
    
    def handle_connection(self, client_socket):
        """处理客户端连接"""
        ss_socket = None
        try:
            # 接收客户端数据
            data = client_socket.recv(4096)
            if not data:
                return
            
            # 解析HTTP请求
            request = self._parse_http_request(data)
            if not request:
                log_error("无法解析HTTP请求")
                client_socket.close()
                return
            
            log_info(f"请求: {request['method']} {request['host']}:{request['port']}")
            
            # 通过Shadowsocks连接目标
            ss_socket = self.connect_to_target(request['host'], request['port'])
            if not ss_socket:
                client_socket.close()
                return
            
            # 对于CONNECT方法，发送200 OK
            if request['method'] == 'CONNECT':
                response = b'HTTP/1.1 200 Connection established\r\n\r\n'
                client_socket.send(response)
                log_info("发送CONNECT响应")
            
            # 如果不是CONNECT方法，发送原始请求
            if request['method'] != 'CONNECT':
                encrypted_data = self._encrypt(data)
                if encrypted_data:
                    ss_socket.send(encrypted_data)
            
            # 双向数据转发
            def forward_data(src, dst, direction, encrypt=False):
                try:
                    while True:
                        # 设置超时
                        src.settimeout(30)
                        data = src.recv(4096)
                        if not data:
                            break
                        
                        if encrypt:
                            encrypted = self._encrypt(data)
                            if encrypted:
                                dst.send(encrypted)
                        else:
                            decrypted = self._decrypt(data)
                            if decrypted:
                                dst.send(decrypted)
                except socket.timeout:
                    log_error(f"数据转发超时 ({direction})")
                except Exception as e:
                    log_error(f"数据转发错误 ({direction}): {e}")
                finally:
                    try:
                        if not src._closed:
                            src.close()
                        if not dst._closed:
                            dst.close()
                    except:
                        pass
            
            # 创建双向转发
            t1 = threading.Thread(target=forward_data, args=(client_socket, ss_socket, "client->ss", True))
            t2 = threading.Thread(target=forward_data, args=(ss_socket, client_socket, "ss->client", False))
            
            t1.daemon = True
            t2.daemon = True
            
            t1.start()
            t2.start()
            
            # 设置超时等待
            t1.join(timeout=60)
            t2.join(timeout=60)
            
        except Exception as e:
            log_error(f"处理连接失败: {e}")
        finally:
            try:
                if client_socket and not client_socket._closed:
                    client_socket.close()
                if ss_socket and not ss_socket._closed:
                    ss_socket.close()
            except:
                pass
    
    def _parse_http_request(self, data):
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

def start_proxy_server():
    """启动代理服务器"""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((LOCAL_HOST, LOCAL_PORT))
        server.listen(5)
        
        log_info(f"Shadowsocks代理服务器启动在 {LOCAL_HOST}:{LOCAL_PORT}")
        log_info("按 Ctrl+C 停止服务器")
        
        # 创建Shadowsocks客户端
        ss_client = ShadowsocksClient(SS_CONFIGS[0])  # 使用第一个节点
        
        while True:
            client_socket, addr = server.accept()
            log_info(f"接受连接: {addr}")
            
            # 为每个连接创建新线程
            client_thread = threading.Thread(target=ss_client.handle_connection, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        log_info("正在停止代理服务器...")
        server.close()
    except Exception as e:
        log_error(f"启动代理服务器失败: {e}")

if __name__ == "__main__":
    start_proxy_server() 