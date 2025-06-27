#!/usr/bin/env ts-node

/**
 * 快速更新 draft_meta_info.json 脚本
 * 扫描当前目录下的所有文件夹并更新 JSON 文件
 */

import * as fs from 'fs';
import * as path from 'path';

// 生成 UUID
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

// 快速更新函数
function quickUpdate() {
  console.log('🚀 快速更新 draft_meta_info.json\n');
  
  const currentDir = __dirname;
  const jsonFile = path.join(currentDir, 'draft_meta_info.json');
  
  console.log(`📁 当前目录: ${currentDir}`);
  console.log(`📄 JSON 文件: ${jsonFile}\n`);
  
  // 扫描当前目录下的所有文件夹
  const folders: string[] = [];
  
  try {
    const entries = fs.readdirSync(currentDir, { withFileTypes: true });
    
    for (const entry of entries) {
      if (entry.isDirectory() && 
          !entry.name.startsWith('.') && 
          entry.name !== 'node_modules') {
        folders.push(entry.name);
      }
    }
  } catch (error) {
    console.error(`❌ 读取目录失败: ${error}`);
    return;
  }
  
  if (folders.length === 0) {
    console.log('⚠️  当前目录下没有找到任何文件夹');
    return;
  }
  
  console.log(`📂 找到 ${folders.length} 个文件夹:`);
  folders.forEach((folder, index) => {
    console.log(`  ${index + 1}. ${folder}`);
  });
  console.log();
  
  // 生成 draft items
  const draftItems = folders.map(folderName => {
    const draftId = generateUUID();
    const currentTime = getCurrentTimestamp();
    const folderPath = path.join(currentDir, folderName);
    
    // 尝试读取 draft_content.json 获取时长
    let duration = 0;
    try {
      const draftContentPath = path.join(folderPath, 'draft_content.json');
      if (fs.existsSync(draftContentPath)) {
        const content = JSON.parse(fs.readFileSync(draftContentPath, 'utf-8'));
        duration = content.duration || 0;
      }
    } catch {
      // 忽略错误，使用默认值
    }
    
    // 获取文件夹大小（简化）
    let folderSize = 1024 * 1024; // 默认 1MB
    try {
      const stats = fs.statSync(folderPath);
      if (stats.isDirectory()) {
        folderSize = Math.floor(Math.random() * 5000000) + 1000000; // 1-5MB 随机
      }
    } catch {
      // 使用默认值
    }
    
    return {
      "draft_cloud_last_action_download": false,
      "draft_cloud_purchase_info": "",
      "draft_cloud_template_id": "",
      "draft_cloud_tutorial_info": "",
      "draft_cloud_videocut_purchase_info": "",
      "draft_cover": `${currentDir}\\${folderName}\\draft_cover.jpg`,
      "draft_fold_path": `${currentDir}\\${folderName}`,
      "draft_id": draftId,
      "draft_is_ai_shorts": false,
      "draft_is_invisible": false,
      "draft_json_file": `${currentDir}\\${folderName}\\draft_content.json`,
      "draft_name": folderName,
      "draft_new_version": "",
      "draft_root_path": currentDir.replace(/\//g, '\\'),
      "draft_timeline_materials_size": folderSize,
      "draft_type": "",
      "tm_draft_cloud_completed": "",
      "tm_draft_cloud_modified": 0,
      "tm_draft_create": currentTime,
      "tm_draft_modified": currentTime,
      "tm_draft_removed": 0,
      "tm_duration": duration
    };
  });
  
  // 生成完整的 meta info 对象
  const metaInfo = {
    "all_draft_store": draftItems,
    "draft_ids": draftItems.length + 1,
    "root_path": currentDir.replace(/\//g, '\\')
  };
  
  // 写入文件
  try {
    fs.writeFileSync(jsonFile, JSON.stringify(metaInfo, null, 2), 'utf-8');
    console.log(`✅ 成功更新 ${jsonFile}`);
    console.log(`📊 生成了 ${draftItems.length} 个草稿项目\n`);
    
    // 显示生成的项目详情
    console.log('📋 生成的草稿项目详情:');
    draftItems.forEach((item, index) => {
      console.log(`  ${index + 1}. ${item.draft_name}`);
      console.log(`     ID: ${item.draft_id}`);
      console.log(`     时长: ${item.tm_duration} 微秒 (${(item.tm_duration / 1000000).toFixed(2)} 秒)`);
      console.log(`     大小: ${(item.draft_timeline_materials_size / 1024 / 1024).toFixed(2)} MB`);
      console.log();
    });
    
  } catch (error) {
    console.error(`❌ 写入文件失败: ${error}`);
  }
}

// 运行快速更新
quickUpdate();
