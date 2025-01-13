import json
import os
import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_der_public_key


def load_users(file_path):
    """
    加载 users.json 文件
    :param file_path: 文件路径
    :return: 用户数据字典
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def encrypt_aes_key_with_rsa(aes_key, public_key_der):
    """
    使用 RSA 公钥加密 AES 密钥
    :param aes_key: 要加密的 AES 密钥（二进制）
    :param public_key_der: 公钥的 DER 编码（二进制）
    :return: 加密后的 AES 密钥（Base64 编码）
    """
    public_key = load_der_public_key(public_key_der)
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted_key).decode('utf-8')


def main():
    # 从环境变量中获取 Base64 编码的 AES 密钥
    aes_key_base64 = os.getenv("ENCRYPTION_PASSWORD")
    if not aes_key_base64:
        raise ValueError("环境变量 ENCRYPTION_PASSWORD 未设置")

    # 解码 AES 密钥为二进制
    aes_key = base64.b64decode(aes_key_base64)

    # 加载 users.json 文件
    users = load_users("users.json")

    output_data = {}

    for user_id, user_data in users.items():
        public_key_b64 = user_data.get("pub")
        private_key_enc = user_data.get("priv_enc")  # 获取加密的私钥

        if not public_key_b64:
            raise ValueError(f"用户 {user_id} 缺少公钥")

        if not private_key_enc:
            raise ValueError(f"用户 {user_id} 缺少加密的私钥")

        # 解码公钥为二进制
        public_key_der = base64.b64decode(public_key_b64)

        # 使用 RSA 公钥加密 AES 密钥
        encrypted_aes_key = encrypt_aes_key_with_rsa(aes_key, public_key_der)

        # 保存加密结果
        output_data[user_id] = {
            "enc_aes_key": encrypted_aes_key,
            "priv_enc": private_key_enc  # 直接复制加密的私钥
        }

    # 写入加密结果到 users_enc_aes_key.json
    with open("users_enc_aes_key.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("加密完成，结果已保存到 users_enc_aes_key.json")


if __name__ == "__main__":
    main()
