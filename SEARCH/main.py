import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json, threading
from vk_module import VkClass
from get_updates_module import TableClass
from database_module import MySQLClass

SEARCH_WORD = "Факультет информационных технологий и анализа больших данных"
URL_DICT =  { 
    False: "http://lists4priemka.fa.ru/enrollment.aspx?fl=0&tl=%D0%B1%D0%BA%D0%BB&le=%D0%92%D0%9F%D0%9E",
    True: "http://lists4priemka.fa.ru/enrollmentpay.aspx?fl=0&tl=%D0%B1%D0%BA%D0%BB&le=%D0%92%D0%9F%D0%9E"
}
PAGE_WAITING_INT = 8

# Драйвер для проверки обновлений
global_threading_driver = webdriver.Chrome("./chromedriver")

# Классы для работы в отдельном потоке
class ResultsClass:
    """
    Класс для получения обновлений через selentium
    """

    def __init__(self):
        # Вводим тех, с кем хотим работать (платка/бюджет)
        money_flag = False
        abit_type = input("С кем начать работу? (п/б) -> ")
        if abit_type == "п":
            money_flag = True

        #Выставляем рабочую БД для СУБД (платники и бюджет отдельно)
        MySQLClass.DATABASE = "FA_platka" if money_flag else "FA"
        print(MySQLClass.DATABASE)
        
        # Получаем данные с сайта приёмки
        self.get_users(money_flag)
        # Добавляем куда-либо эти данные
        self.result_processing()

    def get_users(self, money_flag):
        driver = global_threading_driver
        parse_obj = ParserClass(SEARCH_WORD, driver, money_flag)
        self.result_list = parse_obj.result_list

    def result_processing(self):
        result_list = self.result_list
        print("Общее кол-во человек в таблице на сайте: {}".format(len(result_list)))
        table_obj = TableClass(result_list)
        vk_obj = VkClass(result_list)


class ParserClass:
    """
    Класс для коммуникации с элементами таблички в selentium

    Вызывается и при регистрации и при проверке обновлённых результатов с разными драйверами
    """

    def __init__(self, searchword, driver, money_flag):
        self.driver = driver
        self.searchword = searchword
        self.result_list = []

        self.url = URL_DICT[money_flag]
        self.money_flag = money_flag

        self.abit_parser()


    def abit_parser(self):
        result_list = self.result_list
        driver = self.driver
        driver.get(self.url)
        element = driver.find_element_by_xpath(
            '//*[@id="ASPxGridView1_DXFREditorcol3_I"]'
        )
        element.click()
        element.clear()
        element.send_keys(self.searchword)

        # Цикл по каждой странице
        next_page_processing = 1
        string_processing = 0
        while next_page_processing != -1:

            # Ожидаем пока прогрузится страничка
            time.sleep(PAGE_WAITING_INT)
            soup_content = BeautifulSoup(driver.page_source, "lxml")

            # Цикл по каждой строке, когда строки нет - выходит
            string_flag = True
            while string_flag:
                try:
                    dx_data = soup_content.find(
                        "tr", {"id": "ASPxGridView1_DXDataRow" + str(string_processing)}
                    )
                    buf_arr = []
                    for element in dx_data:
                        buf_arr.append(element.string)
                    
                    # TODO Фикс для платки т.к. мне влом это делать как-то адекватно
                    if self.money_flag:
                        buf_arr[6:0] = ["Есть"]
                    print(buf_arr)
                    
                    result_list.append(buf_arr)
                    string_processing += 1
                except TypeError:
                    string_flag = False

            try:
                next_button_element = driver.find_element_by_class_name("dxWeb_pNext")
                next_button_element.click()
                next_page_processing += 1
                print("Переход на " + str(next_page_processing) + " страницу..")
            except:
                next_page_processing = -1

        self.result_list = result_list


if __name__ == "__main__":
    ResultsClass()
