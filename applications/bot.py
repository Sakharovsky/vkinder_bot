from vk_classes import vk_classes as vk
from vk_classes.vk_const import *
from database import database as db

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
                    status = "".join([f"{i} - {v}\n" for i, v in STATUSES.items()])
                    text = """Не вижу семейное положение человека, для которого будем подбирать пару. Укажи, в каком статусе он находится.
                    Доступные варианты:
                    """
                    vk.message(user_id, 103, text + status)
                    
                elif db_client.sex_id == None:
                    sex = "".join([f"{i} - {v}\n" for i, v in SEXES.items()])
                    text = """Не вижу пола человека, для которого будем подбирать пару. Укажи, какого он/она пола.
                    Доступные варианты:
                    """
                    vk.message(user_id, 104, text + sex)
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
                                Возраст: {int(client_age)}
                                Город: {client_city}
                                Семейное положение: {client_status}
                                Пол: {client_sex}
                                Приоритет на противоположный пол, а для "любой" будут подбираться кандидаты вне зависимости от пола.
                                
                                У меня есть следующие команды:
                                "next" - пришлю ссылку на подходящий профиль ВК и ТОП 3 фотографии по популярности
                                "token" - запрошу у вас новый токен
                                "client" - запрошу другой VK id или screen_name
                                "age"/"city"/"status"/"sex" - изменю параметры возраста/города/положения/пола для client
                                "quit" - сбор моих настроек, но предпочтения я запомнил  ;)
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
        text = "Привет! Я могу помочь подобрать тебе пару для знакомств. Пришли токен от своего аккаунта."
        vk.message(user_id, 100, text)