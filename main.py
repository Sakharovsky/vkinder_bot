from applications import vk_classes as vk
from applications import database as db
from applications.vk_const import *

def check_user_info(user_id):
    db_user = db.get_user_info(user_id)
    if db_user != None:
        token = db_user.token
        if token != None:
            db_client = db.get_user_client(user_id)
            if db_client != None:
                if db_client.age == None:
                    text = "Не вижу даты рождения человека, для которого будем подбирать пару. Напиши, сколько ему лет."
                    vk.message(user_id, 102, text)
                elif db_client.status == None:
                    text = """Не вижу семейное положение человека, для которого будем подбирать пару. Укажи, в каком статусе он находится.
                    Доступные варианты:
                    1 - не женат (не замужем)
                    2 - встречается
                    3 - помолвлен(-а)
                    4 - женат (замужем)
                    5 - всё сложно
                    6 - в активном поиске
                    7 - влюблен(-а)
                    8 - в гражданском браке
                    """
                    vk.message(user_id, 103, text)
                    
                elif db_client.sex_id == None:
                    text = """Не вижу пола человека, для которого будем подбирать пару. Укажи, какого он/она пола.
                    Доступные варианты:
                    1 - женщина
                    2 - мужчина
                    3 - любой
                    """
                    vk.message(user_id, 104, text)
                elif db_client.city == None:
                    text = """Не вижу в каком городе живёт человек, для которого будем подбирать пару. Напиши, где он сейчас.
                    Если я найду несколько похожих вариантов, то попрошу выбрать."""
                    vk.message(user_id, 105, text)
                else:
                    client_name = db_client.name
                    client_lastname = db_client.lastname
                    client_age = db_client.age
                    client_city = vk.find_city(db_client.city, token)[1]
                    client_status = STATUSES.get(db_client.status)
                    client_sex = SEXES.get(db_client.sex_id)
                    text = f"""Мы готовы начинать подбор! Параметры следующие:
                                Ищем пару для: {client_name} {client_lastname}

                                Возраст: {client_age}
                                Допустимое отклонение поиска в 1 год.

                                Город: {client_city}
                                Поиск будет производиться только по этому городу.

                                Семейное положение: {client_status}
                                Отбор будет производиться для этого статуса, а также для открытых в отношениях.

                                Пол: {client_sex}
                                Приоритет на противоположный пол, а для "любой" будут подбираться кандидаты вне зависимости от пола.

                                Параметры можно изменить в настройках. Для большей информации отправьте "\settings".
                    """
                    vk.message(user_id, 110, text)
            else:
                text = "Отлично! Пришли id или screen_name аккаунта, которому будем подбирать пару."
                vk.message(user_id, 101, text)
        else:
            text = "Привет! Пришли токен от своего аккаунта."
            vk.message(user_id, 100, text)
    else:
        vk_user = vk.user_info(user_id)
        db_user = db.users(vk_user[0]['first_name'], vk_user[0]['last_name'], vk_user[0]['id'])
        db.to_db(db_user)
        text = "Привет! Пришли токен от своего аккаунта."
        vk.message(user_id, 100, text)

if __name__ == '__main__':

    for event in vk.longpoll.listen():
        if event.type == vk.VkEventType.MESSAGE_NEW and event.from_me == False and event.from_user:
            
            last_random_id = vk.get_last_random_id(event.user_id)

            # Функция выхода
            if event.message == '\quit':
                text = "Команда принята! Сбрасываюсь до заводских настроек! Но я тебя запомнил..."
                vk.message(event.user_id, 300, text)
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
                    db.upd_client(event.user_id, age=reply)
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
                    db.upd_client(event.user_id, status=reply)
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
                    db.upd_client(event.user_id, sex=sex_id)
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
                    db.upd_client(event.user_id, city=city[0])
                    text = f'Выбран город {city[1]}'
                    vk.message(event.user_id, 300, text)
                    check_user_info(event.user_id)
                else:
                    text = 'Не могу понять ответ. Я ожидаю получить либо название города, либо номер его id в VK.'
                    vk.message(event.user_id, 105, text)

