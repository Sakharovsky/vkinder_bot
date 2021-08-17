from applications.vk_classes import vk_classes as vk
from applications.vk_classes.vk_const import *
from applications.database import database as db
from applications import bot

if __name__ == '__main__':

    for event in vk.longpoll.listen():
        if event.type == vk.VkEventType.MESSAGE_NEW and event.from_me == False and event.from_user:
            
            last_random_id = vk.get_last_random_id(event.user_id)

            # Функция выхода
            if event.message == 'quit':
                text = "Команда принята! Сбрасываюсь до заводских настроек! Но я тебя запомнил..."
                vk.message(event.user_id, 300, text)
                continue
            
            # Замена токена
            if event.message == 'token':
                text = "Окей, давай поменяем твой токен. Пришли его в чат."
                vk.message(event.user_id, 100, text)
                continue

            # Замена клиента
            if event.message == 'client':
                text = "Окей, давай изменим, для кого будем подбирать пару. Пришли его VK id или screen_name."
                vk.message(event.user_id, 101, text)
                continue

            # Замена возраста
            if event.message == 'age':
                text = "Окей, давай поменяем возраст пользователя, для которого будем искать пару. Напиши, сколько ему лет."
                vk.message(event.user_id, 102, text)
                continue
            
            # Замена семейного положения
            if event.message == 'status':
                text = """Окей, давай поменяем семейное положение пользователя, для которого будем искать пару. Укажи, в каком статусе он находится.
                    Доступные варианты:
                    1 - не женат (не замужем)
                    2 - встречается
                    3 - помолвлен(-а)
                    4 - женат (замужем)
                    5 - всё сложно
                    6 - в активном поиске
                    7 - влюблен(-а)
                    8 - в гражданском браке"""
                vk.message(event.user_id, 103, text)
                continue
            
            # Замена пола
            if event.message == 'sex':
                text = """Окей, давай поменяем город пользователя, для которого будем искать пару. Укажи, какого он/она пола.
                    Доступные варианты:
                    1 - женщина
                    2 - мужчина
                    3 - любой"""
                vk.message(event.user_id, 104, text)
                continue

            # Замена города
            if event.message == 'city':
                text = """Окей, давай поменяем город пользователя, для которого будем искать пару. Напиши, где он сейчас.
                    Если я найду несколько похожих вариантов, то попрошу выбрать."""
                vk.message(event.user_id, 105, text)
                continue

            # None: Сообщение от нового пользователя или после выхода
            if last_random_id == None or last_random_id == 300:
                check_user_info(event.user_id)

            # 100: Ожидаем получения токена пользователя, проверяем токен
            if last_random_id == 100:
                message = {len(item): item for item in event.message.split(' ')}
                token = message[max(message.keys())]
                if vk.user_token_check(event.user_id, token) == True:
                    db.upd_token(event.user_id, token)
                    check_user_info(event.user_id)
                else:
                    text = "Ой-ой! Этот токен не имеет достаточно прав. Пришли другой!"
                    vk.message(event.user_id, 100, text)

            # 101: Ожидаем получения vk id или screen_name
            if last_random_id == 101:
                client_id = vk.client_id_check(event.message)
                if client_id != None:
                    # Проверка, если клиент в базе имеется для этого юзера
                    db_client = db.get_user_client(event.user_id)
                    if db_client != None: 
                        db.upd_client(event.user_id, chosen=0)

                    vk_client = vk.user_info(client_id)
                    client_age = vk.check_age(vk_client)
                    client_city = vk.check_city(vk_client)
                    client_status = vk.check_status(vk_client)
                    client_sex = vk.check_sex(vk_client)

                    db_client = db.clients(vk_id=vk_client[0]['id'],
                                            name=vk_client[0]['first_name'],
                                            lastname=vk_client[0]['last_name'],
                                            age=client_age,
                                            city=client_city,
                                            status=client_status,
                                            sex_id=client_sex)

                    db.to_db(db_client)
                    db.conn_user_client(event.user_id, db_client)

                    user_name = vk.get_user_name(client_id)
                    check_user_info(event.user_id)

                elif client_id == None:
                    text = "Ой-ой! Я не могу найти этого пользователя. Проверь правильность и повтори запрос."
                    vk.message(event.user_id, 101, text)
            
            #102: Ожидаем получения возраста клиента
            if last_random_id == 102:
                try:
                    reply = int(event.message)
                except TypeError:
                    reply = event.message
                if isinstance(reply, int) and reply > 0 and reply < 99:
                    db.upd_client(event.user_id, age=reply, search_list=None)
                    check_user_info(event.user_id)
                else:
                    text = "Ой-ой! Я вижу число полных лет. Проверь правильность и повтори запрос."
                    vk.message(event.user_id, 102, text)
            
            #103: Ожидаем получения семейного положения
            if last_random_id == 103:
                try:
                    reply = int(event.message)
                except TypeError:
                    reply = event.message
                if isinstance(reply, int) and reply >= 1 and reply <= 8:
                    db.upd_client(event.user_id, status=reply, search_list=None)
                    check_user_info(event.user_id)
                else:
                    text = "Ой-ой! Я вижу номер семейного положения. Проверь правильность и повтори запрос."
                    vk.message(event.user_id, 103, text)
            
            #104: Ожидаем получения пола
            if last_random_id == 104:
                try:
                    reply = int(event.message)
                except TypeError:
                    reply = event.message
                if isinstance(reply, int) and reply >= 1 and reply <= 3:
                    sex_id = reply
                    if sex_id == 3:
                        sex_id = 0
                    db.upd_client(event.user_id, sex=sex_id, search_list=None)
                    check_user_info(event.user_id)
                else:
                    text = "Ой-ой! Я вижу номер пола из предложенных. Проверь правильность и повтори запрос."
                    vk.message(event.user_id, 104, text)
            
            #105: Ожидаем получения названия города
            if last_random_id == 105:
                try:
                    reply = int(event.message)
                except:
                    reply = event.message
                if isinstance(reply, str):
                    if len(reply) > 14:
                        reply = reply[0:15]
                    user = db.get_user_info(event.user_id)
                    city_list = vk.city_list(reply, user.token)
                    text = 'Мне удалось найти следующие варианты. Выбери один из них или повтори запрос.\n'
                    for id, city in city_list.items():
                        text += f'{id} - {city}\n'
                    vk.message(event.user_id, 105, text)
                elif isinstance(reply, int):
                    user = db.get_user_info(event.user_id)
                    city = vk.find_city(reply, user.token)
                    db.upd_client(event.user_id, city=city[0], search_list=None)
                    text = f'Выбран город {city[1]}'
                    vk.message(event.user_id, 300, text)
                    check_user_info(event.user_id)
                else:
                    text = 'Не могу понять ответ. Я ожидаю получить либо название города, либо номер его id в VK.'
                    vk.message(event.user_id, 105, text)

            #110: Ожидаем next для получения фотографий профиля
            if last_random_id == 110 and event.message == 'next':
                user = db.get_user_info(event.user_id)
                client = db.get_user_client(event.user_id)
                ban_list = db.get_searches(event.user_id)
                if client.search_list == None:
                    searches = vk.search(1000, ban_list, client.age, client.city, client.sex_id, client.status, user.token)
                    db.upd_client(event.user_id, search_list=searches)
                else:
                    searches = client.search_list
                
                while True:
                    # Если список опустел, обновляем список
                    if searches == []:
                        searches = vk.search(1000, ban_list, client.age, client.city, client.sex_id, client.status, user.token)
                        db.upd_client(event.user_id, search_list=searches)
                    
                    search = searches[0]
                    photos = vk.get_photos(search['id'], user.token)
                    # Если пользователь в базе или у профиля недостаточно фотографий, заносим в базу и переходим к следующему
                    if search['id'] in ban_list or photos == None or len(photos.keys()) < 3:
                        searches.pop(0)
                        db_search = db.searches(search['id'], client.id, search['first_name'], search['last_name'], 4)
                        db.conn_user_search(event.user_id, db_search)
                    else:
                        vk_site = 'http://vk.com/'
                        text = f"{search['first_name']} {search['last_name']} - {vk_site}{search['screen_name']}"
                        photos = vk.get_photos(search['id'], user.token)
                        vk.message_photo(event.user_id, 110, text, photos, user.token)
                        searches.pop(0)
                        db_search = db.searches(search['id'], client.id, search['first_name'], search['last_name'], 0)
                        db.conn_user_search(event.user_id, db_search)
                        db.upd_client(event.user_id, search_list=searches)
                        for photo in photos.values():
                            db_search_id = db.get_last_search(event.user_id, search['id'])
                            db_photo = db.photos(db_search_id, photo[0], photo[1], photo[3])
                            db.to_db(db_photo)
                        break
