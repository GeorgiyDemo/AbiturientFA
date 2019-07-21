"""
    Клиент Telegram для определения рейтинга абитуры
"""
import telegram, yaml, requests, time, threading
from telegram.error import NetworkError, Unauthorized

update_id = None

def threading_check_client_results(bot):
    while True:
        try:
            update_request = requests.post("http://127.0.0.1:5000/updates").json()
            if update_request != []:
                for update in update_request:
                    if int(update["changed_from"])>int(update["changed_to"]):
                        viewflag = "⬆️"
                    else:
                        viewflag = "⬇️"
                    bot.send_message(chat_id=update["tid"], text=viewflag+" Изменение места с "+update["changed_from"]+" на "+update["changed_to"]+" на направлении "+update["wayname"])
        except:
            continue
        time.sleep(60)

def main():
    """Запуск бота"""
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
    p_mode = telegram.ParseMode.HTML
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1
        if update.message.text == "/start":
            update.message.reply_text("Привет 🐾\nЯ помогу тебе следить за конкурсом на сайте fa.ru\nДля активации введи команду вида\n<b>/set фамилия имя отчество</b>", parse_mode=p_mode)

        elif update.message.text.split(" ")[0]=="/set":
            name = update.message.text.split(" ")
            #Чтоб ФИО было полное
            if len(name) != 4:
                update.message.reply_text("Что-то пошло не так\nОбщий синтаксис команды:\n<b>/set фамилия имя отчество</b>", parse_mode=p_mode)

                return 0
            name = name[1]+" "+name[2]+" "+name[3]
            update.message.reply_text("Ищем в списках \""+name+"\" (может занять некоторое время)")
            r = requests.post("http://127.0.0.1:5000/adduser",json={"tid":update.message.from_user.id, "username":name}).json()
            if r["status"] == "ok":
                update.message.reply_text("Да, ты есть в списках, успешно добавил тебя в систему 😌\nЕсли заменил направления или ФИО, то воспользуйся заново командой <b>/set</b>", parse_mode=p_mode)
            else:
                update.message.reply_text("Я не нашел тебя в списках 😔")

if __name__ == '__main__':
    main()