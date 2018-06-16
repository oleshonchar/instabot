# from .models import Profile
from telegram_bot.models import Authentication
from django.core.exceptions import ObjectDoesNotExist
from api import InstagramAPI
import logging
import time


logger = logging.getLogger(__name__)


class InstaBot(object):

    def __init__(self, user_id):
        self.api = self.login(user_id)
        self.api.login()

    @staticmethod
    def login(user_id):
        try:
            data = Authentication.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            return False
        else:
            login = data.login
            password = data.password
            return InstagramAPI(login, password)

    def get_user_id(self, *username_list):
        user_id_list = list()
        for username in username_list:
            self.api.searchUsername(username)
            try:
                user_id_list.append(int(self.api.LastJson['user']['pk']))
            except KeyError:
                logger.info('Ошибка: страница недоступна')
                return False
        return user_id_list

    def get_photo_id(self, *username_list):
        photo_list = list()
        user_id_list = self.get_user_id(*username_list)
        if user_id_list:
            for user_id in user_id_list:
                user_feed = self.api.getUserFeed(user_id)
                if not user_feed:
                    logger.info('Ошибка: пользователь не найден или доступ закрыт')
                    return False
                pictures = self.api.LastJson['items']
                for picture in pictures:
                    photo_list.append(int(picture['pk']))
                time.sleep(5)
            return photo_list
        else:
            logger.info('Ошибка: страница недоступна')
            return False
