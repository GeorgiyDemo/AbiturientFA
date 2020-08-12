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
        obj = database_module.MySQLClass(
            "INSERT INTO vk_users (first_name, last_name, link, full_name) VALUES ('{}','{}','{}','{}')".format(item["first_name"], item["last_name"], vk_link, long_name),1)
        
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



        database_module.MySQLClass("DELETE FROM FA.buf_table;",1)
        USERS_PER_REQUEST = 1000
        print("Обновляем участников групп..")
        for group in GROUPS_ID_LIST:
            
            print("Работаем с группой https//vk.com/club"+str(group))
            users_count = 1
            group_results = self.api.groups.getMembers(count=USERS_PER_REQUEST, group_id=group, v=self.APIVersion)
            group_users = group_results["count"]
            print("Общее кол-во участников: "+str(group_users))
            
            #Получаем инфу о пользователях
            user_results = self.api.users.get(user_ids=group_results["items"], v=self.APIVersion)

            for item in user_results:
                print("{} {}, https://vk.com/{}".format(item["first_name"], item["last_name"], item["id"]))
                database_module.MySQLClass("INSERT INTO buf_table (profile_link, first_name, last_name, club_link) VALUES (\"https://vk.com/id{}\",\"{}\",\"{}\",\"https://vk.com/club{}\")".format(item["id"], item["first_name"], item["last_name"], group),1)
                print("[{}/{}] Записали пользователя https://vk.com/id{} с группы https://vk.com/club{}".format(users_count, group_users, item["id"], group))
                users_count += 1

            
            #Если меньше , чем число участников в группе - выкачиваем все
            if len(group_results["items"]) < group_users:
                #Кол-во смещений
                offset_count = int(group_users/USERS_PER_REQUEST)
                print(offset_count)
                
                
                for i_offset in range(offset_count):
                    print("count={}, group_id={}, offset={}".format(USERS_PER_REQUEST, group, users_count))
                    thisgroup_results = self.api.groups.getMembers(count=USERS_PER_REQUEST, group_id=group, offset=users_count, v=self.APIVersion)
                    #Получаем инфу о пользователях
                    user_results = self.api.users.get(user_ids=thisgroup_results["items"], v=self.APIVersion)
                    
                    for item in user_results:
                        print("{} {}, https://vk.com/{}".format(item["first_name"], item["last_name"], item["id"]))
                        database_module.MySQLClass("INSERT INTO buf_table (profile_link, first_name, last_name, club_link) VALUES (\"https://vk.com/id{}\",\"{}\",\"{}\",\"https://vk.com/club{}\")".format(item["id"], item["first_name"], item["last_name"], group),1)
                        print("[{}/{}] Записали пользователя https://vk.com/id{} с группы https://vk.com/club{}".format(users_count, group_users, item["id"], group))
                        users_count += 1
                    time.sleep(1)
                    
            
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
            obj = database_module.MySQLClass("SELECT * FROM vk_users WHERE full_name='{}'".format(long_name),2)
            
            if obj.result is None:

                print("\n🍺 Работаем с пользователем {} 🍺\nМесто {}, {} балл [{}]\n{}".format(long_name, item[1], item[7], item[5], item[4]))
                first_name, last_name, *_ = long_name.split(" ")
                
                check = database_module.MySQLClass("SELECT * FROM buf_table WHERE first_name='{}' AND last_name='{}'".format(first_name,last_name),3)
                print(check.result)

            
            else:
                print("{} - уже проверяли, пропускаем..".format(long_name))