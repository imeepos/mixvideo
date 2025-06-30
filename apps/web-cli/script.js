// Simple HTTP-based command execution
let isConnected = true;

// Update connection status indicator
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    const dot = statusElement.querySelector('div');
    const text = statusElement.querySelector('span');

    if (connected) {
        dot.className = 'w-3 h-3 bg-green-400 rounded-full';
        text.textContent = 'Connected';
    } else {
        dot.className = 'w-3 h-3 bg-red-400 rounded-full';
        text.textContent = 'Disconnected';
    }
}

// Add message to terminal output
function addToOutput(message, level = 'info') {
    const output = document.getElementById('terminal-output');
    const timestamp = new Date().toLocaleTimeString();
    
    const colors = {
        info: 'text-blue-400',
        success: 'text-green-400',
        error: 'text-red-400',
        warning: 'text-yellow-400'
    };
    
    const div = document.createElement('div');
    div.className = `${colors[level] || 'text-gray-400'} mb-1`;
    div.innerHTML = `<span class="text-gray-500">[${timestamp}]</span> ${message}`;
    
    output.appendChild(div);
    output.scrollTop = output.scrollHeight;
}

// Clear terminal output
function clearOutput() {
    const output = document.getElementById('terminal-output');
    output.innerHTML = '<div class="text-green-400">MixVideo CLI Web Interface Ready...</div>';
}

// Show/hide loading overlay
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.toggle('hidden', !show);
}

// Show command forms
function showCommandForm(formHtml) {
    const container = document.getElementById('command-forms');
    container.innerHTML = formHtml;
    container.classList.remove('hidden');
    container.scrollIntoView({ behavior: 'smooth' });
}

// Hide command forms
function hideCommandForm() {
    const container = document.getElementById('command-forms');
    container.classList.add('hidden');
}

// Execute command via HTTP
async function executeCommand(command, args = {}) {
    showLoading(true);
    addToOutput(`🚀 开始执行命令: ${command}`, 'info');

    try {
        const response = await fetch('/api/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command, args })
        });

        const result = await response.json();

        if (result.success) {
            addToOutput(`✅ 命令执行完成`, 'success');
            if (result.stdout) {
                addToOutput(result.stdout, 'info');
            }
        } else {
            addToOutput(`❌ 命令执行失败 (退出码: ${result.exitCode})`, 'error');
            if (result.stderr) {
                addToOutput(result.stderr, 'error');
            }
        }
    } catch (error) {
        addToOutput(`❌ 请求失败: ${error.message}`, 'error');
    } finally {
        showLoading(false);
        hideCommandForm();
    }
}

// Show login form
function showLoginForm() {
    const formHtml = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-semibold mb-4">
                <i class="fas fa-sign-in-alt mr-2"></i>用户登录
            </h3>
            <form onsubmit="handleLogin(event)" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">用户名</label>
                    <input type="text" id="username" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           placeholder="请输入用户名">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
                    <input type="password" id="password" required 
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                           placeholder="请输入密码">
                </div>
                <div class="flex space-x-3">
                    <button type="submit" class="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded-lg transition-colors">
                        <i class="fas fa-sign-in-alt mr-2"></i>登录
                    </button>
                    <button type="button" onclick="hideCommandForm()" class="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors">
                        取消
                    </button>
                </div>
            </form>
        </div>
    `;
    showCommandForm(formHtml);
}

// Handle login form submission
function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    executeCommand('login', { username, password });
}

// Show analyze form
function showAnalyzeForm() {
    const formHtml = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-semibold mb-4">
                <i class="fas fa-brain mr-2"></i>视频分析
            </h3>
            <form onsubmit="handleAnalyze(event)" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">视频目录路径</label>
                    <div class="flex">
                        <input type="text" id="analyze-path" required
                               class="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                               placeholder="例如: ./videos 或 outputs/产品使用">
                    </div>
                    <div id="analyze-path-display"></div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">输出目录</label>
                    <div class="flex">
                        <input type="text" id="analyze-output"
                               class="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                               placeholder="默认: ./analyzed (可选)">
                    </div>
                    <div id="analyze-output-display"></div>
                </div>
                <div class="flex space-x-3">
                    <button type="submit" class="flex-1 bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-lg transition-colors">
                        <i class="fas fa-brain mr-2"></i>开始分析
                    </button>
                    <button type="button" onclick="hideCommandForm()" class="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors">
                        取消
                    </button>
                </div>
            </form>
        </div>
    `;
    showCommandForm(formHtml);

    // Initialize directory selectors after form is shown
    setTimeout(() => {
        createDirectorySelector('analyze-path', 'analyze-path-display');
        createDirectorySelector('analyze-output', 'analyze-output-display', { isOutput: true });
    }, 100);
}

// Handle analyze form submission
function handleAnalyze(event) {
    event.preventDefault();
    const path = document.getElementById('analyze-path').value;
    const output = document.getElementById('analyze-output').value;

    const args = { path };
    if (output) args.output = output;

    executeCommand('analyze', args);
}

