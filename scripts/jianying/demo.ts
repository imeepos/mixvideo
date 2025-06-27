#!/usr/bin/env ts-node

/**
 * 演示脚本 - 展示如何使用更新脚本
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

console.log('🎬 剪映草稿元信息更新脚本演示\n');

// 创建演示目录结构
function createDemoStructure() {
  console.log('📁 创建演示目录结构...');
  
  const demoProjects = [
    '我的旅行视频',
    '产品介绍片',
    '生日聚会记录',
    'Tutorial_2024'
  ];
  
  // 创建项目文件夹
  demoProjects.forEach(projectName => {
    const projectDir = path.join(__dirname, projectName);
    if (!fs.existsSync(projectDir)) {
      fs.mkdirSync(projectDir, { recursive: true });
      console.log(`  ✅ 创建文件夹: ${projectName}`);
      
      // 为部分项目创建 draft_content.json
      if (projectName === '我的旅行视频' || projectName === '产品介绍片') {
        const draftContent = {
          duration: Math.floor(Math.random() * 30000000) + 5000000, // 5-35秒
          fps: 30,
          canvas_config: {
            width: 1920,
            height: 1080
          },
          materials: {
            videos: [
              {
                id: `video_${Date.now()}`,
                path: `${projectName}_main.mp4`,
                duration: Math.floor(Math.random() * 20000000) + 3000000
              }
            ]
          }
        };
        
        const draftPath = path.join(projectDir, 'draft_content.json');
        fs.writeFileSync(draftPath, JSON.stringify(draftContent, null, 2));
        console.log(`    📄 创建 draft_content.json (时长: ${(draftContent.duration / 1000000).toFixed(1)}秒)`);
      }
    }
  });
  
  console.log();
}

// 运行演示
function runDemo() {
  console.log('🚀 运行演示...\n');
  
  try {
    // 1. 创建演示结构
    createDemoStructure();
    
    // 2. 运行快速更新
    console.log('📋 步骤 1: 运行快速更新脚本');
    console.log('命令: ts-node quick-update.ts\n');
    
    execSync('ts-node quick-update.ts', { 
      stdio: 'inherit',
      cwd: __dirname 
    });
    
    console.log('\n' + '='.repeat(60) + '\n');
    
    // 3. 显示生成的文件内容摘要
    console.log('📊 步骤 2: 查看生成的文件摘要');
    
    const metaFile = path.join(__dirname, 'draft_meta_info.json');
    if (fs.existsSync(metaFile)) {
      const metaData = JSON.parse(fs.readFileSync(metaFile, 'utf-8'));
      
      console.log(`✅ 成功生成 draft_meta_info.json`);
      console.log(`📁 根路径: ${metaData.root_path}`);
      console.log(`🎬 项目数量: ${metaData.all_draft_store.length}`);
      console.log(`🆔 下一个ID: ${metaData.draft_ids}\n`);
      
      console.log('📋 项目列表:');
      metaData.all_draft_store.forEach((project: any, index: number) => {
        const durationSeconds = (project.tm_duration / 1000000).toFixed(1);
        const sizeKB = (project.draft_timeline_materials_size / 1024).toFixed(1);
        
        console.log(`  ${index + 1}. ${project.draft_name}`);
        console.log(`     🆔 ID: ${project.draft_id}`);
        console.log(`     ⏱️  时长: ${durationSeconds} 秒`);
        console.log(`     💾 大小: ${sizeKB} KB`);
        console.log(`     📁 路径: ${project.draft_fold_path}`);
        console.log();
      });
    }
    
    console.log('='.repeat(60) + '\n');
    
    // 4. 演示完整脚本的使用
    console.log('📋 步骤 3: 演示完整脚本参数');
    console.log('以下是一些常用的命令示例:\n');
    
    console.log('# 基本用法（扫描当前目录）');
    console.log('ts-node update-draft-meta.ts\n');
    
    console.log('# 指定扫描目录');
    console.log('ts-node update-draft-meta.ts --scan /path/to/projects\n');
    
    console.log('# 指定输出文件');
    console.log('ts-node update-draft-meta.ts --json ./my_meta.json\n');
    
    console.log('# 完整参数示例');
    console.log('ts-node update-draft-meta.ts --json ./meta.json --scan ./projects --root /jianying/root\n');
    
    console.log('# 查看帮助');
    console.log('ts-node update-draft-meta.ts --help\n');
    
    console.log('='.repeat(60) + '\n');
    
    console.log('🎉 演示完成！');
    console.log('\n💡 提示:');
    console.log('- 脚本会自动跳过隐藏文件夹和 node_modules');
    console.log('- 如果文件夹中有 draft_content.json，会尝试读取真实时长');
    console.log('- 生成的 UUID 确保每个项目都有唯一标识');
    console.log('- 路径会自动转换为 Windows 格式（反斜杠）');
    console.log('\n📚 更多功能请查看 packages/jianying 包！');
    
  } catch (error) {
    console.error('❌ 演示过程中出现错误:', error);
  }
}

// 清理演示文件
function cleanup() {
  console.log('\n🧹 清理演示文件...');
  
  const demoProjects = [
    '我的旅行视频',
    '产品介绍片', 
    '生日聚会记录',
    'Tutorial_2024'
  ];
  
  demoProjects.forEach(projectName => {
    const projectDir = path.join(__dirname, projectName);
    if (fs.existsSync(projectDir)) {
      fs.rmSync(projectDir, { recursive: true, force: true });
      console.log(`  🗑️  删除: ${projectName}`);
    }
  });
  
  console.log('✅ 清理完成');
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--cleanup') || args.includes('-c')) {
    cleanup();
    return;
  }
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
🎬 剪映草稿元信息更新脚本演示

用法:
  ts-node demo.ts [选项]

选项:
  -c, --cleanup    清理演示文件
  -h, --help       显示帮助信息

示例:
  # 运行完整演示
  ts-node demo.ts
  
  # 清理演示文件
  ts-node demo.ts --cleanup
    `);
    return;
  }
  
  runDemo();
}

// 运行主函数
if (require.main === module) {
  main();
}
