from app.model import Position,Skill
from pandas import DataFrame
import datetime
import matplotlib.pyplot as plt
import seaborn
def getPosintionNum_by_time():
    columns = Skill.query.all()
    rower = Position.query.all();

    datelist = get_last_month()
    print(datelist)
    info = {}
    for month in datelist:
        print(month)
        list = []
        for column in columns:
            # 查询 每个月 每个技能 的岗位数
            count = Position.query.filter(Position.skillName == column.skillName,Position.createTime.like(month+'%')).count()
            list.append(count)
        info[month] = list
    df = DataFrame(info)
    df.to_csv(
        ".\\info.csv"
    )
    seaborn.distplot(df['2018-04'])
    plt.show()
    print(info)

def getSkillNum_by_type():
    info = {}
    name = []
    num = []
    for skill in Skill.query.order_by(Skill.skillNum.desc()):
        name.append(skill.skillName)
        num.append(skill.skillNum)
    info['skillname'] = name
    info['skillnum'] = num
    print(info)
    df = DataFrame(info)
    seaborn.set(font_scale=1.5,font='STSong')
    f, ax=plt.subplots(figsize=(20,20))

    #orient='h'表示是水平展示的，alpha表示颜色的深浅程度
    seaborn.barplot(y=df.skillname.values, x=df.skillnum.values,orient='h', alpha=0.8, color='red')

    #设置y轴、X轴的坐标名字与字体大小
    plt.ylabel('skillnum', fontsize=16)
    plt.xlabel('skillname', fontsize=16)

    #设置X轴的各列下标字体是水平的
    plt.xticks(rotation='horizontal')

    #设置Y轴下标的字体大小
    plt.yticks(fontsize=15)
    plt.show()

def getPositionNum_by_tend(skillName):
    datelist = get_last_month()
    info = {}
    month = []
    num = []
    for date in datelist:
        month.append(date)
        count = Position.query.filter(Position.skillName == skillName,Position.createTime.like(date+'%')).count()
        num.append(count)
    info['month'] = month
    info['num'] = num
    print(info)
    # f, ax=plt.subplots(figsize=(20,20))
    # seaborn.set(font_scale=1.5,font='STSong')
    # df = DataFrame(info)
    # seaborn.barplot(x=df.month.values, y=df.num.values, alpha=0.8, color='red')
    # plt.ylabel('number', fontsize=16)
    # plt.xlabel('month', fontsize=16)
    df = DataFrame(info)
    seaborn.distplot(df['num'])
    plt.show()

def get_last_month():
    #获取过去的12个月
    now = datetime.datetime.now()
    today_year = now.year
    last_year =  int(now.year) -1
    today_year_months = range(1,now.month+1)
    last_year_months = range(now.month+1, 13)
    data_list_lasts = []
    for last_year_month in last_year_months:
        if last_year_month < 10:
            data_list = '%s-0%s' % (last_year, last_year_month)
            data_list_lasts.append(data_list)
        else:
            date_list = '%s-%s' % (last_year, last_year_month)
            data_list_lasts.append(date_list)

    data_list_todays = []
    for today_year_month in today_year_months:
        if today_year_month < 10:
            data_list = '%s-0%s' % (today_year, today_year_month)
            data_list_todays.append(data_list)
        else:
            data_list = '%s-%s' % (today_year, today_year_month)
            data_list_todays.append(data_list)
    data_year_month = data_list_lasts + data_list_todays
    data_year_month.reverse()
    return data_year_month