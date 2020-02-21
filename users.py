#! /usr/bin/env python
# -*- coding: utf-8 -*-

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)
import pickle
import time
from copy import deepcopy


def load(path):
    with open(path, 'rb') as f:
        ret = pickle.load(f)
    return ret


def dump(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)

def saveAnswer(participant, sex, to, mark1, mark2):
    f.write(str(participant) + " " + str(sex) + " " + str(to) + " " + str(mark1) + " " + str(mark2))
    f.write('\n')


"""
Types:
u - unknown
p - participient
a - admin
"""
admins = [line[:-1] for line in open('admins', 'r').readlines()]
# admins = []
first_circle_n = 15
max_n = 30

max_con = 18

f = open("answers.txt", "a+")

messages = {
    'code': 'Ну, что же! Надеюсь, ты не потерял свой номерок участника! Посмотри внимательно на обратную сторону и найдешь номер, состоящий из пяти цифр, который нужно указать ниже👇🏻',
    'wrong_code': 'Неверный код! 🙊 \nПопробуй еще раз!',
    'mark_1': 'Время свидания подошло к концу! Хотел бы продолжить общение с %s?',
    'mark_2': 'Насколько тебе понравилось общение? Оцени по 10-балльной шкале.',
    'late': 'Ты не успел(а) поставить оценку прошлому партнёру, сделай это с помощью анкеты',
    'accepted': 'Твои оценки приняты, спасибо!',
    'start': 'Мы Начинаем! \nТвой первый собеседник – это %s под номером %d',
    'finish': 'Вот и все! Теперь можно выдохнуть и расслабиться😌 \nРезультаты будут объявлены в ближайшее время, хорошего вечера!',
    'next_m': 'Теперь можно познакомиться с еще одной очаровательной девушкой. Кстати, ее зовут %s, она ждет тебя у столика под номером %d',
    'next_f': 'Следующим к тебе подойдет %s под номером %d!',
    'hello': 'Привет, %s! Мы скоро начнем! '

}


