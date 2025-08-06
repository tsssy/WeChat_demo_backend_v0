#!/bin/bash

# 服务器端代理管理脚本
# 使用SSH隧道转发的本地代理

PROXY_PORT="7891"  # SSH隧道转发的代理端口

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 检查SSH隧道代理是否可用
check_tunnel_proxy() {
    log_info "检查SSH隧道代理..."
    
    if netstat -tlnp | grep ":$PROXY_PORT" > /dev/null 2>&1; then
        log_info "SSH隧道代理可用 (端口: $PROXY_PORT)"
        return 0
    else
        log_error "SSH隧道代理不可用 (端口: $PROXY_PORT)"
        return 1
    fi
}

# 启动代理
start_proxy() {
    log_info "启动代理..."
    
    # 检查SSH隧道代理
    if ! check_tunnel_proxy; then
        log_error "SSH隧道代理不可用，请先在本地启动隧道"
        log_info "在本地运行: ./ssh_tunnel.sh start"
        return 1
    fi
    
    # 设置环境变量
    export http_proxy="http://127.0.0.1:$PROXY_PORT"
    export https_proxy="http://127.0.0.1:$PROXY_PORT"
    
    # 设置Git代理
    git config --global http.proxy "http://127.0.0.1:$PROXY_PORT"
    git config --global https.proxy "http://127.0.0.1:$PROXY_PORT"
    
    log_info "代理已启动"
    log_info "HTTP代理: $http_proxy"
    log_info "HTTPS代理: $https_proxy"
}

# 停止代理
stop_proxy() {
    log_info "正在停止代理..."
    
    # 清除环境变量
    unset http_proxy https_proxy
    
    # 清除Git代理
    git config --global --unset http.proxy
    git config --global --unset https.proxy
    
    log_info "代理已停止"
}

# 推送代码
push_code() {
    log_info "正在推送代码到GitHub..."
    
    # 启动代理
    if ! start_proxy; then
        return 1
    fi
    
    # 测试网络连接
    if ! test_connection; then
        log_error "网络连接测试失败"
        return 1
    fi
    
    # 推送代码
    if git push; then
        log_info "✅ 代码推送成功！"
    else
        log_error "❌ 代码推送失败！"
        return 1
    fi
}

# 测试连接
test_connection() {
    log_info "正在测试网络连接..."
    
    # 设置环境变量用于测试
    export http_proxy="http://127.0.0.1:$PROXY_PORT"
    export https_proxy="http://127.0.0.1:$PROXY_PORT"
    
    if curl -I https://google.com --connect-timeout 10 > /dev/null 2>&1; then
        log_info "网络连接正常"
        return 0
    else
        log_error "网络连接失败"
        return 1
    fi
}

# 显示状态
show_status() {
    echo "=== SSH隧道代理状态 ==="
    if check_tunnel_proxy; then
        log_info "SSH隧道代理正在运行"
    else
        log_warn "SSH隧道代理未运行"
    fi
    
    echo ""
    echo "=== 代理状态 ==="
    if [ -n "$http_proxy" ]; then
        log_info "代理已启动"
        echo "HTTP代理: $http_proxy"
        echo "HTTPS代理: $https_proxy"
    else
        log_warn "代理未启动"
    fi
    
    echo ""
    echo "=== Git代理配置 ==="
    git config --global --get http.proxy
    git config --global --get https.proxy
    
    echo ""
    echo "=== 网络测试 ==="
    if test_connection; then
        log_info "网络连接正常"
    else
        log_error "网络连接失败"
    fi
}

# 显示使用说明
show_help() {
    echo "=== SSH隧道代理使用说明 ==="
    echo ""
    echo "步骤1: 在本地机器上配置代理"
    echo "  - 确保本地代理运行在端口7890"
    echo "  - 修改ssh_tunnel.sh中的服务器IP"
    echo ""
    echo "步骤2: 在本地启动SSH隧道"
    echo "  ./ssh_tunnel.sh start"
    echo ""
    echo "步骤3: 在服务器上使用代理"
    echo "  ./remote_proxy.sh push"
    echo ""
    echo "步骤4: 完成后停止隧道"
    echo "  ./ssh_tunnel.sh stop"
}

# 主函数
main() {
    case "$1" in
        "start")
            start_proxy
            ;;
        "stop")
            stop_proxy
            ;;
        "push")
            push_code
            ;;
        "status")
            show_status
            ;;
        "test")
            test_connection
            ;;
        "help")
            show_help
            ;;
        *)
            echo "使用方法: $0 [start|stop|push|status|test|help]"
            echo ""
            echo "命令说明:"
            echo "  start  - 启动代理"
            echo "  stop   - 停止代理"
            echo "  push   - 推送代码到GitHub"
            echo "  status - 显示当前状态"
            echo "  test   - 测试网络连接"
            echo "  help   - 显示使用说明"
            echo ""
            echo "注意：需要先在本地启动SSH隧道"
            ;;
    esac
}

# 执行主函数
main "$@" 