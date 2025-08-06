#!/bin/bash

# 简化的Git推送测试脚本

PROXY_PORT="7890"

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

# 检查代理服务器是否运行
check_proxy() {
    if netstat -tlnp | grep ":7890" > /dev/null 2>&1; then
        log_info "代理服务器正在运行"
        return 0
    else
        log_error "代理服务器未运行"
        return 1
    fi
}

# 测试推送
test_push() {
    log_info "开始测试Git推送..."
    
    # 检查代理
    if ! check_proxy; then
        return 1
    fi
    
    # 设置代理
    export http_proxy="http://127.0.0.1:$PROXY_PORT"
    export https_proxy="http://127.0.0.1:$PROXY_PORT"
    
    log_info "代理已设置: $http_proxy"
    
    # 设置Git代理
    git config --global http.proxy "http://127.0.0.1:$PROXY_PORT"
    git config --global https.proxy "http://127.0.0.1:$PROXY_PORT"
    
    # 设置超时
    export GIT_HTTP_TIMEOUT=30
    
    log_info "开始推送代码..."
    
    # 使用timeout命令限制执行时间
    if timeout 60 git push; then
        log_info "✅ 代码推送成功！"
        
        # 清除Git代理
        git config --global --unset http.proxy
        git config --global --unset https.proxy
        log_info "Git代理已清除"
        
        return 0
    else
        log_error "❌ 代码推送失败！"
        
        # 清除Git代理
        git config --global --unset http.proxy
        git config --global --unset https.proxy
        log_info "Git代理已清除"
        
        return 1
    fi
}

# 主函数
main() {
    case "$1" in
        "push")
            test_push
            ;;
        "status")
            check_proxy
            ;;
        *)
            echo "使用方法: $0 [push|status]"
            echo ""
            echo "命令说明:"
            echo "  push   - 测试推送代码"
            echo "  status - 检查代理状态"
            ;;
    esac
}

# 执行主函数
main "$@" 