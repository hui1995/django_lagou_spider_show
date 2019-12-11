#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template
from flask import request
from flask import session
from flask import g
from flask import jsonify
from flask import json
from . import main
from app.mysqldb import MySQL_DB
from app.parse import Parse
from app.drawimg import Drawimg
from app.model import User, Statistics, Position
from exts import db
from app.formcheck import LoginCheck, RegisterCheck
import datetime
import time
from app.analysis import get_last_month
# test 导包
from app.analysis import getPosintionNum_by_time, getSkillNum_by_type, getPositionNum_by_tend


# 表单中的路由映射
#

@main.route('/simple_query')  # 简单查询 将数据库中的爬取的职位信息全部展示出来
def simple_query():
    user = g.user
    page = request.args.get('page', 1, type=int)  # 分页
    search = request.args.get('search')  # 获取查询内容
    pagination = Position.query.filter(Position.skillName == search).order_by(Position.createTime.desc()).paginate(page,
                                                                                                                   per_page=20,
                                                                                                                   error_out=False)
    # pagination = Position.query.filter(Position.skillName.like('%'+search+'%')).order_by(Position.createTime.desc()).paginate(page,
    #                                                                                                                per_page=20,
    #                                                                                                                error_out=False)
    result = pagination.items  # 分页功能
    print(result)
    return render_template('simple.html', search=search, result=result, user=user, pagination=pagination)


@main.route('/test')
def test():
    return render_template('test.html')


@main.route('/pro_query', methods=['POST', 'GET'])  # 精确查询
def pro_query():
    search = request.args.get('search')  # 获取查询内容
    city = request.args.get('city')  # 获取查询内容
    salary = request.args.get('salary')  # 获取查询内容
    education = request.args.get('education')
    workyear = request.args.get('workyear')
    date_begin = request.args.get('date_begin')  # 获取查询内容
    date_end = request.args.get('date_end')  # 获取查询内容
    print("search", search)
    print("city", city)
    print("salary", salary)
    print("education", education)
    print("workyear", workyear)

    print("date_begin", date_begin)
    print("date_end", date_end)

    if salary == "不限":
        salary = ''

    if education == "不限":
        education = ''

    if workyear == '不限':
        workyear = ''

    if date_end == '':
        date_end = datetime.date.today()

    print(date_end)

    user = g.user
    page = request.args.get('page', 1, type=int)  # 分页
    pagination = Position.query.filter(
            Position.skillName.like('%' + search + '%'),
            Position.city.like('%' + city + '%'),
            Position.salary.like('%' + salary + '%'),
            Position.education.like('%' + education + '%'),
            Position.workYear.like('%' + workyear + '%'),
            Position.createTime.between(date_begin, date_end)
    ).order_by(Position.createTime.desc()).paginate(page, per_page=10, error_out=False)
    result = pagination.items  # 分页功能
    print('职位对象', result)
    return render_template('proquery.html', search=search, city=city, salary=salary,
                           education=education, workyear=workyear, date_begin=date_begin,
                           date_end=date_end, result=result, user=user, pagination=pagination)


@main.route('/count_query')  #
def count_query():
    dd = MySQL_DB()
    dd.__init__()
    dd.dbconn()
    sql = "select * from position where skillName like '%" + request.args.get('search') + "%'"
    if request.args.get('search') == '':
        context = {
            'result': None,
            'name': '',
            'user': g.user,
            'statisticsID': None,
        }
        return render_template('count.html', **context)
    else:
        result = dd.select(sql)
        name = request.args.get('search')
        pc = Parse.PositionCount(result)
        cp = Parse.CityParse(result)
        sp = Parse.SalaryParse(result)
        ep = Parse.EducationParse(result)

        cpath = Drawimg.draw(cp, name, 'city')
        spath = Drawimg.draw(sp, name, 'salary')
        epath = Drawimg.draw(ep, name, 'education')

        path = {
            'cpath': Parse.pathParse(cpath),
            'spath': Parse.pathParse(spath),
            'epath': Parse.pathParse(epath),
        }
        result = Position.query.filter(Position.skillName)
        result = Parse.resultParse(name, pc, cp, sp, ep)
        result['path'] = path
        if g.user == None:
            context = {
                'result': result,
                'name': name,
                'user': g.user,
                'statisticsID': -1,
            }
            return render_template('count.html', **context)
        else:
            stat = Statistics(
                    skillName=result['skillName'],
                    positionCount=result['positionCount'],
                    firstCity=result['mainCity']['firstCity'],
                    secondCity=result['mainCity']['secondCity'],
                    thirdCity=result['mainCity']['thirdCity'],
                    mainSalary=result['mainSalary'],
                    mainEducation=result['mainEducation'],
                    cityImgUrl=result['path']['cpath'],
                    salaryImgUrl=result['path']['spath'],
                    educationImgUrl=result['path']['epath'],
                    queryDate=datetime.date.today()
            )
            print(stat)
            querydates = []
            for stats in Statistics.query.filter(Statistics.skillName == stat.skillName):
                querydates.append(stats.queryDate)
            print(querydates)
            print(stat.queryDate)
            if stat.queryDate not in querydates:
                db.session.add(stat)
                db.session.commit()

            else:
                stat = Statistics.query.filter(Statistics.skillName == stat.skillName,
                                               Statistics.queryDate == stat.queryDate).first()
            print(stat.statisticsID)
            dd.close()

            context = {
                'result': result,
                'name': name,
                'user': g.user,
                'statisticsID': stat.statisticsID
            }
            return render_template('count.html', **context)


