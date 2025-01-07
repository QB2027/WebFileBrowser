async function decryptFiles() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
        document.getElementById("output").textContent = "请填写用户名和密码！";
        return;
    }

    try {
        // 根据密码生成私钥
        const seed = generateSeed(password);
        const keyPair = nacl.sign.keyPair.fromSeed(seed);

        // 加载加密的文件列表
        const encryptedFilesResponse = await fetch("files.json.enc");
        const encryptedFiles = await encryptedFilesResponse.text();

        // 加载加密的 AES 密钥片段
        const encryptedKeysResponse = await fetch("encrypted_keys.json");
        const encryptedKeys = await encryptedKeysResponse.json();

        // 检查用户的加密 AES 密钥片段
        const encryptedKey = encryptedKeys[username];
        if (!encryptedKey) {
            document.getElementById("output").textContent = "用户不存在或没有对应的加密密钥片段！";
            return;
        }

        // 解密 AES 密钥
        const aesKey = decryptRSA(keyPair.secretKey, encryptedKey);

        // 解密文件列表
        const files = decryptAES(encryptedFiles, aesKey);

        // 显示解密后的文件列表
        document.getElementById("output").textContent = JSON.stringify(files, null, 2);
    } catch (error) {
        console.error(error);
        document.getElementById("output").textContent = "解密失败，请检查用户名和密码是否正确！";
    }
}

function generateSeed(password) {
    /**
     * 根据用户密码生成固定种子（SHA-256 哈希）
     */
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = nacl.hash(data);
    return new Uint8Array(hashBuffer.slice(0, 32));
}

function decryptRSA(secretKey, encryptedKey) {
    /**
     * 使用 Ed25519 私钥解密加密的 AES 密钥
     */
    const encryptedKeyBytes = nacl.util.decodeBase64(encryptedKey);
    const decrypted = nacl.sign.open(encryptedKeyBytes, secretKey);
    if (!decrypted) {
        throw new Error("解密失败！");
    }
    return nacl.util.encodeUTF8(decrypted);
}

function decryptAES(encryptedData, aesKey) {
    /**
     * 模拟 AES 解密文件列表（需替换为实际 AES 解密逻辑）
     */
    return JSON.parse(atob(encryptedData));
}
