"""
SSL辅助工具模块
提供多种SSL配置选项来解决豆包API的SSL连接问题
"""

import ssl
import urllib3
import requests
from urllib3.util.ssl_ import create_urllib3_context
from typing import Optional, Dict, Any

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SSLHelper:
    """SSL配置辅助类"""
    
    @staticmethod
    def create_ssl_session(strategy: str = "auto") -> requests.Session:
        """
        创建SSL配置的requests session
        
        Args:
            strategy: SSL策略
                - "auto": 自动选择最佳策略
                - "secure": 标准HTTPS
                - "custom": 自定义SSL上下文
                - "http": HTTP降级
                - "insecure": 最低安全级别
        
        Returns:
            requests.Session: 配置好的session
        """
        session = requests.Session()
        
        if strategy == "secure":
            # 标准HTTPS，使用默认SSL验证
            session.verify = True
        elif strategy == "custom":
            # 自定义SSL上下文
            ssl_context = create_urllib3_context(ciphers='DEFAULT@SECLEVEL=1')
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            adapter = requests.adapters.HTTPAdapter()
            session.mount('https://', adapter)
            session.verify = False
        elif strategy == "http":
            # HTTP降级，不使用SSL
            session.verify = False
        elif strategy == "insecure":
            # 最低安全级别
            session.verify = False
        else:  # auto
            # 自动选择：先尝试自定义SSL上下文
            ssl_context = create_urllib3_context(ciphers='DEFAULT@SECLEVEL=1')
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            adapter = requests.adapters.HTTPAdapter()
            session.mount('https://', adapter)
            session.verify = False
        
        return session
    
    @staticmethod
    def get_ssl_strategies() -> list:
        """
        获取所有可用的SSL策略
        
        Returns:
            list: SSL策略列表
        """
        return [
            {
                "name": "标准HTTPS（推荐）",
                "strategy": "secure",
                "url_transform": lambda url: url,
                "verify": True
            },
            {
                "name": "自定义SSL上下文",
                "strategy": "custom", 
                "url_transform": lambda url: url,
                "verify": False
            },
            {
                "name": "HTTP降级",
                "strategy": "http",
                "url_transform": lambda url: url.replace("https://", "http://"),
                "verify": False
            },
            {
                "name": "最低安全级别",
                "strategy": "insecure",
                "url_transform": lambda url: url,
                "verify": False
            }
        ]
    
    @staticmethod
    def test_ssl_connection(url: str, headers: Dict[str, str], data: Dict[str, Any], 
                           timeout: int = 30) -> tuple[bool, Optional[Dict], str]:
        """
        测试SSL连接
        
        Args:
            url: API URL
            headers: 请求头
            data: 请求数据
            timeout: 超时时间
            
        Returns:
            tuple: (是否成功, 响应数据, 使用的策略名称)
        """
        strategies = SSLHelper.get_ssl_strategies()
        
        for strategy in strategies:
            try:
                session = SSLHelper.create_ssl_session(strategy["strategy"])
                test_url = strategy["url_transform"](url)
                
                response = session.post(
                    test_url,
                    json=data,
                    headers=headers,
                    timeout=timeout,
                    verify=strategy["verify"]
                )
                
                if response.status_code == 200:
                    return True, response.json(), strategy["name"]
                else:
                    print(f"策略 {strategy['name']} 返回状态码: {response.status_code}")
                    
            except Exception as e:
                print(f"策略 {strategy['name']} 失败: {str(e)}")
                continue
        
        return False, None, "所有策略都失败"
    
    @staticmethod
    def get_best_ssl_config() -> Dict[str, Any]:
        """
        获取最佳的SSL配置
        
        Returns:
            Dict: 最佳SSL配置
        """
        # 根据经验，自定义SSL上下文通常是最佳选择
        return {
            "strategy": "custom",
            "verify": False,
            "description": "自定义SSL上下文，兼容性最好"
        }

def create_doubao_session() -> requests.Session:
    """
    创建专门用于豆包API的requests session
    
    Returns:
        requests.Session: 配置好的session
    """
    return SSLHelper.create_ssl_session("custom")

def test_doubao_ssl():
    """测试豆包API的SSL连接"""
    api_key = "1e65c3d6-b827-4706-9fa8-93732bed0a8a"
    api_url = "https://api.doubao.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    data = {
        "model": "doubao-seed-1.6-250615",
        "messages": [
            {
                "role": "system", 
                "content": "你是一个专业的AI助手。"
            },
            {
                "role": "user",
                "content": "你好"
            }
        ],
        "temperature": 0.7,
        "stream": False
    }
    
    print("🧪 测试豆包API SSL连接...")
    success, response, strategy = SSLHelper.test_ssl_connection(api_url, headers, data)
    
    if success:
        print(f"✅ 连接成功！使用策略: {strategy}")
        print(f"📄 响应: {response}")
        return True
    else:
        print(f"❌ 连接失败: {strategy}")
        return False

if __name__ == "__main__":
    test_doubao_ssl() 