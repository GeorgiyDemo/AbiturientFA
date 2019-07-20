"""
    Клиент Telegram для определения рейтинга абитуры
"""
import telegram, yaml, requests, time, threading
from telegram.error import NetworkError, Unauthorized

update_id = None

def threading_check_client_results(bot):
    while True:
        update_request = requests.post("http://127.0.0.1:5000/updates").json()
        if update_request != []:
            for update in update_request:
                bot.send_message(chat_id=update["tid"], text="Изменение места с "+update["changed_from"]+" на "+update["changed_to"]+" на направлении "+update["wayname"])

        print(update_request)
        time.sleep(60)

def main():
    """Run the bot."""
    global update_id
    with open("./tokens.yaml", 'r') as stream:
        token = yaml.load(stream)
    bot = telegram.Bot(token)
    threading.Thread(target=threading_check_client_results, args=(bot,)).start()
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    while True:
        try:
            handler(bot)
        except NetworkError:
            time.sleep(1)
        except Unauthorized:
            update_id += 1


def handler(bot):
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1
        if update.message.text == "/start":
            update.message.reply_text("Привет, введи своё ФИО и получай уведомления об изменениях места в Telegram✨\n\"/set фамилия имя отчество\"")

        #Обновление направлений (если что-то менял)
        elif update.message.text == "/update":
            update.message.reply_text("ОБНОВИЛИ НАПРАВЛЕНИЯ (ПОКА НЕТ)")

        elif update.message.text.split(" ")[0]=="/set":
            #Вы уже установили ФИО, хотите заменить?
            name = update.message.text.split(" ")
            #Чтоб ФИО было полное
            if len(name) != 4:
                return 0
            name = name[1]+" "+name[2]+" "+name[3]
            update.message.reply_text("Ищем в списках \""+name+"\"..")
            r = requests.post("http://127.0.0.1:5000/adduser",json={"tid":update.message.from_user.id, "username":name}).json() #TODO УЗНАТЬ КАК ВЗЯТЬ ID TELEGRAM'А
            print(r)
            if r["status"] == "ok":
                update.message.reply_text("🦀 Да, ты есть в списках, добавляем 🦀")
            else:
                update.message.reply_text("Я не нашел тебя в списках :c")

            #name = update.message.text
            #if len(name.split(" ")) == 3:
            #    update.message.reply_text("Хорошо, это похоже на ФИО, давай тебя поищем в списках..")
                #ЕСЛИ В СПИСКАХ ЕСТЬ - ЗАНЕСЕНИЕ ПРЕДМЕТОВ А ТАБЛИЧКУ И ЗАПИСЬ В БД
                #ЕСЛИ НЕТ - сказать

                #Я не понял, что ты хочешь этим сказать? Если хочешь заменить Фио - хорошо
                #

if __name__ == '__main__':
    main()