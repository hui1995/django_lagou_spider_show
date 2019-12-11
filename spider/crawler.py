# -*- coding: utf-8 -*-
from spider.https import Http
from spider.parse import Parse
from spider.setting import headers
from spider.setting import cookies
from spider.mysqlpipeline import MySQL_DB
import time
import logging
import codecs
import random
from flask import g,session

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s Process%(process)d:%(thread)d %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='diary.log',
                    filemode='a')


def getInfo(url, para,pagerange):
    """
    获取信息
    """
    generalHttp = Http()
    htmlCode = generalHttp.post(url, para=para, headers=headers, cookies=cookies)
    print(htmlCode)
    generalParse = Parse(htmlCode)
    print(generalParse)
    pageCount = generalParse.parsePage()
    print(pageCount)
    info = []
    # 最多爬取前500页
    if pageCount > 500:
        pageCount = 500
    if pagerange > pageCount:
        pagerange = pageCount
    for i in range(1, pagerange + 1):
    # for i in range(1, pageCount + 1):
        print('第%s页' % i)
        para['pn'] = str(i)
        htmlCode = generalHttp.post(url, para=para, headers=headers, cookies=cookies)
        generalParse = Parse(htmlCode)
        info = info + getInfoDetail(generalParse)
        time.sleep(random.randint(20, 40))
    return info


def getInfoDetail(generalParse):
    """
    信息解析
    """
    info = generalParse.parseInfo()
    return info


#
# def processInfo(info, para):
#     """
#     信息存储
#     """
#     logging.error('Process start')
#     try:
#         title = '公司名称\t公司类型\t融资阶段\t标签\t公司规模\t公司所在地\t职位类型\t学历要求\t福利\t薪资\t工作经验\n'
#         file = codecs.open('%s职位.xls' % para['city'], 'w', 'utf-8')
#         file.write(title)
#         for p in info:
#             line = str(p['companyName']) + '\t' + str(p['companyType']) + '\t' + str(p['companyStage']) + '\t' + \
#                    str(p['companyLabel']) + '\t' + str(p['companySize']) + '\t' + str(p['companyDistrict']) + '\t' + \
#                    str(p['positionType']) + '\t' + str(p['positionEducation']) + '\t' + str(
#                     p['positionAdvantage']) + '\t' + \
#                    str(p['positionSalary']) + '\t' + str(p['positionWorkYear']) + '\n'
#             file.write(line)
#         file.close()
#         return True
#     except Exception as e:
#         print(e)
#         return None


def kd_list(beginskill,endskill):
    db = MySQL_DB()
    db.__init__()
    db.dbconn()
    sql = "select skillName from skill where skillID > '"+str(beginskill-1)+"' and skillID < '"+ str(endskill+1) +"'"
    skill_list = db.select(sql)
    return skill_list


def crawler_main(url, para,pagerange):
    """
    主函数逻辑
    """
    logging.error('Main start')
    print(url)
    if url:
        info = getInfo(url, para,pagerange)  # 获取信息
        # print(info)
        # flag = processInfo(info, para)  # 信息储存
        # print(flag)
        # return flag
        return True
    else:
        return None

def start(url,beginskill,endskill,pagerange):
    kdList = [u'']
    # g.spiderstate = 1
    # print(g.spiderstate)
    session['spiderstate'] = 1
    print("运行开始",session.get("spiderstate"))
    # print(kd_list())
    cityList = [u'']
    #url = 'https://www.lagou.com/jobs/positionAjax.json'
    try:
        for kd in kd_list(beginskill,endskill):
            print("运行中",session.get("spiderstate"))
            print('爬取%s' % kd)
            para = {'first': 'true', 'pn': '1', 'kd': kd, 'city': cityList[0]}
            flag = crawler_main(url, para,pagerange)
            print('%s爬取成功' % kd)
            # g.spiderstate = 2
            session['spiderstate'] = 2
            return "爬虫结束，爬取成功"
    except Exception as e:
        print("爬取失败,在%s处遇到错误" % kd)
        # g.spiderstate = 3
        session['spiderstate'] = 3
        return "爬虫中断，在%s处遇到错误" % kd

def start_keyword(url,keyword):
    kdList = [u'']
    print("运行开始",session.get("spiderstate"))
    cityList = [u'']
    #url = 'https://www.lagou.com/jobs/positionAjax.json'
    try:
        print('爬取%s' % keyword)
        para = {'first': 'true', 'pn': '1', 'kd': keyword, 'city': cityList[0]}
        flag = crawler_main(url, para,500)
        print('%s爬取成功' % keyword)
        return "爬虫结束，爬取成功"
    except Exception as e:
        print("爬取失败,在%s处遇到错误" % keyword)
        return "爬虫中断，在%s处遇到错误" % keyword
#
# def start():
#     info = "success"
#     return info

#
#
# if __name__ == '__crawler__':
#     kdList = [u'']
#
#     # print(kd_list())
#     cityList = [u'']
#     url = 'https://www.lagou.com/jobs/positionAjax.json'
#     for kd in kd_list():
#         print('爬取%s' % kd)
#         para = {'first': 'true', 'pn': '1', 'kd': kd, 'city': cityList[0]}
#         flag = main(url, para)
#         if flag:
#             print('%s爬取成功' % kd)
#         else:
#             print('%s爬取失败' % kd)
