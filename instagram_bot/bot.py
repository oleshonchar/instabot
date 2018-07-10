from django.core.exceptions import ObjectDoesNotExist
import logging
import time
import random

from InstagramAPI import InstagramAPI

from telegram_bot.models import TgUser
from .models import Profile, Whitelist
import telegram_bot.bot


logger = logging.getLogger(__name__)


class InstaBot(object):

    def __init__(self, user_id, max_followers=500, max_profile_count=20):
        self.is_logged_in = False
        self.api = self.login(user_id)
        if self.api:
            login_status = self.api.login()
            self.max_followers = max_followers
            self.max_profile_count = max_profile_count
            if login_status is True:
                self.is_logged_in = True
            else:
                print('Ошибка: некорректный ввод instagram данных')

    @staticmethod
    def login(user_id):
        try:
            data = TgUser.objects.get(user_id=user_id)
        except ObjectDoesNotExist:
            return False
        else:
            login = data.login
            password = data.hash
            salt = data.salt
            password = telegram_bot.bot.decrypt(password, salt)
            if not password:
                print('Ошибка авторизации')
                return False
            else:
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
        if not user_id_list:
            logger.info('Ошибка: страница недоступна')
            return False
        else:
            for user_id in user_id_list:
                user_feed = self.api.getUserFeed(user_id)
                if not user_feed:
                    logger.info('Ошибка: пользователь не найден или доступ закрыт')
                    return False
                pictures = self.api.LastJson['items']
                for picture in pictures:
                    photo_list.append(int(picture['pk']))
                time.sleep(5)
            if photo_list:
                return photo_list
            else:
                logger.info('Ошибка: нет доступных фото')

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
                        print(len(username_list), '|', username)
                    else:
                        return username_list
                else:
                    continue
            time.sleep(1.5)
        return username_list

    def like(self, user_id, number_of_users):
        data = Profile.objects.filter(tg_user=user_id, like=None)[:number_of_users]
        done = 0
        error = 0

        for username in data:
            photo_list = self.get_photo_list(self.get_user_id(username))
            count = 0
            while count < 2:
                if not photo_list:
                    Profile.objects.filter(username=username).update(like=False)
                    error += 1
                    count = 2
                else:
                    random_post_id = photo_list[random.randint(0, (len(photo_list) - 1))]
                    self.api.like(random_post_id)
                    print(str(username) + ' | liked')
                    Profile.objects.filter(username=username).update(like=True)
                    done += 1
                    time.sleep(15)
                count += 1
        return 'Successful liked: {}, unsuccessful liked: {}'.format(done, error)

    def follow(self, user_id, number_of_users):
        data = Profile.objects.filter(tg_user=user_id, follow=None)[:number_of_users]
        done = 0
        error = 0

        for username in data:
            user_id = self.get_user_id(username)
            if user_id:
                self.api.follow(user_id[0])
                print(str(username) + ' | follow')
                Profile.objects.filter(username=username).update(follow=True)
                done += 1
                time.sleep(35)
            else:
                Profile.objects.filter(username=username).update(follow=False)
                error += 1
                continue
        return 'Successful subscriptions: {}, unsuccessful subscriptions: {}'.format(done, error)

    def unfollow(self, user_id, number_of_users):
        data = Profile.objects.filter(tg_user=user_id, follow=True, unfollow=None)[:number_of_users]
        done = 0
        error = 0

        for username in data:
            user_id = self.get_user_id(username)
            if user_id:
                self.api.unfollow(user_id[0])
                print(str(username) + ' | unfollow')
                Profile.objects.filter(username=username).update(unfollow=True)
                done += 1
                time.sleep(35)
            else:
                Profile.objects.filter(username=username).update(unfollow=False)
                error += 1
                continue
        return 'Successful cancel subscriptions: {}, unsuccessful cancel subscriptions: {}'.format(done, error)

    def create_whitelist(self, chat_id):
        user = TgUser.objects.filter(user_id=chat_id).first()
        user_id = self.get_user_id(user.login)
        followers = self.api.getTotalFollowings(user_id[0])
        for username in followers:
            Whitelist.objects.get_or_create(tg_user=user, username=username['username'])


def save_usernames(username_list, user_id):
    for username in username_list:
        profile, created = Profile.objects.get_or_create(username=username, tg_user=user_id)
        if created:
            print('INFO: {} already exists'.format(username))
