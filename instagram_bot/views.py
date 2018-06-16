# from .models import Profile
from telegram_bot.models import Authentication
from django.core.exceptions import ObjectDoesNotExist
from api import InstagramAPI
import logging


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

