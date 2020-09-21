from sqlalchemy import create_engine, text
from Config import config

db_url = f"mysql+mysqlconnector://{config.user}:{config.password}@{config.host}:{config.port}/{config.db_name}?charset=utf8"

try:
    database = create_engine(db_url, encoding='utf-8', max_overflow=0)
except:
    database = None
## TODO : database -> singleton

def to_user_info(row):
    return {'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'password': row['password'],
            'profile': row['profile'],
            'phone_number': row['phone_number']} if row else None

def get_user_with_id(user_id):
    '''
    SELECT user info matched with user_id.
    user_id : dictionary. (*user_id)
    '''
    select = """
            SELECT id, name, email, password, profile, phone_number
            FROM users
            WHERE id = :user_id
            """
    result = database.execute(text(select), user_id).fetchone()
    return to_user_info(result)

def get_user_with_email(user_email):
    '''
    SELECT user info matched with email.
    user_email : dictionary. (*email)
    '''
    select = """
            SELECT id, name, email, password, profile, phone_number
            FROM users
            WHERE email = :email
            """
    result = database.execute(text(select), user_email).fetchone()
    return to_user_info(result)

def get_user_with_phonenumber(user_phone_number):
    '''
    SELECT password matched with phone number.
    user_phonenumber : dictionary. (*user_phone_number)
    '''
    select = """
            SELECT id, name, email, password, profile, phone_number
            FROM users
            WHERE phone_number = :user_phone_number
            """
    result = database.execute(text(select), user_phone_number).fetchone()
    return to_user_info(result)

def insert_user(new_user):
    '''
    INSERT new user into db.
    new_user : dictionary. (*name, *email, *password, *phone_number, profile)
    '''

    insert = """
            INSERT INTO users ( name, email, profile, password, phone_number)
            VALUES ( :name, :email, :profile, :password, :phone_number)
            """
    return database.execute(text(insert), new_user).lastrowid

def insert_tweet(new_tweet):
    '''
    INSERT new timeline into db.
    new_tweet : dictionary. (*id, *tweet)
    '''

    insert = """
            INSERT INTO tweets ( user_id, tweet )
            VALUES ( :id, :tweet )
            """
    return database.execute(text(insert), new_tweet).lastrowid

def get_tweet(old_tweet):
    '''
    SELECT old tweet from db.
    old_tweet : dictionary. (*tweet_id)
    '''
    select = """
            SELECT id, user_id, tweet, created_at
            FROM tweets
            WHERE id = :tweet_id
            """
    result = database.execute(text(select), old_tweet).fetchone()
    return {'id': result['id'],
            'user_id': result['user_id'],
            'tweet': result['tweet'],
            'create_at': result['created_at']} if result else None

def delete_tweet(old_tweet):
    '''
    Delete old tweet from db.
    old_tweet : dictionary. (*tweet_id)
    '''
    delete = """
            DELETE FROM tweets
            WHERE id = :tweet_id
            """
    result = database.execute(text(delete), old_tweet).rowcount
    return result

def get_timeline(user_id):
    '''
    SELECT timeline with user_id
    user_id : dictionary. (*user_id)
    '''

    select = """
            SELECT t.user_id, t.tweet
            FROM tweets t
            LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
            WHERE t.user_id = :user_id
            OR t.user_id = ufl.id_to_follow
            """
    # order by TIMESTAMP
    result = database.execute(text(select), user_id).fetchall()
    return [{'user_id':tweet['user_id'], 'tweet':tweet['tweet']} for tweet in result]

def insert_follower(new_follower):
    '''
    INSERT new follower into db.
    new_follower : dictionary. (*user_id, *id_to_follow)
    '''

    insert = """
            INSERT INTO users_follow_list ( user_id, id_to_follow )
            VALUES ( :user_id, :id_to_follow )
            """
    return database.execute(text(insert), new_follower).rowcount

def delete_follower(old_follower):
    '''
    DELETE old follower from db.
    old_follower : dictionary. (*user_id, *id_to_unfollow)
    '''

    delete = """
            DELETE FROM users_follow_list
            WHERE user_id = :user_id
            AND id_to_follow = :id_to_unfollow
            """
    return database.execute(text(delete), old_follower).rowcount

def select_follower(old_follower):
    '''
    CHECK old follower from db.
    old_follower : dictionary. (*user_id, *id_to_follow)
    '''
    select = """
            SELECT * 
            FROM users_follow_list
            WHERE user_id = :user_id AND id_to_follow = :id_to_follow
            """

    result = database.execute(text(select), old_follower).fetchone()
    return {'user_id': result['user_id'],
            'id_to_follow': result['id_to_follow']} if result else None


