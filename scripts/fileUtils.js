// scripts/fileUtils.js

/**
 * 过滤出指定 path 下的内容
 */
export function filterFilesByPath(files, path) {
  return files.filter(item => {
    const itemPath = item.path;
    if (path === '') {
      // 根目录下的文件和文件夹
      return !itemPath.includes('/') || itemPath.endsWith('/');
    } else {
      // 指定路径下的文件和文件夹
      return itemPath.startsWith(path) && (itemPath.split('/').filter(part => part).length === path.split('/').filter(part => part).length + (item.type === 'folder' ? 1 : 0));
    }
  });
}
