// scripts/cryptoUtils.js

/**
 * 解密数据
 * @param {string} encryptedData - Base64编码的加密数据（包含盐和IV）
 * @param {string} password - 用户密码
 * @returns {Promise<string>} - 解密后的数据
 */
export async function decryptData(encryptedData, password) {
  const backend = crypto.subtle;
  const binaryString = atob(encryptedData);
  const encryptedBytes = new Uint8Array([...binaryString].map(char => char.charCodeAt(0)));

  // 提取盐、IV和密文
  const salt = encryptedBytes.slice(0, 16);
  const iv = encryptedBytes.slice(16, 32);
  const ciphertext = encryptedBytes.slice(32);

  // 导入密码为原始密钥材料
  const keyMaterial = await backend.importKey(
    'raw',
    new TextEncoder().encode(password),
    { name: 'PBKDF2' },
    false,
    ['deriveKey']
  );

  // 使用 PBKDF2 派生出 AES-CFB 密钥
  const key = await backend.deriveKey(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: 100000,
      hash: 'SHA-256'
    },
    keyMaterial,
    { name: 'AES-CFB', length: 256 },
    false,
    ['decrypt']
  );

  // 解密
  const decrypted = await backend.decrypt(
    {
      name: 'AES-CFB',
      iv: iv
    },
    key,
    ciphertext
  );

  return new TextDecoder().decode(decrypted);
}
