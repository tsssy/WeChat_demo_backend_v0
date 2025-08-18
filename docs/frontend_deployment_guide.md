# 🚀 前端部署指南

基于当前后端部署情况：`https://loveluretech.xyz`

## 📋 当前后端状态

### ✅ 已确认的后端配置：
- **后端域名**: `https://loveluretech.xyz`
- **API文档**: `https://loveluretech.xyz/docs`
- **API接口**: `https://loveluretech.xyz/api/v1/*`
- **SSL证书**: ✅ 已配置
- **Nginx代理**: ✅ 正常运行

### 🔍 后端服务架构：
```
用户请求 → https://loveluretech.xyz (443端口)
    ↓
Nginx反向代理
    ↓
localhost:8000 (Python FastAPI后端)
    ↓
MongoDB数据库
```

## 🎯 推荐部署方案

### 方案1: 子路径部署 (推荐，简单快速)

#### 配置方式：
```
前端: https://loveluretech.xyz
后端: https://loveluretech.xyz/api (已存在)
```

#### 优势：
- ✅ 不需要额外域名
- ✅ 不需要额外SSL证书
- ✅ 配置简单
- ✅ 快速部署

#### 部署步骤：

##### 1. 创建前端目录
```bash
# 创建前端部署目录
sudo mkdir -p /var/www/frontend
sudo chown -R www-data:www-data /var/www/frontend
sudo chmod -R 755 /var/www/frontend
```

##### 2. 备份现有配置
```bash
# 备份当前配置
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)
```

##### 3. 修改Nginx配置
```bash
# 编辑Nginx配置
sudo nano /etc/nginx/sites-available/default
```

##### 3. 修改Nginx配置

**重要：** 基于当前后端配置，需要修改现有的Nginx配置，而不是添加新的配置。

**当前配置位置：** `/etc/nginx/sites-available/default`

**修改方案：** 将现有的 `location /` 改为前端静态文件服务，并添加API代理。

**完整配置：**

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name www.loveluretech.xyz loveluretech.xyz;
    return 301 https://$host$request_uri;
}

