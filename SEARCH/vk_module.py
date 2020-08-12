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
GROUPS_ID_LIST = [134724725, 27590309, 196939200, 37015953]
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
        
        user_input = input("Обновить участников групп? (y/n) -> ")
        if user_input == "y":
            print("Понял, обновляем..")
            self.groups_dumper()
        else:
            print("Понял, пропускаем..")

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
        
        #Получаем данные из каждой группы

    def groups_dumper(self):
        """Дамп участников с указанных групп"""

        
        database_module.MySQLWriter("DELETE FROM FA.buf_table;")
        USERS_PER_REQUEST = 1000
        print("Обновляем участников групп..")
        for group in GROUPS_ID_LIST:
            
            print("Работаем с группой https//vk.com/club"+str(group))
            users_count = 0
            group_results = self.api.users.search(count=USERS_PER_REQUEST, group_id=group, v=self.APIVersion)
            group_users = group_results["count"]
            print("Общее кол-во участников: "+str(group_users))
            for item in group_results["items"]:
                obj = database_module.MySQLWriter("INSERT INTO buf_table (profile_link, first_name, last_name, club_link) VALUES ('https://vk.com/id{}','{}','{}','https://vk.com/club{}')".format(item["id"], item["first_name"], item["last_name"], group))
                print("[{}] Записали пользователя https://vk.com/id{} с группы https://vk.com/club{}".format(users_count, item["id"], group))
                users_count += 1

            
            #Если меньше , чем число участников в группе - выкачиваем все
            if len(group_results["items"]) < group_users:
                #Смещение
                offset = int(group_users/USERS_PER_REQUEST)
                print(offset)

                for i in range(offset):
                    print("Смещение ",i)
                    thisgroup_results = self.api.users.search(count=USERS_PER_REQUEST, group_id=group, offset=users_count, v=self.APIVersion)
                    for item in thisgroup_results["items"]:
                        obj = database_module.MySQLWriter("INSERT INTO buf_table (profile_link, first_name, last_name, club_link) VALUES ('https://vk.com/id{}','{}','{}','https://vk.com/club{}')".format(item["id"], item["first_name"], item["last_name"], group))
                        print("[{}] Записали пользователя https://vk.com/id{} с группы https://vk.com/club{}".format(users_count, item["id"], group))
                        users_count += 1
                    time.sleep(2)
                    
            
            else:
                print("Все дампнули за один раз")
            if users_count == group_users:
                print("Добавили всех участников группы")
            else:
                print("Что-то пошло не так и бы добавили не всех участников группы")


    def processing(self):

        #Для каждого результата
        for item in self.result_array:
        
            long_name = item[3]

            #Проверяем, есть ли результаты по нему в таблице
            obj = database_module.MySQLReaderOne("SELECT * FROM vk_users WHERE full_name='{}'".format(long_name))
            
            if obj.result is None:

                print("\n🍺 Работаем с пользователем {} 🍺\nМесто {}, {} балл [{}]\n{}".format(long_name, item[1], item[7], item[5], item[4]))
                first_name, last_name, *_ = long_name.split(" ")
                
                check = database_module.MySQLReaderAll("SELECT * FROM buf_table WHERE first_name='{}' AND last_name='{}'".format(first_name,last_name))
                print(check)

                #Поиск по группам, самый действенный метод
                #self.search_groups(short_name, long_name)
                #time.sleep(3)
                
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