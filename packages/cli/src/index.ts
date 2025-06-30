#!/usr/bin/env node

import { Command } from 'commander';
import { createAnalyzeCommand } from './commands/analyze';
import { createGenerateCommand } from './commands/generate';
import { createAuthCommands } from './commands/auth';

/**
 * MixVideo CLI 工具
 *
 * 功能：
 * 1. 登录/退出
 * 2. 分析商品视频并自动分类
 * 3. 生成剪映草稿文件
 * 4. 查看任务状态
 */

/**
 * 主程序入口
 */
async function main(): Promise<void> {
    const program = new Command();

    program
        .name('mixvideo')
        .version('1.0.0')
        .description('视频分析和混剪工具');

    // 添加认证命令
    program.addCommand(createAuthCommands().login);
    program.addCommand(createAuthCommands().logout);

    // 添加分析命令
    program.addCommand(createAnalyzeCommand());

    // 添加生成命令
    program.addCommand(createGenerateCommand());

    // 解析命令行参数
    program.parse();
}

// 运行主程序
main().catch((error) => {
    console.error('❌ 程序运行出错:', error);
    process.exit(1);
});