// Show organize form
function showOrganizeForm() {
    const formHtml = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-semibold mb-4">
                <i class="fas fa-folder-open mr-2"></i>视频整理
            </h3>
            <form onsubmit="handleOrganize(event)" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">源视频目录</label>
                    <div class="flex">
                        <input type="text" id="organize-source" required
                               class="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                               placeholder="例如: ./videos">
                    </div>
                    <div id="organize-source-display"></div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">目标目录</label>
                    <div class="flex">
                        <input type="text" id="organize-target" required
                               class="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                               placeholder="例如: ./organized">
                    </div>
                    <div id="organize-target-display"></div>
                </div>
                <div class="flex items-center space-x-2">
                    <input type="checkbox" id="organize-backup" class="rounded">
                    <label for="organize-backup" class="text-sm text-gray-700">创建备份</label>
                </div>
                <div class="flex space-x-3">
                    <button type="submit" class="flex-1 bg-teal-500 hover:bg-teal-600 text-white py-2 px-4 rounded-lg transition-colors">
                        <i class="fas fa-folder-open mr-2"></i>开始整理
                    </button>
                    <button type="button" onclick="hideCommandForm()" class="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors">
                        取消
                    </button>
                </div>
            </form>
        </div>
    `;
    showCommandForm(formHtml);

    // Initialize directory selectors after form is shown
    setTimeout(() => {
        createDirectorySelector('organize-source', 'organize-source-display');
        createDirectorySelector('organize-target', 'organize-target-display', { isOutput: true });
    }, 100);
}

// Handle organize form submission
function handleOrganize(event) {
    event.preventDefault();
    const source = document.getElementById('organize-source').value;
    const target = document.getElementById('organize-target').value;
    const backup = document.getElementById('organize-backup').checked;

    const args = { source, target };
    if (backup) args.backup = true;

    executeCommand('organize', args);
}

// Show generate form
function showGenerateForm() {
    const formHtml = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-semibold mb-4">
                <i class="fas fa-file-video mr-2"></i>生成剪映项目
            </h3>
            <form onsubmit="handleGenerate(event)" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">视频目录</label>
                    <div class="flex">
                        <input type="text" id="generate-source" required
                               class="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                               placeholder="例如: outputs/产品使用">
                    </div>
                    <div id="generate-source-display"></div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">输出文件名</label>
                    <input type="text" id="generate-output"
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                           placeholder="默认: draft_content.json">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">项目标题</label>
                    <input type="text" id="generate-title"
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                           placeholder="默认: 视频项目">
                </div>
                <div class="flex space-x-3">
                    <button type="submit" class="flex-1 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded-lg transition-colors">
                        <i class="fas fa-file-video mr-2"></i>生成项目
                    </button>
                    <button type="button" onclick="hideCommandForm()" class="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors">
                        取消
                    </button>
                </div>
            </form>
        </div>
    `;
    showCommandForm(formHtml);

    // Initialize directory selector after form is shown
    setTimeout(() => {
        createDirectorySelector('generate-source', 'generate-source-display');
    }, 100);
}

// Handle generate form submission
function handleGenerate(event) {
    event.preventDefault();
    const source = document.getElementById('generate-source').value;
    const output = document.getElementById('generate-output').value;
    const title = document.getElementById('generate-title').value;

    const args = { source };
    if (output) args.output = output;
    if (title) args.title = title;

    executeCommand('generate', args);
}

