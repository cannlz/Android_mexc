from ldPlayer_api import list_emulators
from setup_account import setup_rooter
from proxy_auto import proxy_rooter
#from mexc_registration import rooter

import os
from pick import pick
from loguru import logger
from utils.readSettings import getSettings, writeSettings, writeLinks
from time import sleep



# Выбор опции
def choose_option():
    title = 'Выберете цель работы скрипта: '
    options = [
        'Регистрация аккаунтов',
        'Настройка аккаунтов'
    ]

    option, index = pick(options, title, indicator='=>', default_index=0)
    return index, option

# Запрос на ID профилей
def get_id_profile():
    writeLinks()
    
    work_type = choose_option()
    
    # Читаем файл с профилями
    with open(f"{os.getcwd()}\\Android_mexc\\accounts_to_work.txt", 'r', encoding='utf-8') as file:
        lines = file.readlines()
    all_profile_data = [line.strip() for line in lines]
    
    if work_type[0] == 0: # Регистрация аккаунтов
        logger.debug(f'Выбрано: {work_type[1]}')
        logger.debug(f'Обнаружил профилей: {len(all_profile_data)}')
    
    elif work_type[0] == 1: # Настройка аккаунтов
        logger.debug(f'Выбрано: {work_type[1]}')
        
        logger.debug(f'Обнаружил профилей: {len(all_profile_data)}')
        setup_accounts(all_profile_data)

    else: 
        logger.error(f'Ошибка, что-то не так выбрали')



# Авторег
def autoreg():
    print('в разработке')

# Настройка аккаунтов
def setup_accounts(profiles_data):
    for data in profiles_data:
        profile_name = data.split(':')[0]
        proxy_user = data.split(':')[1].split(':')[0]
        proxy_pass = data.split(':')[2].split('@')[0]
        proxy_ip = data.split('@')[1].split(':')[0]
        proxy_port = data.split('@')[1].split(':')[1]
        if proxy_rooter(proxy_ip, proxy_port, proxy_user, proxy_pass, False):
            setup_rooter(profile_name)
            
            
get_id_profile()