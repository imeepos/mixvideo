#!/usr/bin/env python3
"""
诊断Cloudflare AI Gateway配置问题
"""

import requests
import json
from config import get_config


def diagnose_gateway_config():
    """诊断Gateway配置问题"""
    print("🔍 诊断Cloudflare AI Gateway配置")
    print("=" * 50)
    
    config = get_config()
    gemini_config = config.gemini
    
    print("📋 当前配置:")
    print(f"  - Cloudflare项目ID: {gemini_config.cloudflare_project_id}")
    print(f"  - Cloudflare Gateway ID: {gemini_config.cloudflare_gateway_id}")
    print(f"  - Google项目ID: {gemini_config.google_project_id}")
    print(f"  - 模型: {gemini_config.model_name}")
    
    # 构建Gateway URL
    region = "us-central1"  # 使用固定区域进行测试
    gateway_url = (
        f"https://gateway.ai.cloudflare.com/v1/"
        f"{gemini_config.cloudflare_project_id}/"
        f"{gemini_config.cloudflare_gateway_id}/"
        f"google-vertex-ai/v1/projects/"
        f"{gemini_config.google_project_id}/"
        f"locations/{region}/publishers/google/models"
    )
    
    print(f"\n🌐 构建的Gateway URL:")
    print(f"  {gateway_url}")
    
    # 测试Gateway可达性
    print(f"\n🔗 测试Gateway可达性...")
    
    try:
        # 获取访问令牌
        print("🔑 获取访问令牌...")
        headers = {
            "Authorization": f"Bearer {gemini_config.bearer_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{gemini_config.base_url}/google/access-token",
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 获取访问令牌失败: {response.status_code}")
            return False
        
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"✅ 访问令牌获取成功")
        
        # 测试Gateway端点
        print(f"\n📡 测试Gateway端点...")
        generate_url = f"{gateway_url}/{gemini_config.model_name}:generateContent"
        print(f"  完整URL: {generate_url}")
        
        # 构建测试请求 - 添加缺少的role字段
        test_payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "Hello, this is a test message."
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 100
            }
        }
        
        gateway_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        print(f"📤 发送测试请求...")
        response = requests.post(
            generate_url,
            headers=gateway_headers,
            json=test_payload,
            timeout=30
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"✅ Gateway测试成功!")
            result = response.json()
            print(f"📄 响应内容: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"❌ Gateway测试失败: {response.status_code}")
            print(f"📄 错误响应: {response.text}")
            
            # 分析错误
            try:
                error_data = response.json()
                if "error" in error_data:
                    errors = error_data["error"]
                    for error in errors:
                        code = error.get("code", "unknown")
                        message = error.get("message", "unknown")
                        print(f"🔍 错误分析:")
                        print(f"  - 错误代码: {code}")
                        print(f"  - 错误信息: {message}")
                        
                        if code == 2001:
                            print(f"💡 解决建议:")
                            print(f"  1. 检查Cloudflare控制台中的AI Gateway配置")
                            print(f"  2. 确认Gateway ID '{gemini_config.cloudflare_gateway_id}' 存在")
                            print(f"  3. 确认项目ID '{gemini_config.cloudflare_project_id}' 正确")
                            print(f"  4. 确认Gateway已启用Google Vertex AI集成")
                            
            except:
                pass
            
            return False
            
    except Exception as e:
        print(f"❌ 诊断过程出错: {e}")
        return False


def check_cloudflare_dashboard_access():
    """检查Cloudflare控制台访问"""
    print(f"\n🌐 Cloudflare控制台访问指南")
    print("=" * 30)
    
    config = get_config()
    gemini_config = config.gemini
    
    dashboard_url = f"https://dash.cloudflare.com/{gemini_config.cloudflare_project_id}/ai/ai-gateway"
    
    print(f"📋 请访问以下URL检查AI Gateway配置:")
    print(f"  {dashboard_url}")
    
    print(f"\n✅ 需要确认的配置项:")
    print(f"  1. AI Gateway是否已创建")
    print(f"  2. Gateway名称是否为: {gemini_config.cloudflare_gateway_id}")
    print(f"  3. 是否已添加Google Vertex AI端点")
    print(f"  4. 端点配置是否正确")
    
    print(f"\n🔧 如果Gateway不存在，请:")
    print(f"  1. 在Cloudflare控制台创建新的AI Gateway")
    print(f"  2. 设置Gateway名称为: {gemini_config.cloudflare_gateway_id}")
    print(f"  3. 添加Google Vertex AI作为上游端点")
    print(f"  4. 配置正确的项目ID和区域")


def suggest_alternative_configs():
    """建议替代配置"""
    print(f"\n🔄 替代配置建议")
    print("=" * 20)
    
    print(f"如果当前Gateway配置有问题，可以尝试:")
    
    print(f"\n1. 使用不同的Gateway ID:")
    print(f"   cloudflare_gateway_id: 'gemini-gateway'")
    print(f"   cloudflare_gateway_id: 'ai-gateway'")
    print(f"   cloudflare_gateway_id: 'video-analysis'")
    
    print(f"\n2. 检查项目ID格式:")
    print(f"   - 确保是32位十六进制字符串")
    print(f"   - 不包含连字符或其他字符")
    
    print(f"\n3. 验证Google项目ID:")
    print(f"   - 确保Google Cloud项目存在")
    print(f"   - 确保已启用Vertex AI API")
    print(f"   - 确保项目ID格式正确")


def main():
    """主函数"""
    try:
        success = diagnose_gateway_config()
        
        if not success:
            check_cloudflare_dashboard_access()
            suggest_alternative_configs()
        
        print(f"\n🎯 诊断完成")
        
    except Exception as e:
        print(f"❌ 诊断失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
