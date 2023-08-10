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
import sys

# 이미지 URL 추출함수
import our_methods
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
    token = request.cookies.get('token') 

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['userId']
        
        user_id = ObjectId(user_id)
        # user_id = int(user_id)
        user = db.users.find_one({'_id': user_id})
        print(user)
        
        user_items = user['rec_item']

        item_list = []
        for itemid in user_items :
            itemid = ObjectId(itemid)
            # itemid = int(itemid)
            item = db.items.find_one({'_id': itemid})
            print(item['date'])
            d_day = our_methods.calcualte_day_left(item['date'])

            removeCheck = []
            if(d_day == 'expired') :
                removeCheck.append(itemid)
                db.items.update_one({'_id' : itemid}, {"$set": {"expired": True}})
                db.users.update_one({'_id' : user_id}, {'$pull': {'rec_item': itemid}})
                continue
            item['date'] = d_day
            print(d_day)
            item_list.append(item)

        print(item_list)
        return render_template('base.html', title='home', data = item_list)
    except jwt.ExpiredSignatureError:
        return redirect('/login')  # 토큰이 만료된 경우 로그인 페이지로 리다이렉트
    except jwt.DecodeError:
        return redirect('/login')
    
@app.route('/item/<item_id>')
def item(item_id) :
    item_id = ObjectId(item_id)
    item = db.items.find_one({'_id' : item_id})
    pay = list(db.pay.find({'item_id' : item_id}))
    return render_template('detail.html', item_info=item, pay_info=pay)

# 로그인 페이지
@app.route('/login')
def login_Page():
    token = request.cookies.get('token')  # 쿠키에서 토큰 가져오기

    if token:  # 토큰이 존재하면
        try:
            jwt.decode(token, secret_key, algorithms=['HS256'])  # 토큰 유효성 확인
            return redirect('/')  # 이미 로그인 상태라면 '/'로 리다이렉트
        except jwt.ExpiredSignatureError:  # 토큰이 만료된 경우
            pass

    return render_template('login.html', title="login")

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
    token = request.cookies.get('token')  # 쿠키에서 토큰 가져오기

    if token:  # 토큰이 존재하면
        try:
            jwt.decode(token, secret_key, algorithms=['HS256'])  # 토큰 유효성 확인
            return redirect('/')  # 이미 로그인 상태라면 '/'로 리다이렉트
        except jwt.ExpiredSignatureError:  # 토큰이 만료된 경우
            pass

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
        'rec_item' : [], 
        'friend' : [], 
        'my_item' : [], 
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
        # user = db.users.find_one({'_id': int(user_id)})
        user_name = user['name']
        user_img = user['img']
        return jsonify({'result' : 'success', 'user_name' : user_name, 'user_img' : user_img})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.DecodeError:
        return jsonify({'message': 'Invalid token'}), 401

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
        # user = db.users.find_one({'_id': int(user_id)})

        name = request.form['name']
        price = request.form['price']
        date = request.form['date']
        descr = request.form['descr']
        prod_url = request.form['img_url'] 

        img_url = our_methods.extract_image_url(prod_url)

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
            'item_url': prod_url,
            'fund_rate': 0
        }
        result = db.items.insert_one(item)
        inserted_id = result.inserted_id
        db.users.update_one({'_id':ObjectId(user_id)}, {'$push': {'my_item':inserted_id}})
        for friend in user['friend'] :
            db.users.update_one({'_id' : friend}, {'$push': {'rec_item': inserted_id}})
        return redirect(url_for('main_page'))
    except jwt.ExpiredSignatureError:
        return redirect('/login') 
    except jwt.DecodeError:
        return redirect('/login')


# 친구 요청 보내는 API
@app.route('/send_request/<friend_id>', methods=['GET'])
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
                return jsonify({'result':'success', 'message':'친구 요청을 보냈습니다.'})
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
        all_requests = list(db.requests.find({'requested_id':ObjectId(user_id), 'status':'unchecked'}, {'requester_id':False,'requested_id':False}))
        request_num = len(all_requests)
        for i in all_requests:
            i['_id'] = str(i['_id'])
        return jsonify({'result':'success', 'all_requests':all_requests, 'request_num':request_num})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.DecodeError:
        return jsonify({'message': 'Invalid token'}), 401

