# @mixvideo/gemini

> 🤖 MixVideo 项目的 Gemini AI API 客户端库

一个功能完整、类型安全的 TypeScript 库，用于通过 Cloudflare Gateway 访问 Google Gemini AI API。

## ✨ 特性

- 🔒 **类型安全**: 完整的 TypeScript 类型定义
- 🚀 **易于使用**: 简洁的 API 设计和工厂函数
- 🔄 **自动重试**: 内置错误处理和重试机制
- 📝 **完整日志**: 可配置的日志记录系统
- 🌐 **多区域支持**: 自动负载均衡的区域选择
- 🛡️ **安全认证**: 集成 Google OAuth2 访问令牌
- 📦 **模块化设计**: 可独立使用的组件

## 📦 安装

```bash
npm install @mixvideo/gemini
```

## 🚀 快速开始

### 1. 自动创建客户端（推荐）

```typescript
import { createAutoGeminiClient } from '@mixvideo/gemini';

// 自动获取访问令牌并创建客户端
const client = await createAutoGeminiClient();

// 生成文本
const response = await client.generateText(
  'gemini-2.5-flash',
  '你好，世界！'
);

console.log(response);
```

### 2. 手动创建客户端

```typescript
import { 
  createRemoteApiClient, 
  createGoogleGenaiClient 
} from '@mixvideo/gemini';

// 1. 创建远程 API 客户端
const remoteClient = createRemoteApiClient();

// 2. 获取访问令牌
const tokenResponse = await remoteClient.getGoogleAccessToken();

// 3. 创建 Generative AI 客户端
const genaiClient = createGoogleGenaiClient(tokenResponse.access_token);

// 4. 生成内容
const result = await genaiClient.generateContent('gemini-2.5-flash', [
  { role: 'user', parts: [{ text: '请介绍一下人工智能' }] }
]);
```

### 3. 批量创建客户端

```typescript
import { createGeminiClients } from '@mixvideo/gemini';

// 同时创建两个客户端
const { remoteClient, genaiClient, tokenInfo } = await createGeminiClients();

// 上传文件
await remoteClient.uploadFileToVertexAI({
  bucketName: 'my-bucket',
  filePrefix: 'uploads/',
  fileBuffer: fileBuffer
});

// 生成文本
const text = await genaiClient.generateText('gemini-2.5-flash', 'Hello!');
```

## 📚 API 文档

### 核心客户端

#### `RemoteApiClient`

用于与远程 Gemini API 服务通信的客户端。

```typescript
const client = createRemoteApiClient({
  baseUrl: 'https://api.example.com',
  bearerToken: 'your-token',
  timeout: 30000,
  enableLogging: true
});

// 获取访问令牌
const token = await client.getGoogleAccessToken();

// 上传文件
const uploadResult = await client.uploadFileToVertexAI({
  bucketName: 'my-bucket',
  filePrefix: 'uploads/',
  fileBuffer: buffer
});

// 健康检查
const health = await client.checkHealth();
```

#### `GoogleGenaiClient`

用于调用 Google Generative AI API 的客户端。

```typescript
const client = createGoogleGenaiClient(accessToken, {
  cloudflareProjectId: 'your-project-id',
  cloudflareGatewayId: 'your-gateway-id',
  googleProjectId: 'your-google-project',
  regions: ['us-central1', 'us-east1']
});

// 简单文本生成
const text = await client.generateText(
  'gemini-2.5-flash',
  '你好，请介绍一下自己',
  {
    temperature: 0.7,
    maxOutputTokens: 1024
  }
);

// 完整内容生成
const result = await client.generateContent(
  'gemini-2.5-flash',
  [
    { role: 'user', parts: [{ text: '我的名字是小明' }] },
    { role: 'model', parts: [{ text: '你好小明！' }] },
    { role: 'user', parts: [{ text: '你还记得我的名字吗？' }] }
  ],
  {
    temperature: 0.8,
    maxOutputTokens: 2048,
    topP: 0.9
  }
);
```

### 工厂函数

#### `createAutoGeminiClient()`

最简单的创建方式，自动处理所有配置。

```typescript
const client = await createAutoGeminiClient({
  enableLogging: true
}, {
  regions: ['us-central1']
});
```

#### `createGeminiClients()`

批量创建客户端，适合需要同时使用多个功能的场景。

```typescript
const { remoteClient, genaiClient, tokenInfo } = await createGeminiClients();
```

#### `validateClientConnections()`

验证客户端连接是否正常。

```typescript
const isValid = await validateClientConnections(remoteClient, genaiClient);
```

## ⚙️ 配置

### 环境变量

支持通过环境变量进行配置：

```bash
# 远程 API 基础 URL
GEMINI_API_BASE_URL=https://your-api.example.com

# Bearer 认证令牌
GEMINI_BEARER_TOKEN=your-bearer-token

# 请求超时时间（毫秒）
GEMINI_TIMEOUT=30000

# 是否启用日志
GEMINI_ENABLE_LOGGING=true
```

### 默认配置

```typescript
import { 
  DEFAULT_REMOTE_API_CONFIG,
  DEFAULT_GOOGLE_GENAI_CONFIG,
  SUPPORTED_GEMINI_MODELS 
} from '@mixvideo/gemini';

console.log('默认远程 API 配置:', DEFAULT_REMOTE_API_CONFIG);
console.log('默认 Google AI 配置:', DEFAULT_GOOGLE_GENAI_CONFIG);
console.log('支持的模型:', SUPPORTED_GEMINI_MODELS);
```

## 🔧 高级用法

### 自定义日志

```typescript
import { createLogger, LogLevel } from '@mixvideo/gemini';

const customLogger = createLogger({
  logLevel: 'debug',
  enableColors: true,
  prefix: '[MyApp]'
});

customLogger.info('自定义日志消息');
customLogger.error('错误信息', { details: 'error details' });
```

### 错误处理

```typescript
try {
  const result = await client.generateContent(modelId, contents);
  
  if (result.statusCode !== 200) {
    console.error('API 错误:', result.error);
    return;
  }
  
  console.log('生成成功:', result.response);
} catch (error) {
  console.error('网络错误:', error.message);
}
```

### 多轮对话

```typescript
const conversation = [
  { role: 'user', parts: [{ text: '你好' }] },
  { role: 'model', parts: [{ text: '你好！有什么可以帮助你的吗？' }] },
  { role: 'user', parts: [{ text: '请介绍一下 TypeScript' }] }
];

const result = await client.generateContent(
gemini-2.5-flash
  conversation
);
```

## 🧪 测试

运行测试套件：

```bash
npm test
```

测试包括：
- ✅ 自动创建客户端
- ✅ 批量创建客户端  
- ✅ 完整内容生成
- ✅ 连接验证
- ✅ 错误处理

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请联系 MixVideo 团队。
