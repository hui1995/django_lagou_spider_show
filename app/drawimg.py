import matplotlib.pyplot as plt
import numpy as np
from time import strftime
import time


# 画图

class Drawimg:
    def draw(info, name, type):
        content = []
        number = []
        for i in info:
            content.append(i[0])
            number.append(i[1])
        print(content)
        print(number)
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        plt.figure(figsize=(10, 10))
        plt.pie(x=number, labels=content, autopct='%1.2f%%')
        title = name + "的" + type + '分布饼图'
        plt.title(title)

        time = strftime("%Y%m%d")
        # path = 'G:\\bishe\\app\\static\\chartimg'
        path = '.\\app\\static\\chartimg'
        filename = time + name + type + '.png'
        if type == 'city':
            path += '\city'
        elif type == 'salary':
            path += '\salary'
        elif type == 'education':
            path += '\education'
        filepath = path + '\\' + filename
        print(filepath)
        plt.savefig(filepath)
        # plt.show()
        return filepath

    def drawLine(result):
        #time.mktime(result[0][7].timetuple())
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

