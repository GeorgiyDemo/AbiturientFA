#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages.
This is built on the API wrapper, see echobot2.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import telegram, yaml.emitter
from telegram.error import NetworkError, Unauthorized
from time import sleep

update_id = None

def main():
    """Run the bot."""
    global update_id
    with open("./tokens.yaml", 'r') as stream:
        token = yaml.load(stream)

    bot = telegram.Bot(token)
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            update_id += 1


def echo(bot):
    """Echo the message the user sent."""
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
            name = name[1]+" "+name[2]+" "+name[3]
            update.message.reply_text("Хорошо, ищем в списках \""+name+"\"..")

            #name = update.message.text
            #if len(name.split(" ")) == 3:
            #    update.message.reply_text("Хорошо, это похоже на ФИО, давай тебя поищем в списках..")
                #ЕСЛИ В СПИСКАХ ЕСТЬ - ЗАНЕСЕНИЕ ПРЕДМЕТОВ А ТАБЛИЧКУ И ЗАПИСЬ В БД
                #ЕСЛИ НЕТ - сказать

                #Я не понял, что ты хочешь этим сказать? Если хочешь заменить Фио - хорошо
                #


#bot.send_message(chat_id=chat_id, text="I'm sorry Dave I'm afraid I can't do that.")

if __name__ == '__main__':
    main()