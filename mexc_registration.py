from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
from loguru import logger


# Добавляем прокси
def type_authData():

    driver = mobile_connect()
    
    
    for _ in range(3):
        try:
            driver.activate_app('com.younger.client')
            
            # Закрываем рекламу при первом запуске
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[@resource-id="com.younger.client:id/tv_skip"]'))).click()
            except:
                pass
            
            # Даём права на доступ к файлам
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@resource-id="com.android.packageinstaller:id/permission_allow_button"]'))).click()
            except:
                pass
            
            # Закрываем все окошки на главной
            while True:
                try:
                    # Нажимаем "Больше никаких напоминаний на сегодня"
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.CheckBox[@resource-id="com.younger.client:id/checkbox"]'))).click()
                    # Закрываем всю рекламу
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.ImageView[@resource-id="com.younger.client:id/iv_close"]'))).click()
                except:
                    break
            
            # Переходим в меню(человечек слева сверху) и нажимаем кнопку "Регистрация"
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.ImageView[@resource-id="com.younger.client:id/iv_user_center_collapse"]'))).click()
            
            for _ in range(2):
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@resource-id="com.younger.client:id/btn_register"]'))).click()
                except:
                    pass
            
            
            # Регистрация аккаунта
            login_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//android.widget.EditText[@class='android.widget.EditText' and @index='3']")))
            login_input.click()
            sleep(1)
            login_input.send_keys('hogan-zine0g@icloud.com')
            
            password_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//android.widget.EditText[@class='android.widget.EditText' and @index='4']")))
            password_input.click()
            sleep(1)
            password_input.send_keys('')
            
            # Нажимаем "Зарегистрироваться"
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//android.view.View[@class='android.view.View' and @content-desc='Зарегистрироваться' and @clickable='true']"))).click()

        
            sleep(15)
            print(driver.contexts)
            #driver.switch_to.context('WEBVIEW_1')
            print(driver.page_source)
            sleep(2222)
        except:
            driver.terminate_app('com.younger.client')
            logger.debug(f'Ошибка при регистрации аккаунта. Повтор через 5 сек...')
            sleep(5)
    return False



# Подключение драйвера
def mobile_connect():
    capabilities = {
        'platformName': 'Android',
        'deviceName': 'emulator-5558',
        'automationName': 'UiAutomator2',
        'noReset': True,
        'app': 'C:\\Users\\Cannl\\Downloads\\MEXC.apk'
    }
    return webdriver.Remote('http://localhost:4723/wd/hub', options=UiAutomator2Options().load_capabilities(capabilities))


type_authData()