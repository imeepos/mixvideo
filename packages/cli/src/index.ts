#!/usr/bin/env node

/**
 * 设计一个cli工具
 * 
 * 模板库 
 * 产品库
 * 产品素材分类库
 * 产品素材库
 * 
 * 功能：
 * 1. 登录/退出
 * 2. 分析商品视频(上传视频)，【离线：提取商品信息并分类 大模型 入库】
 * 3. 生成视频，产品视频/产品图片/产品文案->匹配模板->循环[分类匹配素材->视频模板填充] x n -> 生成 n 个 draft_content.json -> 剪映预览出片
 * 4. 查看任务状态
 */
import { parse } from '@mixvideo/jianying'
import { readdir, writeFile } from 'fs/promises';
import { join } from 'path';
async function main() {
    const draft = parse(join(__dirname, 'draft_content.json'))
    draft.materials.videos = await Promise.all(draft.materials.videos.map(async video => {
        const material_name = video.material_name
        const videoPath = await getMaterialVideoByName(material_name)
        video.path = videoPath;
        return video;
    }))
    await writeFile(join(__dirname, 'draft_content.json'), JSON.stringify(draft, null, 2))
}

async function getMaterialVideoByName(name: string): Promise<string> {
    const root = join(__dirname, '../../../resources/1001001')
    const files = await readdir(root)
    return files[Math.floor(Math.random() * files.length)]
}

main();

