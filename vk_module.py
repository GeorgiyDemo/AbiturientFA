from pytils import numeral
import vk, random, time, datetime, os, json, requests, xlrd, re, yaml


with open("./token.yaml", 'r') as stream:
    API_TOKEN = yaml.load(stream)

API_VERSION = 5.73
USERS_YEARS = ["1999","2000", "2001","2002"]
OUT_TXT_FILE = "OUTPUT.txt"

def vk_search_good_output(vk_json):
    out_str = ""
    for item in vk_json:
        out_str += item["first_name"]+" "+item["last_name"]+" "+"https://vk.com/id"+str(item["id"])+"\n"

    f = open(OUT_TXT_FILE, 'a')
    f.write(out_str)
    f.close()
    return out_str

class vk_processing():
    def __init__(self, result_array):
        self.result_array = result_array
        session = vk.Session(access_token=API_TOKEN)
        self.api = vk.API(session)
        self.APIVersion = API_VERSION
        self.input_processing()

    def input_processing(self):
        for item in self.result_array:
            print("*Работаем с пользователем "+item[3]+"*\nМесто "+str(item[1])+str(", балл ")+str(item[6])+" ["+str(item[5])+"]")
            print(item[4]+"\n")
            buf_name = item[3].split(" ")
            self.search_profile_method(buf_name[0]+" "+buf_name[1])
            time.sleep(5)

    def search_profile_method(self, inputname):
        year_processing_flag = True

        #Практически не помогает
        print("[1] Простой поиск пользователя по VK")
        simple_profiles = self.api.users.search(q=inputname,v=self.APIVersion)["items"]
        if len(simple_profiles) >= 3:
            print("Ойй, много людей переезжаем на поиск по годам")
        else:
            print("Отлично, выборка достаточно малая")
            print(vk_search_good_output(simple_profiles))
            year_processing_flag = False

        if year_processing_flag == True:
            good_flag = False
            for born_year in USERS_YEARS:
                time.sleep(1)
                profiles = self.api.users.search(q=inputname,birth_year=born_year,v=self.APIVersion)["items"]
                if (len(profiles)<=3):
                    print("Отлично, выборка достаточно малая по "+born_year+" году")
                    print(vk_search_good_output(profiles))
                    good_flag = True
                else:
                    print(born_year+" год, очень много профилей")

            if good_flag == True:
                print("Кайф, возможно мы нашли Ч Е Л О В Е 4 К А")

    #def search_news_def(self):
    #    result = self.api.newsfeed.search(q='"'+string+'"',v=APIVersion)['items']






