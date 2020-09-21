from sqlalchemy import create_engine, text
from Config import config

db_url = f"mysql+mysqlconnector://{config.user}:{config.password}@{config.host}:{config.port}/{config.db_name}?charset=utf8"

database = create_engine(db_url, encoding = 'utf-8', max_overflow = 0)

def fetches(user_id):
    select = """
                SELECT id, name, email, profile
                FROM users
                WHERE id = :user_id
                """
    result = database.execute(text(select), {'user_id': user_id}).fetchone()
    print(result)       # print using tuple.
    print(type(result)) # sqlachemy.engine.result.RowProxy
    print(result.keys()) # RowProxy using key-value pair.

    result = database.execute(text(select), {'user_id': user_id}).fetchall()
    print(result)  # print using tuple.
    print(type(result))  # list of sqlachemy.engine.result.RowProxy

    return result

if __name__ == '__main__':
    '''
        SELECT password matched with email.
        user_email : dictionary. (*email)
        '''
    select = """
                SELECT password
                FROM users
                WHERE email = :email
                """
    result = database.execute(text(select), {'email': 'user002@gmail.com'}).fetchone()
    print(result['password'])