#!/usr/bin/env python3
"""
Gemini配置检查工具
检查config.yaml中的Gemini配置是否正确
"""

import sys
from pathlib import Path


def check_gemini_config():
    """检查Gemini配置"""
    print("🔍 检查Gemini配置...")
    print("=" * 50)
    
    try:
        # 检查config.yaml文件是否存在
        config_file = Path("config.yaml")
        if not config_file.exists():
            print("❌ config.yaml文件不存在")
            print("💡 请先创建config.yaml文件，可以参考config_gemini_example.yaml")
            return False
        
        # 加载配置
        from config import load_config
        config = load_config("config.yaml")
        gemini_config = config.gemini
        
        print("📋 当前Gemini配置:")
        print(f"  - Cloudflare项目ID: {gemini_config.cloudflare_project_id}")
        print(f"  - Cloudflare网关ID: {gemini_config.cloudflare_gateway_id}")
        print(f"  - Google项目ID: {gemini_config.google_project_id}")
        print(f"  - 模型: {gemini_config.model_name}")
        print(f"  - 区域: {', '.join(gemini_config.regions)}")
        print(f"  - 缓存: {'启用' if gemini_config.enable_cache else '禁用'}")
        print(f"  - 缓存目录: {gemini_config.cache_dir}")
        
        # 检查必需的配置项
        issues = []
        
        if gemini_config.cloudflare_project_id == "your_cloudflare_project_id_here":
            issues.append("Cloudflare项目ID未设置")
        
        if gemini_config.cloudflare_gateway_id == "your_cloudflare_gateway_id_here":
            issues.append("Cloudflare网关ID未设置")
        
        if gemini_config.google_project_id == "your_google_project_id_here":
            issues.append("Google项目ID未设置")
        
        if not gemini_config.regions:
            issues.append("未配置任何区域")
        
        # 检查缓存目录
        if gemini_config.enable_cache:
            cache_dir = Path(gemini_config.cache_dir)
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ 缓存目录可用: {cache_dir.absolute()}")
            except Exception as e:
                issues.append(f"缓存目录创建失败: {e}")
        
        # 显示检查结果
        print("\n🔍 配置检查结果:")
        if issues:
            print("❌ 发现以下问题:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
            print("\n💡 解决方案:")
            print("  1. 编辑config.yaml文件")
            print("  2. 替换所有'your_xxx_here'为实际配置值")
            print("  3. 参考config_gemini_example.yaml获取配置示例")
            return False
        else:
            print("✅ 配置检查通过！")
            
            # 测试缓存功能
            if gemini_config.enable_cache:
                try:
                    from gemini_video_analyzer import create_gemini_analyzer
                    analyzer = create_gemini_analyzer(
                        cloudflare_project_id=gemini_config.cloudflare_project_id,
                        cloudflare_gateway_id=gemini_config.cloudflare_gateway_id,
                        google_project_id=gemini_config.google_project_id,
                        cache_dir=gemini_config.cache_dir,
                        enable_cache=True
                    )
                    
                    cache_stats = analyzer.get_cache_stats()
                    print(f"📊 缓存统计: {cache_stats.get('total_files', 0)} 个文件")
                    
                except Exception as e:
                    print(f"⚠️ 缓存测试失败: {e}")
            
            return True
        
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False


def show_config_help():
    """显示配置帮助"""
    print("📖 Gemini配置帮助")
    print("=" * 50)
    print("""
1. 获取Cloudflare配置:
   - 登录 Cloudflare Dashboard
   - 进入 AI Gateway 部分
   - 创建或选择一个Gateway
   - 获取项目ID和网关ID

2. 获取Google项目配置:
   - 登录 Google Cloud Console
   - 创建或选择一个项目
   - 启用 Vertex AI API
   - 获取项目ID

3. 编辑config.yaml:
   - 找到 gemini 部分
   - 替换所有 'your_xxx_here' 为实际值
   - 保存文件

4. 验证配置:
   - 运行此脚本检查配置
   - 在GUI中点击"重新加载"按钮

示例配置文件: config_gemini_example.yaml
""")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        show_config_help()
    else:
        success = check_gemini_config()
        
        if not success:
            print("\n💡 需要帮助？运行: python check_gemini_config.py help")
        else:
            print("\n🎉 配置完成！现在可以在GUI中使用Gemini视频分析功能了。")


if __name__ == "__main__":
    main()
