#!/usr/bin/env python3
"""
Test Runner
测试运行器
"""

import sys
import unittest
import os
from pathlib import Path
import time
from io import StringIO

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class ColoredTextTestResult(unittest.TextTestResult):
    """带颜色的测试结果"""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self._verbosity = verbosity

    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self._verbosity > 1:
            self.stream.write("✅ ")
            self.stream.writeln(self.getDescription(test))

    def addError(self, test, err):
        super().addError(test, err)
        if self._verbosity > 1:
            self.stream.write("❌ ")
            self.stream.writeln(self.getDescription(test))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self._verbosity > 1:
            self.stream.write("❌ ")
            self.stream.writeln(self.getDescription(test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self._verbosity > 1:
            self.stream.write("⏭️ ")
            self.stream.writeln(f"{self.getDescription(test)} (跳过: {reason})")


class ColoredTextTestRunner(unittest.TextTestRunner):
    """带颜色的测试运行器"""
    
    resultclass = ColoredTextTestResult
    
    def run(self, test):
        """运行测试"""
        print("🧪 Shot Detection 单元测试")
        print("=" * 50)
        
        start_time = time.time()
        result = super().run(test)
        end_time = time.time()
        
        # 打印测试结果摘要
        print("\n" + "=" * 50)
        print("📊 测试结果摘要")
        print(f"⏱️ 运行时间: {end_time - start_time:.2f} 秒")
        print(f"✅ 成功: {result.success_count}")
        print(f"❌ 失败: {len(result.failures)}")
        print(f"💥 错误: {len(result.errors)}")
        print(f"⏭️ 跳过: {len(result.skipped)}")
        print(f"📈 总计: {result.testsRun}")
        
        if result.failures:
            print("\n❌ 失败的测试:")
            for test, traceback in result.failures:
                print(f"   - {test}")
        
        if result.errors:
            print("\n💥 错误的测试:")
            for test, traceback in result.errors:
                print(f"   - {test}")
        
        # 计算成功率
        if result.testsRun > 0:
            success_rate = (result.success_count / result.testsRun) * 100
            print(f"\n🎯 成功率: {success_rate:.1f}%")
            
            if success_rate == 100:
                print("🎉 所有测试通过！")
            elif success_rate >= 80:
                print("👍 大部分测试通过")
            else:
                print("⚠️ 需要修复失败的测试")
        
        return result


def discover_tests(test_dir="tests", pattern="test_*.py"):
    """发现测试用例"""
    test_path = project_root / test_dir
    
    if not test_path.exists():
        print(f"⚠️ 测试目录不存在: {test_path}")
        return unittest.TestSuite()
    
    # 发现测试
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_path), pattern=pattern, top_level_dir=str(project_root))
    
    return suite


def run_specific_test(test_module, test_class=None, test_method=None):
    """运行特定测试"""
    try:
        # 导入测试模块
        module = __import__(f"tests.{test_module}", fromlist=[test_module])
        
        if test_class and test_method:
            # 运行特定测试方法
            suite = unittest.TestSuite()
            test_case = getattr(module, test_class)(test_method)
            suite.addTest(test_case)
        elif test_class:
            # 运行特定测试类
            suite = unittest.TestLoader().loadTestsFromTestCase(getattr(module, test_class))
        else:
            # 运行整个模块
            suite = unittest.TestLoader().loadTestsFromModule(module)
        
        return suite
        
    except ImportError as e:
        print(f"❌ 无法导入测试模块 {test_module}: {e}")
        return unittest.TestSuite()
    except AttributeError as e:
        print(f"❌ 测试类或方法不存在: {e}")
        return unittest.TestSuite()


def run_coverage_analysis():
    """运行覆盖率分析"""
    try:
        import coverage
        
        print("📊 开始覆盖率分析...")
        
        # 创建覆盖率对象
        cov = coverage.Coverage(source=['core', 'config', 'gui'])
        cov.start()
        
        # 运行测试
        suite = discover_tests()
        runner = unittest.TextTestRunner(verbosity=0, stream=StringIO())
        result = runner.run(suite)
        
        # 停止覆盖率收集
        cov.stop()
        cov.save()
        
        # 生成报告
        print("\n📋 覆盖率报告:")
        cov.report()
        
        # 生成HTML报告
        html_dir = project_root / "coverage_html"
        cov.html_report(directory=str(html_dir))
        print(f"📄 HTML报告已生成: {html_dir}/index.html")
        
        return result
        
    except ImportError:
        print("⚠️ 未安装coverage包，跳过覆盖率分析")
        print("   安装命令: pip install coverage")
        return None


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Shot Detection 测试运行器")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("-m", "--module", help="运行特定测试模块")
    parser.add_argument("-c", "--class", dest="test_class", help="运行特定测试类")
    parser.add_argument("-t", "--test", dest="test_method", help="运行特定测试方法")
    parser.add_argument("--coverage", action="store_true", help="运行覆盖率分析")
    parser.add_argument("--pattern", default="test_*.py", help="测试文件模式")
    
    args = parser.parse_args()
    
    # 设置详细程度
    verbosity = 2 if args.verbose else 1
    
    # 运行覆盖率分析
    if args.coverage:
        result = run_coverage_analysis()
        if result:
            return 0 if result.wasSuccessful() else 1
        else:
            return 1
    
    # 运行特定测试
    if args.module:
        suite = run_specific_test(args.module, args.test_class, args.test_method)
    else:
        # 发现所有测试
        suite = discover_tests(pattern=args.pattern)
    
    # 检查是否找到测试
    if suite.countTestCases() == 0:
        print("⚠️ 没有找到测试用例")
        return 1
    
    # 运行测试
    runner = ColoredTextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # 返回退出码
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
