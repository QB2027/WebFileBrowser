// scripts/main.js

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
      await fetchFiles();
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

// 获取并展示文件列表
async function fetchFiles() {
  try {
    const response = await fetch('files.json');
    if (!response.ok) {
      throw new Error('无法加载文件列表');
    }
    const files = await response.json();
    displayFiles(files, currentPath);
  } catch (error) {
    console.error('Error:', error);
    document.querySelector('.file-list').innerHTML = '<li>加载文件列表时出错。</li>';
  }
}

// 显示文件和文件夹列表
function displayFiles(files, path) {
  const container = document.querySelector('.file-list');
  const breadcrumb = document.getElementById('breadcrumb');
  container.innerHTML = '';
  breadcrumb.innerHTML = '';

  // 生成导航路径
  const pathParts = path.split('/').filter(part => part);
  let accumulatedPath = '';
  const breadcrumbList = [];

  // 添加“首页”链接
  breadcrumbList.push({ name: '首页', path: '' });

  pathParts.forEach(part => {
    accumulatedPath += part + '/';
    breadcrumbList.push({ name: part, path: accumulatedPath });
  });

  // 渲染导航路径
  breadcrumbList.forEach((crumb, index) => {
    const crumbLink = document.createElement('a');
    crumbLink.href = '#';
    crumbLink.innerText = crumb.name;
    crumbLink.addEventListener('click', (e) => {
      e.preventDefault();
      currentPath = crumb.path;
      fetchFiles();
    });
    breadcrumb.appendChild(crumbLink);
    if (index < breadcrumbList.length - 1) {
      const separator = document.createElement('span');
      separator.innerText = ' / ';
      breadcrumb.appendChild(separator);
    }
  });

  // 过滤当前目录下的文件和文件夹
  const items = files.filter(item => {
    const itemPath = item.path;
    if (currentPath === '') {
      return !itemPath.includes('/') || itemPath.indexOf('/') === itemPath.length - 1;
    }
    return itemPath.startsWith(currentPath) && itemPath.split('/').filter(part => part).length === currentPath.split('/').filter(part => part).length + (item.type === 'folder' ? 1 : 0);
  });

  // 处理文件夹和文件
  items.forEach(item => {
    const listItem = document.createElement('li');
    listItem.classList.add('file-item');

    if (item.type === 'folder') {
      listItem.innerHTML = `<span class="folder" data-path="${item.path}">📁 ${item.name}</span>`;
      listItem.querySelector('.folder').addEventListener('click', () => {
        currentPath = item.path.endsWith('/') ? item.path : item.path + '/';
        fetchFiles();
      });
    } else if (item.type === 'file') {
      listItem.innerHTML = `<span>📄 ${item.name}</span> <a href="${item.url}" target="_blank">下载</a>`;
    }

    container.appendChild(listItem);
  });
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
    fetchFiles();
  }
}

// 监听认证状态变化
window.login = login;
window.logout = logout;

// 初始化页面加载
window.onload = init;
