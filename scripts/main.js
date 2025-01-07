<!-- index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>钱班文件下载</title>
  <!-- 引入外部CSS -->
  <link rel="stylesheet" href="styles/main.css">
</head>
<body>
  <h1>钱班文件下载</h1>
  
  <!-- 登录表单 -->
  <div id="login-form">
    <h2>登录</h2>
    <input type="text" id="username" placeholder="用户名" required>
    <input type="password" id="password" placeholder="密码" required>
    <button id="login-button">登录</button>
    <p id="error-message" class="error-message"></p>
  </div>

  <!-- 文件下载区域 -->
  <div id="download-section" style="display: none;">
    <h2>文件下载</h2>
    <!-- 导航路径 -->
    <div id="breadcrumb"></div>
    <!-- 文件和文件夹列表 -->
    <ul class="file-list">
      <!-- 文件和文件夹将由JS动态填充 -->
    </ul>
    <button onclick="logout()">登出</button>
  </div>

  <!-- 引入主脚本 -->
  <script src="scripts/main.js" type="module"></script>
</body>
</html>
