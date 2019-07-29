import vk, time, json, requests, xlrd, yaml
import database_module

with open("./yaml/token.yaml", 'r') as stream:
    API_TOKEN = yaml.safe_load(stream)

API_VERSION = 5.73
USERS_YEARS = ["1999","2000", "2001","2002"]
GROUPS_ID_LIST = [134724725, 6319, 153039551, 27590309, 184403760]
OUT_TXT_FILE = "./OUTPUT/OUTPUT_VK.txt"

def vk_search_good_output(vk_json, groupflag):
    out_str = ""
    for item in vk_json:

        vk_link = "https://vk.com/id"+str(item["id"])
        obj = database_module.mysql_writer("INSERT INTO vk_users (first_name, last_name, link) VALUES ('"+item["first_name"]+"','"+item["last_name"]+"','"+vk_link+"')")
        if obj.result == True:
            groupflag = (groupflag == True and " [по группе в вк]" or "" )
            out_str += item["first_name"]+" "+item["last_name"]+" "+vk_link+groupflag+"\n"

    f = open(OUT_TXT_FILE, 'a')
    f.write(out_str)
    f.close()
    return out_str

class vk_processing():
    def __init__(self, result_array):
        print("*Модуль поиска по VK*")
        self.result_array = result_array
        session = vk.Session(access_token=API_TOKEN)
        self.api = vk.API(session)
        self.APIVersion = API_VERSION
        #Отчистка файла от предыдущей сессии
        open(OUT_TXT_FILE, 'w').close()
        self.input_processing()

    def input_processing(self):
        for item in self.result_array:
            print("**Работаем с пользователем "+item[3]+"**\nМесто "+str(item[1])+str(", балл ")+str(item[6])+" ["+str(item[5])+"]")
            print(item[4])
            buf_name = item[3].split(" ")
            abit_name = buf_name[0]+" "+buf_name[1]
            self.search_by_groups(abit_name)
            time.sleep(3)
            self.search_profile_method(abit_name)
            time.sleep(3)

    def search_profile_method(self, inputname):
        year_processing_flag = True

        #Практически не помогает
        print("***Простой поиск пользователя по VK***")
        simple_profiles = self.api.users.search(q=inputname,v=self.APIVersion)["items"]
        if len(simple_profiles) > 5 or simple_profiles == []:
            print("Ойй, много людей переезжаем на поиск по годам..")
        else:
            print("Отлично, выборка достаточно малая")
            print(vk_search_good_output(simple_profiles, False))
            year_processing_flag = False

        if year_processing_flag == True:
            good_flag = False
            for born_year in USERS_YEARS:
                time.sleep(1)
                profiles = self.api.users.search(q=inputname,birth_year=born_year,v=self.APIVersion)["items"]
                if (len(profiles) < 5) and profiles != []:
                    print("Отлично, выборка достаточно малая по "+born_year+" году")
                    print(vk_search_good_output(profiles,False))
                    good_flag = True
                else:
                    print(born_year+" год, очень много профилей или их нет совсем((")

            if good_flag == True:
                print("Кайф, возможно мы нашли Ч Е Л О В Е 4 К А")

    def search_by_groups(self, inputname):
        """
        Метод для поиска людей по группам Финашки
        """
        print ("Поиск по группам в вк..")
        for group in GROUPS_ID_LIST:
            group_results = self.api.users.search(q=inputname,group_id=group,v=self.APIVersion)["items"]
            if group_results != []:
                print(vk_search_good_output(group_results,True))