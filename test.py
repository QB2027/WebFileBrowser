import ecies

# 生成密钥对
private_key = ecies.utils.generate_private_key()
public_key = ecies.utils.private_key_to_public_key(private_key)

# 待加密的消息
message = b"Hello, this is a secret message!"

# 使用公钥加密数据
encrypted_message = ecies.encrypt(public_key, message)
print(f"Encrypted Message (hex): {encrypted_message.hex()}")  # 以16进制显示加密后的消息

# 使用私钥解密数据
decrypted_message = ecies.decrypt(private_key, encrypted_message)
print(f"Decrypted Message: {decrypted_message.decode()}")

# 打印公钥和私钥的字节表示，供后续分析
print(f"Private Key (hex): {private_key.hex()}")
print(f"Public Key (hex): {public_key.hex()}")
