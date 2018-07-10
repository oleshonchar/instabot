import string
import requests
import json
import datetime
import time
import random

import rncryptor

from telegram_bot import url
from telegram_bot.models import TgUser
from instagram_bot.bot import InstaBot, save_usernames
from instagram_bot.models import Profile


class TgBotHandler(object):

    def __init__(self, user_id, username):
        self.user, self.user_created = TgUser.objects.get_or_create(user_id=user_id, username=username)
        self.insta_bot = InstaBot(user_id)

    def send_message(self, user_id, text, reply_markup=None):
        params = {'chat_id': user_id, 'text': text, 'reply_markup': reply_markup, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        response = requests.post(url + method, params)
        return response

    def reply_keyboard(self, user_id, text, button_text='Empty', remove_keyboard=False):
        if remove_keyboard:
            keyboard = {'remove_keyboard': remove_keyboard}
        else:
            button = [[{'text': button_text}]]
            keyboard = {'keyboard': button, 'resize_keyboard': True, 'one_time_keyboard': True}
        keyboard = json.dumps(keyboard)
        self.send_message(user_id, text, reply_markup=keyboard)

    def inline_keyboard(self, user_id, text, accept_data, cancel_data):
        accept = {'text': 'Accept', 'callback_data': accept_data}
        cancel = {'text': 'Cancel', 'callback_data': cancel_data}
        buttons = [[accept, cancel]]
        inline_keyboard = {'inline_keyboard': buttons}
        inline_keyboard = json.dumps(inline_keyboard)
        self.send_message(user_id, text, reply_markup=inline_keyboard)

    def edit_message_text(self, user_id, message_id, text):
        params = {'chat_id': user_id, 'message_id': message_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'editMessageText'
        response = requests.post(url + method, params)
        return response

    def sign_in(self, user_id, data):
        if self.user.login and self.user.hash:
            text = 'Successful login'
            self.reply_keyboard(user_id, text, remove_keyboard=True)
        else:
            text = 'Unsuccessful login'
            self.reply_keyboard(user_id, text, remove_keyboard=True)
            text = 'Will you register?'
            self.inline_keyboard(user_id, text, 'accept', 'cancel')

    def register_instagram_account(self, user_id, data):
        message_id = data['callback_query']['message']['message_id']
        text = '<b>Please enter your instagram account login and password</b>\n' \
               'in this format:\n\n' \
               '<i>login: your login</i>\n' \
               '<i>password: your password</i>'
        self.edit_message_text(user_id, message_id, text)

    def save_login_password(self, user_id, data):
        message_text = str(data['message']['text'])
        message_id = int(data['message']['message_id'])
        if message_text.startswith('login') or message_text.startswith('password'):
            key = message_text.split(':')[0]
            value = message_text.split(':')[1].replace(' ', '')
            if value:
                if key == 'login':
                    TgUser.objects.filter(user_id=user_id).update(login=value)
                elif key == 'password':
                    value, salt = encrypt(value)
                    TgUser.objects.filter(user_id=user_id).update(hash=value, salt=salt)
                self.send_message(user_id, text='{} accepted'.format(key))
            else:
                self.send_message(user_id, text='Input error')

    def get_confirmation(self, user_id, data):
        if self.insta_bot.is_logged_in:
            message_text = str(data['message']['text'])
            accept_data = message_text[1:] + '_accept'
            cancel_data = message_text[1:] + '_cancel'
            text = 'You activate the "{}" mode\n\n' \
                   '<b>Caution! The process lasts about 12 hours</b>\n' \
                   'in the process you will receive notifications'.format(message_text[1:])

            self.inline_keyboard(user_id, text, accept_data, cancel_data)
        else:
            self.send_message(user_id, 'Instagram: Ошибка авторизации\nВведите корректные данные')

    def router(self, user_id, data):
        callback = data['callback_query']['data']
        message_id = int(data['callback_query']['message']['message_id'])
        if callback == 'liking_accept':
            text = 'Mode "Liking" activated'
            self.edit_message_text(user_id, message_id, text)
        elif callback == 'liking_cancel':
            text = 'Mode "Liking" canceled'
            self.edit_message_text(user_id, message_id, text)
        if callback == 'following_accept':
            text = 'Mode "Liking + following" activated'
            self.edit_message_text(user_id, message_id, text)
            self.automode(user_id, data, mode='following')
        elif callback == 'following_cancel':
            text = 'Mode "Liking + following" canceled'
            self.edit_message_text(user_id, message_id, text)
        if callback == 'unfollowing_accept':
            text = 'Mode "Liking + unfollowing" activated'
            self.edit_message_text(user_id, message_id, text)
            self.automode(user_id, data, mode='unfollowing')
        elif callback == 'unfollowing_cancel':
            text = 'Mode "Liking + unfollowing" canceled'
            self.edit_message_text(user_id, message_id, text)

    def automode(self, user_id, data, mode):
        counter = 1
        check = self.check_for_emptiness_db()
        if check is False:
            while counter < 5:
                text = 'Launching {}!\n\n' \
                       'Iteration will be end at {}\n' \
                       '<b>Caution! Do not use your instagram account until the next pause</b>'.format(
                       'liking' if counter % 2 == 1 else mode, self.get_time(3600))
                self.send_message(user_id, text)

                if mode == 'unfollowing':
                    msg = self.insta_bot.like(self.user.id, 5) if counter % 2 == 1 else \
                          self.insta_bot.unfollow(self.user.id, 5)
                else:
                    msg = self.insta_bot.like(self.user.id, 5) if counter % 2 == 1 else \
                        self.insta_bot.follow(self.user.id, 5)

                text = 'Completed {} iteration\n' \
                       '<i>{} - the rest of the iterations</i>\n\n' \
                       'The next iteration starts at {}\n' \
                       'While pausing, you can use an instagram account'.format(
                        counter, 4 - counter, self.get_time(7200)
                )
                self.send_message(user_id, text)
                self.send_message(user_id, '<b>' + msg + '</b>')
                time.sleep(30)
                counter += 1
            text = 'Liking+{} completed!\n\n' \
                   'You can start a new process'.format(mode)
            self.send_message(user_id, text)
        else:
            self.send_message(user_id, 'WARNING: There are not enough objects in the database')

    def get_time(self, seconds):
        return datetime.datetime.strptime(time.ctime(time.time() + seconds), "%a %b %d %H:%M:%S %Y").strftime(
            "%H:%M:%S")

    def whilelist(self, user_id, data):
        if self.insta_bot.is_logged_in:
            self.insta_bot.create_whitelist(user_id)
            self.send_message(user_id, 'Whitelist was created')
        else:
            self.send_message(user_id, 'Instagram: Ошибка авторизации\nВведите корректные данные')

    def start_handler(self, user_id, data):
        button_text = 'Sign in'
        text = 'Hello, {}'.format(self.user.username)
        self.reply_keyboard(user_id, text, button_text=button_text)

    def parse_users_handler(self, user_id, data):
        if self.insta_bot.is_logged_in:
            insta_bot = InstaBot(user_id)
            user_id_list = insta_bot.get_user_id('d.lidiyaaa')
            photo_list = insta_bot.get_photo_list(user_id_list)
            username_list = insta_bot.get_like_list(photo_list)
            if not username_list:
                self.send_message(user_id, 'Instagram: Ошибка сбора ЦА\nВведите другой профиль')
            else:
                save_usernames(username_list, self.user)
        else:
            self.send_message(user_id, 'Instagram: Ошибка авторизации\nВведите корректные данные')

    def check_for_emptiness_db(self, *args):
        data = Profile.objects.filter(tg_user=self.user.id).count()
        if data >= 20:
            return False
        else:
            return True


def generate_key(size=30):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


def encrypt(data):
    password = generate_key()
    encrypted_data = rncryptor.encrypt(data, password)
    return encrypted_data, password


def decrypt(data, password):
    try:
        decrypted_data = rncryptor.decrypt(data, password)
    except:
        print('Некорректный ввод')
        return False
    return decrypted_data