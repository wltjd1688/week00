from pymongo import MongoClient
import json
import jwt
import requests
from flask import Flask, render_template, jsonify, request, redirect, url_for, make_response
import datetime
# 운영체제에 따라 port 다르게 하기
import platform

# 이미지 URL 추출함수
import image_method, init_db

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
        user_id = int(user_id)
        # 지금 디비 아이디가 수동 아이디에서 int로 바꿔줘야 해서 이렇게 씀
        user = db.users.find_one({'_id': user_id})
        
        #  최종에선 이거쓰면됨
        #user = db.users.find_one({'_id': ObjectId(user_id)})

        user_items = user['rec_item']
        item_list = []
        for itemid in user_items :
            item = db.items.find_one({'_id': itemid})
            item_list.append(item)
        # print(item_list)

        data = [
            {'items':item_list}
        ]
        # return jsonify(data)
        return render_template('base.html', title='home', data='data')
    except jwt.ExpiredSignatureError:
        return redirect('/login')  # 토큰이 만료된 경우 로그인 페이지로 리다이렉트
    except jwt.DecodeError:
        return redirect('/login')

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
    # img_receive = request.form['img_give']

    user = db.users.find_one({"user_id" : id_receive})
    if user:
        return jsonify({"result": "failure", "msg":"이미 존재하는 아이디입니다."})

    new_member = {'user_id':id_receive, 'pw':pw_receive, 'name':name_receive, 'mail':mail_receive}

    db.users.insert_one(new_member)

    return jsonify({"result": "success", "msg":"가입 완료!"})

# nav바에 사용자 이름, 사진 넘겨주기
@app.route('/nav', methods=['GET'])
def whoAmI():
    token = request.cookies.get('token')  # 쿠키에서 토큰 가져오기

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = decoded_token['userId']

        user = db.users.find_one({'_id': user_id})
        user_name = user['name']
        user_img = user['image']
        return jsonify({'result' : 'success', 'user_name' : user_name, 'user_img' : user_img})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.DecodeError:
        return jsonify({'message': 'Invalid token'}), 401

# 프로필 화면전환 필요
@app.route('/profile')
def profile():
    return render_template('profile.html')

# 위시리스트 화면전환 필요
@app.route('/item')
def item():
    return render_template('item.html')

# 아이템 추가
@app.route('/addItem', methods=['POST'])
def addItem():

    token = request.cookies.get('token')  # 쿠키에서 토큰 가져오기

    name = request.form['item_name']
    price = request.form['price']
    d_day = request.form['d_day']
    description = request.form['description']
    img_url = request.form['img_url'] 
    #카테고리
    img_url = image_method.extract_image_url(img_url)

    item = {
        'owner' : {
            
        },
        'item_name': name,
        'price': price,
        'total_funding': 0,
        'd-day': d_day,
        'description': description,
        'img_url': img_url,
        'achievement_rate': 0
    },
    db.users.insert_one(item)
    return jsonify({'result:success'})

# 펀딩 API 추가
@app.route('/fund/<item_id>', methods=['POST'])
def funding(item_id):
    item_id = int(item_id)
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
    return jsonify({'result':item})

init_db.delete_existing_data()
init_db.insert_initial_data()

if platform.system()=="Darwin":
    if __name__ == '__main__':
        app.run('0.0.0.0', port=8000, debug=True)
else:
    if __name__ == '__main__':
        app.run('0.0.0.0', port=5000, debug=True)