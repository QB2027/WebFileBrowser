import { loadConfig } from './config.js';
import { loadDirectory } from './directory.js';
import { getCurrentDirectory } from './utils.js';

async function init() {
  try {
    // 加载 GitHub 仓库配置信息
    await loadConfig();
    
    // 获取当前 URL 中 ?path= 指定的目录路径
    const currentDirectory = getCurrentDirectory();
    
    // 加载并展示当前目录内容
    await loadDirectory(currentDirectory);
  } catch (error) {
    console.error('Error:', error);
    document.querySelector('.file-list').innerHTML = '<li>Error loading directory.</li>';
  }
}

// 初始化
init();