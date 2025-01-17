import hashlib
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def decrypt_aes256(encrypted_data, key):
    """
    使用 AES256 解密数据
    :param encrypted_data: 要解密的字节数据
    :param key: 密钥字符串
    :return: 解密后的字节数据
    """
    # 使用 SHA-256 对输入的字符串密钥进行哈希，得到 256 位（32 字节）密钥
    aes_key = hashlib.sha256(key.encode('utf-8')).digest()

    # 提取 IV（前 16 字节）和密文
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    # 创建 AES256 解密器
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # 解密数据
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    # 去除 PKCS7 填充
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return unpadded_data

# 解密文件并保存为原始文件
def decrypt_and_save(input_file, output_file, password):
    # 读取加密文件
    with open(input_file, 'rb') as f:
        encrypted_data = f.read()

    # 解密
    decrypted_data = decrypt_aes256(encrypted_data, password)

    # 将解密后的数据保存到文件
    with open(output_file, 'wb') as f:
        f.write(decrypted_data)

    print(f"文件解密成功，保存为: {output_file}")

# 解密过程
input_file = 'files.json.enc'
output_file = 'files.json'
password = '1234'

decrypt_and_save(input_file, output_file, password)
