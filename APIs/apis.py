from flask import Flask, jsonify, request

app = Flask(__name__)
app.users = {}
app.id_count = 1 # TODO : have problem about atomic and security.

def get_json_of_request():
    return request.json

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/sign-up", methods=['POST'])
def sign_up():
    new_user = request.json             # get user data from http as json format.
    new_user["id"] = app.id_count       # add user id for new user.
    app.users[app.id_count] = new_user  # add new user to app.
    app.id_count = app.id_count + 1     # increase user id.

    return jsonify(new_user), 200       # return new user data.

app.tweets = []

@app.route('/tweet', methods=['POST'])
def tweet():
    payload = request.json
    user_id = int(payload['id'])
    tweet = payload['tweet']

    if user_id not in app.users:
        return f'No user : {user_id}', 400

    if len(tweet) > 300:
        return f'tweet is over 300 limit', 400

    app.tweets.append({
        'user_id' : user_id,
        'tweet' : tweet
    })
    return '', 200

@app.route('/follow', methods=['POST'])
def follow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['follow'])

    if user_id not in app.users:
        return f'No user : {user_id}', 400

    if user_id_to_follow not in app.users:
        return f'No user to follow : {user_id_to_follow}', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).add(user_id_to_follow)
    return jsonify(user)

@app.route('/unfollow', methods=['POST'])
def unfollow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_unfollow = int(payload['unfollow'])

    if user_id not in app.users:
        return f'No user : {user_id}', 400
    if user_id_to_unfollow in app.users:
        return f'No user to unfollow : {user_id_to_unfollow}', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).discard(user_id_to_unfollow)
    return jsonify(user)

@app.route('/timeline/<int:user_id>', methods=['GET'])
def timeline(user_id):
    if user_id not in app.users:
        return f"No user : {user_id}", 400

    follow_list = app.users[user_id].get('follow', set())
    follow_list.add(user_id)
    timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]
    return jsonify({
        'user_id' : user_id,
        'timeline' : timeline
    })

