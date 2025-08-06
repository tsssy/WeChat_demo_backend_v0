#!/bin/bash

# 🚀 前端快速部署脚本
# 基于当前后端配置: https://loveluretech.xyz

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 配置变量
FRONTEND_DIR="/var/www/frontend"
BACKUP_DIR="/var/www/frontend_backup"
NGINX_CONFIG="/etc/nginx/sites-available/default"
DOMAIN="loveluretech.xyz"

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root权限运行此脚本"
        exit 1
    fi
}

# 检查后端服务状态
check_backend() {
    log_info "检查后端服务状态..."
    
    # 检查后端进程
    if ! ps aux | grep python | grep 8000 > /dev/null; then
        log_error "后端服务未运行，请先启动后端服务"
        exit 1
    fi
    
    # 检查8000端口
    if ! netstat -tlnp | grep ":8000" > /dev/null; then
        log_error "8000端口未监听，后端服务可能有问题"
        exit 1
    fi
    
    log_info "后端服务状态正常"
}

# 创建前端目录
setup_directories() {
    log_info "创建前端部署目录..."
    
    # 创建目录
    mkdir -p "$FRONTEND_DIR"
    mkdir -p "$BACKUP_DIR"
    
    # 设置权限
    chown -R www-data:www-data "$FRONTEND_DIR"
    chmod -R 755 "$FRONTEND_DIR"
    
    log_info "目录创建完成"
}

# 备份当前配置
backup_config() {
    log_info "备份当前Nginx配置..."
    
    if [ -f "$NGINX_CONFIG" ]; then
        cp "$NGINX_CONFIG" "${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
        log_info "配置已备份"
    else
        log_error "未找到Nginx配置文件"
        exit 1
    fi
}

# 更新Nginx配置
update_nginx_config() {
    log_info "更新Nginx配置..."
    
    # 检查是否已存在前端配置
    if grep -q "root /var/www/frontend" "$NGINX_CONFIG"; then
        log_warn "前端配置已存在，跳过配置更新"
        return 0
    fi
    
    # 创建新的完整配置文件
    cat > /tmp/nginx_new_config << 'EOF'
##
# You should look at the following URL's in order to grasp a solid understanding
# of Nginx configuration files in order to fully unleash the power of Nginx.
# https://www.nginx.com/resources/wiki/start/
# https://www.nginx.com/resources/wiki/start/topics/tutorials/config_pitfalls/
# https://wiki.debian.org/Nginx/DirectoryStructure
#
# In most cases, administrators will remove this file from sites-enabled/ and
# leave it as reference inside sites-available where it will continue to be
# updated by the nginx packaging team.
#
# This file will automatically load configuration files provided by other
# applications, such as Drupal or Wordpress. These applications will be made
# available underneath a path with that package name, such as /drupal8.
#
# Please see /usr/share/doc/nginx-doc/examples/ for more detailed examples.
##

# Default server configuration
#
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        root /var/www/html;

        index index.html index.htm index.nginx-debian.html;

        server_name _;

        location / {
                try_files $uri $uri/ =404;
        }
}

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
EOF

    # 替换现有配置
    sudo cp /tmp/nginx_new_config "$NGINX_CONFIG"
    
    log_info "Nginx配置已更新"
}

# 测试Nginx配置
test_nginx_config() {
    log_info "测试Nginx配置..."
    
    if nginx -t; then
        log_info "Nginx配置测试通过"
        return 0
    else
        log_error "Nginx配置测试失败"
        return 1
    fi
}

# 重启Nginx
reload_nginx() {
    log_info "重启Nginx服务..."
    
    if systemctl reload nginx; then
        log_info "Nginx重启成功"
        return 0
    else
        log_error "Nginx重启失败"
        return 1
    fi
}

