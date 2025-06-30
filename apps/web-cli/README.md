# MixVideo CLI Web Interface

🌐 **MixVideo CLI 命令的可视化 Web 界面**

一个现代化的 Web 界面，用于可视化执行 MixVideo CLI 的所有命令，提供友好的图形界面和实时命令执行反馈。

## ✨ 功能特性

### 🎯 **核心功能**
- **实时命令执行**：通过 WebSocket 实时显示命令执行过程
- **可视化界面**：友好的图形界面，无需记忆命令行参数
- **分类管理**：按功能分类组织所有 CLI 命令
- **实时反馈**：命令执行状态和输出实时显示

### 🔧 **支持的命令**

#### **认证管理**
- **登录**：`mixvideo login -u <username> -p <password>`
- **退出登录**：`mixvideo logout`

#### **视频分析**
- **分析视频**：`mixvideo analyze <path> [-o output]`
- **整理视频**：`mixvideo organize <source> <target> [--backup]`

#### **项目生成**
- **生成剪映项目**：`mixvideo generate from-videos <source> [-o output] [--title title]`
- **生成草稿项目**：`mixvideo generate from-videos <source> --draft-dir --title <title>`

## 🚀 快速开始

### **1. 安装依赖**
```bash
cd apps/web-cli
npm install
```

### **2. 启动开发服务器**
```bash
npm run dev
```

### **3. 启动后端服务**
```bash
npm run serve
```

### **4. 访问界面**
打开浏览器访问：`http://localhost:3000`

## 🏗️ 项目结构

```
apps/web-cli/
├── index.html          # 主页面
├── script.js           # 前端逻辑
├── server.js           # 后端服务器
├── vite.config.js      # Vite 配置
├── package.json        # 项目配置
└── README.md          # 文档
```

## 🔧 技术栈

### **前端**
- **HTML5 + CSS3**：现代化的响应式界面
- **Tailwind CSS**：快速样式开发
- **Font Awesome**：图标库
- **WebSocket**：实时通信

### **后端**
- **Node.js + Express**：Web 服务器
- **WebSocket (ws)**：实时通信
- **Child Process**：CLI 命令执行

## 📱 界面预览

### **主界面**
- 🔑 **认证管理**：登录/退出功能
- 🔍 **视频分析**：分析和整理视频
- ✨ **项目生成**：生成剪映项目和草稿

### **命令执行**
- 📝 **表单界面**：友好的参数输入
- 💻 **终端输出**：实时显示命令执行结果
- 🔄 **状态指示**：连接状态和执行进度

## 🎯 使用流程

### **1. 选择命令类别**
在主界面选择要执行的命令类别（认证、分析、生成）

### **2. 填写参数**
在弹出的表单中填写必要的参数

### **3. 执行命令**
点击执行按钮，实时查看命令执行过程

### **4. 查看结果**
在终端输出区域查看详细的执行结果

## 🔌 API 接口

### **WebSocket 消息格式**

#### **执行命令**
```json
{
  "type": "execute_command",
  "command": "login",
  "args": {
    "username": "user@example.com",
    "password": "password"
  }
}
```

#### **命令输出**
```json
{
  "type": "output",
  "message": "✅ 登录成功！",
  "level": "success"
}
```

### **REST API**

#### **健康检查**
```
GET /health
```

#### **获取可用命令**
```
GET /api/commands
```

## 🛠️ 开发指南

### **添加新命令**

1. **在 `script.js` 中添加表单函数**
2. **在 `server.js` 中添加命令处理逻辑**
3. **在 `index.html` 中添加按钮**

### **自定义样式**
修改 `index.html` 中的 Tailwind CSS 类名或添加自定义 CSS

### **扩展功能**
- 添加文件上传功能
- 集成更多 CLI 命令
- 添加命令历史记录
- 实现用户认证

## 📝 许可证

MIT License - 详见 [LICENSE](../../LICENSE) 文件
