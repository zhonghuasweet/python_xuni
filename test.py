
# from flask import Flask,request,jsonify,current_app,make_response
# from werkzeug.routing import BaseConverter
# from flask_sqlalchemy import SQLAlchemy
#
# app = Flask(__name__)
#
# class RegexConverter(BaseConverter):
#     def __init__(self,url_map,*args):
#         super(RegexConverter,self).__init__(url_map)
#         self.regex = args[0]
#
# app.url_map.converters['re'] = RegexConverter
#
# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root@mysql@127.0.0.1:3306/test2'
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
#
# db = SQLAlchemy(app)
#
# class Author(db.Model):
#     __tablename__ = "author"
#     id = db.Column(db.Integer,primary_key=True)
#     name = db.Column(db.String(32),unique = True)
#     books = db.relationship("Book",backref = 'author')
#     def __repr__(self):
#         return "Author:%s"%self.name
#
# class Book(db.Model):
#     __table__ = "books"
#     id = db.Column(db.Integer,primary_key = True)
#     name = db.Column(db.String(32))
#     au_book = db.Column(db.Integer,db.ForeignKey('author.id'))
#     def __repr__(self):
#         return "Book:%s,%s"%(self.id,self.name)
#
# if __name__ == "__main__":
#     db.drop_all()
#     db.create_all()
#     app.run(debug = True)
    






# @app.route('/user/<re("[0-9]{3}"):user_id>')
# def user_info(user_id):
#     return "user_id 为%s"%user_id
#
# @app.route('/users/<int:user_id>')
# def func(user_id):
#     json_data = {'name':'bob'}
#     return jsonify(json_data)
#     # return "hello world"
#
# @app.route('/demo3')
# def demo3():
#     json_dict = {
#         "user_id": 10,
#         "user_name": "laowang"
#     }
#     return jsonify(json_dict)
#
# if __name__ == "__main__":
#     app.run()
#
#
from flask import Blueprint,render_template,request,make_response,jsonify,current_app
import re
import random
pass_blu = Blueprint("passport",__name__,url_prefix = "/passport")
# from . import views


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

import flask_appbuilder
@manager.option('-n','-name',dest='name')
@manager.option('-p','-password',data = 'password')
def createsuperuser(name,password):
    if not all([name,password]):
        return "参数不足"
    user = User()
    user.name = name
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

@admin_blu.route('/login',methods = ["POST","GET"])
def admin_login():
    if request_login():
        return render_template('admin/login.html')
    username = request.form.get("username")
    password = request.form.get("password")
    if not all([username,password]):
        return render_template('admin/login.html',errmsg = "参数不足")
    try:
        user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        return render_template('admin/login.html',errmsg = '数据查询失败')
    if not user:
        return render_template('admin/login.html',errmsg = "用户不存在")
    if not user.check_password(password):
        return render_template('admin/login.html',errmsg = "用户权限错误")
    session['user_id'] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    session["is_admin"] = True
    return "登录成功，需要跳转到主页"

@admin.route('/news_review_detail')
def news_review_detail():
    news_id = request.args.get("news_id")
    if not news_id:
        return render_template('admin/news_review_detail.html',data = {"errmsg":"未查询到此新闻"})
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        return render_template('admin/news_revice_detail.html',data = 'errmsg = "未查询到此新闻')
    data = {'news':news.to_dict()}
    return render_template('admin/news_review_detail.html',data = data)






import threading
threading.Thread()
threading.current_thread()
threading.enumerate()
# import time
# def count_time(func):
#     def wrapper():
#         start = time.time()
#         func()
#         end = time.time()
#         print("共计执行：%s秒"%(end-start))
#     return wrapper
#
# @count_time
# def my_count():
#     s = 0
#     for i in range(1000000):
#         s += 1
#     print("sum:",s)
# my_count = count_time(my_count)
# # my_count()
#
# # 类属性可以使用 类对象 或 实例对象 访问
# class Dog:
#     type = "狗"  # 类属性
#
# dog1 = Dog()
# dog1.name = "旺财"
#
# dog2 = Dog()
# dog2.name = "来福"
#
# # 类属性  取值
# print(Dog.type)  # 结果：狗
# print(dog1.type)  # 结果：狗
# print(dog2.type)  # 结果：狗


def logging(level):
    def wrapper(func):
        def inner_wrapper(*args, **kwargs):
            print("[{level}]: enter function {func}()".format(
                level=level,
                func=func.__name__))
            return func(*args, **kwargs)
        return inner_wrapper
    return wrapper
# logging(level="INFO")(say)
# @logging(level='INFO')
# def say(something):
#     print("say {}!".format(something))
# say('hello')


def func1(num):
    def func2(a):
        print(num,"333")
        print(a)
        def func3(*args):
            a("Q")
            print("hello world",a,a.__name__)
        return func3
    return func2

# @func1(num = 3)
# def Func(c):
#     print("Good {}".format(c))

# Func("china")

sum = lambda arg1,arg2:arg1 + arg2
print("Value of total1:{}".format(sum(10,20)))

def fun(a,b,opt):
    print("a = {}".format(a))
    print("b = {}".format(b))
    print("result = {}".format(opt))
fun(1,2,lambda x,y:x+y)


stus = [
    {"name": "zhangsan", "age": 18},
    {"name": "lisi", "age": 19},
    {"name": "wangwu", "age": 17}
]
stus.sort(key = lambda x : x["name"])
print(stus)













