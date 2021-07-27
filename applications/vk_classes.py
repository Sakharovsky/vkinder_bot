from random import randrange
from pprint import pprint
import vk_api
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from datetime import datetime as dt

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
from vk_const import *
sys.path.insert(0, parent_dir)
import config

vk_session = VkApi(token=config.GROUP_TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

def message(user_id, random_id, message):
    vk.messages.send(user_id=user_id, random_id = random_id * 10 ** 6 + randrange(1, 10 ** 6, 1), message=message)

def message_photo(user_id: int, random_id: int, message: str, photos: list, token: str):
    attachment = []
    for media_id, photo in photos.items():
        attach = f'photo{photo[3]}_{media_id}_{token}'
        attachment.append(attach)
    vk.messages.send(user_id=user_id, random_id = random_id * 10 ** 6 + randrange(1, 10 ** 6, 1), message=message, attachment=",".join(attachment))

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

def search(limit, ban_list, age, city, sex, status, user_token):
    """Принимает параметры пользователя и возвращает список подходящих профилей ВК."""

    vk_session = VkApi(token=user_token)
    vk = vk_session.get_api()

    # Подбираем возможные статусы профилей под доступные для отношений + статус пользователя
    statuses = STATUSES_SEARCH
    if statuses.get(status) == None:
        statuses.update({status: STATUSES.get(status)})

    # Меняем параметр поиска по полу в зависимости от пола пользователя
    if sex == 1:
        sex = 2
    elif sex == 2:
        sex = 1

    file = []
    for bmonth in range (1, 12):
        for status in statuses.keys():
            responce = vk.users.search(count=1000, birth_month=bmonth, age_from=age, age_to=age, country=1, city=city, sex=sex, status=status, fields=('screen_name', 'has_photo', 'interests', 'books'))
            searches = responce['items']

            # Убираем закрытые профили и уже просмотренные
            for search in searches:
                if search['is_closed'] is False and search['id'] not in ban_list:
                    file.append(search)
            
            if len(file) > limit:
                break

        # Ограничение на количество профилей
        if len(file) > limit:
            break

    return file
    
def get_photos(vk_id, token):
    """Принимает id профиля VK и возвращает ТОП 3 фотографии по сумме лайков и комментариев."""

    vk_session = VkApi(token=token)
    vk = vk_session.get_api()

    try:
        photos = vk.photos.getAll(owner_id=vk_id, extended=1, skip_hidden=1)
        comments = vk.photos.getAllComments(owner_id=vk_id)

        photo_dict = {}
        for photo in photos['items']:
            url = photo['sizes'][len(photo['sizes'])-1]
            photo_dict.update({photo['id']: [photo['likes']['count'], 0, url['url'], photo['owner_id']]})
        for comment in comments['items']:
            if comment['pid'] in photo_dict.keys() and comment['from_id'] != vk_id:
                photo_dict[comment['pid']][1] += 1
        
        # Выбираем ТОП 3 фотографии
        like_comments = [item[0]+item[1] for item in photo_dict.values()]
        like_comments = sorted(like_comments, reverse=True)[0:3]
        top_photos = {}
        for photo, item in photo_dict.items():
            if item[0] + item[1] in like_comments and len(top_photos.keys()) < 3:
                top_photos.update({photo: item})
        
        return top_photos

    except:
        return None

    

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

    """Проверка поиска профилей"""
    # pprint(search(1000, [], 27, 1, 1, 1, 'b727c15bd515d82a2c107faade52ec39803105ecd21f673d3a5f3e188c0cfed1fde5b93b38a12754a0992')[0])

    """Проверка выгрузки ТОП 3 фотографии профиля"""
    # pprint(get_photos(154873356, 'b727c15bd515d82a2c107faade52ec39803105ecd21f673d3a5f3e188c0cfed1fde5b93b38a12754a0992'))

    