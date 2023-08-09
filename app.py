from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import jwt
import requests
from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
from bson.objectid import ObjectId
import datetime
# 운영체제에 따라 port 다르게 하기
import platform

# 이미지 URL 추출함수
import image_method, init_db
from bson.objectid import ObjectId

import os

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbjungle

# JWT 시크릿 키
secret_key = 'your_secret_key_here'

# 메인 페이지
@app.route('/')
def main_page():
    token = request.cookies.get('token')  # 쿠키에서 토큰 가져오기

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['userId']

        user = db.users.find_one({'_id': ObjectId(user_id)})
        print(user)
        
        user_items = user['rec_item']

        item_list = []
        for itemid in user_items :
            item = db.items.find_one({'_id': ObjectId(itemid)})
            item_list.append(item)

        data = [
            {'items':item_list}
        ]
        # return jsonify(data)
        return render_template('base.html', title='home', data = item_list)
    except jwt.ExpiredSignatureError:
        return redirect('/login')  # 토큰이 만료된 경우 로그인 페이지로 리다이렉트
    except jwt.DecodeError:
        return redirect('/login')
    
@app.route('/item/<item_id>',methods=['GET'])
def item(item_id) :
    item_id = int(item_id)
    items = list(db.items.find({'_id' : item_id}))
    pays = list(db.pay.find({'_id' : item_id}))
    print(items)
    return render_template('detail.html', item_info=items, pay_info=pays)

