from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from threading import Thread
import json

from config import TG_TOKEN
from .bot import TgBotHandler


class CommandReceiveView(View):
    def post(self, request, bot_token):

        if bot_token != TG_TOKEN:
            return HttpResponseForbidden('Invalid token')

        try:
            data = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            # TODO: переписати try, exept на зрозумілішу логіку
            # Зараз: по кліку на інлайн-кнопку приходить інший об'єкт
            try:
                chat_id = data['message']['chat']['id']
                cmd = data['message'].get('text')
                username = data['message']['from']['first_name'] + ' ' + data['message']['from']['last_name']
                callback = False
            except KeyError:
                callback = data['callback_query']['data']
                chat_id = data['callback_query']['from']['id']
                username = data['callback_query']['from']['first_name'] + ' ' + data['callback_query']['from']['last_name']
                cmd = False

            tg_bot = TgBotHandler(chat_id, username)

            commands = {
                '/parse': tg_bot.parse_users_handler,
                '/liking': tg_bot.get_confirmation,
                '/following': tg_bot.get_confirmation,
                '/unfollowing': tg_bot.get_confirmation,
                '/start': tg_bot.start_handler,
                '/whitelist': tg_bot.whilelist,
                'sign': tg_bot.sign_in,
                'accept': tg_bot.register_instagram_account,
                'login:': tg_bot.save_login_password,
                'password:': tg_bot.save_login_password,
                'liking_accept': tg_bot.router,
                'liking_cancel': tg_bot.router,
                'following_accept': tg_bot.router,
                'following_cancel': tg_bot.router,
            }

            if callback:
                func = commands.get(str(callback))
            else:
                func = commands.get(cmd.split()[0].lower())

            if func:
                t = Thread(target=func, args=(chat_id, data,))
                t.start()
            else:
                tg_bot.send_message(chat_id, 'I do not understand you!')

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
