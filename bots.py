from telebot import TeleBot
from users import *
from threading import Lock

import os



class Bot(TeleBot):
    users_path = 'users.pckl'
    # (,1) - male; (,0) female
    order_male2name = {}
    username2id = {}

    def __init__(self, logger):
        logger.info("Initializing bot...")
        self.token = open('token', 'r').readline()

        TeleBot.__init__(self, self.token)

        self.users = {}
        for user_file in os.listdir('users/'):
            try:
                user = load('users/' + user_file)
                user.bot = self
            except:
                continue
            self.users[user.id] = user
            self.username2id[user.username] = user.id

        self.logger = logger

        self.code2user = self.get_user_list_from_csv()

        for user in self.code2user.values():
            self.order_male2name[(user['order'], 1 if user['sex'] == 'male' else 0)] = user['name'].split()[1] if len(
                user['name'].split()) > 1 else user['name']

        # print(self.order_male2name)
        self.con = 0

        self.lock = Lock()

        @TeleBot.message_handler(self, commands=['start'])
        def greeting(message):
            self.lock.acquire()
            if message.from_user.id in self.users:
                self.send_message(message.from_user.id, 'Alredy logged in')
                self.lock.release()
                return
            self.users[message.from_user.id] = User(message.from_user, self)
            self.lock.release()


        @TeleBot.message_handler(self)
        def onNewMessage(message):
            self.logger.info('New message from %s (%s %s): %s'
                             % (message.from_user.username, message.from_user.first_name, message.from_user.last_name,
                                message.text))
            self.lock.acquire()
            if not message.from_user.id in self.users:
                self.send_message(message.from_user.id, 'Type "/start" to start')
                self.lock.release()
                return
            self.users[message.from_user.id].onNewMessage(message)
            self.lock.release()

        self.logger.info('Bot initialized')

    def start(self):
        super().polling(none_stop=True, timeout=123)

    def update(self):
        self.code2user = self.get_user_list_from_csv()
        for code, user in self.users.items():
            if user.code == code:
                user.update(self.code2user[code])

    def get_user_list_from_csv(self):
        code2user = {}

        f_girls = open("girls.csv", encoding="utf-8")
        girls = f_girls.readlines()

        for user in girls:
            splitted = user[:-1].split(',')
            code2user[splitted[3]] = {
                'sex': 'female',
                'name': splitted[1],
                'from': splitted[2],
                'order': int(splitted[0])
            }
        f_girls.close()

        f_boys = open("boys.csv", encoding="utf-8")
        boys = f_boys.readlines()
        for user in boys:
            splitted = user[:-1].split(',')
            code2user[splitted[3]] = {
                'sex': 'male',
                'name': splitted[1],
                'from': splitted[2],
                'order': int(splitted[0]
                             )
            }
        return code2user
