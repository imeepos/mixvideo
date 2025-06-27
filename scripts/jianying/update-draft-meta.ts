#!/usr/bin/env ts-node

/**
 * 更新 draft_meta_info.json 脚本
 * 扫描指定目录下的所有文件夹，为每个文件夹生成一个 draft item
 */

import * as fs from 'fs';
import * as path from 'path';

// 生成 UUID 的简单函数
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16).toUpperCase();
  });
}

// 获取当前时间戳（微秒）
function getCurrentTimestamp(): number {
  return Date.now() * 1000;
}

// 获取文件夹大小（简化版本，返回固定值）
function getFolderSize(folderPath: string): number {
  try {
    const stats = fs.statSync(folderPath);
    return stats.isDirectory() ? 1024 * 1024 : 0; // 默认 1MB
  } catch {
    return 0;
  }
}

// 获取草稿时长（从 draft_content.json 中读取，如果存在）
function getDraftDuration(folderPath: string): number {
  try {
    const draftContentPath = path.join(folderPath, 'draft_content.json');
    if (fs.existsSync(draftContentPath)) {
      const content = JSON.parse(fs.readFileSync(draftContentPath, 'utf-8'));
      return content.duration || 0;
    }
  } catch {
    // 忽略错误
  }
  return 0;
}

// 生成单个 draft item
function generateDraftItem(folderName: string, folderPath: string, rootPath: string): any {
  const draftId = generateUUID();
  const currentTime = getCurrentTimestamp();
  const duration = getDraftDuration(folderPath);
  const folderSize = getFolderSize(folderPath);
  
  // 使用 Windows 路径格式（根据原始数据的格式）
  const windowsRootPath = rootPath.replace(/\//g, '\\');
  const windowsFolderPath = folderPath.replace(/\//g, '\\');
  
  return {
    "draft_cloud_last_action_download": false,
    "draft_cloud_purchase_info": "",
    "draft_cloud_template_id": "",
    "draft_cloud_tutorial_info": "",
    "draft_cloud_videocut_purchase_info": "",
    "draft_cover": `${windowsFolderPath}\\draft_cover.jpg`,
    "draft_fold_path": windowsFolderPath,
    "draft_id": draftId,
    "draft_is_ai_shorts": false,
    "draft_is_invisible": false,
    "draft_json_file": `${windowsFolderPath}\\draft_content.json`,
    "draft_name": folderName,
    "draft_new_version": "",
    "draft_root_path": windowsRootPath,
    "draft_timeline_materials_size": folderSize,
    "draft_type": "",
    "tm_draft_cloud_completed": "",
    "tm_draft_cloud_modified": 0,
    "tm_draft_create": currentTime,
    "tm_draft_modified": currentTime,
    "tm_draft_removed": 0,
    "tm_duration": duration
  };
}

// 扫描目录并生成 draft items
function scanDirectoryForDrafts(scanPath: string, rootPath?: string): any[] {
  const items: any[] = [];
  const actualRootPath = rootPath || scanPath;
  
  try {
    const entries = fs.readdirSync(scanPath, { withFileTypes: true });
    
    for (const entry of entries) {
      if (entry.isDirectory()) {
        // 跳过特殊目录
        if (entry.name.startsWith('.') || entry.name === 'node_modules') {
          continue;
        }
        
        const folderPath = path.join(scanPath, entry.name);
        const item = generateDraftItem(entry.name, folderPath, actualRootPath);
        items.push(item);
        
        console.log(`✅ 生成草稿项目: ${entry.name}`);
      }
    }
  } catch (error) {
    console.error(`❌ 扫描目录失败: ${error instanceof Error ? error.message : String(error)}`);
  }
  
  return items;
}

// 更新 draft_meta_info.json 文件
function updateDraftMetaInfo(jsonFilePath: string, scanPath?: string, rootPath?: string): void {
  console.log('🔄 开始更新 draft_meta_info.json...\n');
  
  // 确定扫描路径
  const actualScanPath = scanPath || path.dirname(jsonFilePath);
  const actualRootPath = rootPath || actualScanPath;
  
  console.log(`📁 扫描路径: ${actualScanPath}`);
  console.log(`📁 根路径: ${actualRootPath}`);
  
  // 扫描目录生成 draft items
  const draftItems = scanDirectoryForDrafts(actualScanPath, actualRootPath);
  
  if (draftItems.length === 0) {
    console.log('⚠️  未找到任何文件夹，跳过更新');
    return;
  }
  
  // 生成新的 meta info 对象
  const metaInfo = {
    "all_draft_store": draftItems,
    "draft_ids": draftItems.length + 1,
    "root_path": actualRootPath.replace(/\//g, '\\') // Windows 路径格式
  };
  
  // 写入文件
  try {
    fs.writeFileSync(jsonFilePath, JSON.stringify(metaInfo, null, 2), 'utf-8');
    console.log(`\n✅ 成功更新 ${jsonFilePath}`);
    console.log(`📊 生成了 ${draftItems.length} 个草稿项目`);
    
    // 显示生成的项目列表
    console.log('\n📋 生成的草稿项目:');
    draftItems.forEach((item, index) => {
      console.log(`  ${index + 1}. ${item.draft_name} (ID: ${item.draft_id})`);
    });
    
  } catch (error) {
    console.error(`❌ 写入文件失败: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// 主函数
function main() {
  const args = process.argv.slice(2);
  
  // 默认参数
  let jsonFilePath = path.join(__dirname, 'draft_meta_info.json');
  let scanPath: string | undefined;
  let rootPath: string | undefined;
  
  // 解析命令行参数
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--json' || arg === '-j') {
      jsonFilePath = args[++i];
    } else if (arg === '--scan' || arg === '-s') {
      scanPath = args[++i];
    } else if (arg === '--root' || arg === '-r') {
      rootPath = args[++i];
    } else if (arg === '--help' || arg === '-h') {
      console.log(`
📝 draft_meta_info.json 更新脚本

用法:
  ts-node update-draft-meta.ts [选项]

选项:
  -j, --json <path>    指定 draft_meta_info.json 文件路径 (默认: ./draft_meta_info.json)
  -s, --scan <path>    指定要扫描的目录路径 (默认: JSON 文件所在目录)
  -r, --root <path>    指定根路径 (默认: 扫描路径)
  -h, --help           显示帮助信息

示例:
  # 扫描当前目录并更新 draft_meta_info.json
  ts-node update-draft-meta.ts
  
  # 扫描指定目录
  ts-node update-draft-meta.ts --scan /path/to/projects
  
  # 指定 JSON 文件和扫描目录
  ts-node update-draft-meta.ts --json ./meta.json --scan ./projects --root /root/path
      `);
      return;
    }
  }
  
  // 检查 JSON 文件是否存在
  if (!fs.existsSync(jsonFilePath)) {
    console.log(`⚠️  JSON 文件不存在，将创建新文件: ${jsonFilePath}`);
  }
  
  // 执行更新
  updateDraftMetaInfo(jsonFilePath, scanPath, rootPath);
}

// 如果直接运行此脚本，执行主函数
if (require.main === module) {
  main();
}

export {
  generateDraftItem,
  scanDirectoryForDrafts,
  updateDraftMetaInfo,
  generateUUID,
  getCurrentTimestamp
};
