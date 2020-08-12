import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json, threading
from vk_module import VkClass
from get_updates_module import TableClass

SEARCH_WORD = "Факультет информационных технологий и анализа больших данных"
GLOBAL_URL = "http://lists4priemka.fa.ru/enrollmentpay.aspx?fl=0&tl=%D0%B1%D0%BA%D0%BB&le=%D0%92%D0%9F%D0%9E"
PAGE_WAITING_INT = 8


#Драйвер для проверки обновлений
global_threading_driver = webdriver.Chrome("./chromedriver")

#Классы для работы в отдельном потоке
class ResultsClass():
    """
    Класс для получения обновлений через selentium
    """
    def __init__(self):
        #Получаем данные с сайта приёмки
        self.get_users()
        #Додавляем куда-либо эти данные
        self.result_processing()
    
    def get_users(self):
        driver = global_threading_driver
        parse_obj = ParserClass(SEARCH_WORD, driver)
        self.result_arr = parse_obj.result_arr

    def result_processing(self):
        print(self.result_arr)
        table_obj = TableClass(self.result_arr)
        vk_obj = VkClass(self.result_arr)
        #TODO Дальше осуществляем какую-либо валидацию

class ParserClass():
    """
    Класс для коммуникации с элементами таблички в selentium

    Вызывается и при регистрации и при проверке обновлённых результатов с разными драйверами
    """
    def __init__(self, searchword, driver):
        self.driver = driver
        self.searchword = searchword
        self.result_arr = []
        self.abit_parser()

    def abit_parser(self):
        result_arr = self.result_arr
        driver = self.driver
        driver.get(GLOBAL_URL)
        element = driver.find_element_by_xpath('//*[@id="ASPxGridView1_DXFREditorcol3_I"]')
        element.click()
        element.clear()
        element.send_keys(self.searchword)

        #Цикл по каждой странице
        next_page_processing = 1
        string_processing = 0
        while next_page_processing != -1:

            #Ожидаем пока прогрузится страничка
            time.sleep(PAGE_WAITING_INT)
            soup_content = BeautifulSoup(driver.page_source, "lxml")

            #Цикл по каждой строке, когда строки нет - выходит
            string_flag = True
            while string_flag == True:
                try:
                    dx_data = soup_content.find('tr',{'id':'ASPxGridView1_DXDataRow'+str(string_processing)})
                    buf_arr = []
                    for element in dx_data:
                        buf_arr.append(element.string)
                    
                    print(buf_arr)
                    #Фикс для платки т.к. мне влом это делать как-то адекватно 
                    buf_arr[6:0] = ['Есть']

                    result_arr.append(buf_arr)
                    string_processing += 1
                except TypeError:
                    string_flag = False

            try:
                next_button_element = driver.find_element_by_class_name('dxWeb_pNext')
                next_button_element.click()
                next_page_processing += 1
                print("Переход на "+str(next_page_processing)+" страницу..")
            except:
                next_page_processing = -1

        self.result_arr = result_arr

if __name__ == '__main__':
    ResultsClass()