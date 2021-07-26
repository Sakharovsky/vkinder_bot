from random import randrange
from pprint import pprint
import vk_api
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_const import *
from datetime import datetime as dt
import csv

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import config

vk_session = VkApi(token=config.GROUP_TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

def message(user_id, random_id, message):
    vk.messages.send(user_id=user_id, random_id = random_id * 10 ** 6 + randrange(1, 10 ** 6, 1), message=message)

def user_info(user_id):
    user_info = vk.users.get(user_ids=user_id, fields='nickname, screen_name, sex, bdate, relation, city, country, home_town, personal, interests, music, movies, books, games')
    return user_info

def get_user_name(user_id):
    user_info = vk.users.get(user_ids=user_id, fields='nickname, screen_name, sex, bdate, relation, city, country, home_town, personal, interests, music, movies, books, games')
    user_name = user_info[0]['first_name'] + ' ' + user_info[0]['last_name']
    return user_name

def client_id_check(client):
    try:
        user_info = vk.users.get(user_ids=client)
        user_id = user_info[0]['id']
        return user_id
    except vk_api.exceptions.ApiError:
        return None

def get_last_random_id(user_id):
    last_messages = vk.messages.getHistory(user_id=-int(config.GROUP_ID), peer_id=user_id)
    for message in last_messages['items']:
        if message['from_id'] == -int(config.GROUP_ID):
            return message['random_id'] // 1000000

def user_access(token):
    session = VkApi(token=token)
    api = session.get_api()
    return api

def user_token_check(used_id, token):
    api = user_access(token)
    try:
        if api.users.get()[0]['id'] == used_id:
            return True
        else:
            return False
    except vk_api.exceptions.ApiError:
        return False

def check_age(vk_client):
    try:
        bd = vk_client[0]['bdate']
        bd = bd.split('.')
        client_bd = dt(int(bd[2]), int(bd[1]), int(bd[0]))
        client_days = dt.now() - client_bd
        client_age = client_days.days / 365.25 // 1
        if client_age <= 0 and client_age >= 99:
            return None
        return client_age
    except:
        return None

def check_city(vk_client):
    try:
        country = vk_client[0]['country']['id']
        if country == 1:
            city = vk_client[0]['city']['id']
            return city
        else:
            return None
    except:
        return None

def check_status(vk_client):
    try:
        status = vk_client[0]['relation']
        return status
    except:
        return None

def check_sex(vk_client):
    try:
        sex_id = vk_client[0]['sex']
        return sex_id
    except:
        return None

def city_list(input_str, user_token):
    vk_session = VkApi(token=user_token)
    vk = vk_session.get_api()
    cities = vk.database.getCities(country_id=1, q=input_str, count=50)
    cities_list = {}
    for city in cities['items']:
        cities_list.update({city["id"]: city["title"]})
    return cities_list

def find_city(input_int, user_token):
    vk_session = VkApi(token=user_token)
    vk = vk_session.get_api()
    try:
        city = vk.database.getCitiesById(city_ids=input_int)
        return (city[0]['id'], city[0]['title'])
    except:
        return None

def search(age, city, sex, status, user_token):
    vk_session = VkApi(token=user_token)
    vk = vk_session.get_api()
    statuses = STATUSES_SEARCH
    if statuses.get(status) == None:
        statuses.update({status: STATUSES.get(status)})
    for bday in range(1, 31):
        for bmonth in range (1, 12):
            for status in statuses:
                searches = vk.users.search(count=100, birth_day=bday, birth_month=bmonth, age_from=age, age_to=age, country=1, city=city, sex=sex, status=status, fields=('has_photo', 'interests', 'books'))
                print(searches['count'])
                print(len(searches['items']))
                with open('searches.csv', 'a', encoding='utf-8') as f:
                    csv.register_dialect('custom', delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    writer = csv.writer(f, 'custom')
                    writer.writerow(searches['items'][0].keys())
                    for row in searches['items']:
                        writer.writerow(row.values())

if __name__ == '__main__':

    """Пример user_info"""
    # user_info = vk.users.get(user_ids=154873356, fields='nickname, screen_name, sex, bdate, relation, city, country, home_town, personal, interests, music, movies, books, games')
    # pprint(user_info)

    """Пример последних сообщений"""
    # last_messages = vk.messages.getHistory(user_id=-int(config.GROUP_ID), peer_id=154873356)
    # print(get_last_random_id(154873356))
    # pprint(last_messages)

    """Проверка обработки возраста"""
    # vk_client = user_info(154873356)
    # bd = vk_client[0]['bdate']
    # bd = bd.split('.')
    # client_bd = dt(int(bd[2]), int(bd[1]), int(bd[0]))
    # client_days = dt.now() - client_bd
    # client_age = client_days.days / 365.25 // 1
    # if client_age <= 0 and client_age >= 99:
    #     client_age = None

    search(27, 1, 1, 1, '3ab0de51ccdb174b0ef9e48ab3ea107cc6466432f735959bb4f5e8788f783c83e68b06892c0b26f8f945d')