# 요청 수락/거절 전달하는 API
@app.route('/respond_request', methods=['POST'])
def respond_request():
    request_id = request.form['id_give']
    action = request.form['action']
    friend_request = db.requests.find_one_and_update({'_id':ObjectId(request_id)}, {'$set':{'status':'checked'}})
    sender = friend_request['requested_id'] # 요청을 받은 사람이 응답을 보냄
    receiver = friend_request['requester_id'] # 요청을 보낸 사람이 응답을 받음

    if action == 'accepted':
        sender_info = db.users.find_one({'_id':ObjectId(sender)})
        sender_name = sender_info['name']        
        new_request = {'requester_id':sender, 'requester_name':sender_name, 'requested_id':receiver, 'status':'unchecked', 'content' : 'accepted'}
        db.users.update_one({'_id':ObjectId(receiver)}, {'$push':{'friend':ObjectId(sender)}}) #친구 요청을 보낸 사람의 friend 리스트에 수락을 받은 사람의 '_id'를 추가
        db.users.update_one({'_id':ObjectId(sender)}, {'$push':{'friend':ObjectId(receiver)}}) #친구 요청을 수락한 사람의 friend 리스트에 수락을 요청한 사람의 '_id'를 추가
        sender_item = sender_info['my_item']
        db.users.update_one({'_id':ObjectId(receiver)}, {'$push':{'rec_item':{'$each':sender_item}}})
        receiver_info = db.users.find_one({'_id':ObjectId(receiver)})
        receiver_item = receiver_info['my_item']
        db.users.update_one({'_id':ObjectId(sender)}, {'$push':{'rec_item':{'$each':receiver_item}}})
    else:
        new_request = {'requester_id':sender, 'requested_id':receiver, 'status':'unchecked', 'content' : 'declined'}
    
    db.requests.insert_one(new_request)
    return jsonify({'result':'success', 'message':'요청에 대한 응답이 전달되었습니다.'})

# 알림 확인하는 API
@app.route('/notify_check', methods=['POST'])
def check_notification():
    request_id = request.form['id_give']
    db.requests.update_one({'_id':ObjectId(request_id)}, {'$set':{'status':'checked'}})
    return jsonify({'result':'success', 'message':'응답을 확인하였습니다.'})

# 펀딩 API 추가
@app.route('/fund/<item_id>', methods=['POST'])
def funding(item_id):
    item_id = ObjectId(item_id)
    item = db.items.find_one({'_id' : item_id})
    print(item)
    price = int(item['price'])
    received = int(request.form['money'])
    before_fund = item['total_fund']
    mid_fund = before_fund + received
    print(mid_fund)
    rate = (mid_fund) / price * 100
    rounded_rate = round(rate, 2)  # 두 자리까지 반올림
    print(rounded_rate)
    result=db.items.update_one({'_id' : item_id},{'$set':{'total_fund':mid_fund}})
    print(result)
    db.items.update_one({'_id' : item_id},{'$set':{'fund_rate':rounded_rate}})
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
        return jsonify({'result':'success'})
    except jwt.ExpiredSignatureError:
        db.pay.insert_one({
            'item_id' : item_id,
            'sender_name' : '익명의 기부천사',
            'price' : received,
        })
        return jsonify({'message':"감사합니다"})
    except jwt.DecodeError:
        db.pay.insert_one({
            'item_id' : item_id,
            'sender_name' : '익명의 기부천사',
            'price' : received,
        })
        return jsonify({'message':"감사합니다"})

if platform.system()=="Darwin":
    if __name__ == '__main__':
        app.run('0.0.0.0', port=8000, debug=True)
else:
    if __name__ == '__main__':
        app.run('0.0.0.0', port=5000, debug=True)