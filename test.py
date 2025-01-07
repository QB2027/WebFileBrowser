import ecies

# 生成以太坊密钥对
private_key = ecies.utils.generate_eth_key()
public_key = private_key.public_key()

# 待加密的消息
message = b"Hello, this is a secret message!"

# 使用公钥加密数据
encrypted_message = ecies.encrypt(public_key, message)
print(f"Encrypted Message: {encrypted_message}")

# 使用私钥解密数据
decrypted_message = ecies.decrypt(private_key, encrypted_message)
print(f"Decrypted Message: {decrypted_message.decode()}")

# 打印私钥和公钥的十六进制格式
print(f"Private Key (hex): {private_key.to_hex()}")
print(f"Public Key (hex): {public_key.to_hex()}")
