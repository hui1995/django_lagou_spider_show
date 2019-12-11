#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, session, g, request,jsonify
from app.model import User, Statistics, Collect, Skill,Position,Stat
from exts import db
from . import main
from app.decorators import login_required
import datetime
from spider.crawler import crawler_main,kd_list,start,start_keyword
from app.analysis import get_last_month
from app.parse import Parse
from app.drawimg import Drawimg
import matplotlib.pyplot as plt
import numpy as np
import time
# 主要路由映射

# 所谓路由映射 就是flask框架提供的url路由—>视图函数的映射
# route('/xxx')里的xxx就是在浏览器中输入的url
# 下方定义的 def函数 就是对应的视图函数
# 当在浏览器中输入url地址时 会调用视图函数

@main.route('/')  # 默认地址 127.0.0.1/
@main.route('/index', methods = ['GET','POST'])  # 主页地址 127.0.0.0/index 当在浏览器中输入这两个地址时会执行index()函数
def index():
    if request.method == 'POST':
        skill = []
        data = []
        skills = Skill.query.all()
        for s in Skill.query.order_by(Skill.skillNum):
            skill.append(s.skillName)
            data.append(s.skillNum)
        return jsonify(skill = skill,data = data)
    else:
        user = g.user  # g是flask中自带的全局变量 全局变量在任何视图函数中都可以使用 可以存放对象 保存用户
        return render_template('index.html', user=user,
                               skill=g.skill)  # render_template()的作用是跳转到templates文件夹下的html页面中 后面的参数是传递到页面中


@main.route('/simple')  # 简单查询
def simple():
    user = g.user
    return render_template('simple.html', user=user)  # 比如在simple.html页面中 就可以使用 {{user}}的方式来读取user的值

@main.route('/proquery')  # 精确查询
def proquery():
    user = g.user
    return render_template('proquery.html', user=user)

@main.route('/count', methods = ['GET','POST'])  # 统计查询
def count():
    if request.method == 'POST':
        skillname = request.form.get('search')
    else:
        user = g.user
        return render_template('count.html', user=user)

@main.route('/showcharts', methods = ['GET','POST'])  # 精确统计查询
def showcharts():
    if request.method == 'POST':
        skillname = request.form.get('search')
        city = request.form.get('city') #获取查询内容
        salary = request.form.get('salary') #获取查询内容
        education = request.form.get('education')
        workyear = request.form.get('workyear')
        chart_type = request.form.get('chart_type') #获取查询内容
        chart_info = request.form.get('chart_info') #获取查询内容
        print('skillname',skillname)
        print('city',city)
        print('salary',salary)
        print('education',education)
        print('workyear',workyear)
        print('chart_type',chart_type)
        print('chart_info',chart_info)

        if salary == "不限":
            salary = ''

        if education == "不限":
            education = ''

        if workyear == '不限':
            workyear = ''

        if chart_info == '技能':
            skillname = ''
        elif chart_info == '城市':
            city = ''
        elif chart_info == '薪资':
            salary = ''
        elif chart_info == '学历':
            education = ''
        elif chart_info == '工作经验':
            workyear = ''

        positions = Position.query.filter(
            Position.skillName.like('%'+skillname+'%'),
            Position.city.like('%'+city+'%'),
            Position.salary.like('%'+salary+'%'),
            Position.education.like('%'+education+'%'),
            Position.workYear.like('%'+workyear+'%'),
        )

        allnumber = Position.query.filter().count()

        if chart_info == '技能':
            result,resultnum = Parse.getSkillData(positions)
        elif chart_info == '城市':
            result,resultnum = Parse.getCityData(positions)
        elif chart_info == '薪资':
            result,resultnum = Parse.getSalaryData(positions)
        elif chart_info == '学历':
            result,resultnum = Parse.getEducationData(positions)
        elif chart_info == '工作经验':
            result,resultnum = Parse.getWorkyearData(positions)

        return jsonify(result=result,resultnum=resultnum,allnumber = allnumber,
                       chart_type=chart_type,chart_info = chart_info)
    else:
        user = g.user
        return render_template('showcharts.html', user=user)

