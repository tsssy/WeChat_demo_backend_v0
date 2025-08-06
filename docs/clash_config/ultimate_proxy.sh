#!/bin/bash

# 最终代理管理脚本
# 使用方法: ./ultimate_proxy.sh [start|stop|push|status]

PROXY_SERVER="ss_proxy.py"
PROXY_PID_FILE="/tmp/ss_proxy.pid"
PROXY_PORT="7890"

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

# 检查代理服务器是否运行
check_proxy_running() {
    if [ -f "$PROXY_PID_FILE" ]; then
        local pid=$(cat "$PROXY_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PROXY_PID_FILE"
        fi
    fi
    return 1
}

# 启动代理服务器
start_proxy_server() {
    log_info "正在启动Shadowsocks代理服务器..."
    
    if check_proxy_running; then
        log_warn "代理服务器已在运行"
        return 0
    fi
    
    if [ ! -f "$PROXY_SERVER" ]; then
        log_error "代理服务器文件不存在: $PROXY_SERVER"
        return 1
    fi
    
    # 启动代理服务器
    nohup python3 "$PROXY_SERVER" > /tmp/ss_proxy.log 2>&1 &
    local pid=$!
    echo "$pid" > "$PROXY_PID_FILE"
    
    sleep 3
    
    if check_proxy_running; then
        log_info "代理服务器启动成功 (PID: $pid)"
        return 0
    else
        log_error "代理服务器启动失败"
        return 1
    fi
}

# 停止代理服务器
stop_proxy_server() {
    log_info "正在停止代理服务器..."
    
    if [ -f "$PROXY_PID_FILE" ]; then
        local pid=$(cat "$PROXY_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            kill "$pid"
            log_info "已停止代理服务器 (PID: $pid)"
        else
            log_warn "代理服务器未运行"
        fi
        rm -f "$PROXY_PID_FILE"
    else
        log_warn "未找到PID文件"
    fi
}

# 启动代理
start_proxy() {
    log_info "正在启动代理..."
    
    # 启动代理服务器
    if ! start_proxy_server; then
        log_error "无法启动代理服务器"
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
    
    # 停止代理服务器
    stop_proxy_server
    
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
    
    # 确保代理已启动
    if ! check_proxy_running; then
        log_warn "代理未启动，正在启动代理..."
        if ! start_proxy; then
            log_error "无法启动代理"
            return 1
        fi
    fi
    
    # 设置环境变量
    export http_proxy="http://127.0.0.1:$PROXY_PORT"
    export https_proxy="http://127.0.0.1:$PROXY_PORT"
    
    # 测试网络连接
    if ! test_connection; then
        log_error "网络连接测试失败"
        return 1
    fi
    
    # 推送代码
    if git push; then
        log_info "代码推送成功！"
    else
        log_error "代码推送失败！"
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
    echo "=== 代理服务器状态 ==="
    if check_proxy_running; then
        local pid=$(cat "$PROXY_PID_FILE")
        log_info "代理服务器正在运行 (PID: $pid)"
    else
        log_warn "代理服务器未运行"
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

# 显示日志
show_logs() {
    if [ -f "/tmp/ss_proxy.log" ]; then
        echo "=== 代理服务器日志 ==="
        tail -20 /tmp/ss_proxy.log
    else
        log_warn "未找到日志文件"
    fi
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
        "logs")
            show_logs
            ;;
        "restart")
            stop_proxy
            sleep 2
            start_proxy
            ;;
        *)
            echo "使用方法: $0 [start|stop|push|status|test|logs|restart]"
            echo ""
            echo "命令说明:"
            echo "  start   - 启动代理"
            echo "  stop    - 停止代理"
            echo "  push    - 推送代码到GitHub"
            echo "  status  - 显示当前状态"
            echo "  test    - 测试网络连接"
            echo "  logs    - 显示日志"
            echo "  restart - 重启代理"
            ;;
    esac
}

# 执行主函数
main "$@" 