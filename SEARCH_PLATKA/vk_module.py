import database_module
import json
import requests
import time
import vk
import xlrd
import yaml

with open("./yaml/token.yaml", 'r') as stream:
    API_TOKEN = yaml.safe_load(stream)

API_VERSION = 5.89
USERS_YEARS = ["2002", "2003"]
GROUPS_ID_LIST = [134724725, 6319, 27590309, 196939200, 37015953]
OUT_TXT_FILE = "./OUTPUT/OUTPUT_VK.txt"


def vk_writer(vk_json, groupflag, long_name):
    """Запись данных о пользователе, которого нашли"""
    for item in vk_json:

        vk_link = "https://vk.com/id" + str(item["id"])
        if groupflag:
            print("✅ Нашли профиль {} по группе VK ".format(vk_link))
        obj = database_module.MySQLWriter(
            "INSERT INTO vk_users (first_name, last_name, link, full_name) VALUES ('{}','{}','{}','{}')".format(item["first_name"], item["last_name"], vk_link, long_name))
        
        #Если успешно записали данные в СУБД
        if obj.result:
            groupflag = (groupflag == True and " [по группе в вк]" or "")
            out_str = item["first_name"] + " " + item["last_name"] + " " + vk_link + groupflag + "\n"
            with open(OUT_TXT_FILE, 'a') as file:
                file.write(out_str)

class VkClass():
    def __init__(self, result_array):
        print("*Модуль поиска по VK*")
        self.result_array = result_array
        session = vk.Session(access_token=API_TOKEN)
        self.api = vk.API(session)
        self.APIVersion = API_VERSION
        self.API_checker()

        # Чистка файла от предыдущей сессии
        open(OUT_TXT_FILE, 'w').close()
        self.processing()

    def API_checker(self):
        """Проверка на работоспособность API т.к. VK может просто не отдавать результаты"""

        #Проверка на то, что API отдает адекватный результат
        group_results = self.api.users.search(q="Alisa Kot", group_id=161406423, v=self.APIVersion)["items"]
        if group_results == []:
            raise Exception("🌚🌚🌚 Меняй токен VK 🌚🌚🌚","Контакт убил токен или ты отписался от группы в условии")
        else:
            print("🌝 VK API работает")



    def processing(self):

        #Для каждого результата
        for item in self.result_array:
        
            long_name = item[3]

            #Проверяем, есть ли результаты по нему в таблице
            obj = database_module.MySQLReaderOne("SELECT * FROM vk_users WHERE full_name='{}'".format(long_name))
            
            if obj.result is None:
                print("\n🍺 Работаем с пользователем {} 🍺\nМесто {}, {} балл [{}]\n{}".format(long_name, item[1], item[7], item[5], item[4]))

                first_name, second_name, *_ = long_name.split(" ")
                short_name = "{} {}".format(first_name, second_name)

                #Поиск по группам, самый действенный метод
                self.search_groups(short_name, long_name)
                time.sleep(3)
                
                #TODO
                #Поиск по профилю
                #self.search_profile_method(short_name, long_name)
                #time.sleep(3)
            
            else:
                print("{} - уже проверяли, пропускаем..".format(long_name))


    def search_profile_method(self, inputname, full_name):
        year_processing_flag = True

        # Практически не помогает
        print(" ➜ Простой поиск пользователя по VK")
        simple_profiles = self.api.users.search(q=inputname, v=self.APIVersion)["items"]
        if len(simple_profiles) > 3 or simple_profiles == []:
            print("Много людей переезжаем на поиск по годам..")
        else:
            print("Отлично, выборка достаточно малая")
            vk_writer(simple_profiles, False, full_name)
            year_processing_flag = False

        if year_processing_flag:
            good_flag = False
            for born_year in USERS_YEARS:
                time.sleep(1)
                profiles = self.api.users.search(q=inputname, birth_year=born_year, v=self.APIVersion)["items"]
                if (len(profiles) == 1) and profiles != []:
                    print("Отлично, выборка достаточно малая по " + born_year + " году")
                    vk_writer(profiles, False, full_name)
                    good_flag = True
                else:
                    print(born_year + " год, очень много профилей или их нет совсем((")

            if good_flag:
                print("⚠️Возможно мы нашли человека с фильтрацией по году⚠")

    def search_groups(self, short_name, long_name):
        """
        Метод для поиска людей по группам Финашки
        """
        print(" ➜ Поиск по группам в VK..")
        for group in GROUPS_ID_LIST:
            
            group_results = self.api.users.search(q=short_name, group_id=group, v=self.APIVersion)["items"]
            if group_results != []:
                print("Совпадение есть")
                vk_writer(group_results, True, long_name)