@main.route('/statistics', methods = ['GET','POST'])  # 简单统计查询
def statistics():
    if request.method == 'POST':
        skillname = request.form.get('search')
        print(skillname)
        positions = Position.query.filter(Position.skillName == skillname)
        city,citynum = Parse.getCityData(positions)
        education,educationnum = Parse.getEducationData(positions)
        salary,salarynum = Parse.getSalaryData(positions)
        print(city,citynum)
        print(education,educationnum)
        print(salary,salarynum)

        city_string,citynum_string = Parse.listToString(city,citynum)
        salary_string,salarynum_string = Parse.listToString(salary,salarynum)
        education_string,educationnum_string = Parse.listToString(education,educationnum)

        querydate = datetime.date.today()
        collectnum = Collect.query.filter(Collect.queryName == skillname,Collect.collectDate==querydate).count()

        stat = Stat(
            city = city_string,
            cityNum = citynum_string,
            salary = salary_string,
            salaryNum = salarynum_string,
            education = education_string,
            educationNum = educationnum_string,
            queryDate = querydate,
            skillName = skillname
        )
        stats = Stat.query.filter(Stat.skillName == stat.skillName)
        date = []
        for s in stats:
            date.append(s.queryDate)
        if stat.queryDate not in date:
            db.session.add(stat)
            db.session.commit()

        return jsonify(city=city,citynum=citynum,education=education,
                       educationnum=educationnum,salary=salary,salarynum=salarynum,skillname = skillname,
                       collectnum = collectnum)
    else:
        user = g.user
        return render_template('statistics.html', user=user)

@main.route('/alldata', methods = ['GET','POST'])  # 统计全部信息
def alldata():
    positions = Position.query.all()
    skillname = 'all'
    city,citynum = Parse.getCityData(positions)
    salary,salarynum = Parse.getSalaryData(positions)
    education,educationnum = Parse.getEducationData(positions)

    print(city,citynum)
    print(salary,salarynum)
    print(education,educationnum)

    querydate = datetime.date.today()
    collectnum = Collect.query.filter(Collect.queryName == skillname,Collect.collectDate==querydate).count()

    city_string,citynum_string = Parse.listToString(city,citynum)
    salary_string,salarynum_string = Parse.listToString(salary,salarynum)
    education_string,educationnum_string = Parse.listToString(education,educationnum)

    print(city_string,citynum_string)
    print(salary_string,salarynum_string)
    print(education_string,educationnum_string)

    stat = Stat(
        city = city_string,
        cityNum = citynum_string,
        salary = salary_string,
        salaryNum = salarynum_string,
        education = education_string,
        educationNum = educationnum_string,
        queryDate = querydate,
        skillName = skillname
    )
    stats = Stat.query.filter(Stat.skillName == stat.skillName)
    date = []
    for s in stats:
        date.append(s.queryDate)
    if stat.queryDate not in date:
        db.session.add(stat)
        db.session.commit()
    return jsonify(city=city,citynum=citynum,salary=salary,salarynum=salarynum,
                   education=education,educationnum=educationnum,skillname = skillname,
                   collectnum=collectnum)


@main.route('/logout')  # 用户登出
def logout():
    # session['userID'] = None  # session是服务器缓存 用来保存用户id 实现保存登录信息的功能
    session.pop('userID', None)  # 将userID从session中删除 实现用户登出的功能
    return render_template('index.html', skill=g.skill)


@main.route('/home')  # 个人主页
def user_home():
    user = g.user
    collections = user.collections  # 获取当前用户的收藏信息 collections是一个列表
    for collection in collections:
        print(collection.collectDate)
    return render_template('home.html', user=user, collections=collections)


@main.route('/admin')  # 后台管理
def admin():
    user = g.user
    return render_template('admin.html', user=user)

