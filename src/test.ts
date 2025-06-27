import { generateDraft, scanDirectory } from "@mixvideo/jianying";
import { writeFileSync } from "fs";
import { join } from "path";

const files = scanDirectory(join(__dirname, '../resources'));

// 生成草稿文件
const draft = generateDraft(files, {
    canvasWidth: 1920,
    canvasHeight: 1080,
    fps: 60,
    projectName: '我的项目',
    useFFProbe: true // 使用 ffprobe 获取真实视频信息
});


writeFileSync(join(__dirname, '../resources', 'generated_draft.json'), JSON.stringify(draft, null, 2));
console.log({ draft })