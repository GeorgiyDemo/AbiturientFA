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


#Класс для провеки есть ли чел в списке в целом
def signup_user_check(user):
    try:
        parse_links_class(user, global_signup_driver)
        return True
    except:
        return False
#Классы для работы в отдельном потоке
class get_results_class():

    def __init__(self):
        self.get_users()

    def get_users(self):
        driver = global_threading_driver
        users = database_module.mysql_writer("SELECT name FROM users",3)
        for name in users.result:
            parse_links_class(name["name"], driver)

class parse_links_class():
    def __init__(self, abitname, driver):
        self.driver = driver
        self.abitname = abitname
        print("***")
        print(abitname)
        self.result_arr = []
        self.abit_parser()
        self.out_result()

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

    #ЕСЛИ ЗАПИСЬ В БД ДРУГАЯ - АПДЕЙТ МАССИВЧИКА
    def out_result(self):
        result_arr = self.result_arr
        print(result_arr[0][4]+"\n")
        for item in result_arr:
            print(item[1]+"\nМесто: "+str(item[3]))


#Flask API для менеджмента
@app.route('/adduser', methods=['POST','GET'])
def add_user():
    """
    Метод для добавления пользователя
    """
    tg_data = request.json
    name = tg_data["username"]
    tid = tg_data["tid"]
    if signup_user_check(name) == False:
        return json.dumps({"status": "exception", "description": "Пользователя нет в списке"})
    return json.dumps({"status": "ok"})
    #return "MEOW"

if __name__ == '__main__':
    threading.Thread(target=threading_check_results).start()
    app.run(host='127.0.0.1', debug=False)