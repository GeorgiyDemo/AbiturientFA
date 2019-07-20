import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
import base64, os
import database_module

class get_users_class():

    def __init__(self):
        self.base_url = "http://lists4priemka.fa.ru/listabits.aspx?fl=0&tl=%D0%B1%D0%BA%D0%BB&le=%D0%92%D0%9F%D0%9E"
        self.get_users()

    def get_users(self):
        driver = webdriver.Chrome()
        driver.get(self.base_url)
        users = database_module.mysql_writer("SELECT name FROM users",3)
        for name in users.result:
            parse_links_class(name["name"], driver)

class parse_links_class():
    def __init__(self, abitname, driver):
        self.driver = driver
        self.abitname = abitname
        self.result_arr = []
        self.abit_parser()
        self.out_result()

    def abit_parser(self):
        result_arr = self.result_arr
        driver = self.driver
        element = driver.find_element_by_xpath('//*[@id="ASPxGridView1_DXFREditorcol3_I"]')
        element.click()
        element.clear()
        #Необходимо для прогрузки таблички
        time.sleep(6)
        #Еще раз находим элемент т.к. старый изменился после clear
        element = driver.find_element_by_xpath('//*[@id="ASPxGridView1_DXFREditorcol3_I"]')
        element.send_keys(self.abitname)
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

    def out_result(self):
        result_arr = self.result_arr
        print(result_arr[0][4]+"\n")
        for item in result_arr:
            print(item[1]+"\nМесто: "+str(item[3]))

get_users_class()