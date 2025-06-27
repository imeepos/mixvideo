#!/usr/bin/env node

import { logger } from './utils.js';
import inquirer from 'inquirer';
import { spawn } from 'child_process';

async function main() {
  logger.title('🎬 MixVideo 视频分析演示');
  console.log('='.repeat(50));
  
  console.log('欢迎使用 MixVideo 视频分析工具演示程序！');
  console.log('');
  console.log('这个演示程序展示了如何使用 @mixvideo/video-analyzer 库');
  console.log('进行智能视频分析，包括场景检测、物体识别、内容总结等功能。');
  console.log('');
  
  const { action } = await inquirer.prompt([
    {
      type: 'list',
      name: 'action',
      message: '请选择要执行的操作:',
      choices: [
        { name: '🧪 运行库组件测试', value: 'test' },
        { name: '📊 开始视频分析', value: 'analyze' },
        { name: '📖 查看使用说明', value: 'help' },
        { name: '🚪 退出程序', value: 'exit' }
      ]
    }
  ]);
  
  switch (action) {
    case 'test':
      await runScript('test');
      break;
    case 'analyze':
      await runScript('analyze');
      break;
    case 'help':
      showHelp();
      break;
    case 'exit':
      logger.info('再见！');
      process.exit(0);
      break;
  }
}

async function runScript(scriptName: string) {
  logger.info(`启动 ${scriptName} 脚本...`);
  console.log('');
  
  const child = spawn('npm', ['run', scriptName], {
    stdio: 'inherit',
    shell: true
  });
  
  return new Promise<void>((resolve, reject) => {
    child.on('close', (code) => {
      if (code === 0) {
        console.log('');
        logger.success(`${scriptName} 脚本执行完成`);
        resolve();
      } else {
        logger.error(`${scriptName} 脚本执行失败 (退出码: ${code})`);
        reject(new Error(`Script failed with code ${code}`));
      }
    });
    
    child.on('error', (error) => {
      logger.error(`启动 ${scriptName} 脚本失败: ${error.message}`);
      reject(error);
    });
  });
}

function showHelp() {
  logger.title('\n📖 使用说明');
  console.log('='.repeat(50));
  
  console.log('\n🔧 环境配置:');
  console.log('1. 复制 .env.example 到 .env');
  console.log('2. 在 .env 文件中设置 GEMINI_API_KEY');
  console.log('3. 从 https://makersuite.google.com/app/apikey 获取 API Key');
  
  console.log('\n📦 可用脚本:');
  console.log('• npm run dev     - 启动交互式演示程序');
  console.log('• npm run test    - 运行库组件测试');
  console.log('• npm run analyze - 开始视频分析');
  console.log('• npm run build   - 构建项目');
  
  console.log('\n🎯 功能特性:');
  console.log('• 🎭 场景检测和描述');
  console.log('• 🔍 物体识别和定位');
  console.log('• 📝 智能内容总结');
  console.log('• ✨ 高光时刻提取');
  console.log('• 🔄 视频相似度对比');
  console.log('• 📦 批量处理支持');
  
  console.log('\n🔗 相关链接:');
  console.log('• 项目文档: packages/video-analyzer/README.md');
  console.log('• 使用指南: packages/video-analyzer/USAGE.md');
  console.log('• API 参考: packages/video-analyzer/src/types/index.ts');
  
  console.log('\n💡 提示:');
  console.log('• 首次使用建议先运行测试确保环境正常');
  console.log('• 支持本地文件和网络URL两种视频输入方式');
  console.log('• 可以使用模拟数据测试功能而无需API Key');
  
  console.log('');
}

// 运行主程序
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    logger.error(`程序执行失败: ${error.message}`);
    process.exit(1);
  });
}
