"""
    Серверочек с Flask API с Selentium для определения рейтинга абитуры
"""

import base64
import os
import re
import time

import database_module
import json
import requests
import threading
from bs4 import BeautifulSoup
from flask import Flask, request
from selenium import webdriver

UPDATE_DATA = []
GLOBAL_URL = "http://lists4priemka.fa.ru/enrollment.aspx?fl=0&tl=%D0%B1%D0%BA%D0%BB&le=%D0%92%D0%9F%D0%9E"
PAGE_WAITING_INT = 8

# Фикс для Docker
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1420,1080")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
# Драйвер для проверки обновлений
global_threading_driver = webdriver.Chrome(chrome_options=chrome_options)
# Драйвер для регистрации пользователей
global_signup_driver = webdriver.Chrome(chrome_options=chrome_options)
app = Flask(__name__)


def threading_check_server_results():
    """
    Метод для отдельного запуска в threading, с Flask не связан
    """
    while True:
        get_results_class()
        time.sleep(120)


# Классы для работы в отдельном потоке
class get_results_class:
    """
    Класс для получения обновлений через selentium
    """

    def __init__(self):
        self.get_users()

    def get_users(self):
        driver = global_threading_driver
        users = database_module.mysql_writer("SELECT name FROM users", 3)
        for name in users.result:
            user_obj = parse_links_class(name["name"], driver)
            self.compare_userdata(user_obj.result_arr)

    def compare_userdata(self, data):
        """
        Метод для сравнения новых данных и данных в БД

        Если данные разные, то формирует элемент в UPDATE_DATA и заносит новые данные в БД
        """
        global UPDATE_DATA
        for item in data:
            try:
                tid_from_name = database_module.mysql_writer(
                    "SELECT tid FROM users WHERE name='" + item[3] + "'", 2
                )
                bufscore = database_module.mysql_writer(
                    "SELECT waynumber FROM ways WHERE wayname='"
                    + item[4]
                    + "' AND tid="
                    + tid_from_name.result["tid"],
                    2,
                )
                if str(bufscore.result["waynumber"]) != str(item[1]):
                    UPDATE_DATA.append(
                        {
                            "tid": tid_from_name.result["tid"],
                            "wayname": item[4],
                            "changed_from": str(bufscore.result["waynumber"]),
                            "changed_to": str(item[1]),
                        }
                    )
                    database_module.mysql_writer(
                        "UPDATE ways SET waynumber="
                        + item[1]
                        + " WHERE wayname='"
                        + item[4]
                        + "' AND tid="
                        + tid_from_name.result["tid"],
                        1,
                    )
            except:
                continue


class signup_user_class:
    """
    Класс для обработки и регистрации пользователей
    """

    def __init__(self, user, tid):
        self.user = user
        self.tid = tid
        self.signup_detection_result = []
        self.signup_detection()
        if self.signup_detection_result != []:
            threading.Thread(target=self.signup_dataparser).start()

    def signup_detection(self):
        """
        Метод проверки на то, чтоб пользователь был в списке
        """
        try:
            signup_obj = parse_links_class(self.user, global_signup_driver)
            self.signup_detection_result = signup_obj.result_arr
        except:
            self.signup_detection_result = []

    def signup_dataparser(self):
        """
        Если пользователь есть, то вызывается этот метод

        В этом методе заносятся новые/обновленные данные в таблицы users (пользователи) и ways (направления)
        """
        input_data = self.signup_detection_result

        # Заносим данные в users
        exist_check = database_module.mysql_writer(
            "SELECT * FROM users WHERE tid=" + str(self.tid), 2
        )
        if exist_check.result != None:
            database_module.mysql_writer(
                "UPDATE users SET name='"
                + self.user
                + "', score="
                + str(input_data[0][6])
                + " WHERE tid="
                + str(self.tid)
                + ";",
                1,
            )
        else:
            database_module.mysql_writer(
                "INSERT INTO users (tid, name, score) VALUES ("
                + str(self.tid)
                + ",'"
                + self.user
                + "',"
                + str(input_data[0][6])
                + ");",
                1,
            )
        # Заносим данные в ways
        way_exist_check = database_module.mysql_writer(
            "SELECT * FROM ways WHERE tid=" + str(self.tid), 2
        )
        if way_exist_check != None:
            database_module.mysql_writer(
                "DELETE FROM ways WHERE tid=" + str(self.tid) + ";", 1
            )
        for way in input_data:
            database_module.mysql_writer(
                "INSERT INTO ways (tid, wayname, waynumber) VALUES ("
                + str(self.tid)
                + ",'"
                + way[4]
                + "',"
                + str(way[1])
                + ");",
                1,
            )


class parse_links_class:
    """
    Класс для коммуникации с элементами таблички в selentium

    Вызывается и при регистрации и при проверке обновлённых результатов с разными драйверами
    """

    def __init__(self, abitname, driver):
        self.driver = driver
        self.abitname = abitname
        self.result_arr = []
        self.abit_parser()

    def abit_parser(self):
        result_arr = self.result_arr
        driver = self.driver
        driver.get(GLOBAL_URL)
        # time.sleep(1) #Иногда происходит дубляж если закомментировано, почему?
        element = driver.find_element_by_xpath(
            '//*[@id="ASPxGridView1_DXFREditorcol2_I"]'
        )
        element.click()
        element.clear()
        element.send_keys(self.abitname)
        # Ожидаем пока прогрузится страничка
        time.sleep(PAGE_WAITING_INT)
        soup_content = BeautifulSoup(driver.page_source, "lxml")

        i = 0
        while i != -1:
            try:
                dx_data = soup_content.find(
                    "tr", {"id": "ASPxGridView1_DXDataRow" + str(i)}
                )
                buf_arr = []
                for element in dx_data:
                    buf_arr.append(element.string)
                result_arr.append(buf_arr)
                i += 1
            except TypeError:
                i = -1
        self.result_arr = result_arr


# Flask API для менеджмента
@app.route("/adduser", methods=["POST", "GET"])
def add_user():
    """
    Метод Flask'а для регистрации новых пользователей
    """
    tg_data = request.json
    name = tg_data["username"]
    tid = tg_data["tid"]
    signup_obj = signup_user_class(name, tid)
    if signup_obj.signup_detection_result == []:
        return json.dumps({"status": "exception"})
    return json.dumps({"status": "ok"})


# Обновления
@app.route("/updates", methods=["POST", "GET"])
def get_updates():
    """
    Метод Flask'а для получения обновлений рейтинга
    """
    global UPDATE_DATA
    out_data = UPDATE_DATA
    UPDATE_DATA = []
    return json.dumps(out_data, ensure_ascii=False)


if __name__ == "__main__":
    threading.Thread(target=threading_check_server_results).start()
    app.run(host="0.0.0.0", debug=False)
