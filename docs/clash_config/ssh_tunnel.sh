#!/bin/bash

# SSH反向隧道脚本
# 在本地机器上运行，将本地代理转发到服务器

# 配置 - 已填入你的服务器IP
SERVER_IP="59.110.30.211"
SERVER_USER="root"
LOCAL_PROXY_PORT="7890"  # 本地代理端口
REMOTE_PROXY_PORT="7891"  # 服务器上的代理端口

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

# 启动反向隧道
start_tunnel() {
    log_info "启动SSH反向隧道..."
    
    # 命令：将本地7890端口转发到服务器的7891端口
    ssh -R $REMOTE_PROXY_PORT:127.0.0.1:$LOCAL_PROXY_PORT $SERVER_USER@$SERVER_IP -N
    
    if [ $? -eq 0 ]; then
        log_info "隧道启动成功！"
        log_info "本地代理端口: $LOCAL_PROXY_PORT"
        log_info "服务器代理端口: $REMOTE_PROXY_PORT"
    else
        log_error "隧道启动失败！"
    fi
}

# 停止隧道
stop_tunnel() {
    log_info "停止SSH隧道..."
    pkill -f "ssh.*-R.*$REMOTE_PROXY_PORT"
    log_info "隧道已停止"
}

# 检查隧道状态
check_tunnel() {
    if pgrep -f "ssh.*-R.*$REMOTE_PROXY_PORT" > /dev/null; then
        log_info "隧道正在运行"
        return 0
    else
        log_warn "隧道未运行"
        return 1
    fi
}

# 主函数
main() {
    case "$1" in
        "start")
            start_tunnel
            ;;
        "stop")
            stop_tunnel
            ;;
        "status")
            check_tunnel
            ;;
        *)
            echo "使用方法: $0 [start|stop|status]"
            echo ""
            echo "命令说明:"
            echo "  start  - 启动SSH反向隧道"
            echo "  stop   - 停止SSH隧道"
            echo "  status - 检查隧道状态"
            echo ""
            echo "注意：请在本地机器上运行此脚本"
            echo "需要先配置好本地代理（端口7890）"
            ;;
    esac
}

main "$@" 