// Show generate draft form
function showGenerateDraftForm() {
    const formHtml = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-semibold mb-4">
                <i class="fas fa-drafting-compass mr-2"></i>生成草稿项目
            </h3>
            <form onsubmit="handleGenerateDraft(event)" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">视频目录</label>
                    <div class="flex">
                        <input type="text" id="draft-source" required
                               class="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                               placeholder="例如: outputs/产品使用">
                    </div>
                    <div id="draft-source-display"></div>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">项目标题</label>
                    <input type="text" id="draft-title" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                           placeholder="例如: 产品展示视频">
                </div>
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <div class="flex items-center">
                        <i class="fas fa-info-circle text-blue-500 mr-2"></i>
                        <span class="text-sm text-blue-700">项目将直接创建在剪映草稿目录中，重启剪映即可使用</span>
                    </div>
                </div>
                <div class="flex space-x-3">
                    <button type="submit" class="flex-1 bg-indigo-500 hover:bg-indigo-600 text-white py-2 px-4 rounded-lg transition-colors">
                        <i class="fas fa-drafting-compass mr-2"></i>生成草稿
                    </button>
                    <button type="button" onclick="hideCommandForm()" class="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors">
                        取消
                    </button>
                </div>
            </form>
        </div>
    `;
    showCommandForm(formHtml);

    // Initialize directory selector after form is shown
    setTimeout(() => {
        createDirectorySelector('draft-source', 'draft-source-display');
    }, 100);
}

// Handle generate draft form submission
function handleGenerateDraft(event) {
    event.preventDefault();
    const source = document.getElementById('draft-source').value;
    const title = document.getElementById('draft-title').value;

    const args = { source, title, draftDir: true };

    executeCommand('generate-draft', args);
}

// Directory selection functionality
function createDirectorySelector(inputId, displayId, options = {}) {
    const input = document.getElementById(inputId);
    const display = document.getElementById(displayId);

    if (!input || !display) return;

    const isOutputDir = options.isOutput || inputId.includes('output') || inputId.includes('target');

    // Create file input for directory selection
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.webkitdirectory = true;
    fileInput.multiple = true;
    fileInput.style.display = 'none';

    // Create browse button
    const browseBtn = document.createElement('button');
    browseBtn.type = 'button';
    browseBtn.className = 'ml-2 px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded transition-colors';
    browseBtn.innerHTML = '<i class="fas fa-folder-open mr-1"></i>浏览';

    // Create new folder button for output directories
    let newFolderBtn = null;
    if (isOutputDir) {
        newFolderBtn = document.createElement('button');
        newFolderBtn.type = 'button';
        newFolderBtn.className = 'ml-2 px-3 py-1 bg-green-500 hover:bg-green-600 text-white text-sm rounded transition-colors';
        newFolderBtn.innerHTML = '<i class="fas fa-plus mr-1"></i>新建';
        newFolderBtn.title = '输入新目录名称';
    }

    // Insert buttons after input
    input.parentNode.insertBefore(browseBtn, input.nextSibling);
    if (newFolderBtn) {
        input.parentNode.insertBefore(newFolderBtn, browseBtn.nextSibling);
        input.parentNode.insertBefore(fileInput, newFolderBtn.nextSibling);
    } else {
        input.parentNode.insertBefore(fileInput, browseBtn.nextSibling);
    }

    // Handle browse button click
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle new folder button click
    if (newFolderBtn) {
        newFolderBtn.addEventListener('click', () => {
            const folderName = prompt('请输入新目录名称:', 'output');
            if (folderName && folderName.trim()) {
                const cleanName = folderName.trim().replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]/g, '_');
                input.value = `./${cleanName}`;

                if (display) {
                    display.innerHTML = `
                        <div class="text-sm text-blue-600 mt-1">
                            <i class="fas fa-folder-plus mr-1"></i>
                            将创建新目录: ${cleanName}
                        </div>
                    `;
                }

                addToOutput(`📁 将创建新目录: ${cleanName}`, 'info');
            }
        });
    }

    // Handle directory selection
    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            // Get the full directory path
            const firstFile = files[0];
            const pathParts = firstFile.webkitRelativePath.split('/');
            const directoryName = pathParts[0];

            // Try to get the full path from the file object
            let fullPath = directoryName;
            if (firstFile.path) {
                // Extract directory path from file path
                const filePath = firstFile.path;
                const dirPath = filePath.substring(0, filePath.lastIndexOf('/'));
                fullPath = dirPath;
            }

            // Update input value with directory path
            input.value = fullPath;

            if (isOutputDir) {
                // For output directories, just show the selected directory
                if (display) {
                    display.innerHTML = `
                        <div class="text-sm text-green-600 mt-1">
                            <i class="fas fa-check-circle mr-1"></i>
                            已选择目录: ${directoryName}
                        </div>
                        <div class="text-xs text-gray-500 mt-1">
                            完整路径: ${fullPath}
                        </div>
                    `;
                }
                addToOutput(`📁 已选择输出目录: ${fullPath}`, 'success');
            } else {
                // For source directories, show video file count
                const videoFiles = files.filter(file =>
                    /\.(mp4|mov|avi|mkv|wmv|flv|webm)$/i.test(file.name)
                );

                if (display) {
                    display.innerHTML = `
                        <div class="text-sm text-green-600 mt-1">
                            <i class="fas fa-check-circle mr-1"></i>
                            已选择目录: ${directoryName} (包含 ${videoFiles.length} 个视频文件)
                        </div>
                        <div class="text-xs text-gray-500 mt-1">
                            完整路径: ${fullPath}
                        </div>
                    `;
                }

                addToOutput(`📁 已选择目录: ${fullPath}，包含 ${videoFiles.length} 个视频文件`, 'success');
            }
        }
    });
}

// Load directory suggestions
async function loadDirectorySuggestions() {
    try {
        const response = await fetch('/api/directories');
        const data = await response.json();

        if (data.directories && data.directories.length > 0) {
            addToOutput(`💡 可用的视频目录: ${data.directories.map(d => d.path).join(', ')}`, 'info');
        }

        return data;
    } catch (error) {
        console.error('获取目录建议失败:', error);
        return null;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateConnectionStatus(true);
    addToOutput('🎉 MixVideo CLI Web Interface Ready', 'success');

    // Load directory suggestions
    loadDirectorySuggestions();
});
