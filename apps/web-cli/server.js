import { createServer } from 'http';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create HTTP server
const server = createServer((req, res) => {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    const url = new URL(req.url, `http://${req.headers.host}`);

    // Handle API execute endpoint
    if (url.pathname === '/api/execute' && req.method === 'POST') {
        handleExecuteCommand(req, res);
        return;
    }

    // Serve static files
    if (url.pathname === '/' || url.pathname === '/index.html') {
        serveFile(res, path.join(__dirname, 'index.html'), 'text/html');
    } else if (url.pathname === '/script.js') {
        serveFile(res, path.join(__dirname, 'script.js'), 'application/javascript');
    } else if (url.pathname === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: 'ok',
            timestamp: new Date().toISOString()
        }));
    } else if (url.pathname === '/api/directories') {
        handleGetDirectories(req, res);
    } else {
        res.writeHead(404);
        res.end('Not Found');
    }
});

// Helper function to serve files
function serveFile(res, filePath, contentType) {
    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(500);
            res.end('Internal Server Error');
            return;
        }
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(data);
    });
}

// Handle command execution endpoint
function handleExecuteCommand(req, res) {
    let body = '';

    req.on('data', chunk => {
        body += chunk.toString();
    });

    req.on('end', async () => {
        try {
            const { command, args } = JSON.parse(body);
            console.log(`🚀 收到命令请求: ${command}`, args);

            const result = await executeCliCommand(command, args);

            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(result));
        } catch (error) {
            console.error('❌ 命令执行错误:', error);
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                error: error.message,
                success: false
            }));
        }
    });

    req.on('error', (error) => {
        console.error('❌ 请求错误:', error);
        if (!res.headersSent) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                error: 'Bad Request',
                success: false
            }));
        }
    });
}

// Handle get directories endpoint
function handleGetDirectories(req, res) {
    try {
        const projectRoot = path.join(__dirname, '../..');
        const outputsDir = path.join(projectRoot, 'outputs');

        let directories = [];

        // Check if outputs directory exists
        if (fs.existsSync(outputsDir)) {
            const items = fs.readdirSync(outputsDir, { withFileTypes: true });
            directories = items
                .filter(item => item.isDirectory())
                .map(item => ({
                    name: item.name,
                    path: `outputs/${item.name}`,
                    fullPath: path.join(outputsDir, item.name)
                }));
        }

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            projectRoot,
            directories,
            suggestions: [
                'outputs/产品使用',
                'outputs/产品展示',
                'outputs/生活场景',
                'outputs/模特实拍'
            ]
        }));
    } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: error.message }));
    }
}

// Execute CLI command
async function executeCliCommand(command, args = {}) {
    return new Promise((resolve, reject) => {
        try {
            // Build command arguments
            const cliArgs = buildCliArgs(command, args);

            // Set working directory to project root
            const projectRoot = path.join(__dirname, '../..');

            console.log(`🚀 执行命令: mixvideo ${cliArgs.join(' ')}`);
            console.log(`📁 工作目录: ${projectRoot}`);

            // Validate paths if they exist in args
            if (args.source || args.path) {
                const targetPath = args.source || args.path;
                const fullPath = path.isAbsolute(targetPath) ? targetPath : path.join(projectRoot, targetPath);
                console.log(`🔍 检查路径: ${fullPath}`);

                // Check if path exists
                if (!fs.existsSync(fullPath)) {
                    console.log(`⚠️ 路径不存在: ${fullPath}`);
                    console.log(`💡 提示: 请确保路径相对于项目根目录 ${projectRoot}`);
                }
            }

            // Spawn the CLI process from the project root directory
            const child = spawn('mixvideo', cliArgs, {
                stdio: ['pipe', 'pipe', 'pipe'],
                shell: true,
                cwd: projectRoot
            });

            let stdout = '';
            let stderr = '';

            // Handle stdout
            child.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            // Handle stderr
            child.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            // Handle process completion
            child.on('close', (code) => {
                resolve({
                    exitCode: code,
                    stdout: stdout.trim(),
                    stderr: stderr.trim(),
                    success: code === 0
                });
            });

            // Handle process error
            child.on('error', (error) => {
                reject(new Error(`进程错误: ${error.message}`));
            });

        } catch (error) {
            reject(new Error(`命令执行失败: ${error.message}`));
        }
    });
}

// Build CLI arguments from command and args
function buildCliArgs(command, args) {
    const cliArgs = [];
    
    switch (command) {
        case 'login':
            cliArgs.push('login');
            if (args.username) cliArgs.push('-u', args.username);
            if (args.password) cliArgs.push('-p', args.password);
            break;
            
        case 'logout':
            cliArgs.push('logout');
            break;
            
        case 'analyze':
            cliArgs.push('analyze', args.path);
            if (args.output) cliArgs.push('-o', args.output);
            break;
            
        case 'organize':
            cliArgs.push('organize', args.source, args.target);
            if (args.backup) cliArgs.push('--backup');
            break;
            
        case 'generate':
            cliArgs.push('generate', 'from-videos', args.source);
            if (args.output) cliArgs.push('-o', args.output);
            if (args.title) cliArgs.push('--title', args.title);
            break;
            
        case 'generate-draft':
            cliArgs.push('generate', 'from-videos', args.source);
            cliArgs.push('--draft-dir');
            if (args.title) cliArgs.push('--title', args.title);
            break;
            
        default:
            throw new Error(`未知命令: ${command}`);
    }
    
    return cliArgs;
}

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
    console.log(`🚀 MixVideo CLI Web Interface 服务器启动`);
    console.log(`📱 访问地址: http://localhost:${PORT}`);
});
