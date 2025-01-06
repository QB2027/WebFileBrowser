let config = {};

// 异步加载 config.json
export async function loadConfig() {
  const response = await fetch('./config.json');
  if (!response.ok) {
    throw new Error('Failed to load config.json');
  }
  config = await response.json();
}

// 获取已加载的配置信息
export function getConfig() {
  return config;
}