# 下面的登录与注册就用到了POST方法
# route函数默认是使用GET方法 所以要写明方法是用GET还是POST
# 简单来说 通过url跳转就是GET方法 通过表单提交就是POST方法
# 这里登录和注册都用到了GET和POST方法
# 因为转到登录注册页面是GET方法
# 通过表单提交是POST方法
# 可以去看一下templates文件夹下的login.html里的
#     <div class="form-group">
#         <h1>登录</h1>
#         <form method="post" action="/login" onsubmit="return validate_form(this)">
#             <label>账号</label><input class="form-control" type="text" id="txt_username" name="useraccount"><br>
#             <label>密码</label><input class="form-control" type="password" id="txt_userpwd" name="userpwd"><br>
#
#             <input type="checkbox" id="ck_rmbUser" name="isRmbUser">一个月内自动登录
#             <input class="btn btn-default" type="submit" id="sub" value="登录">
#         </form>
#     </div>
# 这段代码 form标签里的method是post action是/login  也就是说 当点击登录按钮提交表单中的登录信息时
# 会通过action 映射到下面登录的/login路由上 执行user_login()函数

@main.route('/login', methods=['GET', 'POST']) #登录功能
def user_login():
    if request.method == 'GET':  # 获取访问方式 如果是GET 就转到登录页面
        return render_template('login.html')
    else:  # 如果是POST 就进行登录验证
        useraccount = request.form.get('useraccount')
        userpwd = request.form.get('userpwd')
        isRmbUser = request.form.get('isRmbUser')
        lc = LoginCheck()
        if lc.is_empty(useraccount=useraccount, userpwd=userpwd):
            error = '请确认用户名或密码填写完整'
            return render_template("error.html", error=error)
        elif not lc.is_exist(useraccount):
            error = '用户名不存在，请检查'
            return render_template("error.html", error=error)
        elif not lc.is_vaild(useraccount, userpwd):
            error = '密码错误，请重新输入'
            return render_template('error.html', error=error)
        else:
            print('success')
            user = User.query.filter(User.userAccount == useraccount).first()
            print(user)
            print(user.userID)
            session['userID'] = user.userID
            if isRmbUser == 'on':
                session.permanent = True
            return render_template('index.html', user=user, skill=g.skill)


@main.route('/register', methods=['GET', 'POST'])  # 注册功能
def user_register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        useraccount = request.form.get('useraccount')
        username = request.form.get('username')
        userpwd = request.form.get('userpwd')
        againpwd = request.form.get('againpwd')

        rc = RegisterCheck()
        if rc.is_empty(useraccount, username, userpwd, againpwd):
            error = '请确认注册信息填写完整'
            return error
        elif not rc.againpwd_check(userpwd, againpwd):
            error = '密码重复错误，请重新输入'
            return error
        elif not rc.useraccount_repeat(useraccount):
            error = '此账号已经被注册'
            return error
        else:
            user = User(
                    userName=username,
                    userAccount=useraccount,
                    userPwd=userpwd,
                    Admin=0,  # 注册用户默认没有管理员权限
            )
            db.session.add(user)
            db.session.commit()
            userid = User.query.filter(User.userAccount == useraccount).first().userID
            session['userID'] = userid
            return '注册成功'
            # return render_template('success.html', user=user)


@main.route('/register_success', methods=['GET', 'POST']) #注册成功跳转
def register_success():
    if request.method == 'GET':
        user = g.user
        return render_template('success.html', user=user)
    else:
        user = g.user
        return render_template('success.html', user=user)


@main.route('/updateuser', methods=['POST']) #更新用户
def updateuser():
    userid = request.form.get('userid')
    username = request.form.get('username')
    # useraccount = request.form.get('useraccount')
    userpwd = request.form.get('userpwd')
    againpwd = request.form.get('againpwd')
    print(userid)
    rc = RegisterCheck()
    if rc.is_empty2(username, userpwd, againpwd):
        error = '请确认信息填写完整'
        return error
    elif not rc.againpwd_check(userpwd, againpwd):
        error = '确认密码错误，请重新输入'
        return error
    # elif not rc.useraccount_repeat(useraccount):
    #     error = '此账号已经被注册'
    #     return error
    else:
        user = User.query.filter(User.userID == userid).first()
        user.userName = username
        user.userPwd = userpwd
        db.session.commit()
        return "修改成功"


@main.route('/deleteuser', methods=['POST']) #删除用户
def deleteuser():
    userid = request.form.get('userid')
    user = User.query.filter(User.userID == userid).first()
    collections = user.collections
    print(collections)
    for collection in collections:
        db.session.delete(collection)
    db.session.delete(user)
    db.session.commit()
    return '删除成功'


@main.route('/updateposition', methods=['POST']) #更新岗位
def updateposition():
    positionid = request.form.get('positionid')
    positionname = request.form.get('positionname')
    companyshortname = request.form.get('companyshortname')
    city = request.form.get('city')
    salary = request.form.get('salary')
    education = request.form.get('education')
    workyear = request.form.get('workyear')
    createtime = request.form.get('createtime')
    print(positionid, positionname, companyshortname, city, salary, education, workyear, createtime)
    if positionname == '' or companyshortname == '' or city == '' or salary == '' or education == '' or workyear == '' or createtime == '':
        error = '请确认信息填写完整'
        return error
    else:
        position = Position.query.filter(Position.positionId == positionid).first()
        position.positionName = positionname
        position.companyShortName = companyshortname
        position.city = city
        position.salary = salary
        position.education = education
        position.workYear = workyear
        position.createTime = createtime
        db.session.commit()
        return "修改成功"


@main.route('/deleteposition', methods=['POST']) #删除岗位
def deleteposition():
    positionid = request.form.get('positionid')
    position = Position.query.filter(Position.positionId == positionid).first()
    db.session.delete(position)
    db.session.commit()
    return '删除成功'
