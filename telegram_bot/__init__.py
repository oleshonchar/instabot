from time import sleep
import requests

from instabot.settings import HOST, TG_TOKEN


url = "https://api.telegram.org/bot{}/".format(TG_TOKEN)


def set_webhook():
    params = {'url': HOST + '/bot/' + TG_TOKEN + '/'}
    method = 'setWebhook'
    response = requests.post(url + method, params)
    print('Set webhook')
    print('Status code:', response.status_code)
    return response


def delete_webhook():
    method = 'deleteWebhook'
    response = requests.post(url + method)
    print('Delete webhook')
    print('Status code:', response.status_code)
    return response


delete_webhook()
sleep(1)
set_webhook()