# Main server configuration for loveluretech.xyz
server {
    listen 443 ssl http2;
    server_name www.loveluretech.xyz loveluretech.xyz;

    ssl_certificate /etc/ssl/aliyun/www.loveluretech.xyz.pem;
    ssl_certificate_key /etc/ssl/aliyun/www.loveluretech.xyz.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # 前端静态文件
    root /var/www/frontend;
    index index.html;

    # 前端路由处理 (SPA应用)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 后端文档
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

##### 4. 测试和重启Nginx
```bash
# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl reload nginx
```

##### 5. 部署前端文件
```bash
# 将构建好的前端文件复制到部署目录
sudo cp -r /path/to/your/frontend/build/* /var/www/frontend/

# 设置权限
sudo chown -R www-data:www-data /var/www/frontend
sudo chmod -R 755 /var/www/frontend
```

**前端部署位置：** `/var/www/frontend/`

**目录结构示例：**
```
/var/www/frontend/
├── index.html          # 主页面
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── assets/
    ├── logo.png
    └── icons/
```

## 🔧 前端配置

### 1. API地址配置
在前端代码中配置API地址：

```javascript
// 开发环境
const API_BASE_URL = 'http://localhost:8000/api/v1';

// 生产环境
const API_BASE_URL = 'https://loveluretech.xyz/api/v1';
```

### 2. 环境变量配置
```javascript
// .env.development
VITE_API_BASE_URL=http://localhost:8000/api/v1

// .env.production
VITE_API_BASE_URL=https://loveluretech.xyz/api/v1
```

### 3. 前端路由配置
确保前端路由与后端API路径不冲突：

```javascript
// 前端路由
const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/dashboard', component: Dashboard },
  // 避免使用 /api/* 路径
];
```

## 🚀 部署脚本

### 自动化部署脚本
```bash
#!/bin/bash
# deploy_frontend.sh

FRONTEND_DIR="/var/www/frontend"
BACKUP_DIR="/var/www/frontend_backup"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份当前版本
if [ -d "$FRONTEND_DIR" ] && [ "$(ls -A "$FRONTEND_DIR")" ]; then
    echo "备份当前版本..."
    sudo cp -r "$FRONTEND_DIR" "$BACKUP_DIR/frontend_$(date +%Y%m%d_%H%M%S)"
fi

# 清理目录
echo "清理部署目录..."
sudo rm -rf "$FRONTEND_DIR"/*

# 复制新文件
echo "部署新文件..."
sudo cp -r ./dist/* "$FRONTEND_DIR/"

# 设置权限
echo "设置权限..."
sudo chown -R www-data:www-data "$FRONTEND_DIR"
sudo chmod -R 755 "$FRONTEND_DIR"

# 重启Nginx
echo "重启Nginx..."
sudo systemctl reload nginx

echo "部署完成！"
echo "访问地址: https://loveluretech.xyz"
```

### 快速部署命令
```bash
# 使用提供的脚本
sudo ./docs/quick_deploy_frontend.sh setup    # 设置环境
sudo ./docs/quick_deploy_frontend.sh deploy /path/to/your/frontend/build  # 部署文件
sudo ./docs/quick_deploy_frontend.sh status   # 查看状态
```

## 🔍 测试和验证

### 1. 测试前端访问
```bash
# 测试前端页面
curl -I https://loveluretech.xyz

# 测试静态资源
curl -I https://loveluretech.xyz/static/js/app.js

# 查看前端页面内容
curl https://loveluretech.xyz
```

### 2. 测试API连接
```bash
# 测试API接口
curl -X GET https://loveluretech.xyz/api/v1/users

# 测试API文档
curl -I https://loveluretech.xyz/docs
```

### 3. 浏览器测试
- 访问 `https://loveluretech.xyz` 查看前端页面
- 检查浏览器控制台是否有API错误
- 测试前端功能是否正常

## 🛠️ 故障排除

### 常见问题

#### 1. 前端页面显示404
```bash
# 检查文件是否存在
ls -la /var/www/frontend/

# 检查index.html是否存在
ls -la /var/www/frontend/index.html

# 检查Nginx配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

#### 2. API请求失败
```bash
# 检查后端服务状态
ps aux | grep python

# 检查8000端口
netstat -tlnp | grep 8000

# 测试本地API
curl http://localhost:8000/api/v1/users
```

#### 3. 静态资源加载失败
```bash
# 检查文件权限
ls -la /var/www/frontend/static/

# 检查Nginx配置中的静态文件路径
grep -r "static" /etc/nginx/sites-available/default
```

### 调试命令
```bash
# 查看Nginx状态
sudo systemctl status nginx

# 查看Nginx配置
sudo nginx -T

# 查看访问日志
sudo tail -f /var/log/nginx/access.log

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

## 📊 性能优化

### 1. 静态资源缓存
```nginx
# 在Nginx配置中添加
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 2. Gzip压缩
```nginx
# 在Nginx配置中添加
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

### 3. 浏览器缓存
```nginx
# 在Nginx配置中添加
location ~* \.(html)$ {
    expires 1h;
    add_header Cache-Control "public, must-revalidate";
}
```

## 🔒 安全配置

### 1. HTTPS强制跳转
```nginx
# 在Nginx配置中添加
server {
    listen 80;
    server_name loveluretech.xyz;
    return 301 https://$host$request_uri;
}
```

### 2. 安全头设置
```nginx
# 在Nginx配置中添加
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## 📈 监控和维护

### 1. 日志监控
```bash
# 创建日志监控脚本
cat > /root/monitor_frontend.sh << 'EOF'
#!/bin/bash
echo "=== 前端部署监控 ==="
echo "时间: $(date)"
echo "Nginx状态: $(systemctl is-active nginx)"
echo "后端状态: $(ps aux | grep python | grep 8000 | wc -l)"
echo "磁盘使用: $(df -h /var/www/frontend)"
echo "内存使用: $(free -h)"
EOF

chmod +x /root/monitor_frontend.sh
```

### 2. 自动备份
```bash
# 创建自动备份脚本
cat > /root/backup_frontend.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/www/frontend_backup"
FRONTEND_DIR="/var/www/frontend"
DATE=$(date +%Y%m%d_%H%M%S)

if [ -d "$FRONTEND_DIR" ]; then
    sudo cp -r "$FRONTEND_DIR" "$BACKUP_DIR/frontend_$DATE"
    echo "备份完成: frontend_$DATE"
fi
EOF

chmod +x /root/backup_frontend.sh
```

## 🎯 部署检查清单

### 部署前检查：
- [ ] 前端代码已构建完成
- [ ] Nginx配置已备份
- [ ] 服务器磁盘空间充足
- [ ] 后端服务正常运行

### 部署后检查：
- [ ] 前端页面正常访问 (`https://loveluretech.xyz`)
- [ ] API接口正常调用 (`https://loveluretech.xyz/api/v1`)
- [ ] 静态资源正常加载
- [ ] HTTPS证书正常
- [ ] 浏览器控制台无错误

### 性能检查：
- [ ] 页面加载速度正常
- [ ] 静态资源缓存生效
- [ ] Gzip压缩生效
- [ ] 移动端适配正常

### 文件位置检查：
- [ ] 前端文件位置：`/var/www/frontend/`
- [ ] Nginx配置位置：`/etc/nginx/sites-available/default`
- [ ] 备份文件位置：`/etc/nginx/sites-available/default.backup.*`

## 📞 技术支持

如果遇到问题，可以：

1. **查看日志**: `/var/log/nginx/error.log`
2. **检查配置**: `sudo nginx -t`
3. **重启服务**: `sudo systemctl reload nginx`
4. **回滚备份**: 从备份目录恢复文件

---

## 📍 实际部署位置

### 前端文件位置：
- **部署目录**: `/var/www/frontend/`
- **主页面**: `/var/www/frontend/index.html`
- **静态资源**: `/var/www/frontend/static/`

### Nginx配置位置：
- **配置文件**: `/etc/nginx/sites-available/default`
- **备份文件**: `/etc/nginx/sites-available/default.backup.*`

### 访问地址：
- **前端页面**: `https://loveluretech.xyz`
- **后端API**: `https://loveluretech.xyz/api/v1/*`
- **API文档**: `https://loveluretech.xyz/docs`

**部署完成后，你的前端将可以通过 `https://loveluretech.xyz` 访问，后端API通过 `https://loveluretech.xyz/api` 访问。** 