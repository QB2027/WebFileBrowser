import { getConfig } from './config.js';

/**
 * 递归过滤出指定 path 下的内容
 */
export function filterFilesByPath(files, path) {
  const segments = path.split('/').filter(Boolean);
  let current = files;

  for (const segment of segments) {
    const match = current.find(
      (item) => item.name === segment && item.type === 'directory'
    );
    if (match && match.children) {
      current = match.children;
    } else {
      // 如果路径不存在则返回空数组
      return [];
    }
  }
  return current;
}

/**
 * 根据 config.json 中的配置信息，拼出 GitHub Raw 文件 URL
 */
export function generateFileUrl(filePath) {
  const { repoOwner, repoName, branch } = getConfig();
  const baseUrl = `https://raw.githubusercontent.com/${repoOwner}/${repoName}/${branch}`;
  return `${baseUrl}/${filePath}`;
}