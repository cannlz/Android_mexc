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


def setup_rooter(profile_name):
    
    account_email = readExcelProfileName(profile_name, 'Login') # Получаем email аккаунта
    googleSecret = readExcelProfileName(profile_name, 'Google2Fa')
    depositAddr = readExcelProfileName(profile_name, 'depositAddr')
    
    # Запускаем драйвер
    if start_emulator():
        sleep(WAIT_LOAD_EMULATOR)
        driver = mobile_connect()
    else:
        return False
    
    # Установка google2fa
    if not googleSecret:
        if (google_secret := set_2fa(account_email)):
            with write_lock:
                writeExcel(account_email, 'Google2Fa', google_secret) # Записываем в excel google2fa
        else:
            logger.error(f'[{profile_name}] Ошибка установки google authenticator')
            return False
    else:
        logger.warning(f"[{profile_name}] На аккаунте уже установлен google authenticator: {googleSecret}")
        
    # Получаем адрес депозита
    if not depositAddr:
        if (dep_addr := get_dep_addr(driver)):
            with write_lock:
                writeExcel(account_email, 'depositAddr', dep_addr) # Записываем в excel google2fa
        else:
            logger.error(f'[{profile_name}] Не удалось получить адрес для пополнения')
            return False
    else:
        logger.warning(f"[{profile_name}] На аккаунте уже получен адрес депозита: {depositAddr}")
    
    driver.quit()
    stop_emulator()
    return True

# Устанавливаем 2FA
def set_2fa(account_email, driver):

    for _ in range(3):
        try:
            driver.activate_app('com.younger.client')
            # Закрываем все окошки
            while True:
                try:
                    # Нажимаем "Больше никаких напоминаний на сегодня"
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.CheckBox[@resource-id="com.younger.client:id/checkbox"]'))).click()
                    # Закрываем всю рекламу
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.ImageView[@resource-id="com.younger.client:id/iv_close"]'))).click()
                except:
                    break
            
            # Тыкаем слева сверху на человечка
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.ImageView[@resource-id="com.younger.client:id/iv_person"]'))).click()
            
            # Тыкаем на безопасность
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[@resource-id="com.younger.client:id/left_text_tv" and @text="Безопасность"]'))).click()
            
            # Тыкаем на Google Authenticator
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.view.ViewGroup[@resource-id="com.younger.client:id/item_google"]/android.view.ViewGroup'))).click()
            
            # Тыкаем на Далее
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@resource-id="com.younger.client:id/next_step_btn"]'))).click()
            
            # Копируем 2FA Код
            google_2faSecret = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[@resource-id="com.younger.client:id/back_up_secret_key_txt"]'))).text

            # Тыкаем на Привязать
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@resource-id="com.younger.client:id/next_step_btn"]'))).click()
            
            if send_codes_2fa(driver, account_email, google_2faSecret):
                # Нажимаем "Отправить"
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@resource-id="com.younger.client:id/submit_btn"]'))).click()
                return google_2faSecret
                
        except:
            driver.terminate_app('com.younger.client')
            logger.debug(f'Ошибка при создании 2FA API. Повтор через 5 сек...')
            sleep(5)
    return False

# Вводим коды подтверждения 2fa
def send_codes_2fa(driver, accountEmail, google_2faSecret):
    
    for _ in range(3):
        try:
            # Тыкаем на "Получить код с почты"
            while True:
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[@resource-id="com.younger.client:id/tv_function" and @text="Получить код"]'))).click()
                    logger.debug(f"Отправил код на почту")
                    emailCode = check_inbox(accountEmail)
                    if emailCode:
                        logger.success(f"Получил код на почту: {emailCode}")
                        break
                except:
                    sleep(5)
                    pass
            
            # Вводим код с почты
            emailCode_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.EditText[@resource-id="com.younger.client:id/edit_text" and @text="Код эл. почты"]')))
            emailCode_input.click()
            sleep(1)
            emailCode_input.send_keys(emailCode)
            
            # Вводим код с 2FA Google
            google2fa_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.EditText[@resource-id="com.younger.client:id/edit_text" and @text="Код Google Authenticator"]')))
            google2fa_input.click()
            sleep(1)
            googleAuthCode = getGoogleAuthCode(google_2faSecret)
            google2fa_input.send_keys(googleAuthCode)
            
            try:
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//android.widget.EditText[@resource-id="com.younger.client:id/edit_text" and @text="Код эл. почты"]')))
            except:
                try:
                    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//android.widget.EditText[@resource-id="com.younger.client:id/edit_text" and @text="Код Google Authenticator"]')))
                except:
                    return True
            return False
        except:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.EditText[@resource-id="com.younger.client:id/edit_text" and @text="Код эл. почты"]'))).clear()
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.EditText[@resource-id="com.younger.client:id/edit_text" and @text="Код Google Authenticator"]'))).clear()
            logger.error(f"Ошибка вводов кодов. Очищаю поля")
            pass
    return False

# Получаем адрес депозита
def get_dep_addr(driver):
    for _ in range(3):
        try:
            driver.activate_app('com.younger.client')
            try:
                # Нажимаем стрелочку "Назад"
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.ImageButton[@content-desc="Перейти вверх"]'))).click()
                
                # Нажимаем стрелочку "Назад" Ещё раз
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.ImageButton'))).click()
            except:
                pass
            
            # Переходим в кошелёк
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.LinearLayout[@resource-id="com.younger.client:id/tab_bar"]/android.widget.RelativeLayout[5]'))).click()

            # Нажимаем "Депозит"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.view.View[@content-desc="Депозит"]'))).click()
            
            # Нажимаем "Внести криптовалюту"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.view.ViewGroup[@resource-id="com.younger.client:id/constraint_chain_deposit"]'))).click()

            # Нажимаем на поиск и ищем USDT
            search_coin = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.EditText')))
            search_coin.click()
            sleep(1)
            search_coin.send_keys('USDT')
            
            # Нажимаем на "USDT"
            WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, '//android.widget.ImageView[contains(@content-desc, "USDT")]'))).click()
            
            # Нажимаем на "BSC"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.view.View[contains(@content-desc, "BNB Smart Chain(BEP20)")]'))).click()

            # Сохраняем адрес пополнения
            deposit_address = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.ImageView[contains(@content-desc, "BNB SMART CHAIN(BEP20)")]')))
            deposit_address = deposit_address.get_attribute('content-desc').split('депозита‬')[1].replace('\n', '')
            logger.success(f"Успешно получил адрес депозита: {deposit_address}")
            return deposit_address
        except:
            driver.terminate_app('com.younger.client')
            logger.debug(f'Ошибка при получени адреса депозита. Повтор через 5 сек...')
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