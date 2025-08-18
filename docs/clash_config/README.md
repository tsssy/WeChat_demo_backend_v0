# 🔧 Clash 代理配置文档

这个文件夹包含了各种代理相关的配置文件和脚本。

## 📚 文件列表

### 代理服务器文件

#### 1. `ss_proxy.py`
- **功能**: Shadowsocks代理服务器
- **端口**: 7890
- **特点**: 支持多个节点、自动切换
- **使用**: `python3 ss_proxy.py`

#### 2. `proxy_server.py`
- **功能**: 通用HTTP代理服务器
- **端口**: 7890
- **特点**: 简单直接、易于调试
- **使用**: `python3 proxy_server.py`

#### 3. `simple_proxy.py`
- **功能**: 简单代理服务器
- **端口**: 7890
- **特点**: 最简实现、学习用
- **使用**: `python3 simple_proxy.py`

### 管理脚本

#### 1. `ultimate_proxy.sh`
- **功能**: 完整的代理管理脚本
- **命令**: `./ultimate_proxy.sh [start|stop|push|status]`
- **特点**: 一键管理、状态监控

#### 2. `remote_proxy.sh`
- **功能**: 服务器端代理管理
- **用途**: 在服务器上管理代理
- **特点**: SSH隧道代理

#### 3. `ssh_tunnel.sh`
- **功能**: SSH反向隧道脚本
- **用途**: 本地代理转发到服务器
- **特点**: 远程代理访问

#### 4. `direct_push.sh`
- **功能**: 直接推送代码脚本
- **用途**: 不使用代理推送代码
- **特点**: 绕过代理

#### 5. `test_push.sh`
- **功能**: 测试推送脚本
- **用途**: 测试代码推送功能
- **特点**: 调试用

## 🎯 使用场景

### 开发环境
```bash
# 启动代理
./ultimate_proxy.sh start

# 推送代码
./ultimate_proxy.sh push

# 查看状态
./ultimate_proxy.sh status
```

### 服务器环境
```bash
# 启动远程代理
./remote_proxy.sh start

# 建立SSH隧道
./ssh_tunnel.sh start
```

### 调试环境
```bash
# 启动简单代理
python3 simple_proxy.py

# 测试推送
./test_push.sh
```

## 🔧 配置说明

### 代理配置
- **本地端口**: 7890
- **协议**: HTTP/SOCKS5
- **节点**: 香港、日本等多个节点
- **加密**: AES-256-GCM

### 网络配置
- **HTTP代理**: `http://127.0.0.1:7890`
- **HTTPS代理**: `http://127.0.0.1:7890`
- **Git代理**: 自动配置

## 💡 注意事项

1. **权限**: 脚本需要执行权限 `chmod +x *.sh`
2. **依赖**: 需要安装Python3和相关库
3. **端口**: 确保7890端口未被占用
4. **防火墙**: 确保端口访问权限

## 🛠️ 故障排除

### 常见问题
1. **代理无法启动**: 检查端口占用
2. **连接失败**: 检查网络配置
3. **推送失败**: 检查代理状态

### 调试命令
```bash
# 检查端口占用
netstat -tlnp | grep 7890

# 检查代理状态
./ultimate_proxy.sh status

# 查看日志
tail -f /tmp/ss_proxy.log
``` 