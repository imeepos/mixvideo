#!/usr/bin/env python3
"""
测试Gemini API的纯文本分析功能
"""

import asyncio
import requests
import json


async def test_gemini_text_analysis():
    """测试Gemini API的纯文本分析"""
    print("🤖 测试Gemini API纯文本分析")
    print("=" * 50)
    
    try:
        # 加载配置
        from config import get_config
        config = get_config()
        gemini_config = config.gemini
        
        print(f"📋 配置信息:")
        print(f"  - 模型: {gemini_config.model_name}")
        print(f"  - 基础URL: {gemini_config.base_url}")
        
        # 创建分析器
        from gemini_video_analyzer import create_gemini_analyzer
        
        analyzer = create_gemini_analyzer(
            cloudflare_project_id=gemini_config.cloudflare_project_id,
            cloudflare_gateway_id=gemini_config.cloudflare_gateway_id,
            google_project_id=gemini_config.google_project_id,
            regions=gemini_config.regions,
            model_name=gemini_config.model_name,
            enable_cache=False,
            cache_dir=gemini_config.cache_dir
        )
        
        # 获取访问令牌
        print(f"🔑 获取访问令牌...")
        access_token = await analyzer.get_access_token()
        print(f"✅ 访问令牌获取成功，长度: {len(access_token)} 字符")
        
        # 创建客户端配置
        client_config = analyzer._create_gemini_client(access_token)
        print(f"🌐 Gateway URL: {client_config['gateway_url']}")
        
        # 构建测试请求
        test_prompt = """请分析以下视频内容描述，并推荐最合适的分类：

视频内容：这是一个白底背景下的女装产品展示视频，展示了一件红色连衣裙的细节特写。

请从以下选项中选择：
- product_display (产品展示)
- model_wearing (模特试穿)
- standard (标准分类)

请以JSON格式回答：
{
  "category": "推荐的分类",
  "confidence": 0.95,
  "reason": "选择原因"
}"""
        
        request_data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": test_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 4096
            }
        }
        
        print(f"📤 发送测试请求...")
        print(f"📝 请求内容长度: {len(test_prompt)} 字符")
        
        # 发送请求
        generate_url = f"{client_config['gateway_url']}/{gemini_config.model_name}:generateContent"
        print(f"🌐 请求URL: {generate_url}")
        
        response = requests.post(
            generate_url,
            headers=client_config['headers'],
            json=request_data,
            timeout=30
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API调用成功!")
            
            # 保存完整响应
            with open("gemini_text_response.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 完整响应已保存: gemini_text_response.json")
            
            # 提取响应文本
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    response_text = candidate['content']['parts'][0]['text']
                    print(f"📄 响应文本:")
                    print(f"{'='*50}")
                    print(response_text)
                    print(f"{'='*50}")
                    
                    # 尝试解析JSON
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        try:
                            classification_result = json.loads(json_str)
                            print(f"✅ JSON解析成功:")
                            print(f"  🎯 分类: {classification_result.get('category', 'unknown')}")
                            print(f"  📊 置信度: {classification_result.get('confidence', 0):.1%}")
                            print(f"  💭 原因: {classification_result.get('reason', 'unknown')}")
                            return True
                        except Exception as e:
                            print(f"❌ JSON解析失败: {e}")
                            print(f"📄 JSON字符串: {json_str}")
                    else:
                        # 尝试直接解析
                        try:
                            classification_result = json.loads(response_text)
                            print(f"✅ 直接JSON解析成功:")
                            print(f"  🎯 分类: {classification_result.get('category', 'unknown')}")
                            return True
                        except Exception as e:
                            print(f"⚠️ 无法解析为JSON，但获得了文本响应")
                            return True
                else:
                    print(f"❌ 响应格式错误: 缺少content或parts")
                    return False
            else:
                print(f"❌ 响应格式错误: 缺少candidates")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"📄 错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    try:
        success = asyncio.run(test_gemini_text_analysis())
        
        if success:
            print(f"\n🎉 Gemini文本分析测试成功!")
        else:
            print(f"\n❌ Gemini文本分析测试失败")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")


if __name__ == "__main__":
    main()
