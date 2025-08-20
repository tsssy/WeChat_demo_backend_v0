# 配置目录说明

## 📁 目录结构

```
config/
├── README.md                    # 本文件
├── nginx_config_new.conf        # Nginx配置文件
├── requirements_pip.txt         # pip依赖列表
└── requirements_conda.txt       # conda依赖列表
```

## 🔧 配置文件说明

### 1. Nginx配置
- **文件**: `nginx_config_new.conf`
- **用途**: Nginx反向代理和负载均衡配置
- **特点**: 支持HTTP/HTTPS、WebSocket、静态文件服务

### 2. 依赖管理
- **requirements_pip.txt**: pip包管理器依赖列表
- **requirements_conda.txt**: conda包管理器依赖列表
- **requirements.txt**: 主依赖文件（项目根目录）

## 🚀 使用说明

### Nginx配置
```bash
# 复制配置文件到Nginx目录
sudo cp config/nginx_config_new.conf /etc/nginx/sites-available/wechat_demo

# 创建软链接
sudo ln -s /etc/nginx/sites-available/wechat_demo /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 依赖安装
```bash
# 使用pip安装
pip install -r config/requirements_pip.txt

# 使用conda安装
conda install --file config/requirements_conda.txt
```

## 📝 配置模板

### 环境变量配置
创建 `.env` 文件：
```bash
# 数据库配置
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=wechat_demo

# AI服务配置
GEMINI_API_KEY=your_gemini_api_key
KIMI_API_KEY=your_kimi_api_key

# 语音转文字配置
WHISPER_MODEL_SIZE=base
WHISPER_DEVICE=cpu
MAX_AUDIO_FILE_SIZE=52428800
SUPPORTED_AUDIO_FORMATS=mp3,wav,m4a,flac,ogg,aac,mp4,webm

# 服务配置
CURRENT_AI_SERVICE=gemini
```

## 🔒 安全配置

### HTTPS配置
```bash
# 生成SSL证书
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# 配置SSL
ssl_certificate /path/to/cert.pem;
ssl_certificate_key /path/to/key.pem;
```

### 防火墙配置
```bash
# 开放必要端口
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 8000/tcp # 后端API
sudo ufw allow 5173/tcp # 前端开发服务器
```

## 📊 性能优化

### Nginx优化
```nginx
# 启用gzip压缩
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# 静态文件缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 后端优化
```bash
# 调整工作进程数
workers = (2 * num_cores) + 1

# 启用异步处理
async def process_request():
    # 异步处理逻辑
    pass
```

## 🐛 故障排除

### 常见问题

#### 1. Nginx配置错误
```bash
# 检查配置语法
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

#### 2. 依赖冲突
```bash
# 清理pip缓存
pip cache purge

# 重新安装依赖
pip install --force-reinstall -r requirements.txt
```

#### 3. 权限问题
```bash
# 检查文件权限
ls -la config/

# 修复权限
chmod 644 config/*.conf
```

## 📚 相关文档

- [Nginx官方文档](https://nginx.org/en/docs/)
- [FastAPI部署指南](https://fastapi.tiangolo.com/deployment/)
- [MongoDB配置参考](https://docs.mongodb.com/manual/reference/configuration-options/)

---

**最后更新**: 2025年8月19日
**维护者**: 开发团队
