from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, jsonify, request, Response, g
from Utils import access_token as at
from Utils.Database import db
from Utils.dictionary import to_dict
from Utils import hashed

app = Flask(__name__)

''' connections '''
#region
@app.route("/ping", methods=['GET'])
def ping():
    return f"pong at {datetime.now()}", 200

def sign_in_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is not None:
            try:
                payload = at.decode_token(access_token)
            except Exception as e:  #jwt.InvalidTokenError
                payload = None

            if payload is None:
                return jsonify({'error': f'Not authorized.'}), 401

            user_id = payload['user_id']
            g.user_id = user_id if user_id else None
            user = db.get_user_with_id({'user_id':user_id}) if user_id else None
            g.user = user
        else:
            return jsonify({'error': f'Not authorized.'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/sign-up", methods=['POST'])
def sign_up():
    payload = request.json

    must_keys = ['name', 'email', 'password', 'phone_number']
    option_keys = ['profile']

    keys = []
    keys += must_keys
    keys += option_keys
    new_user = to_dict(payload, keys)

    new_user['password'] = hashed.get_hashed_password(new_user['password'])

    try:
        new_user_id = db.insert_user(new_user)
    except Exception as e:
        new_user.pop('password')
        new_user['error'] = e
        return jsonify(new_user), 400

    new_user_info = db.get_user_with_id({'user_id': new_user_id})
    new_user_info.pop('password')

    return jsonify(new_user_info), 200

@app.route("/sign-in", methods=['POST'])
def sign_in():
    payload = request.json

    func = {'id': db.get_user_with_id,
            'email': db.get_user_with_email,
            'phone_number': db.get_user_with_phonenumber}
    sign_in_type = None
    for _type in func.keys():
        if _type in payload:
            sign_in_type = _type
            break

    if sign_in_type is None:
        return {'error': "sign-in error"}, 400

    keys = [sign_in_type, 'password']
    user = to_dict(payload, keys)

    # email | id | phone_number & password
    user_info = func[sign_in_type](user)
    if user_info is None:
        user.pop('password')
        user['error'] = f"Not registered user."
        return jsonify(user), 400

    if not hashed.check_password(user['password'], user_info['password']):
        user.pop('password')
        user['error'] = f"Wrong password."
        return jsonify(user), 400

    payload = {'user_id': user_info['id'],
               'exp': datetime.utcnow() + timedelta(seconds=60*60*24)}
    token = at.encode_token(payload)
    try:
        return jsonify({'access_token': token.decode('UTF-8')}), 200
    except:
        return '', 400
#endregion

''' tweets '''
#region
@app.route('/new-tweet', methods=['POST'])
@sign_in_required
def new_tweet():
    payload = request.json

    keys = ['tweet']
    user_tweet = to_dict(payload, keys)
    user_tweet['id'] = g.user_id

    try:
        user_id = int(user_tweet['id'])
    except Exception as e:
        user_tweet['error'] = f"Invalid user id."
        return jsonify(user_tweet), 400

    user_info = db.get_user_with_id({'user_id': user_id})
    if user_info is None:
        user_tweet['error'] = f"Not registered user."
        return jsonify(user_tweet), 400

    tweet = user_tweet['tweet']
    if len(tweet) > 300:
        user_tweet['error'] = f"Tweet is over 300 limits."
        return jsonify(user_tweet), 400

    try:
        tweet_id = db.insert_tweet(user_tweet)
    except Exception as e:
        user_tweet['error'] = f"{e}"
        return jsonify(user_tweet), 400
    user_tweet['tweet_id'] = tweet_id
    return jsonify(user_tweet), 200

@app.route('/delete-tweet', methods=['POST'])
@sign_in_required
def delete_tweet():
    payload = request.json

    keys = ['tweet_id']
    user_tweet = to_dict(payload, keys)
    user_tweet['user_id'] = g.user_id

    old_tweet = db.get_tweet({'tweet_id': user_tweet['tweet_id']})
    if old_tweet is None:
        return jsonify({'error': f"Not existed tweet."}), 400

    if old_tweet['user_id'] != user_tweet['user_id']:
        return jsonify({'error': f"Not allowed. wrong user."}), 400

    r = db.delete_tweet(old_tweet)
    old_tweet.pop('user_id')
    return jsonify(old_tweet), 200

@app.route('/timeline', methods=['POST'])
@sign_in_required
def timeline():
    payload = request.json

    keys = ['user_id']
    user_timeline = to_dict(payload, keys)

    user = db.get_user_with_id(user_timeline)
    if user is None:
        # TODO : none user.
        return jsonify({'error': f'No user.'}), 400

    tweets = db.get_timeline(user_timeline)
    return jsonify(tweets), 200

#endregion

''' follows '''
#region
@app.route('/follow', methods=['POST'])
@sign_in_required
def follow():
    payload = request.json

    user_id = int(payload['id'])
    user = db.get_user_with_id(user_id)
    if user is None:
        payload['error'] = f'No user.'
        return jsonify(payload), 400

    id_to_follow = int(payload['follow'])
    user_to_follow = db.get_user_with_id(id_to_follow)
    if user_to_follow is None:
        payload['error'] = f'No user to follow.'
        return jsonify(payload), 400

    db.insert_follower({'user_id': user_id, 'id_to_follow': id_to_follow})

    return jsonify(payload), 200

@app.route('/unfollow', methods=['POST'])
@sign_in_required
def unfollow():
    payload = request.json

    user_id = int(payload['id'])
    user = db.get_user_with_id(user_id)
    if user is None:
        payload['error'] = f'No user.'
        return jsonify(payload), 400

    id_to_unfollow = int(payload['unfollow'])
    user_to_unfollow = db.get_user_with_id(id_to_unfollow)
    if user_to_unfollow is None:
        payload['error'] = f'No user to un-follow'
        return jsonify(payload), 400

    db.delete_follower({'user_id': user_id, 'id_to_unfollow': id_to_unfollow})
    return jsonify(payload), 200

#endregion

def run_app():
    # app.run()
    app.run(host="localhost", port=5000, debug=1 )
