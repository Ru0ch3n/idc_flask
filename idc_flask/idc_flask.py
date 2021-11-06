# -*- coding: utf-8 -*
import os

from flask import Flask, request, session, url_for, send_from_directory
from werkzeug.utils import redirect
from utils.status_code import *
from utils.file_checker import *
from utils.md5 import *
from utils.file_traverser import *
import sqlite3
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './db/file/'

# 初始化idc flask应用
app = Flask(__name__)

# 配置sqlite3连接本地数据库
try:
    conn = sqlite3.connect('./db/idc_sqlite.db', check_same_thread=False)
    cursor = conn.cursor()
except:
    print("数据库连接错误")
    exit(int(status_code.internal_error))
else:
    print("数据库成功连接")

# 这数值要保密，签名用的！
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def has_worker(phone):
    cursor.execute("SELECT * FROM worker_info WHERE phone_num=?", (phone,))
    ls = []
    for row in cursor:
        ls.append(row)
    return len(ls) > 0


# 店家注册
@app.route("/shop_registry", methods=['GET', "POST"])
def shop_registry():
    if request.method == 'POST':
        # print(request.form)
        try:
            shop_info = (request.form['phone_num'],
                         md5(request.form['passwd']))
        except:
            print("注册请求异常")
            return status_code.request_error
        try:
            cursor.execute(
                "INSERT INTO shop_info (phone_num,passwd_md5) VALUES (?,?)",
                shop_info)
            conn.commit()
            session['phone_num'] = request.form['phone_num']
            session['role'] = 'shop'
        except:
            print('店家信息插入失败')
            return status_code.internal_error
        return status_code.success
    else:
        return '''
        <form method="post">
            <p>手机号<input type=text name=phone_num>
            <p>密码<input type=text name=passwd>
            <p>提交<input type=submit value=Login>
        </form>
    '''


# 工人注册
@app.route("/worker_registry", methods=['GET', "POST"])
def worker_registry():
    if request.method == 'POST':
        print(request.form)
        try:
            worker_info = (request.form['phone_num'],
                           md5(request.form['passwd']))
        except:
            print("注册请求异常")
            return status_code.request_error
        try:
            cursor.execute(
                "INSERT INTO worker_info (phone_num,name,passwd_md5,china_id) VALUES (?,?,?,?)",
                worker_info)
            conn.commit()
            session['phone_num'] = request.form['phone_num']
            session['role'] = 'worker'
        except:
            print('工人信息插入失败')
            return status_code.internal_error
        return status_code.success
    else:
        return '''
        <form method="post">
            <p>手机号<input type=text name=phone_num>
            <p>姓名<input type=text name=name>
            <p>密码<input type=text name=passwd>
            <p>身份证号<input type=text name=china_id>
            <p>提交<input type=submit value=Login>
        </form>
    '''


@app.route('/shop_login', methods=['GET', 'POST'])
def shop_login():
    if request.method == 'POST':
        cursor = conn.execute("SELECT passwd_md5 FROM shop_info WHERE phone_num=?", (request.form['phone_num'],))
        conn.commit()
        true_passwd_md5 = ""
        for row in cursor:
            true_passwd_md5 = row[0]
        # 查无此人时，跳转登录页面；有人则对比passwd
        if true_passwd_md5 == "" or true_passwd_md5 is None:
            return "未注册，请检查手机号是否注册！"
        else:
            passwd = request.form['passwd']
            passwd_md5 = md5(passwd)
            if passwd_md5 != true_passwd_md5:  # 密码错误
                return "密码错误！"
            else:  # 密码正确
                session['phone_num'] = request.form['phone_num']
                session['role'] = 'shop'
            return redirect(url_for('index'))
    return '''
        <form method="post">
            <p>手机号<input type=text name=phone_num>
            <p>密码<input type=text name=passwd>
            <p>登录<input type=submit value=Login>
        </form>
    '''


@app.route('/worker_login', methods=['GET', 'POST'])
def worker_login():
    if request.method == 'POST':
        cursor = conn.execute("SELECT passwd_md5 FROM worker_info WHERE phone_num=?", (request.form['phone_num'],))
        conn.commit()
        true_passwd_md5 = ""
        for row in cursor:
            true_passwd_md5 = row[0]
        # 查无此人时，跳转登录页面；有人则对比passwd
        if true_passwd_md5 == "" or true_passwd_md5 is None:
            return "未注册，请检查手机号是否注册！"
        else:
            passwd = request.form['passwd']
            passwd_md5 = md5(passwd)
            if passwd_md5 != true_passwd_md5:  # 密码错误
                return "密码错误！"
            else:  # 密码正确
                session['phone_num'] = request.form['phone_num']
                session['role'] = 'worker'
            return redirect(url_for('index'))
    return '''
        <form method="post">
            <p>手机号<input type=text name=phone_num>
            <p>密码<input type=text name=passwd>
            <p>登录<input type=submit value=Login>
        </form>
    '''


