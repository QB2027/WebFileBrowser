import json
import base64
import ecies
import os

def encrypt_with_ecies(public_key_pem, aes_key):
    """
    使用 ECIES 加密 AES 密钥
    :param public_key_pem: 用户的 EC 公钥（PEM 格式字符串）
    :param aes_key: AES 密钥（字节数据）
    :return: Base64 编码的加密 AES 密钥
    """
    try:
        # 加载 EC 公钥
        public_key = ecies.utils.deserialize_public(public_key_pem.encode('utf-8'))

        # 使用 ECIES 加密 AES 密钥
        encrypted_aes_key = ecies.encrypt(public_key, aes_key)

        # 返回加密后的 AES 密钥（Base64 编码）
        return base64.b64encode(encrypted_aes_key).decode("utf-8")

    except Exception as e:
        raise ValueError(f"ECIES 加密失败，请检查公钥是否正确：{e}")

def main():
    try:
        # 加载用户公钥
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)

        # 加载 AES 密钥
        with open("files.json.enc", "rb") as f:
            encrypted_files = f.read()

        aes_key = base64.b64decode(encrypted_files[:44])  # 获取 AES 密钥的前 32 字节（解码）

        # 用每个用户的 EC 公钥加密 AES 密钥
        encrypted_keys = {}
        for username, public_key_pem in users.items():
            try:
                encrypted_key = encrypt_with_ecies(public_key_pem, aes_key)
                encrypted_keys[username] = encrypted_key
            except ValueError as e:
                print(f"跳过用户 {username} 的加密，原因：{e}")

        # 保存加密的 AES 密钥片段
        with open("encrypted_keys.json", "w", encoding="utf-8") as f:
            json.dump(encrypted_keys, f, ensure_ascii=False, indent=2)
        print("加密的 AES 密钥片段已生成：encrypted_keys.json")

    except Exception as e:
        print(f"发生错误：{e}")

if __name__ == "__main__":
    main()
