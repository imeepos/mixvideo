#!/usr/bin/env python3
"""
测试Gemini API连接功能
"""

import asyncio
from pathlib import Path


def test_gemini_connection():
    """测试Gemini API连接"""
    print("🔗 测试Gemini API连接")
    print("=" * 50)
    
    try:
        # 加载配置
        print("📋 加载配置...")
        from config import get_config
        config = get_config()
        gemini_config = config.gemini
        
        print(f"✅ 配置加载成功:")
        print(f"  - Cloudflare项目: {gemini_config.cloudflare_project_id}")
        print(f"  - Google项目: {gemini_config.google_project_id}")
        print(f"  - 模型: {gemini_config.model_name}")
        print(f"  - 基础URL: {gemini_config.base_url}")
        print(f"  - Bearer Token: {gemini_config.bearer_token}")
        print(f"  - 区域: {', '.join(gemini_config.regions)}")
        
        # 创建分析器
        print("\n🔧 创建Gemini分析器...")
        from gemini_video_analyzer import create_gemini_analyzer
        
        analyzer = create_gemini_analyzer(
            cloudflare_project_id=gemini_config.cloudflare_project_id,
            cloudflare_gateway_id=gemini_config.cloudflare_gateway_id,
            google_project_id=gemini_config.google_project_id,
            regions=gemini_config.regions,
            model_name=gemini_config.model_name,
            enable_cache=gemini_config.enable_cache,
            cache_dir=gemini_config.cache_dir
        )
        
        print("✅ 分析器创建成功")
        
        # 测试获取访问令牌
        print("\n🔑 测试获取访问令牌...")
        
        async def test_token():
            try:
                access_token = await analyzer.get_access_token()
                return access_token
            except Exception as e:
                print(f"❌ 获取访问令牌失败: {e}")
                return None
        
        access_token = asyncio.run(test_token())
        
        if access_token:
            print(f"✅ 访问令牌获取成功!")
            print(f"🔑 令牌长度: {len(access_token)} 字符")
            print(f"🔑 令牌前缀: {access_token[:20]}...")
            
            # 测试缓存功能
            print("\n📊 测试缓存功能...")
            cache_stats = analyzer.get_cache_stats()
            print(f"✅ 缓存统计: {cache_stats}")
            
            return True
        else:
            print("❌ 访问令牌获取失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint():
    """测试API端点可达性"""
    print("\n🌐 测试API端点可达性")
    print("=" * 30)
    
    try:
        import requests
        from config import get_config
        
        config = get_config()
        base_url = config.gemini.base_url
        bearer_token = config.gemini.bearer_token
        
        # 测试基础连接
        print(f"📡 测试连接到: {base_url}")
        
        # 测试获取访问令牌的端点
        token_url = f"{base_url}/google/access-token"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        
        print(f"🔑 测试令牌端点: {token_url}")
        response = requests.get(token_url, headers=headers, timeout=10)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ 令牌端点测试成功!")
            print(f"🔑 返回数据: {list(token_data.keys())}")
            return True
        else:
            print(f"❌ 令牌端点测试失败: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False


def test_config_validation():
    """测试配置验证"""
    print("\n📋 测试配置验证")
    print("=" * 20)
    
    try:
        from config import get_config
        config = get_config()
        gemini_config = config.gemini
        
        # 检查必需的配置项
        required_fields = [
            'cloudflare_project_id',
            'cloudflare_gateway_id', 
            'google_project_id',
            'model_name',
            'base_url',
            'bearer_token'
        ]
        
        missing_fields = []
        for field in required_fields:
            value = getattr(gemini_config, field, None)
            if not value:
                missing_fields.append(field)
            else:
                print(f"✅ {field}: {value}")
        
        if missing_fields:
            print(f"❌ 缺少必需配置: {', '.join(missing_fields)}")
            return False
        else:
            print("✅ 所有必需配置都已设置")
            return True
            
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return False


def test_gemini_analyzer_creation():
    """测试Gemini分析器创建"""
    print("\n🔧 测试Gemini分析器创建")
    print("=" * 25)
    
    try:
        from gemini_video_analyzer import create_gemini_analyzer, GeminiConfig
        from config import get_config
        
        config = get_config()
        gemini_config = config.gemini
        
        # 测试使用配置创建分析器
        analyzer = create_gemini_analyzer(
            cloudflare_project_id=gemini_config.cloudflare_project_id,
            cloudflare_gateway_id=gemini_config.cloudflare_gateway_id,
            google_project_id=gemini_config.google_project_id,
            regions=gemini_config.regions,
            model_name=gemini_config.model_name,
            enable_cache=gemini_config.enable_cache,
            cache_dir=gemini_config.cache_dir
        )
        
        print("✅ 分析器创建成功")
        print(f"📊 分析器类型: {type(analyzer)}")
        print(f"📊 配置: {analyzer.config}")
        
        # 测试缓存目录创建
        cache_dir = Path(gemini_config.cache_dir)
        if cache_dir.exists():
            print(f"✅ 缓存目录已创建: {cache_dir}")
        else:
            print(f"⚠️ 缓存目录不存在: {cache_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析器创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🧪 Gemini API连接测试套件")
    print("=" * 60)
    
    tests = [
        ("配置验证", test_config_validation),
        ("分析器创建", test_gemini_analyzer_creation),
        ("API端点测试", test_api_endpoint),
        ("完整连接测试", test_gemini_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 运行测试: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
                
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过 ({passed/total:.1%})")
    
    if passed == total:
        print("🎉 所有测试通过！Gemini API连接正常")
    else:
        print("⚠️ 部分测试失败，请检查配置和网络连接")


if __name__ == "__main__":
    main()
