// scripts/utils.js

/**
 * 获取当前 URL 中的 ?path= 值
 * @returns {string} - 当前目录路径
 */
export function getCurrentDirectory() {
  const params = new URLSearchParams(window.location.search);
  return params.get('path') || '';
}

/**
 * 从当前 path 中移除最后一级，得到上一级路径
 * @param {string} path - 当前目录路径
 * @returns {string} - 上一级目录路径
 */
export function getParentPath(path) {
  const segments = path.split('/').filter(Boolean);
  segments.pop(); // 移除最后一节
  return segments.join('/');
}