# 部署前端文件
deploy_frontend() {
    local source_dir="$1"
    
    if [ -z "$source_dir" ]; then
        log_error "请指定前端构建文件目录"
        echo "使用方法: $0 deploy <前端构建目录>"
        exit 1
    fi
    
    if [ ! -d "$source_dir" ]; then
        log_error "前端构建目录不存在: $source_dir"
        exit 1
    fi
    
    log_info "开始部署前端文件..."
    
    # 备份当前前端文件
    if [ -d "$FRONTEND_DIR" ] && [ "$(ls -A "$FRONTEND_DIR")" ]; then
        log_info "备份当前前端文件..."
        cp -r "$FRONTEND_DIR" "$BACKUP_DIR/frontend_$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 清理前端目录
    rm -rf "$FRONTEND_DIR"/*
    
    # 复制新的前端文件
    log_info "复制前端文件..."
    cp -r "$source_dir"/* "$FRONTEND_DIR/"
    
    # 设置权限
    chown -R www-data:www-data "$FRONTEND_DIR"
    chmod -R 755 "$FRONTEND_DIR"
    
    log_info "前端文件部署完成"
}

# 测试部署
test_deployment() {
    log_info "测试部署结果..."
    
    # 测试前端页面
    if curl -I "https://$DOMAIN" > /dev/null 2>&1; then
        log_info "前端页面访问正常"
    else
        log_warn "前端页面访问异常"
    fi
    
    # 测试API接口
    if curl -I "https://$DOMAIN/api/v1" > /dev/null 2>&1; then
        log_info "API接口访问正常"
    else
        log_warn "API接口访问异常"
    fi
    
    # 测试API文档
    if curl -I "https://$DOMAIN/docs" > /dev/null 2>&1; then
        log_info "API文档访问正常"
    else
        log_warn "API文档访问异常"
    fi
}

# 显示部署状态
show_status() {
    echo "=== 前端部署状态 ==="
    
    # 检查前端目录
    if [ -d "$FRONTEND_DIR" ]; then
        log_info "前端目录存在: $FRONTEND_DIR"
        echo "文件数量: $(find "$FRONTEND_DIR" -type f | wc -l)"
        if [ -f "$FRONTEND_DIR/index.html" ]; then
            log_info "index.html 文件存在"
        else
            log_warn "index.html 文件不存在"
        fi
    else
        log_warn "前端目录不存在"
    fi
    
    echo ""
    echo "=== Nginx配置状态 ==="
    if grep -q "root /var/www/frontend" "$NGINX_CONFIG"; then
        log_info "前端Nginx配置已存在"
    else
        log_warn "前端Nginx配置不存在"
    fi
    
    echo ""
    echo "=== 服务状态 ==="
    systemctl status nginx --no-pager -l
    
    echo ""
    echo "=== 端口监听状态 ==="
    netstat -tlnp | grep -E ":(80|443)" | head -5
}

# 主函数
main() {
    check_root
    
    case "$1" in
        "setup")
            check_backend
            setup_directories
            backup_config
            update_nginx_config
            if test_nginx_config; then
                reload_nginx
                log_info "前端部署环境设置完成！"
                log_info "下一步: 部署前端文件"
                log_info "命令: $0 deploy <前端构建目录>"
            else
                log_error "Nginx配置测试失败，请检查配置"
            fi
            ;;
        "deploy")
            deploy_frontend "$2"
            test_deployment
            log_info "前端部署完成！"
            log_info "访问地址: https://$DOMAIN"
            ;;
        "status")
            show_status
            ;;
        "test")
            test_deployment
            ;;
        *)
            echo "使用方法: $0 [setup|deploy <目录>|status|test]"
            echo ""
            echo "命令说明:"
            echo "  setup   - 设置前端部署环境"
            echo "  deploy  - 部署前端文件"
            echo "  status  - 显示部署状态"
            echo "  test    - 测试部署结果"
            echo ""
            echo "示例:"
            echo "  $0 setup                    # 设置环境"
            echo "  $0 deploy ./dist           # 部署dist目录中的文件"
            echo "  $0 status                   # 查看状态"
            echo "  $0 test                     # 测试部署"
            ;;
    esac
}

# 执行主函数
main "$@" 