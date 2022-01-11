from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'STUDYWITH'

client = MongoClient('localhost', 27017)
db = client.DO_STUDY
if (db.number.find_one({"id": 'autoIncrement'}) is None):
    db.number.insert_one({"number": 1, "id": 'autoIncrement'})


def return_list(list):
    token_receive = request.cookies.get('mytoken')
    print(list)
    # 토큰이 있고 만료되지 않았으면 리뷰리스트 나열
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('reviews.html', user_info=user_info, review_list=list)
    # 토큰이 있으나 시간 만료 되었을떄
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    # 토큰이 없음
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # 유저 닉네임 중복확인
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/')
def home():
    # /로 들어왔을 때 조건에 따라 구현
    review_list = list(db.reviews.find({}, {'_id': False}))
    return  return_list(review_list)



@app.route('/guest')
def guest():
    # 게스트로 입장한다면 -> 기능 구현 필요 def home()에 추가해야함
    return render_template("reviews.html")


@app.route('/login')
def login():
    # 로그인 페이지로 들어왔을때 렌더링
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # 회원 가입 기능 구현 ajax로 아이디 패스워드를 받아서 패스워드를 해시화한 후 db에 저장
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "like_list": [],  # 내가 좋아요누른 리스트
        "review_list": [],  # 내가 리뷰한 리스트
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인 기능 구현
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})
    # 로그인과 동시에 토큰 발급 캐시로 포함되어 넘어감
    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/reviews', methods=['POST'])
def saving():
    # 리뷰글을 디비에 저장하는 과정, 리뷰글을 누가 작성했는지 유저 디비에 저장
    special_number = db.number.find_one({'id': 'autoIncrement'})['number']
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    review_list = list(db.users.find_one({'username': payload['id']})['review_list'])
    review_list.append(special_number);
    my_set = set(review_list)
    review_list = list(my_set)
    db.users.update_one({'username': payload['id']}, {'$set': {'review_list': review_list}})
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']
    studyOption_receive = request.form['studyOption_give']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    title = soup.select_one('meta[property="og:title"]')['content']
    url = soup.select_one('meta[property="og:url"]')['content']
    image = soup.select_one('meta[property="og:image"]')['content']
    desc = soup.select_one('meta[property="og:description"]')['content']
    doc = {'title': title, 'desc': desc, 'image': image, 'url': url, 'comment': comment_receive,
           'studyOption': studyOption_receive, 'like': 0, 'special_number': special_number}
    db.reviews.insert_one(doc)
    special_number += 1
    db.number.update_one({'id': 'autoIncrement'}, {'$set': {'number': special_number}})
    return redirect('/')


@app.route('/mypage')
def user():
    # 각 사용자의 리뷰글 추천글 회원 정보를 볼 수 있는 페이지
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('mypage.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reviews/like', methods=['POST'])
def update_like():
    # 좋아요 기능 구현 누가 좋아요를 했는지 유저 디비에 저장
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        number_receive = int(request.form['number_give'])

        review = db.reviews.find_one({'special_number': number_receive})
        like = review['like'] + 1
        db.reviews.update_one({'special_number': number_receive}, {'$set': {'like': like}})
        like_list = list(db.users.find_one({'username': payload['id']})['like_list'])
        like_list.append(number_receive);
        my_set = set(like_list)
        like_list = list(my_set)
        db.users.update_one({'username': payload['id']}, {'$set': {'like_list': like_list}})
        return jsonify({"result": "success", 'msg': '좋아요!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/reviews/section', methods=["GET"])
def review_filter():
    # 분류화 기능 추가 작업 필요
    option = request.args.get('option')
    print(option)
    selected_reviews = list(db.reviews.find({"studyOption" : option}))
    for selected_review in selected_reviews:
        print(selected_review)
    return return_list(selected_reviews)


@app.route('/reviews')
def search():
    search = request.args.get('search')
    reviews = list(db.reviews.find({}, {'_id': False}))
    review_list = []
    for review in reviews:
        if (search in review['title'] or search in review['comment'] or search in review['desc']):
            review_list.append(review)
    return return_list(review_list)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
