from Crypto.Cipher import AES

def aes_encrypt(data, key):
    #Encrypts data using pycryptodome encryption
    cipher = AES.new(key, AES.MODE_CFB)
    iv = cipher.iv
    encrypted_data = cipher.encrypt(data)
    return iv + encrypted_data

def aes_decrypt(encrypted_data, key):
    #Decrypts data using pycryptodome
    iv = encrypted_data[:16]
    cipher = AES.new(key, AES.MODE_CFB, iv=iv)
    data = cipher.decrypt(encrypted_data[16:])
    return data
