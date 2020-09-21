import hashlib
import bcrypt

def SHA256(data):
    sha256 = hashlib.sha256()
    sha256.update(str.encode(data))
    return sha256.hexdigest()

def to_bytes(str_data:str):
    # bytes = str.encode(data, 'UTF-8')
    return str_data.encode('UTF-8')

def to_string(byte_data:bytes):
    # data = bytes.decode(byte_data, 'UTF-8')
    return byte_data.decode('UTF-8')

def get_hashed_password(password:str):
    ''' return hased_password as string '''
    if type(password) is not str:
        raise Exception("Not supported password type.")

    password = password.encode('UTF-8')
    stretch = 1
    for i in range(stretch):
        password = bcrypt.hashpw(password, bcrypt.gensalt())
    return password.decode('UTF-8')

def check_password(password:str, hashed_password:str):
    ''' compare password with hashed_password '''
    if type(password) is not str:
        raise Exception("Invalid password type.")
    password = password.encode('UTF-8')

    if type(hashed_password) is not str:
        raise Exception("Invalid hased_password type.")
    hashed_password = hashed_password.encode('UTF-8')

    return bcrypt.checkpw(password, hashed_password)

if __name__ == '__main__':
    password = "testpassword"

    salt = bcrypt.gensalt()
    print(f"salt : {salt}")

    # hashed = bcrypt.hashpw(password.encode('UTF-8'))
    # print(f"not salted hashed : {hashed}")

    hashed = bcrypt.hashpw(password.encode('UTF-8'), salt)
    print(f"salted hashed : {hashed}")

    result = bcrypt.checkpw(password.encode('UTF-8'), hashed)
    print(result)

    hashed1 = get_hashed_password(password)
    string = hashed1.decode('UTF-8')
    print(string)