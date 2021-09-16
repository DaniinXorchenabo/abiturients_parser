"""
предназначено для получения списка подавших заявление абитуриентов
с сайтов разных вузов
"""

import requests
from requests import Request, Session
import json
from re import sub, findall
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def nicer_list(students_list):
    students_list = list(students_list)
    # print(students_list)
    nise_stud = list(zip(*[i for i in students_list if bool(i)]))
    # print(nise_stud)
    maximums = [max([len(j) for j in i]) + 1 for i in nise_stud]
    nise_stud = list(zip(*[[i.ljust(m, ' ') for i in nise_stud[ind]] for ind, m in enumerate(maximums) if m > 1]))
    nise_stud = [' '.join([str(ind).ljust(3, ' ')] + list(i)) for ind, i in enumerate(nise_stud)]
    return nise_stud


def get_nise_text(name, dop_info, stud_list):
    main_title = name.center(40) + '\n\n'
    end = '-' * 60 + '\nВсего: ' + str(len(stud_list)) + '\n\n'
    stud_list = '\n'.join(stud_list) + '\n'
    dop_info = '\n' + dop_info + '\n\n'
    return ''.join([main_title, dop_info, stud_list, end])


def select_from_common_list(students, filter_func=lambda i: True):
    return filter(filter_func, students)


