#!/bin/bash

# 直接推送脚本
# 使用你的代理配置直接推送代码到GitHub

# 代理配置
PROXY_HOST="l94p0-g04.hk01-ae5.entry.v50708.dev"
PROXY_PORT="19274"

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

# 测试代理连接
test_proxy_connection() {
    log_info "测试代理连接..."
    
    if timeout 5 bash -c "</dev/tcp/$PROXY_HOST/$PROXY_PORT" 2>/dev/null; then
        log_info "代理节点可用: $PROXY_HOST:$PROXY_PORT"
        return 0
    else
        log_error "代理节点不可用: $PROXY_HOST:$PROXY_PORT"
        return 1
    fi
}

# 推送代码
push_code() {
    log_info "正在推送代码到GitHub..."
    
    # 测试代理连接
    if ! test_proxy_connection; then
        log_error "代理连接失败"
        return 1
    fi
    
    # 设置Git代理 - 尝试SOCKS5
    git config --global http.proxy "socks5://$PROXY_HOST:$PROXY_PORT"
    git config --global https.proxy "socks5://$PROXY_HOST:$PROXY_PORT"
    
    log_info "Git代理已设置: socks5://$PROXY_HOST:$PROXY_PORT"
    
    # 推送代码
    if git push; then
        log_info "代码推送成功！"
        
        # 清除Git代理
        git config --global --unset http.proxy
        git config --global --unset https.proxy
        log_info "Git代理已清除"
        
        return 0
    else
        log_error "代码推送失败！"
        
        # 清除Git代理
        git config --global --unset http.proxy
        git config --global --unset https.proxy
        log_info "Git代理已清除"
        
        return 1
    fi
}

# 显示状态
show_status() {
    echo "=== 代理状态 ==="
    if test_proxy_connection; then
        log_info "代理节点可用"
    else
        log_error "代理节点不可用"
    fi
    
    echo ""
    echo "=== Git代理配置 ==="
    git config --global --get http.proxy
    git config --global --get https.proxy
}

# 主函数
main() {
    case "$1" in
        "push")
            push_code
            ;;
        "status")
            show_status
            ;;
        "test")
            test_proxy_connection
            ;;
        *)
            echo "使用方法: $0 [push|status|test]"
            echo ""
            echo "命令说明:"
            echo "  push   - 推送代码到GitHub"
            echo "  status - 显示当前状态"
            echo "  test   - 测试代理连接"
            ;;
    esac
}

# 执行主函数
main "$@" 