@main.route('/userlist') # 用户列表
def userlist():
    user = g.user
    page = request.args.get('page', 1, type=int) #分页
    pagination = User.query.filter().paginate(page,per_page=10,error_out=False)
    result = pagination.items #分页功能
    print(result)
    return render_template('userlist.html', result=result, user=user, pagination=pagination)

@main.route('/positionlist') # 岗位列表
def positionlist():
    user = g.user
    page = request.args.get('page', 1, type=int) #分页
    pagination = Position.query.order_by(Position.createTime.desc()).paginate(page,per_page=10,error_out=False)
    result = pagination.items #分页功能
    print(result)
    return render_template('positionlist.html', result=result, user=user, pagination=pagination)

@main.route('/statisticslist') # 统计列表
def statisticslist():
    user = g.user
    page = request.args.get('page', 1, type=int) #分页
    pagination = Stat.query.order_by(Stat.queryDate.desc()).paginate(page,per_page=10,error_out=False)
    result = pagination.items #分页功能
    print(result)
    return render_template('statisticslist.html', result=result, user=user, pagination=pagination)

@main.route('/spider', methods = ['GET','POST']) # 爬虫
def spider():
    user = g.user
    if request.method == 'GET':
        return render_template('spider.html',user = user,skill = g.skill)
    else:
        beginskill = int(request.form.get('startskill'))
        endskill = int(request.form.get('endskill'))
        pagerange = int(request.form.get('pagerange'))
        url = request.form.get('url')
        info = start(url,beginskill,endskill,pagerange)
        return info
        print(kd_list(beginskill,endskill))
        cityList = [u'']
        url = 'https://www.lagou.com/jobs/positionAjax.json'
        try:
            for kd in kd_list(beginskill,endskill):
                print('爬取%s' % kd)
                para = {'first': 'true', 'pn': '1', 'kd': kd, 'city': cityList[0]}
                flag = crawler_main(url, para,startpage,endpage)
                print('%s爬取成功' % kd)
                return jsonify(page = startpage,skillname = kd,spiderstate = 1)
        except Exception as e:
            print("爬取失败,在%s处遇到错误" % kd)
            return jsonify(page = startpage,skillname = kd,spiderstate = 3)

@main.route('/spider_keyword', methods = ['POST']) # 显示爬虫关键字列表
def spider_keyword():
    keyword = request.form.get('keyword')
    url = request.form.get('url')
    info = start_keyword(url,keyword)
    return info

@main.route('/add_keyword',methods = ['POST']) # 增加爬虫关键字
def add_keyword():
    keyword = request.form.get('keyword')
    skill = Skill.query.filter(Skill.skillName == keyword).first()
    if skill:
        return "关键词已经存在，无需增加，请直接爬取数据"
    else:
        skill = Skill(
            skillName = keyword,
            skillNum = 0,
        )
        db.session.add(skill)
        db.session.commit()
        return "关键字已经保存，可以对其进行爬取"

@main.route('/spiderstate', methods = ['GET','POST'])
def spiderstate():
    spiderstate = session.get("spiderstate")
    print("重复获取",session.get("spiderstate"))
    return jsonify(spiderstate = spiderstate)

@main.route('/ajax',methods = ['POST','GET'])
def ajax():
    if request.method == 'POST':
        skill = []
        skills = Skill.query.all()
        for s in skills:
            skill.append(s.skillName)
        print(skill)
        datelist = get_last_month()
        month = []
        datas = []
        context = {}
        for skillname in skill:
            context[skillname] = []
        for date in datelist:
            month.append(date)
            for skillname in skill:
                count = Position.query.filter(Position.skillName == skillname,Position.createTime.like(date + "%")).count()
                context[skillname].append(count)
        for skillname in skill:
            datas.append(context[skillname])
        print(datas)
        return jsonify(time = month,skill = skill,datas = datas)
    else:
        return render_template('ajax.html')

