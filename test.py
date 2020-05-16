
from flask import Flask,request,jsonify,current_app,make_response
from werkzeug.routing import BaseConverter

app = Flask(__name__)

class RegexConverter(BaseConverter):
    def __init__(self,url_map,*args):
        super(RegexConverter,self).__init__(url_map)
        self.regex = args[0]

app.url_map.converters['re'] = RegexConverter

@app.route('/user/<re("[0-9]{3}"):user_id>')
def user_info(user_id):
    return "user_id 为%s"%user_id

@app.route('/users/<int:user_id>')
def func(user_id):
    json_data = {'name':'bob'}
    return jsonify(json_data)
    # return "hello world"

@app.route('/demo3')
def demo3():
    json_dict = {
        "user_id": 10,
        "user_name": "laowang"
    }
    return jsonify(json_dict)

if __name__ == "__main__":
    app.run()


from flask import Blueprint,render_template
import re
import random
pass_blu = Blueprint("passport",__name__,url_prefix = "/passport")
from . import views


@pass_blu.route('/image_code')
def get_image_code():
    code_id = request.args.get('code_id')
    name,text,image = captcha.generate_captcha()
    try:
        redis_store.setex("ImageCode_" + code_id,constants.IMAGE_REDIS_EXPIRES,text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno = RET.DATAERR,errmsg = "保存图片验证码失败"))
    resp = make_response(image)
    resp.headers['Content-Type'] = 'image/ipg'
    return resp

@passport_blu.route('/smscode')
def send_sms():
    param_dict = request.json
    mobile = param_dict.get("mobile")
    image_code = param_dict.get("image_code")
    image_code_id = param_dict.get("image_code_id")
    if not all([mobile,image_code_id,image_code]):
        return jsonify(errno = RET.PARAMERR,errmsg = "参数不全")
    if not re.match("^1[3578][0-9]{9}$",mobile):
        return jsonify(errno = RET.DATAERR,errmsg = "手机号不正确")
    try:
        real_image_code = redis_store.get("ImageCode_" + iamge_code_id)
        if real_image_code:
            real_image_code = real_image_code.decode()
            redis_store.delete("ImageCode_" + iamge_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg  = "获取图片验证码失败")
    if not real_image_code:
        return jsonify(errno = RET.NODATA,errmsg = "验证码已过期")
    if image_code.lower() != real_image_code.lower():
        return jsonify(errno = RET.DATAERR,errmsg = "验证码输入错误")
    try:
        user = User.query.filter_by(mobile = mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = "数据库查询错误")
    if user:
        return jsonify(errno = RET.DATAERR,errmsg = "该手机已被注册")
    result = random.randint(0,999999)
    sms_code = "%06d"%result
    current_app.logger.debug("短信验证码的内容：%s"%sms_code)
    result = CCP().send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_REPIRES / 60],'1')
    if result != 0:
        return jsonify(errno = RET.THIRDERR,errmsg = "发送短信失败")
    try:
        redis_store.set("SMS_" + mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = "保存短信验证码失败")
    return jsonify(errno = RET.OK,errmsg = "发送成功")


@passport_blu.route('/register',methods = ["POST"])
def redister():
    json_data = request.json
    mobile = json_data.get("mobile")
    sms_code = json_data.get("smscode")
    password = json_data.get("password")
    if not all([mobile,sms_code,password]):
        return jsonify(errno = RET.PARAMERR,errmsg = "参数不全")
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR,errmsg = "获取本地验证码失败")
    if not real_sms_code:
        return jsonify(errno = RET.NODATA,errmsg = "短信验证码过期")
    if sms_code != real_sms_code:
        return jsonify(errno = RET.DBERR,ermsg = "短信验证码错误")
    try:
        redis_store.delete("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno = RET.DATAERR,errmsg = "数据保存错误")
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    return jsonify(errno = RET.OK,errmsg = "OK")

@index_blu.route('/')
def index():
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
        return render_template('news/index.html',data = {'user_info':user.to_dict() if user else None})


import threading
import time
def show_info():
    for i in range(5):
        print("test:",i)
        time.sleep(0.5)
if __name__ == "__main__":
    sub_thread = threading.Thread(target = show_info)
    sub_thread.start()
    time.sleep(1)
    print("over")


import time

def show_info():
    for i in range(5):
        print("test:",i)
        time.sleep(0.5)
if __name__ == "__main__":
    sub_thread = threading.Thread(target = show_info,deamon = True)
    sub_thread.start()
    time.sleep(1)
    print("over")

import threading

class MyThread(threading.Thread):
    def __init__(self,info1,info2):
        super(MyThread,self).__init__()
        self.info1 = info1
        self.info2 = info2
    def test1(self):
        print(self.info1)
    def test2(self):
        print(self.info2)
    def run(self):
        self.test1()
        self.test2()
my_thread = MyThread("测试1","测试2")
my_thread.start()

import threading
import time
my_list = list()
def write_data():
    for i in range(5):
        my_list.append(i)
        time.sleep(0.1)
    print("write_data:",my_list)
def read_data():
    print("read_data:",my_list)
if __name__ == "__main__":
    write_thread = threading.Thread(target = write_data)
    read_thread = threading.Thread(target = read_data)
    write_thread.start()
    write_thread.join()
    write_thread.join()
    read_thread.start()

import multiprocessing
import time

def run_proc():
    while True:
        print("---2---")
        time.sleep(1)
if __name__ == "__main__":
    sub_process = multiprocessing.Process(target = proc)
    sub_process.start()
    while True:
        print("---1---")
        time.sleep(1)
        











