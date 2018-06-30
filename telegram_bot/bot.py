import requests

from telegram_bot import url
from telegram_bot.models import Authentication
from instagram_bot.bot import InstaBot, save_usernames


class TgBotHandler(object):

    def __init__(self, user_id):
        self.user = Authentication.objects.get(user_id=user_id)
        self.insta_bot = InstaBot(user_id)

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        response = requests.post(url + method, params)
        return response

    def parse_users_handler(self, user_id):
        insta_bot = InstaBot(user_id)
        user_id_list = insta_bot.get_user_id('olesgonchar')
        photo_list = insta_bot.get_photo_list(user_id_list)
        username_list = insta_bot.get_like_list(photo_list)
        save_usernames(username_list, self.user)

    def like_handler(self, *args):
        self.insta_bot.like(self.user.id, 5)

    def follow_handler(self, *args):
        self.insta_bot.follow(self.user.id, 5)

    def unfollow_handler(self, *args):
        self.insta_bot.unfollow(self.user.id, 5)