@main.route('/ajax2',methods = ['POST','GET'])
def ajax2():
    if request.method == 'POST':
        skillname = 'java'
        positions = Position.query.filter(Position.skillName == skillname)
        context = {}
        for position in positions:
            if position.city not in context.keys():
                context[position.city] = 1
            else:
                context[position.city]+=1
        city = []
        num = []
        for k,v in context.items():
            city.append(k)
            num.append(v)
        print(city,num)
        return jsonify(city=city,num=num)
    else:
        return render_template('ajax2.html')

@main.route('/collect', methods = ['POST','GET'])  # 收藏功能
def collect():
    #statisticsID = request.args.get('statisticsID')  # 获取url中的参数 statisticsID 统计信息表中的ID
    # 一般浏览器与服务器传输数据有两种方式 GET和 POST
    # GET方法一般从服务器获取数据不对服务器造成影响 通过url传参数 比如百度python会看到浏览器上的搜索栏内容如下
    # https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&ch=9&tn=98012088_6_dg&wd=python&oq=pycharm%25E5%25AF%25BC%25E5%2587%25BArequirement%25E6%2596%2587%25E4%25BB%25B6&rsv_pq=87ee94770000a13e&rsv_t=827bWDC3Mjm7oY3z67M%2F%2F9thxK1vGCXjMALR56I%2BTho%2B0rqP84oh2BTH79qK0jBiEj8v1g&rqlang=cn&rsv_enter=1&rsv_sug3=1&rsv_sug2=0&inputT=1565&rsv_sug4=1565
    # 其中/s 是路径 就比如我这里的/collect
    # 后面的？及其后面的内容不参与url路由映射
    # ？后面的 ie=utf-8&中 ie是参数名，utf-8是参数值 &符号是连接符，连接后面的参数
    # 如果我想获取 参数ie 的值 那么就可以用 a = request.args.get('ie')
    # 变量a 的结果就是utf-8
    # POST方法一般用于上传数据给服务器 通过表单获取参数 在views_forms.py文件中详细解释
    # print(statisticsID)
    # user = g.user
    # stat = Statistics.query.filter(Statistics.statisticsID == statisticsID).first()
    # # 这是sqlalchemy模块中的语句 用来进行数据库查询的 结果就是在数据库的statistics表中找到ID为从url中获取的statisticsID的那条记录并保存为对象
    # collectdate = datetime.date.today()
    # collection = Collect(
    #         userID=user.userID,
    #         statisticsID=statisticsID,
    #         collectDate=collectdate,
    #         queryName=stat.skillName,
    # )  # 创建一个收藏对象 也就是一个收藏记录 如果表中没有这个记录就保存到数据库中
    # statids = []
    # for collections in user.collections:
    #     statids.append(str(collections.statisticsID))
    # print(statids)
    # print(collection.statisticsID)
    # if str(collection.statisticsID) not in statids:
    #     db.session.add(collection)  # 保存到数据库中
    #     db.session.commit()  # 提交这次保存操作
    #     return "收藏成功"
    # else:
    #     return "已经收藏过了"
    if request.method == 'POST':
        skillname = request.form.get('skillname')
        print(skillname)
        querydate = datetime.date.today()
        stat = Stat.query.filter(Stat.skillName == skillname,Stat.queryDate == querydate).first()
        print(stat.statID)
        user = g.user
        print(user)
        collection = Collect(
            userID = user.userID,
            statisticsID = stat.statID,
            collectDate = querydate,
            queryName = skillname
        )
        statIDs = []
        for collections in user.collections:
            statIDs.append(str(collections.statisticsID))
        if str(collection.statisticsID) not in statIDs:
            db.session.add(collection)
            db.session.commit()
            return '收藏成功'
        else:
            return '已经收藏过了'
    else:
        user = g.user
        collections = user.collections  # 获取当前用户的收藏信息 collections是一个列表
        collectinos_position = []
        collections_statistics = []
        for collection in collections:
            if collection.positionID != None:
                position = Position.query.filter(Position.positionId==collection.positionID).first()
                position_and_collection = [position,collection]
                collectinos_position.append(position_and_collection)
            else:
                collections_statistics.append(collection)

        return render_template('collect.html', user=user, collectinos_position=collectinos_position,collections_statistics=collections_statistics)

