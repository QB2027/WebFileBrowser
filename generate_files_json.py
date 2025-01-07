import os
import json
import base64
import secrets
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def load_aes_key():
    """
    从环境变量中加载 AES 密钥。
    :return: AES 密钥（字节形式）
    """
    encryption_password = os.getenv("ENCRYPTION_PASSWORD")
    if not encryption_password:
        raise ValueError("环境变量 ENCRYPTION_PASSWORD 未设置")

    # 确保 AES 密钥长度为 32 字节（256 位）
    key = encryption_password.encode("utf-8")
    if len(key) != 32:
        raise ValueError("AES 密钥必须为 32 字节（256 位）")
    return key


def encrypt_aes(data, key):
    """
    使用 AES 加密数据。
    :param data: 待加密的字符串
    :param key: AES 密钥（字节形式，32 字节 = 256 位）
    :return: 加密后的 Base64 编码字符串
    """
    iv = secrets.token_bytes(16)  # 随机生成 IV
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data.encode("utf-8")) + encryptor.finalize()
    # 返回 Base64 编码的 IV + 加密数据
    return base64.b64encode(iv + encrypted_data).decode("utf-8")


def encrypt_with_rsa(public_key_pem, data):
    """
    使用 RSA 公钥加密数据。
    :param public_key_pem: RSA 公钥（PEM 格式字符串）
    :param data: 待加密的字节数据
    :return: 加密后的 Base64 编码字符串
    """
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    encrypted = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted).decode("utf-8")


def main():
    try:
        # 加载 AES 密钥
        aes_key = load_aes_key()

        # 加载文件列表并加密
        with open("files.json", "r", encoding="utf-8") as f:
            files_data = f.read()

        encrypted_files = encrypt_aes(files_data, aes_key)
        with open("files.json.enc", "w", encoding="utf-8") as f:
            f.write(encrypted_files)
        print("加密后的文件列表已生成：files.json.enc")

        # 加载用户的公钥
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)

        # 加密 AES 密钥片段并保存到 encrypted_keys.json
        encrypted_keys = {}
        for username, public_key_pem in users.items():
            encrypted_key = encrypt_with_rsa(public_key_pem, aes_key)
            encrypted_keys[username] = encrypted_key

        with open("encrypted_keys.json", "w", encoding="utf-8") as f:
            json.dump(encrypted_keys, f, ensure_ascii=False, indent=2)
        print("加密的 AES 密钥片段已生成：encrypted_keys.json")

    except Exception as e:
        print(f"发生错误：{e}")
        raise


if __name__ == "__main__":
    main()
