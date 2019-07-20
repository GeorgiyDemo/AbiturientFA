"""
    Серверочек с Flask API с Selentium для определения рейтинга абитуры
"""

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
import base64, os
import database_module, json, threading
from flask import Flask, request
UPDATE_DATA = []
GLOBAL_URL = "http://lists4priemka.fa.ru/listabits.aspx?fl=0&tl=%D0%B1%D0%BA%D0%BB&le=%D0%92%D0%9F%D0%9E"
global_threading_driver = webdriver.Chrome()
global_signup_driver = webdriver.Chrome()
app = Flask(__name__)
# Подключение для получения результатов обработки документов

#Запуск в отдельном потоке от Flask
def threading_check_results():
    while True:
        get_results_class()
        time.sleep(60)


#Классы для работы в отдельном потоке
class get_results_class():

    def __init__(self):
        self.get_users()

    def get_users(self):
        driver = global_threading_driver
        users = database_module.mysql_writer("SELECT name FROM users",3)
        for name in users.result:
            user_obj = parse_links_class(name["name"], driver)
            self.compare_userdata(user_obj.result_arr)

#Сравнение НОВЫХ ДАННЫХ И ДАННЫХ ИЗ БД
#TODO  Более адексатное переименование JSON
    def compare_userdata(self, data):
        global UPDATE_DATA
        tid_from_name = database_module.mysql_writer("SELECT tid FROM users WHERE name='"+data[0][4]+"'", 2)
        changes_bufarr = {"tid" : tid_from_name.result["tid"], "updates":[]}
        bool_flag = False
        for item in data:
            bufscore = database_module.mysql_writer("SELECT waynumber FROM ways WHERE wayname='"+item[1]+"' AND tid="+tid_from_name.result["tid"], 2)
            if bufscore.result["waynumber"] != item[3]:
                bool_flag = True
                changes_bufarr["updates"].append(
                    {
                        "wayname": item[1],
                        "changed_from" : bufscore.result["waynumber"],
                        "changed_to": item[3]
                    }
                )
                database_module.mysql_writer("UPDATE ways SET waynumber="+item[3]+" WHERE wayname='"+item[1]+"' AND tid="+tid_from_name.result["tid"], 1)
        if bool_flag == True:
            UPDATE_DATA.append(changes_bufarr)


#Класс обработки регистрации пользователя
class signup_user_class():
    def __init__(self, user, tid):
        self.user = user
        self.tid = tid
        self.signup_detection_result = []
        self.signup_detection()
        if self.signup_detection_result != []:
            threading.Thread(target=self.signup_dataparser).start()

    def signup_detection(self):
        try:
            signup_obj = parse_links_class(self.user, global_signup_driver)
            self.signup_detection_result = signup_obj.result_arr
        except:
            self.signup_detection_result = []

    def signup_dataparser(self):
        input_data = self.signup_detection_result

        #Заносим данные в таблицу users
        exist_check = database_module.mysql_writer("SELECT * FROM users WHERE tid="+str(self.tid),2)
        if exist_check.result != None:
            database_module.mysql_writer("UPDATE users SET name='"+self.user+"', score="+str(input_data[0][6])+" WHERE tid="+str(self.tid)+";",1)
        else:
            database_module.mysql_writer("INSERT INTO users (tid, name, score) VALUES ("+str(self.tid)+",'"+self.user+"',"+str(input_data[0][6])+");",1)
        way_exist_check = database_module.mysql_writer("SELECT * FROM ways WHERE tid="+str(self.tid),2)
        if way_exist_check != None:
            database_module.mysql_writer("DELETE FROM ways WHERE tid="+str(self.tid)+";",1)
        for way in input_data:
            database_module.mysql_writer("INSERT INTO ways (tid, wayname, waynumber) VALUES ("+str(self.tid)+",'"+way[1]+"',"+str(way[3])+");",1)

class parse_links_class():
    def __init__(self, abitname, driver):
        self.driver = driver
        self.abitname = abitname
        self.result_arr = []
        self.abit_parser()

    def abit_parser(self):
        result_arr = self.result_arr
        driver = self.driver
        driver.get(GLOBAL_URL)
        #time.sleep(1)
        element = driver.find_element_by_xpath('//*[@id="ASPxGridView1_DXFREditorcol3_I"]')
        element.click()
        element.clear()
        element.send_keys(self.abitname)
        #Ожидаем пока прогрузится страничка
        time.sleep(6)
        soup_content = BeautifulSoup(driver.page_source, "lxml")

        i = 0
        while i != -1:
            try:
                dx_data = soup_content.find('tr',{'id':'ASPxGridView1_DXDataRow'+str(i)})
                buf_arr = []
                for element in dx_data:
                    buf_arr.append(element.string)
                result_arr.append(buf_arr)
                i += 1
            except TypeError:
                i = -1
        self.result_arr = result_arr


#Flask API для менеджмента
@app.route('/adduser', methods=['POST','GET'])
def add_user():
    """
    Метод для добавления пользователя
    """
    tg_data = request.json
    name = tg_data["username"]
    tid = tg_data["tid"]
    signup_obj = signup_user_class(name, tid)
    if signup_obj.signup_detection_result == []:
        return json.dumps({"status": "exception", "description": "Пользователя нет в списке"})
    return json.dumps({"status": "ok"})

#Обновления
@app.route('/updates', methods=['POST','GET'])
def get_updates():
    global UPDATE_DATA
    out_data = UPDATE_DATA
    UPDATE_DATA = []
    return json.dumps(out_data, ensure_ascii=False)

if __name__ == '__main__':
    threading.Thread(target=threading_check_results).start()
    app.run(host='127.0.0.1', debug=False)