# 로그인 페이지
@app.route('/login')
def login_Page():
    return render_template('login.html', title = "login")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    print("Received data:", data)
    username = data["username"]
    password = str(data["password"])

    user = db.users.find_one({'user_id': username, 'pw': password})
    print("User:", user)

    if user:
        token = jwt.encode({"userId": str(user["_id"]), "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, secret_key, algorithm="HS256")
        response = make_response(redirect(url_for('main_page')))  # 리다이렉트 생성
        response.set_cookie('token', token, path='/')  # 쿠키에 토큰 설정
        return response
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# 회원가입 페이지
@app.route('/signup-page')
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=["POST"])
def signup():
    id_receive = request.form['id_give']
    pw_receive = str(request.form['pw_give'])
    name_receive = request.form['name_give']
    mail_receive = request.form['mail_give']

    try:
        img_receive = request.files['img_give'] 
    except:
        img_receive = str("")
    
    img_url = ''
    if img_receive== str("") :
        img_url = 'static/img/default.png'
    else :
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime('%Y%m%d%H%M%S')  # 시간을 문자열로 변환
        file_name = id_receive + formatted_time + img_receive.filename
        
        path = 'static/img/'
        # 이미지 파일 저장
        img_receive.save(os.path.join(path, file_name))
        img_url = path + file_name

    user = db.users.find_one({"user_id" : id_receive})
    print(img_url)

    if user:
        return jsonify({"result": "failure", "msg":"이미 존재하는 아이디입니다."})

    new_member = {
        'user_id':id_receive, 'pw':pw_receive, 'name':name_receive, 'mail':mail_receive, 'img' : img_url,
        'rec_item' : ''
    }

    db.users.insert_one(new_member)
    return jsonify({"result": "success", "msg":"가입 완료!"})

# nav바에 사용자 이름, 사진 넘겨주기
@app.route('/nav', methods=['GET'])
def whoAmI():
    token = request.cookies.get('token')  # 쿠키에서 토큰 가져오기

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['userId']

        user = db.users.find_one({'_id': ObjectId(user_id)})
        user_name = user['name']
        user_img = user['img']
        return jsonify({'result' : 'success', 'user_name' : user_name, 'user_img' : user_img})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.DecodeError:
        return jsonify({'message': 'Invalid token'}), 401

# 프로필 요청
@app.route('/profile')
def profile_Page():
    return render_template('profile.html')

# 위시리스트 요청
@app.route('/addItem')
def item_Page():
    return render_template('addItem.html')

# 아이템 추가
@app.route('/addItem', methods=['POST'])
def addItem():
    token = request.cookies.get('token')  # 쿠키에서 토큰 가져오기

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['userId']
        user = db.users.find_one({'_id': ObjectId(user_id)})
        print(user)

        name = request.form['name']
        price = request.form['price']
        date = request.form['date']
        descr = request.form['descr']
        img_url = request.form['img_url'] 

        img_url = image_method.extract_image_url(img_url)

        item = {
            'owner' : {
                '_id' : user_id,
                'name' : user['name'],
                'img' : user['img'], 
            },
            'name': name,
            'price': price,
            'total_fund': 0,
            'date': date,
            'descr': descr,
            'img_url': img_url,
            'fund_rate': 0
        }
        print(item)
        db.items.insert_one(item)

        return jsonify({'result':'success'})
    except jwt.ExpiredSignatureError:
        return redirect('/login') 
    except jwt.DecodeError:
        return redirect('/login')


# 친구 요청 보내는 API
@app.route('/send_request/<requested_id>', methods=['POST'])
def send_request(friend_id):
    token = request.cookies.get('token')  # 쿠키에서 토큰 가져오기
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['userId']
        requester_id = ObjectId(user_id)
        user = db.users.find_one({'_id':requester_id})
        friend = db.users.find_one({'user_id':friend_id})
        if friend:
            friend_objectId = friend['_id']
            if friend_objectId in user['friend']:
                return jsonify({'result': 'failure', 'message':'이미 친구 추가가 되어 있습니다.'})
            else:
                friend_request = {
                    "requester_id" : requester_id,
                    "requester_name" : user['name'],
                    "requested_id" : friend['_id'],
                    "status" : "unchecked",
                    "content" : "request"
                }
                db.requests.insert_one(friend_request)
        else:
            return jsonify({'result':'failure', 'message':'해당 아이디를 가진 사용자가 존재하지 않습니다.'})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.DecodeError:
        return jsonify({'message': 'Invalid token'}), 401

# 알림 조회하는 API
@app.route('/notify_get', methods=['GET'])
def get_notification():
    token = request.cookies.get('token') #쿠키에서 토큰 가져오기
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['userId']
        all_requests = list(db.requests.find({'requested_id':ObjectId(user_id), 'status':'unchecked'}))
        request_num = len(all_requests)
        return jsonify({'result':'success', 'all_requests':all_requests, 'request_num':request_num})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.DecodeError:
        return jsonify({'message': 'Invalid token'}), 401

# 요청 수락/거절 전달하는 API
@app.route('/respond_request/<request_id>/<action>', methods=['POST'])
def respond_request(request_id, action):
    friend_request = db.requests.find_one({'_id':request_id}, {'$set':{'status':'checked'}})
    sender = friend_request['requested_id'] # 요청을 받은 사람이 응답을 보냄
    receiver = friend_request['requester_id'] # 요청을 보낸 사람이 응답을 받음

    if action == 'accepted':
        new_request = {'requester_id':sender, 'requested_id':receiver, 'status':'unchecked', 'content' : 'accepted'}
    else:
        new_request = {'requester_id':sender, 'requested_id':receiver, 'status':'unchecked', 'content' : 'declined'}
    
    db.requests.insert_one(new_request)
    
# 알림 확인하는 API
@app.route('/notify_check/<request_id>', methods=['POST'])
def check_notification(request_id):
    db.requests.find_one_and_update({'_id':request_id}, {'$set':{'status':'checked'}})


# 펀딩 API 추가
@app.route('/fund/<item_id>', methods=['POST'])
def funding(item_id):
    item_id = ObjectId(item_id)
    item = db.items.find_one({'_id' : item_id})
    print(item)
    price = item['price']
    received = int(request.form['money'])
    before_fund = item['total_funding']
    sum = before_fund + received
    rate = (sum) / price * 100
    rounded_rate = round(rate, 2)  # 두 자리까지 반올림
    print(rounded_rate)
    db.items.update_one({'_id' : item_id},{'$set':{'total_funding':sum}})
    db.items.update_one({'_id' : item_id},{'$set':{'achievement_rate':rounded_rate}})

    item = db.items.find_one({'_id' : item_id})

    token = request.cookies.get('token')  # 쿠키에서 토큰 가져오기
    
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['userId']        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        sender_name = user['name']
        db.pay.insert_one({
            'item_id' : item_id,
            'sender_name' : sender_name,
            'price' : received,
        })
    except jwt.ExpiredSignatureError:
        db.pay.insert_one({
            'item_id' : item_id,
            'sender_name' : '익명의 기부천사',
            'price' : received,
        })

    except jwt.DecodeError:
        db.pay.insert_one({
            'item_id' : item_id,
            'sender_name' : '익명의 기부천사',
            'price' : received,
        })
    return jsonify({'result':item})

@app.route('/fund/<item_id>', methods=['GET'])
def fund_list(item_id) :
    payList = db.pay.find({'_id' : ObjectId(item_id)})
    # payList = list(db.pay.find({'_id' : item_id}))
    return jsonify(payList)

init_db.delete_existing_data()
init_db.insert_initial_data()

if platform.system()=="Darwin":
    if __name__ == '__main__':
        app.run('0.0.0.0', port=8000, debug=True)
else:
    if __name__ == '__main__':
        app.run('0.0.0.0', port=5000, debug=True)