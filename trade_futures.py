from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import threading
from time import sleep
from loguru import logger
from dotenv import load_dotenv
from codes.readEmail import check_inbox
from codes.get2faGoogle import getGoogleAuthCode
from utils.excel import readExcelProfileName, writeExcel
from ldPlayer_api import start_emulator, stop_emulator

write_lock = threading.Lock()
load_dotenv()
WAIT_LOAD_EMULATOR = int(os.environ['WAIT_LOAD_EMULATOR'])


def futures_rooter(profile_name):
    
    account_email = readExcelProfileName(profile_name, 'Login') # Получаем email аккаунта
    googleSecret = readExcelProfileName(profile_name, 'Google2Fa')
    depositAddr = readExcelProfileName(profile_name, 'depositAddr')
    
    # Запускаем драйвер
    if start_emulator():
        sleep(WAIT_LOAD_EMULATOR)
        driver = mobile_connect()
    else:
        return False
    
    driver.quit()
    stop_emulator()
    return True

# Устанавливаем 2FA
def trade_futures(account_email, driver):

    for _ in range(3):
        driver.activate_app('com.younger.client')
        try:
            # Закрываем все окошки
            while True:
                try:
                    # Нажимаем "Больше никаких напоминаний на сегодня"
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.CheckBox[@resource-id="com.younger.client:id/checkbox"]'))).click()
                    # Закрываем всю рекламу
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.ImageView[@resource-id="com.younger.client:id/iv_close"]'))).click()
                except:
                    break
            
            # Тыкаем снизу на "Фьючерсы"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.LinearLayout[@resource-id="com.younger.client:id/tab_bar"]/android.widget.RelativeLayout[4]'))).click()

            # Тыкаем снизу на "Фьючерсы"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.LinearLayout[@resource-id="com.younger.client:id/tab_bar"]/android.widget.RelativeLayout[4]'))).click()
        
        
        
        
        except:
            driver.terminate_app('com.younger.client')
            logger.debug(f'Ошибка при создании 2FA API. Повтор через 5 сек...')
            sleep(5)
    return False



# Подключение драйвера
def mobile_connect():
    capabilities = {
        'platformName': 'Android',
        'deviceName': 'emulator-5558',
        'automationName': 'UiAutomator2',
        'noReset': True
    }
    return webdriver.Remote('http://localhost:4723/wd/hub', options=UiAutomator2Options().load_capabilities(capabilities))



#driver = mobile_connect()
#driver.activate_app('com.younger.client')
#get_dep_addr(driver)