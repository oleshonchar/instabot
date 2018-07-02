import requests
import json
import datetime
import time

from telegram_bot import url
from telegram_bot.models import Authentication
from instagram_bot.bot import InstaBot, save_usernames
from instagram_bot.models import Profile


class TgBotHandler(object):

    def __init__(self, user_id, username):
        self.user, self.user_created = Authentication.objects.get_or_create(user_id=user_id, username=username)
        self.insta_bot = InstaBot(user_id)

    def send_message(self, chat_id, text, reply_markup=None):
        params = {'chat_id': chat_id, 'text': text, 'reply_markup': reply_markup, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        response = requests.post(url + method, params)
        return response

    def reply_keyboard(self, chat_id, text, button_text='Empty', remove_keyboard=False):
        if remove_keyboard:
            keyboard = {'remove_keyboard': remove_keyboard}
        else:
            button = [[{'text': button_text}]]
            keyboard = {'keyboard': button, 'resize_keyboard': True, 'one_time_keyboard': True}
        keyboard = json.dumps(keyboard)
        self.send_message(chat_id, text, reply_markup=keyboard)

    def inline_keyboard(self, chat_id, text, accept_data, cancel_data):
        accept = {'text': 'Accept', 'callback_data': accept_data}
        cancel = {'text': 'Cancel', 'callback_data': cancel_data}
        buttons = [[accept, cancel]]
        inline_keyboard = {'inline_keyboard': buttons}
        inline_keyboard = json.dumps(inline_keyboard)
        self.send_message(chat_id, text, reply_markup=inline_keyboard)

    def edit_message_text(self, chat_id, message_id, text):
        params = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'editMessageText'
        response = requests.post(url + method, params)
        return response

    def sign_in(self, chat_id, data):
        if self.user.login or self.user.password:
            text = 'Successful login'
            self.reply_keyboard(chat_id, text, remove_keyboard=True)
        else:
            text = 'Unsuccessful login'
            self.reply_keyboard(chat_id, text, remove_keyboard=True)
            text = 'Will you register?'
            self.inline_keyboard(chat_id, text, 'accept')

    def register_instagram_account(self, chat_id, data):
        message_id = data['callback_query']['message']['message_id']
        text = '<b>Please enter your instagram account login and password</b>\n' \
               'in this format:\n\n' \
               '<i>login: your login</i>\n' \
               '<i>password: your password</i>'
        self.edit_message_text(chat_id, message_id, text)

    def save_login_password(self, chat_id, data):
        message_text = str(data['message']['text'])
        message_id = int(data['message']['message_id'])
        print(message_id)
        if message_text.startswith('login') or message_text.startswith('password'):
            key = message_text.split(':')[0]
            value = message_text.split(':')[1].replace(' ', '')
            if value:
                # TODO: як передать вміст змінної як аргумент функції?
                # Authentication.objects.filter(user_id=chat_id).update(key=value)
                if key == 'login':
                    Authentication.objects.filter(user_id=chat_id).update(login=value)
                elif key == 'password':
                    Authentication.objects.filter(user_id=chat_id).update(password=value)
                self.send_message(chat_id, text='{} accepted'.format(key))
            else:
                self.send_message(chat_id, text='Input error')

    def get_confirmation(self, chat_id, data):
        message_text = str(data['message']['text'])
        accept_data = message_text[1:] + '_accept'
        cancel_data = message_text[1:] + '_cancel'
        text = 'You activate the "{}" mode\n\n' \
               '<b>Caution! The process lasts about 12 hours</b>\n' \
               'in the process you will receive notifications'.format(message_text[1:])

        self.inline_keyboard(chat_id, text, accept_data, cancel_data)

    def router(self, chat_id, data):
        callback = data['callback_query']['data']
        message_id = int(data['callback_query']['message']['message_id'])
        if callback == 'liking_accept':
            text = 'Mode "Liking" activated'
            self.edit_message_text(chat_id, message_id, text)
        elif callback == 'liking_cancel':
            text = 'Mode "Liking" canceled'
            self.edit_message_text(chat_id, message_id, text)
        if callback == 'following_accept':
            text = 'Mode "Liking + following" activated'
            self.edit_message_text(chat_id, message_id, text)
            self.automode(chat_id, data, mode='following')
        elif callback == 'following_cancel':
            text = 'Mode "Liking + following" canceled'
            self.edit_message_text(chat_id, message_id, text)

    def automode(self, chat_id, data, mode):
        counter = 1
        check = self.check_for_emptiness_db()
        if check is False:
            while counter < 5:
                text = 'Launching {}!\n\n' \
                       'Iteration will be end at {}\n' \
                       '<b>Caution! Do not use your instagram account until the next pause</b>'.format(
                       'liking' if counter % 2 == 1 else mode, self.get_time(3600))
                self.send_message(chat_id, text)

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
                self.send_message(chat_id, text)
                self.send_message(chat_id, '<b>' + msg + '</b>')
                time.sleep(30)
                counter += 1
            text = 'Liking+{} completed!\n\n' \
                   'You can start a new process'.format(mode)
            self.send_message(chat_id, text)
        else:
            self.send_message(chat_id, 'WARNING: There are not enough objects in the database')

    def get_time(self, seconds):
        return datetime.datetime.strptime(time.ctime(time.time() + seconds), "%a %b %d %H:%M:%S %Y").strftime(
            "%H:%M:%S")

    def whilelist(self, chat_id, data):
        self.insta_bot.create_whitelist(chat_id)
        self.send_message(chat_id, 'Whitelist was created')

    def start_handler(self, chat_id, data):
        button_text = 'Sign in'
        text = 'Hello, {}'.format(self.user.username)
        self.reply_keyboard(chat_id, text, button_text=button_text)

    def parse_users_handler(self, user_id, data):
        insta_bot = InstaBot(user_id)
        user_id_list = insta_bot.get_user_id('olesgonchar')
        photo_list = insta_bot.get_photo_list(user_id_list)
        username_list = insta_bot.get_like_list(photo_list)
        save_usernames(username_list, self.user)

    def check_for_emptiness_db(self, *args):
        data = Profile.objects.filter(user_id=self.user.id).count()
        if data >= 20:
            return False
        else:
            return True
