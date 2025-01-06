import { filterFilesByPath, generateFileUrl } from './fileUtils.js';
import { getParentPath } from './utils.js';

/**
 * 加载并渲染指定路径下的所有文件（file）和文件夹（directory）
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
    container.innerHTML += `<li class="back-button"><a href="?path=${parentPath}">../</a></li>`;
  }

  // 生成并插入文件 / 目录列表
  container.innerHTML += generateFileList(directoryContent, path);
}

/**
 * 根据当前目录文件数据生成 HTML 列表
 */
function generateFileList(files, basePath) {
  let html = '';

  files.forEach(item => {
    if (item.type === 'file') {
      const fileUrl = generateFileUrl(item.path);
      html += `<li class="file-item"><a href="${fileUrl}" target="_blank">${item.name}</a></li>`;
    } else if (item.type === 'directory') {
      const subPath = basePath ? `${basePath}/${item.name}` : item.name;
      html += `<li class="directory-item"><a href="?path=${subPath}">${item.name}/</a></li>`;
    }
  });

  return html;
}