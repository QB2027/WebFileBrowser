// scripts/main.js

import { loadDirectory } from './directory.js';

let currentPath = ''; // 当前目录路径

// 登录函数
async function login() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const errorMessage = document.getElementById('error-message');

  try {
    // 获取 users.json
    const usersResponse = await fetch('users.json');
    if (!usersResponse.ok) {
      throw new Error('无法加载用户数据');
    }
    const users = await usersResponse.json();

    // 使用 SHA-256 对输入密码进行哈希
    const hashedPassword = await sha256(password);

    // 验证用户名和密码
    if (users[username] && users[username] === hashedPassword) {
      // 存储登录状态
      localStorage.setItem('authToken', 'authenticated');

      // 隐藏登录表单，显示下载区域
      document.getElementById('login-form').style.display = 'none';
      document.getElementById('download-section').style.display = 'block';

      // 获取并展示文件列表
      await loadDirectory(currentPath, updatePath);
    } else {
      errorMessage.innerText = '用户名或密码错误';
    }
  } catch (error) {
    console.error('Error:', error);
    errorMessage.innerText = '登录时出错，请稍后再试';
  }
}

// 登出函数
function logout() {
  // 清除登录状态
  localStorage.removeItem('authToken');

  // 隐藏下载区域，显示登录表单
  document.getElementById('download-section').style.display = 'none';
  document.getElementById('login-form').style.display = 'block';
}

// 更新路径并加载目录
async function updatePath(newPath) {
  currentPath = newPath;
  // 更新 URL without reloading
  window.history.pushState({}, '', `?path=${newPath}`);
  await loadDirectory(currentPath, updatePath);
}

// SHA-256 哈希函数
async function sha256(message) {
  // 转换为 UTF-8 编码
  const msgBuffer = new TextEncoder().encode(message);
  // 进行哈希
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  // 转换为十六进制字符串
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
}

// 初始化页面
function init() {
  const authToken = localStorage.getItem('authToken');
  if (authToken === 'authenticated') {
    // 如果已登录，显示下载区域
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('download-section').style.display = 'block';
    // 获取当前 URL 中 ?path= 指定的目录路径
    const params = new URLSearchParams(window.location.search);
    currentPath = params.get('path') || '';
    loadDirectory(currentPath, updatePath);
  }
}

// 监听认证状态变化
window.login = login;
window.logout = logout;

// 初始化页面加载
window.onload = init;
