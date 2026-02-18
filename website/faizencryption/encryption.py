from Crypto.Cipher import AES, DES, ARC4
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib
from flask import current_app

# For generating the salt
def generate_key(user_uuid : str, method : str):
    # Determine the key length based on the capabilities of each encryption algorithm
    if method == "aes_cbc" or method == "rc4":
        dklen=32
    elif method == "des_cbc":
        dklen=8
    
    # Generate salt from the username
    return hashlib.scrypt(
        user_uuid.encode(),
        salt=current_app.config['SECRET_KEY'].encode(),  
        n=2**14, # CPU & Memory cost factor, controls how computationally expensive key derivation is
        r=8, # Block size parameter
        p=1, # parallelization factor, single threaded in this case
        dklen=dklen 
    )

# Encryption controller
def encrypt(user_uuid : str, data : bytes, method : str):
    if method == "aes_cbc":
        return enc_aes_cbc(user_uuid=user_uuid, data=data)
    if method == "des_cbc":
        return enc_des_cbc(user_uuid=user_uuid, data=data)
    if method == "rc4":
        return enc_rc4(user_uuid=user_uuid, data=data)

def decrypt(user_uuid : str, enc_data : bytes, method : str):
    if method == "aes_cbc":
        return dec_aes_cbc(user_uuid=user_uuid, enc_data=enc_data)
    if method == "des_cbc":
        return dec_des_cbc(user_uuid=user_uuid, enc_data=enc_data)
    if method == "rc4":
        return dec_rc4(user_uuid=user_uuid, enc_data=enc_data)
    
## AES - CBC method
def enc_aes_cbc(user_uuid : str, data : bytes):
    try:
        # Generate new cipher object, IV is already randomly initialized
        cipher = AES.new(generate_key(user_uuid, "aes_cbc"), AES.MODE_CBC)
    
        # Pad the data to fit the AES 16 Byte block size then encrypt the data
        ciphertext = cipher.encrypt(pad(data, AES.block_size))

        # Return the IV and Ciphertext together
        return cipher.iv, ciphertext, None
    except Exception as e:
        return None, e
    
def dec_aes_cbc(user_uuid : str, enc_data : bytes):
    try:
        # Obtain the IV and encrypted data
        iv = enc_data[:16]
        ciphertext = enc_data[16:]
                
        # Generate new cipher object with the IV obtained from before
        cipher = AES.new(generate_key(user_uuid, "aes_cbc"), AES.MODE_CBC, iv=iv)
    
        # Decrypt the data
        dec_data = unpad(cipher.decrypt(ciphertext), AES.block_size)

        # Return the IV and encrypted data
        return len(iv), len(ciphertext), dec_data , None
    except Exception as e:
        return None, e
    
## DES - CBC method
def enc_des_cbc(user_uuid : str, data : bytes):
    try:
        # Generate new cipher object, IV is already randomly initialized
        cipher = DES.new(generate_key(user_uuid, "des_cbc"), DES.MODE_CBC)
    
        # Pad the data to fit the AES 16 Byte block size then encrypt the data
        ciphertext = cipher.encrypt(pad(data, DES.block_size))

        # Return the IV and Ciphertext together
        return cipher.iv, ciphertext, None
    except Exception as e:
        return None, e

def dec_des_cbc(user_uuid : str, enc_data : bytes):
    try:
        # Obtain the IV and encrypted data
        iv = enc_data[:8]
        ciphertext = enc_data[8:]
                
        # Generate new cipher object with the IV obtained from before
        cipher = DES.new(generate_key(user_uuid, "des_cbc"), DES.MODE_CBC, iv=iv)
    
        # Decrypt the data
        dec_data = unpad(cipher.decrypt(ciphertext), DES.block_size)

        # Return the IV and encrypted data
        return len(iv), len(ciphertext), dec_data , None
    except Exception as e:
        return None, e

# RC4
def enc_rc4(user_uuid : str, data : bytes):
    try:
        # Generate new cipher object with the obtained key
        cipher = ARC4.new(generate_key(user_uuid=user_uuid, method="rc4"))
        
        # Encrypt the data
        ciphertext = cipher.encrypt(data)
        
        # Return the encrypted data
        return None, ciphertext, None
    except Exception as e:
        return None, e

def dec_rc4(user_uuid : str, enc_data : bytes):
    try: 
        # Generate new cipher object with the obtained key
        cipher = ARC4.new(generate_key(user_uuid=user_uuid, method="rc4"))
        
        # Encrypt the data
        dec_data = cipher.decrypt(enc_data)
        
        # Return the decrypted data
        return None, len(enc_data), dec_data, None
    except Exception as e:
        return None, e