@app.route('/worker_update', methods=['GET', 'POST'])
def worker_update():
    if 'phone_num' not in session:
        return redirect(url_for("worker_registry"))
    if request.method == 'POST':
        print(request.form)
        try:
            worker_info = (request.form['name'], request.form['others'],
                           request.form['china_id'], request.form['skill'],
                           session['phone_num'])
            print(worker_info)
        except:
            print("更新异常")
            return status_code.request_error
        try:
            cursor.execute(
                "UPDATE worker_info SET name=?,others=?,china_id=?,skill=? WHERE phone_num=?",
                worker_info)
            conn.commit()
        except:
            print('工人信息更新失败')
            return status_code.internal_error
        return status_code.success
    else:
        return '''
        <form method="post">
            <h1>工人更新</h1>
            <p>姓名<input type=text name=name>
            <p>自我介绍<input type=text name=others>
            <p>身份证号<input type=text name=china_id>
            <p>我会<input type=text name=skill>
            <p>提交<input type=submit value=Login>
        </form>
    '''


@app.route('/shop_update', methods=['GET', 'POST'])
def shop_update():
    if 'phone_num' not in session:
        return redirect(url_for("shop_registry"))
    if request.method == 'POST':
        print(request.form)
        try:
            shop_info = (request.form['name'], request.form['china_id'],
                         request.form['shop_name'], request.form['shop_addr'],
                         request.form['others'], session['phone_num'])
            print(shop_info)
        except:
            print("商家信息更新异常")
            return status_code.request_error
        cursor.execute(
            "UPDATE shop_info SET name=?,china_id=?,shop_name=?,shop_addr=?,others=? WHERE phone_num=?",
            shop_info)
        conn.commit()
        '''
        try:
            cursor.execute(
                "UPDATE shop_info SET name=?,china_id=?,shop_name=?,shop_addr=?,others=？WHERE phone_num=?",
                shop_info)
            conn.commit()
        except:
            print('商家信息更新失败')
            return status_code.internal_error
        '''
        return status_code.success
    else:
        return '''
        <form method="post">
            <h1>商家更新</h1>
            <p>姓名<input type=text name=name>
            <p>身份证号<input type=text name=china_id>
            <p>商店名称<input type=text name=shop_name>
            <p>商店地址<input type=text name=shop_addr>
            <p>商店介绍<input type=text name=others>
            <p>提交<input type=submit value=Login>
        </form>
    '''


@app.route('/head_upload', methods=['GET', 'POST'])
def upload_images():
    role = session['role']
    if request.method == 'POST':
        # 检查是否存在空file内容
        if 'file' not in request.files:
            return redirect(status_code.request_error)
        file = request.files['file']
        # 检查是否filename为空字符串
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            img_all = traverse_files('./db/file/img/head/')
            img_of_this = [img for img in img_all if img.startswith(role + session['phone_num'])]
            print(img_of_this[0])
            os.remove('./db/file/img/head/' + img_of_this[0])
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER + 'img/head/',
                                   role + session['phone_num'] + '.' + filename.rsplit('.', 1)[1].lower()))
            return status_code.success
    return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''


@app.route('/head_download', methods=['GET', 'POST'])
def download_image():
    role = session['role']
    if request.method == 'GET':
        img_all = traverse_files('./db/file/img/head/')
        img_of_this = [img for img in img_all if img.startswith(role + session['phone_num'])]
        print(img_of_this[0])
        if os.path.isfile(os.path.join(UPLOAD_FOLDER + 'img/head/', img_of_this[0])):
            return send_from_directory(UPLOAD_FOLDER + 'img/head/', img_of_this[0], as_attachment=False)
    return status_code.request_error


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('phone_num', None)
    session.pop('role', None)
    return redirect(url_for('index'))


@app.route('/')
def index():
    if 'phone_num' in session:
        return f'Logged in as {session["phone_num"]}' + f' {session["role"]}'
    return 'You are not logged in'

