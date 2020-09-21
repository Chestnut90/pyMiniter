import jwt

encryption_secret = 'secrete'   # secret key for encryption. TODO : use more complex key..
algorithm = 'HS256'             # algorithm to encrypt to signature part..

def encode_token(data_to_encode):
    return jwt.encode(data_to_encode, encryption_secret, algorithm=algorithm)

def decode_token(data_to_decode):
    return jwt.decode(data_to_decode, encryption_secret, algorithm=[algorithm])

if __name__ == '__main__':
    data_to_encode = {'some': 'payload'}

    encoded = jwt.encode(data_to_encode, encryption_secret, algorithm=algorithm)
    print(encoded)

    decoded = jwt.decode(encoded, encryption_secret, algorithm=[algorithm])
    print(decoded)