class User:
    excpecting = ''

    def __init__(self, user, bot):
        self.id = user.id
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.username = user.username
        self.bot = bot
        self.code = ''
        self.type = 'u'
        self.bot.username2id[user.username] = self.id
        if self.username in admins:
            self.type = 'a'
            self.excpecting = 'command'
            self.message('Hello, admin')
            self.bot.logger.info('New admin logged in: %s' % self.username)

        else:
            self.excpecting = 'code'
            self.bot.logger.info('New unknown user: %s' % self.username)
            self.message(messages['code'])
        self.save()

    def update_user_info(self, user_info):
        self.real_name = user_info['name']
        self.from_ = user_info['from']
        self.sex = user_info['sex']
        self.type = 'p'
        self.order = user_info['order']
        # todo circle from file, not from order
        self.circle = 2 if self.order > first_circle_n else 1
        self.bot.logger.info('User %s updated' % self)
        self.bot.order_male2name[(self.order, 1 if self.sex == 'male' else 0)] = (self.id, self.get_name())
        self.save()

    def onNewMessage(self, message):

        if self.excpecting == 'code':
            code = message.text

            if not code in self.bot.code2user:
                self.bot.logger.info('Wrong code from %s' % self)
                self.message(messages['wrong_code'])
            else:
                user_info = self.bot.code2user[code]
                self.code = code
                self.excpecting = 'wait'
                self.update_user_info(user_info)
                self.bot.logger.info('New user: %s - %s' % (self, self.real_name))
                self.message(messages['hello'] % self.get_name())
            return

        # todo new marks
        if self.excpecting in ['mark_1', 'mark_2']:
            try:
                mark = int(message.text)
            except:
                self.message("Wrong mark")
                return
            if mark < 0 or mark > 5:
                self.message('Mark must be in range [0, 5]')
                return

            self.bot.logger.info('New mark from: %s %s - %d' % (self.excpecting, self.real_name, mark))

            if self.excpecting == 'mark_1':
                self.excpecting = 'mark_2'
                self.ask_second_mark(messages['mark_2'])
                self.mark_1 = mark
                return
            else:
                self.mark_2 = mark
                partner = self.get_partner(self.bot.con)
                pair = (self.order, partner[0])

                # todo new logging
                if self.sex != 'male':
                    pair = (pair[1], pair[0])
                # self.bot.sheet.update('write', pair, self.circle, (self.mark_1, self.mark_2), self.sex)
                saveAnswer(self.order, self.sex, partner[0], self.mark_1, self.mark_2)

                self.excpecting = 'wait'
                self.message(messages['accepted'])
                if self.bot.con == max_con:
                    self.message(messages['finish'])
                else:
                    self.message(messages['next_m'] %
                                 (self.bot.order_male2name.get(self.get_partner(self.bot.con + 1), ''),
                                  self.get_partner(self.bot.con + 1)[0]) if self.sex == 'male' else messages['next_f'] %
                                                                                                    (
                                                                                                    self.bot.order_male2name.get(
                                                                                                        self.get_partner(
                                                                                                            self.bot.con + 1),
                                                                                                        ''),
                                                                                                    self.get_partner(
                                                                                                        self.bot.con + 1)[
                                                                                                        0]))
                return
            return

        if self.excpecting == 'command':
            command = message.text.lower().split()
            if command[0] == 'ask':
                self._ask_marks()
                self.message("Ok")


            elif command[0] == 'update':
                if len(command) > 2 and command[1] == 'n':
                    try:
                        first_circle_n = int(command[2])
                    except:
                        self.message('Could not read number')
                    return

                self.bot.update()
                self.message('Ok')

            elif command[0] == 'go':
                self._start()
                self.bot.logger.info('Speed dating started!')
                self.message('Ok')
            elif command[0] == 'alert':
                self._alert(' '.join(command[1:]))
                self.message('Ok')
            elif command[0] == 'flush':
                f.flush()
                # self.close_file()

                self.message("Ok")
            elif command[0] == "close":
                self.close_file()
            elif command[0] == "open":
                self.open_file()
            else:
                self.message('Wrong command')
            return

    def _alert(self, s):

        # test rps

        last_request_time = time.time()
        for user in self.bot.users.values():
            if user.type == 'p':
                sleep_time = last_request_time + (1 / 30) - time.time()
                time.sleep(max(0, sleep_time))
                user.message(s)

    def _start(self):
        # todo rps
        for user in self.bot.users.values():
            if user.type == 'p':
                user.message(messages['start']
                             % (self.bot.order_male2name.get(user.get_partner(1), ''), user.get_partner(1)[0]))

    def _ask_marks(self):
        self.bot.logger.info('Asking marks...')
        self.bot.con += 1

        # todo rps
        for user in self.bot.users.values():
            if user.type == 'p':
                user.ask_first_mark(messages['mark_1'] %
                              self.bot.order_male2name.get(user.get_partner(self.bot.con), ''))
                user.excpecting = 'mark_1'
        self.message('Ok')

    def get_partner(self, con):
        try:
            tmp = self.sex
        except:
            return (1, 1)
        if self.sex == 'male':
            p_order = (self.order + con - 1) % (first_circle_n if self.order <= first_circle_n else max_n)
            if p_order <= first_circle_n and self.circle == 2:
                p_order += first_circle_n
            if p_order == first_circle_n:
                p_order = max_n
        else:
            p_order = self.order - con + 1
            if p_order < 0 or (self.circle == 2 and p_order <= first_circle_n):
                p_order += first_circle_n
        if p_order == 0:
            p_order = (first_circle_n if self.order <= first_circle_n else max_n)

        p_sex = 0 if self.sex == 'male' else 1
        return (p_order, p_sex)

    def get_name(self):
        if not self.real_name:
            return 'Unknown'
        return self.real_name.split()[1] if len(self.real_name.split()) > 1 else self.real_name

    def message(self, text=''):
        self.bot.send_message(self.id, text)

    def ask_first_mark(self, text):
        if self.excpecting == 'mark_1':
            self.message(messages['late'])

        kb = ReplyKeyboardMarkup(one_time_keyboard=True)
        for i in range(["Да!", "Нет:("]):
            kb.add(KeyboardButton(text=str(i)))
        self.bot.send_message(self.id, text, reply_markup=kb)

    def ask_second_mark(self, text):
        if self.excpecting == 'mark_1':
            self.message(messages['late'])

        kb = ReplyKeyboardMarkup(one_time_keyboard=True)
        for i in range(1, 11):
            kb.add(KeyboardButton(text=str(i)))
        self.bot.send_message(self.id, text, reply_markup=kb)

    def save(self):
        bot = self.bot
        self.bot = None
        dump(self, 'users/%s_%s' % (self.username, self.id))
        self.bot = bot
        self.bot.logger.info('User %s saved' % self)

    def __str__(self):
        return "%s %s %s" % (self.username, self.first_name, self.last_name)

    def open_file(self):
        global f
        f = open("answers.txt", "a+")

    def close_file(self):
        f.close()