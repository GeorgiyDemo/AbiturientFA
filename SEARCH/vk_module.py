import database_module
import json
import requests
import time
import vk
import xlrd
import yaml

with open("./yaml/token.yaml", 'r') as stream:
    API_TOKEN = yaml.safe_load(stream)

API_VERSION = 5.73
USERS_YEARS = ["2000", "2001", "2002", "2003"]
GROUPS_ID_LIST = [134724725, 6319, 153039551, 27590309, 76552532, 196939200]
OUT_TXT_FILE = "./OUTPUT/OUTPUT_VK.txt"


def vk_search_good_output(vk_json, groupflag, full_name):
    out_str = ""
    for item in vk_json:

        vk_link = "https://vk.com/id" + str(item["id"])
        obj = database_module.MySQLWriter(
            "INSERT INTO vk_users (first_name, last_name, link, full_name) VALUES ('{}','{}','{}','{}')".format(item["first_name"], item["last_name"], vk_link, full_name))
        
        if obj.result:
            groupflag = (groupflag == True and " [по группе в вк]" or "")
            out_str += item["first_name"] + " " + item["last_name"] + " " + vk_link + groupflag + "\n"
            f = open(OUT_TXT_FILE, 'a')
            f.write(out_str)
            f.close()

    return out_str

class VkClass():
    def __init__(self, result_array):
        print("*Модуль поиска по VK*")
        self.result_array = result_array
        session = vk.Session(access_token=API_TOKEN)
        self.api = vk.API(session)
        self.APIVersion = API_VERSION

        # Отчистка файла от предыдущей сессии
        open(OUT_TXT_FILE, 'w').close()
        self.input_processing()

    def input_processing(self):

        for item in self.result_array:
        
            #Проверяем, есть ли результаты по нему в таблице
            obj = database_module.MySQLReaderOne("SELECT * FROM vk_users WHERE full_name='{}'".format(item[3]))
            if obj.result is None:

                print("**Работаем с пользователем " + item[3] + "**\nМесто " + str(item[1]) + str(", балл ") + str(
                    item[7]) + " [" + str(item[5]) + "]")
                print(item[4])
                buf_name = item[3].split(" ")
                abit_name = buf_name[0] + " " + buf_name[1]
                self.search_by_groups(abit_name, item[3])
                time.sleep(3)
                self.search_profile_method(abit_name, item[3])
                time.sleep(3)
            
            else:
                print("{} - уже проверяли, пропускаем..".format(item[3]))


    def search_profile_method(self, inputname, full_name):
        year_processing_flag = True

        # Практически не помогает
        print("***Простой поиск пользователя по VK***")
        simple_profiles = self.api.users.search(q=inputname, v=self.APIVersion)["items"]
        if len(simple_profiles) > 5 or simple_profiles == []:
            print("Ойй, много людей переезжаем на поиск по годам..")
        else:
            print("Отлично, выборка достаточно малая")
            print(vk_search_good_output(simple_profiles, False, full_name))
            year_processing_flag = False

        if year_processing_flag == True:
            good_flag = False
            for born_year in USERS_YEARS:
                time.sleep(1)
                profiles = self.api.users.search(q=inputname, birth_year=born_year, v=self.APIVersion)["items"]
                if (len(profiles) < 5) and profiles != []:
                    print("Отлично, выборка достаточно малая по " + born_year + " году")
                    print(vk_search_good_output(profiles, False, full_name))
                    good_flag = True
                else:
                    print(born_year + " год, очень много профилей или их нет совсем((")

            if good_flag == True:
                print("Кайф, возможно мы нашли Ч Е Л О В Е 4 К А")

    def search_by_groups(self, inputname, full_name):
        """
        Метод для поиска людей по группам Финашки
        """
        print("Поиск по группам в вк..")
        for group in GROUPS_ID_LIST:
            group_results = self.api.users.search(q=inputname, group_id=group, v=self.APIVersion)["items"]
            if group_results != []:
                print(vk_search_good_output(group_results, True, full_name))