@main.route('/collect_position',methods = ['POST','GET']) # 收藏岗位
def collect_position():
    if request.method == 'POST':
        positionid = request.form.get('positionid')
        user = g.user
        querydate = datetime.date.today()
        collection = Collect(
                userID = user.userID,
                positionID = positionid,
                collectDate = querydate,
            )
        positionids = []
        for collections in user.collections:
            positionids.append(collections.positionID)
        print(positionids)
        if collection.positionID not in positionids:
            db.session.add(collection)
            db.session.commit()
            return '收藏成功'
        else:
            return '已经收藏过了'

@main.route('/delete_expire', methods = ['POST','GET']) # 删除过期
def delete_expire():
    date_begin = request.args.get()
    date_end = request.args.get()
    delete_position = Position.query.filter(Position.createTime.between(date_begin,date_end))
    for d in delete_position:
        db.session.delete(d)
        db.commit()
    return "success"

@main.route('/detail',methods = ['POST','GET'])  # 收藏详情
def detail():
    if request.method == 'POST':
        statisticsID = request.form.get('statisticsID')
        stat = Stat.query.filter(Stat.statID == statisticsID).first()  # 从数据库中找到对应的statisticsID记录
        collection = Collect.query.filter(Collect.statisticsID == stat.statID,Collect.userID == g.user.userID).first()
        city,citynum = Parse.stringToList(stat.city,stat.cityNum)
        salary,salarynum = Parse.stringToList(stat.salary,stat.salaryNum)
        education,educationnum = Parse.stringToList(stat.education,stat.salaryNum)
        collectdate = str(collection.collectDate)
        skillname = stat.skillName
        return jsonify(city=city,citynum=citynum,education=education,
                       educationnum=educationnum,salary=salary,salarynum=salarynum,
                       skillname = skillname,collectdate = collectdate)
    else:
        statisticsID = request.args.get('statisticsID')
        print(statisticsID)
        user = g.user
        #stat = Stat.query.filter(Stat.statID == statisticsID).first()  # 从数据库中找到对应的statisticsID记录
        return render_template('detail.html', statisticsID=statisticsID, user=user)


@main.route('/delete_collect',methods = ['POST'])  # 删除收藏
def delete_collect():
    collectid = request.form.get('collectid')
    collection = Collect.query.filter(Collect.collectID == collectid).first()
    db.session.delete(collection)  # 删除
    db.session.commit()
    return "删除成功"

@main.route('/drawline',methods = ['GET','POST']) # 画线
def drawline():
    skillname = 'java'
    result = Position.query.filter(Position.skillName == skillname).all()
    data = dict()
    for i in result:
        temp = time.mktime(i.createTime.timetuple())
        if data.keys().__contains__(temp):
            data[temp] += 1
        else:
            data[temp] = 1

    x = list(data.keys())
    y = list(data.values())
    z1 = np.polyfit(x, y, 3)
    yy = np.polyval(z1,x)
    xx = []
    for i in x:
        i = time.localtime(int(i))
        i = time.strftime("%m-%d",i)
        xx.append(i)
    plt.plot(xx,y,'b^',label='f(x)')
    plt.plot(xx,yy,'r.',label='regression')
    plt.legend(loc=0)
    plt.grid(True)
    plt.xlabel('x')
    plt.ylabel('f(x)')
    print('draw')
    plt.show()
    return '111'


@main.before_request  # 钩子函数 在路由函数之前执行
def get_session_user():
    userid = session.get('userID')  # 在session中获取用户id 实现用户登录缓存的功能
    user = User.query.filter(User.userID == userid).first()
    g.user = user  # 将session中获取到的id对应的用户保存到全局变量g中
    skill = Skill.query.all()  # 将数据库skill表中所有信息提取出来 以便主页展示
    g.skill = skill

@main.before_app_first_request
def set_spider_state():
    g.spiderstate = 0
    print(g.spiderstate)
    session['spiderstate'] = g.spiderstate
    print('xxxx')