from pymongo import MongoClient
import json
import jwt
import requests
from flask import Flask, render_template, jsonify, request
import datetime
# 운영체제에 따라 port 다르게 하기
import platform

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbjungle

# JWT 시크릿 키
secret_key = 'your_secret_key_here'

# 메인 페이지
@app.route('/')
def main_Page():
    return render_template('base.html' ,title = "home")

# 로그인 페이지
@app.route('/login')
def login_Page():
    return render_template('login.html', title = "login")

# 회원가입 페이지
@app.route('/signup-page')
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=["POST"])
def signup():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    mail_receive = request.form['mail_give']

    new_member = {'id':id_receive, 'pw':pw_receive, 'name':name_receive, 'e-mail':mail_receive}
    db.users.insert_one(new_member)

    return jsonify({"result": "success", "msg":"가입 완료!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    print("Received data:", data)
    username = data["username"]
    password = data["password"]

    # Check if the provided credentials are valid
    user = db.users.find_one({'id': username, 'pw': password})
    print("User:", user)
    
    if user:
        token = jwt.encode({"userId": str(user["_id"]), "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, secret_key, algorithm="HS256")
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# 친구 목록 가져오기
@app.route('/friends', methods=['GET'])
def get_friends():
    token = request.headers.get('Authorization').split(' ')[1]

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['userId']
        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        friend_ids = user['friends']

        friends = db.users.find({'_id': {'$in': friend_ids}}, {'id': 1})
        friend_list = [{'username': friend['id']} for friend in friends]

        return jsonify({'friends': friend_list})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.DecodeError:
        return jsonify({'message': 'Invalid token'}), 401

@app.route('/my-friend-products', methods=['GET'])
def get_my_friend_products():
    token = request.headers.get('Authorization').split(' ')[1]

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['userId']
        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        friend_ids = user['friends']

        friend_products = db.products.find({'ownerId': {'$in': friend_ids}})
        friend_product_list = [{'name': product['name'], 'description': product['description']} for product in friend_products]

        return jsonify({'friendProducts': friend_product_list})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.DecodeError:
        return jsonify({'message': 'Invalid token'}), 401
    
@app.route('/getMyItems')
def song() :
    user_items = db.users.find_one({'user_id' : 'song'})['received_item']
    result = []
    for itemid in user_items :
        item = db.items.find_one({'_id': itemid})
        print(item)
        result.append(item)
    return render_template('song.html', data=result)
    
@app.route('/addMyItems', methods=['POST'])
def song2():
    name = request.form['item_name']
    price = request.form['price']
    d_day = request.form['d_day']
    description = request.form['description']
    img_url = request.form['img_url']

    user_items = db.users.find_one({'user_id' : 'song'})['freind']
    result = []
    for itemid in user_items :
        item = db.items.find_one({'_id': itemid})
        print(item)
        result.append(item)
    return render_template('song.html', data=result)


if platform.system()=="Darwin":
    if __name__ == '__main__':
        app.run('0.0.0.0', port=8000, debug=True)
else:
    if __name__ == '__main__':
        app.run('0.0.0.0', port=5000, debug=True)