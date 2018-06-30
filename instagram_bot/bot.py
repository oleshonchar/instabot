from .models import Profile
from telegram_bot.models import Authentication
from django.core.exceptions import ObjectDoesNotExist
from api import InstagramAPI
import logging
import time


logger = logging.getLogger(__name__)


class InstaBot(object):

    def __init__(self, user_id, max_followers=500, max_profile_count=200):
        self.api = self.login(user_id)
        self.api.login()
        self.max_followers = max_followers
        self.max_profile_count = max_profile_count

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
        return user_id_list

    def get_photo_list(self, *username_list):
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

    def check_follower_count(self, username):
        self.api.searchUsername(username)
        try:
            total = self.api.LastJson['user']['follower_count']
        except KeyError:
            logger.info('Ошибка: пользователь не найден или доступ закрыт')
            return False
        finally:
            time.sleep(1)
        if total < self.max_followers:
            return total
        else:
            return False

    def get_like_list(self, photo_list):
        username_list = list()
        for photo_id in photo_list:
            self.api.getMediaLikers(photo_id)
            users_list = self.api.LastJson['users']
            for user in users_list:
                username = user['username']
                if username not in username_list and self.check_follower_count(username):
                    if len(username_list) < self.max_profile_count:
                        username_list.append(username)
                    else:
                        return username_list
                else:
                    continue
            time.sleep(1.5)
        return username_list


def save_usernames(username_list, user_id):
    for username in username_list:
        data = Profile.objects.get_or_create(username=username, user_id=user_id)
        if data:
            print('INFO: {} already exists'.format(username))