def all_PGY(filter_func=lambda i: True):
    def pgy(name_sp, url):
        driver = webdriver.Chrome('C:/Users/Acer/Downloads/chromedriver_win32/chromedriver.exe')
        driver.get(url)
        # print('77777777')
        selectors = {'faculty': 'Факультет вычислительной техники',
                     'edu_base':'Бюджет',
                     'edu_form': 'Очная',
                     'edu_level': 'Бакалавриат',
                     'speciality': name_sp}
        for name, change in selectors.items():
            element = driver.find_element_by_xpath(f"//select[@name='{name}']")
            all_options = element.find_elements_by_tag_name("option")
            for option in all_options:
                if option.text.lower().split() == change.lower().split():
                    option.click()
                    break
        elements = driver.find_elements_by_name("search_list")
        elements[0].click()
        # -----------------------------------------------------------------
        element = driver.find_elements_by_class_name("pages_container")[0]
        max_num = int([i for i in element.text.split()[::-1] if i.isdigit()][0])
        all_students = []
        for i in range(max_num):
            html = str(driver.page_source)
            rec_table = r'<table[^>]*?list_table.*?>(?:.|\n)*?<tbody.*?>((?:.|\n)*?)</tbody>'
            table = findall(rec_table, html)[0]
            rec1 = r'<tr.*?list_row_1.*?>(?:.|\n)*?list_row_4(?:.|\n)*?</tr>'
            students = findall(rec1, table)
            rec2 = r'<td.*?>(?:<.*?>)*((?:[^<>])*?)(?:<.*?>)*?</td>'
            students = [findall(rec2, i) for i in students]
            all_students.extend(students)
            element = driver.find_elements_by_class_name("pages_container")[0]
            element = element.find_elements_by_class_name('page_passive')[-1]
            element.click()

        useless = [0, 2, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23]
        # print(*all_students, sep='\n')
        all_students = list(zip(*(i for ind, i in enumerate(zip(*all_students)) if ind not in useless)))
        titles = ['имя', "бюджет", "доки", "согласие", "доп", "", "М", "И", "Р", "ОП", "Цел", "Преим"]
        all_students = sorted([[j.replace('&nbsp;', ' ') for j in i] for i in all_students], key=lambda i: int(i[5]), reverse=True)
        all_students = [titles] + all_students

        driver.close()
        # print(*all_students, sep='\n')
        # print(len(all_students[-1]))
        return get_nise_text(name_sp, '', nicer_list(select_from_common_list(all_students, filter_func)))



    url = 'https://pnzgu.ru/apply/list/faculty/31429808/speciality/1060/edu_level/2/edu_form/1/edu_base/1/p/1/sum/sort_type/descsort_field/sum/sort_type/desc/'
    names = ['09.03.01 Информатика и вычислительная техника',
             '01.03.02 Прикладная математика и информатика',
             '09.03.04 Программная инженерия']
    with open('pgy_list.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join([pgy(name, url) for name in names]))


def all_misis(filter_func=lambda i: True):
    def MISiS(name, url):
        URL_TEMPLATE = url
        recq = requests.get(URL_TEMPLATE)
        reg_st0 = r'(?:<tr>(?:.|\n)*?</tr>)'
        reg_st2 = r'<td>((?:.|\n)*?)</td>'
        students = findall(reg_st0, recq.text)
        students = [findall(reg_st2, i) for i in students]
        students = [i for i in students if bool(i)]
        titles = ['№', 'id', 'Имя', "все", "И", "М", "Р", "Доп", "", "Согл", "", "общага", "резы"]
        students = [titles] + students
        elements = []
        try:
            driver = webdriver.Chrome('C:/Users/Acer/Downloads/chromedriver_win32/chromedriver.exe')
            driver.get(url)
            elements = driver.find_elements_by_class_name('data-indent')  # data-indent

            useless = [1, 2, 3, 4, 9]
            elements = [j.text.split('\n') for i in elements for j in i.find_elements_by_class_name('row') if True or ind*ind1 not in useless]
            driver.close()
        except Exception:
            if not bool(elements) or typr(elements[0]) != list:
                elements = []

        elements = [i for ind, i in enumerate(elements) if ind not in useless]
        dop = '\n'.join(nicer_list(elements))
        print(dop)
        # print(students)



        stud_list = nicer_list(select_from_common_list(students, filter_func))
        line = int(elements[-1][-1]) + 1  #  + 1 с учетом загаловка
        if len(stud_list) - 1 >= line:
            stud_list.insert(line, f'КОНЕЦ БЮДЖЕТА {elements[-1][-1]}'.ljust(len(stud_list[-1]), '-'))
        return get_nise_text(name, dop, stud_list)

    misis_url = {
        "01.03.04 Прикладная математика": 'https://misis.ru/applicants/admission/progress/baccalaureate-and-specialties/list-of-applicants/list/?id=BAC-BUDJ-O-010304',
        "09.03.01 Информатика и вычислительная техника": 'https://misis.ru/applicants/admission/progress/baccalaureate-and-specialties/list-of-applicants/list/?id=BAC-BUDJ-O-090301',
        "09.03.03 Прикладная информатика": 'https://misis.ru/applicants/admission/progress/baccalaureate-and-specialties/list-of-applicants/list/?id=BAC-BUDJ-O-090303'}

    arr = '\n'.join([MISiS(name, url) for name, url in misis_url.items()])
    with open('misis_list.txt', 'w', encoding='utf-8') as f:
        f.write(arr)


def all_MIET(filter_func=lambda i: True):
    def MIET(name, url, sleep_t=2):
        driver = webdriver.Chrome('C:/Users/Acer/Downloads/chromedriver_win32/chromedriver.exe')
        driver.get(url)
        sleep(sleep_t)
        html = driver.page_source
        rec0 = r'<tbody>((?:.|\n)*?)</tbody>'
        rec1 = r'<tr.*?>((?:.|\n)*?)</tr>'
        rec2 = r'<td.*?>(.*?)</td>'
        table = findall(rec0, str(html))
        driver.close()
        if type(table) == list:
            table = table[0]
        students = findall(rec1, table)
        students = [findall(rec2, i) for i in students]
        # sorted_st = [i for ind, i in enumerate(students) if '+' in i[3]]

        return get_nise_text(name, '', nicer_list(select_from_common_list(students, filter_func)))

        # nise_stud = list(zip(*sorted_st))
        # maximums = [max([len(j) for j in i]) + 1 for i in nise_stud]
        # nise_stud = list(zip(*[[i.ljust(m, ' ') for i in nise_stud[ind]] for ind, m in enumerate(maximums) if m > 1]))
        # nise_stud = [' '.join([str(ind).ljust(3, ' ')] + list(i)) for ind, i in enumerate(nise_stud)]
        #
        # # print(*nise_stud, sep='\n')
        # # print('--------------------')
        # # print(len(nise_stud))
        # start = '\n' + ' ' * 20 + name + '\n'
        # main = '\n'.join(nise_stud) + '\n'
        # end = '-------------------\nВсего: ' + str(len(nise_stud)) + '\n'
        # return ''.join([start, main, end])

    urls = {
        "Информатика и вычислительная техника": 'https://abit.miet.ru/lists/list-all/list.php?d=09.03.01&fo=o&fin=b',
        "Прикладная математика": "https://abit.miet.ru/lists/list-all/list.php?d=01.03.04&fo=o&fin=b",
        "Программная инженерия": "https://abit.miet.ru/lists/list-all/list.php?d=09.03.04&fo=o&fin=b"}
    with open('MIET.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join([MIET(name, url) for name, url in urls.items()]))

def pgy_2(filter_func=lambda i: True):
    def read_goten_list_pgy():
        with open('PGY_ended_list.txt', 'r', encoding='utf-8') as f:
            data = list(zip(*map(lambda i: [f'{i[0]} {i[1][0]}', i[-1]], (i.split()[1:] for i in f.read().split('\n') if bool(i) and i.split()[0][:-1].isdigit()))))  #
        return data

    def processing_list_pgy(name_sp, url):
        from functools import reduce
        data = read_goten_list_pgy()
        useless = [0, 2, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23]
        driver = webdriver.Chrome('C:/Users/Acer/Downloads/chromedriver_win32/chromedriver.exe')
        driver.get(url)
        html = str(driver.page_source)
        driver.close()

        rec_table = r'<table[^>]*?list_table.*?>(?:.|\n)*?<tbody.*?>((?:.|\n)*?)</tbody>'
        table = findall(rec_table, html)[0]
        rec1 = r'<tr.*?list_row_1.*?>(?:.|\n)*?list_row_4(?:.|\n)*?</tr>'
        students = findall(rec1, table)
        rec2 = r'<td.*?>(?:<.*?>)*((?:[^<>])*?)(?:<.*?>)*?</td>'
        students = [findall(rec2, i) for i in students]
        students = zip(*(i for ind, i in enumerate(zip(*students)) if ind not in useless))
        protected_f = lambda i, arr=[]: (reduce(lambda p1, p2: (data[0].index(i, p1 + 1), arr.append(data[0].index(i, p1 + 1)))[0], range(data[0].count(i) + 1)), arr)[1]
        students = [[j.replace('&nbsp;', ' ') for j in i] for i in students]
        students = [i for i in students if not bool([j for j in protected_f(i[0].split('.')[0]) if data[1][j] == i[5]])]
        # print(i[0].split('.')[0]) or
        students = sorted(students, key=lambda i: int(i[5]), reverse=True)
        titles = ['имя', "бюджет", "доки", "согласие", "доп", "", "М", "И", "Р", "ОП", "Цел", "Преим"]
        students = [titles] + students
        # print(*students, sep='\n')
        return get_nise_text(name_sp, '', nicer_list(select_from_common_list(students, filter_func)))

    _dict = {'09.03.01 — Информатика и вычислительная техника (очно)': "https://pnzgu.ru/apply/k_list_20/speciality/1060/",
             '01.03.02 — Прикладная математика и информатика (очно)': "https://pnzgu.ru/apply/k_list_20/speciality/1042/",
             "09.03.04 — Программная инженерия (очно)": "https://pnzgu.ru/apply/k_list_20/speciality/1069/"}
    # [processing_list_pgy(name, url) for name, url in _dict.items()]
    with open('pgy_list.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join([processing_list_pgy(name, url) for name, url in _dict.items()]))



if __name__ == '__main__':
    from functools import reduce

    a = [1,2,3,4,5,2,3,4,5,3,4]
    mass = []
    reduce(lambda p1, p2: (a.index(3, p1 + 1), mass.append(a.index(3, p1 + 1)))[0], range(a.count(3) + 1))
    print(mass)
    pgy_2()
    #print(*pgy_2(), sep='\n')
    #all_misis(lambda i: ('+' in i[9] or "Согл" in i) and (i[10].lower().strip() not in ['ок;', "цп;"]))
    # all_MIET(lambda i: '+' in i[3])
    # all_PGY(lambda i: 'да' in i[3].lower() or i[3] == 'согласие')