
from collections import OrderedDict

# 用于统计处理从数据库中获取到的职位信息
class Parse:
    def resultParse(name, count, citylist, salarylist, educationlist):
        if count:
            info_count = {
                'skillName': name,
                'positionCount': count,
                'mainCity': {
                    'firstCity': citylist[0][0],
                    'secondCity': citylist[1][0],
                    'thirdCity': citylist[2][0],
                },
                'mainSalary': salarylist[0][0],
                'mainEducation': educationlist[0][0],
            }
        else:
            info_count = {}
        print(info_count)
        return info_count

    def PositionCount(result):
        count = 0
        for c in result:
            count += 1
        return count

    def CityParse(result):
        citylist = {}
        for r in result:
            if r[3] not in citylist.keys():
                citylist[r[3]] = 1
            else:
                citylist[r[3]] += 1
        print(citylist)
        citylist = sorted(citylist.items(), key=lambda c: c[1], reverse=True)
        print(citylist)
        return citylist

    def SalaryParse(result):
        salarylist = {
            '1k-5k': 0,
            '5k-10k': 0,
            '10k-15k': 0,
            '15k-20k': 0,
            '20k以上': 0,
        }
        for r in result:
            low = int(r[4].lower().split('k', 1)[0])
            str = r[4].lower().split('k')[1].split('-')
            if len(str) == 2:
                high = int(r[4].lower().split('k')[1].split('-')[1])
            elif len(str) == 1:
                high = low
            avg = (low + high) / 2
            if avg >= 2 and avg < 5:
                salarylist['2k-5k'] += 1
            elif avg >= 5 and avg < 10:
                salarylist['5k-10k'] += 1
            elif avg >= 10 and avg < 15:
                salarylist['10k-15k'] += 1
            elif avg >= 15 and avg < 20:
                salarylist['15k-20k'] += 1
            elif avg >= 20:
                salarylist['20k以上'] += 1
        salarylist = sorted(salarylist.items(), key=lambda c: c[1], reverse=True)
        print(salarylist)
        return salarylist

    def EducationParse(result):
        educationlist = {}
        for r in result:
            if r[5] not in educationlist.keys():
                educationlist[r[5]] = 1
            else:
                educationlist[r[5]] += 1
        educationlist = sorted(educationlist.items(), key=lambda c: c[1], reverse=True)
        print(educationlist)
        return educationlist

    def pathParse(path):
        path = path.split('\\', 2)[2].replace('\\', '/')
        path = '/' + path
        oldsignal = ['+', '#']
        newsignal = [r'%2B', r'%23']
        for s in oldsignal:
            if s in path:
                i = oldsignal.index(s)
                path.replace(s, newsignal[i])
                print(i, s, newsignal[i])
        print(path)
        return path

    def getReslut(result, name):
        name = name
        pc = Parse.PositionCount(result)
        cp = Parse.CityParse(result)
        sp = Parse.SalaryParse(result)
        ep = Parse.EducationParse(result)
        result = Parse.resultParse(name, pc, cp, sp, ep)
        return result

    def getSkillData(positions):
        skill_context = {}
        for position in positions:
            if position.skillName not in skill_context.keys():
                skill_context[position.skillName] = 1
            else:
                skill_context[position.skillName] += 1
        skill = []
        skillnum = []
        for k,v in skill_context.items():
            skill.append(k)
            skillnum.append(v)
        return skill,skillnum

    def getCityData(positions):
        city_context = {}
        for position in positions:
            if position.city not in city_context.keys():
                city_context[position.city] = 1
            else:
                city_context[position.city] += 1
        city = []
        citynum = []
        for k,v in city_context.items():
            city.append(k)
            citynum.append(v)
        return city,citynum

    def getEducationData(positions):
        education_context = {}
        for position in positions:
            if position.education not in education_context.keys():
                education_context[position.education] = 1
            else:
                education_context[position.education] += 1
        print(education_context)
        education = []
        educationnum  = []
        for k,v in education_context.items():
            education.append(k)
            educationnum.append(v)
        return education,educationnum

    def getSalaryData(positions):
        salary_context = {
            '1k-5k': 0,
            '5k-10k': 0,
            '10k-15k': 0,
            '15k-20k': 0,
            '20k以上': 0,
        }
        for position in positions:
            low = int(position.salary.lower().split('k', 1)[0])
            str = position.salary.lower().split('k')[1].split('-')
            if len(str) == 2:
                high = int(position.salary.lower().split('k')[1].split('-')[1])
            elif len(str) == 1:
                high = low
            avg = (low + high) / 2
            if avg >= 1 and avg < 5:
                if '1k-5k' not in salary_context.keys():
                    salary_context['1k-5k'] = 1
                else:
                    salary_context['1k-5k'] += 1
            elif avg >= 5 and avg < 10:
                if '5k-10k' not in salary_context.keys():
                    salary_context['5k-10k'] = 1
                else:
                    salary_context['5k-10k'] += 1
            elif avg >= 10 and avg < 15:
                if '10k-15k' not in salary_context.keys():
                    salary_context['10k-15k'] = 1
                else:
                    salary_context['10k-15k'] += 1
            elif avg >= 15 and avg < 20:
                if '15k-20k' not in salary_context.keys():
                    salary_context['15k-20k'] = 1
                else:
                    salary_context['15k-20k'] += 1
            elif avg >= 20:
                if '20k以上' not in salary_context.keys():
                    salary_context['20k以上'] = 1
                else:
                    salary_context['20k以上'] += 1
        for k,v in salary_context.items():
            if v == 0:
                salary_context.pop(k)
        print(salary_context)
        salary = []
        salarynum  = []
        for k,v in salary_context.items():
            salary.append(k)
            salarynum.append(v)
        return salary,salarynum

    def getWorkyearData(positions):
        workyear_context = {}
        for position in positions:
            if position.workYear not in workyear_context.keys():
                workyear_context[position.workYear] = 1
            else:
                workyear_context[position.workYear] += 1
        print(workyear_context)
        workyear = []
        workyearnum  = []
        for k,v in workyear_context.items():
            workyear.append(k)
            workyearnum.append(v)
        return workyear,workyearnum

    def listToString(trans,transnum):
        trans_string = ''
        transnum_string = ''
        for t in trans:
            trans_string += t + ' '
        for tn in transnum:
            transnum_string += str(tn) + ' '
        return trans_string,transnum_string

    def stringToList(trans_string,transnum_string):
        # trans = []
        # transnum = []
        trans = trans_string.strip().split(' ')
        transnum = transnum_string.strip().split(' ')
        transnum = list(map(int,transnum)) #将字符数组转为整型数组
        return trans,transnum

    def format_date(date):
        year = date.year
        month = date.month
        day = date.day
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        year = str(year)
        return year + '-' + month + '-' + day

