import re
import time
from datetime import datetime
from threading import Thread

import requests
import telebot
from bs4 import BeautifulSoup

TOKEN = ''
with open('TOKEN.txt') as fl:
    for i in fl:
        TOKEN = i
        break
bot = telebot.TeleBot(TOKEN)
url = 'https://codeforces.com/api/contest.list?gym=false'

responce = requests.get(url)
soup = BeautifulSoup(responce.content, 'lxml')
arr = soup.text.split('},{')


# предупреждение с момента появления/за 2 дня/за 1 день/за 2 часа
def get_list_contests():
    data = []
    for i in arr:
        if 'BEFORE' in i:
            name = str(re.search('"name":"(.*)","type":', i).group(1))
            id = str(re.search('"id":(.*),"name":"', i).group(1))
            date_begin = datetime.fromtimestamp(
                int(re.search('"startTimeSeconds":(.*),"relativeTimeSeconds"', i).group(1)))
            secs_dur = int(re.search('"durationSeconds":(.*),"startTimeSeconds"', i).group(1))
            duration_time = str(secs_dur // (60 * 60)) + 'ч ' + str(secs_dur % 60) + 'м'
            _data = [name, id, str(date_begin.strftime("%A, %B %d, %Y %I:%M:%S")), duration_time]
            data.append([tuple(_data), date_begin])
    return data


def get_list_contests_exist():
    contests_exist = []
    with open('contests_ids.txt') as fl:
        for i in fl:
            contests_exist.append(int(i))
    return contests_exist


def send_new_cont(contest):
    contest = contest[0]
    contests_exists = get_list_contests_exist()
    with open('contests_ids.txt', 'w') as fl:
        for i in contests_exists:
            fl.write(str(i) + '\n')
        fl.write(contest[1] + '\n')

    print('new contest is ' + contest[1] + '; arrived at: ' + str(datetime.now()))
    for i in get_ids():
        bot.send_message(i, '%s\n\nid: %s\ndate: %s\ndur_time: %s' % contest)
    return


def news():
    contests = get_list_contests()
    contests_exist = get_list_contests_exist()

    for i in contests:
        delta = i[1] - datetime.now()
        delta = delta.total_seconds()
        days = delta // (60 * 60 * 24)
        hours = delta // (60 * 60)
        ids = get_ids()
        if days == 2 and (delta - days * (60 * 60 * 24)) <= (60 * 60):
            for q in ids:
                bot.send_message(q, 'До %s осталось 2 дня' % i[0][0])
        elif days == 1 and (delta - days * (60 * 60 * 24)) <= (60 * 60):
            for q in ids:
                bot.send_message(q, 'До %s осталось 1 день' % i[0][0])
        elif hours == 2 and (delta - (hours * 60 * 60)) <= 60:
            for q in ids:
                bot.send_message(q, 'До %s осталось 2 часа' % i[0][0])
    for i in contests:
        if not (int(i[0][1]) in contests_exist):
            send_new_cont(i)

    return


def get_ids():
    ids = []
    with open('users_ids.txt') as fl:
        for i in fl:
            ids.append(int(i))
    return ids


def add_id(id):
    ids = get_ids()
    ids.append(id)
    with open('users_ids.txt', 'w') as fl:
        for i in ids:
            fl.write(str(i) + '\n')
    return


def checker():
    while True:
        try:
            news()
            time.sleep(60 * 60 - 5)
        except Exception:
            try:
                bot.send_message(450543987, 'со мной чтото не так')
            except Exception:
                pass
            time.sleep(60 ** 3)


main_trad = Thread(target=checker)
main_trad.start()


@bot.message_handler(commands=['start', 'check'])
def text_handler(msg):
    ids = get_ids()
    user_id = msg.from_user.id
    if user_id not in ids:
        add_id(user_id)
    bot.send_message(user_id, 'i am fine')


while True:
    try:
        print('connecting')
        bot.polling()
    except Exception:
        print('smthg is wrong, reconnecting')
