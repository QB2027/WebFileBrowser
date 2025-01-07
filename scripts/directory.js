// scripts/directory.js

import { filterFilesByPath } from './fileUtils.js';
import { getParentPath } from './utils.js';

/**
 * 加载并渲染指定路径下的所有文件（file）和文件夹（folder）
 */
export async function loadDirectory(path) {
  const response = await fetch('./files.json');
  if (!response.ok) {
    throw new Error('Failed to load files.json');
  }
  const files = await response.json();

  const container = document.querySelector('.file-list');
  const directoryContent = filterFilesByPath(files, path);

  // 清空当前列表内容
  container.innerHTML = '';

  // 如果不在根目录，显示返回上一级的按钮
  if (path) {
    const parentPath = getParentPath(path);
    const backButton = document.createElement('li');
    backButton.classList.add('back-button');
    backButton.innerHTML = `<a href="?path=${parentPath}">📂 ../</a>`;
    backButton.querySelector('a').addEventListener('click', (e) => {
      e.preventDefault();
      window.history.pushState({}, '', `?path=${parentPath}`);
      currentPath = parentPath;
      fetchFiles();
    });
    container.appendChild(backButton);
  }

  // 生成并插入文件 / 文件夹列表
  directoryContent.forEach(item => {
    const listItem = document.createElement('li');
    listItem.classList.add(item.type === 'folder' ? 'directory-item' : 'file-item');

    if (item.type === 'folder') {
      listItem.innerHTML = `<span class="folder">📁 ${item.name}</span>`;
      listItem.querySelector('.folder').addEventListener('click', () => {
        currentPath = item.path.endsWith('/') ? item.path : item.path + '/';
        window.history.pushState({}, '', `?path=${currentPath}`);
        fetchFiles();
      });
    } else if (item.type === 'file') {
      listItem.innerHTML = `<span>📄 ${item.name}</span> <a href="${item.url}" target="_blank">下载</a>`;
    }

    container.appendChild(listItem);
  });
}
