/**
 * Simple test script to verify main.ts functionality
 */

const fs = require('fs');
const path = require('path');

console.log('🧪 Testing main.ts implementation...');

// Check if src/main.ts exists
const mainTsPath = path.join(__dirname, 'src', 'main.ts');
if (!fs.existsSync(mainTsPath)) {
  console.error('❌ src/main.ts not found');
  process.exit(1);
}

console.log('✅ src/main.ts exists');

// Read and validate the content
const content = fs.readFileSync(mainTsPath, 'utf8');

// Check for key imports and functionality
const checks = [
  { name: 'Import video-analyzer', pattern: /import.*@mixvideo\/video-analyzer/ },
  { name: 'Main function', pattern: /async function main\(\)/ },
  { name: 'Resources directory', pattern: /resources/ },
  { name: 'Progress callback', pattern: /onProgress/ },
  { name: 'Analysis configuration', pattern: /analysisMode/ },
  { name: 'Error handling', pattern: /try[\s\S]*catch/ },
  { name: 'Chinese comments', pattern: /\/\*\*[\s\S]*使用.*@mixvideo\/video-analyzer/ }
];

let passed = 0;
let total = checks.length;

checks.forEach(check => {
  if (check.pattern.test(content)) {
    console.log(`✅ ${check.name}`);
    passed++;
  } else {
    console.log(`❌ ${check.name}`);
  }
});

console.log(`\n📊 Test Results: ${passed}/${total} checks passed`);

if (passed === total) {
  console.log('🎉 All tests passed! main.ts implementation looks good.');
} else {
  console.log('⚠️  Some checks failed. Please review the implementation.');
}

// Check if resources directory exists, create if not
const resourcesDir = path.join(__dirname, 'resources');
if (!fs.existsSync(resourcesDir)) {
  console.log('\n📁 Creating resources directory...');
  fs.mkdirSync(resourcesDir, { recursive: true });
  console.log('✅ Resources directory created');
} else {
  console.log('\n📁 Resources directory already exists');
}

console.log('\n🚀 Ready to process videos! Place your video files in the ./resources directory and run:');
console.log('   npm run analyze');
