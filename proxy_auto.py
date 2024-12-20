from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
from loguru import logger


# Руутер прокси
def proxy_rooter(proxy_ip, proxy_port, proxy_user, proxy_pass, first_run):
    
    driver = mobile_connect(first_run)
    if add_proxy(driver, proxy_ip, proxy_port, proxy_user, proxy_pass):
        if connect_proxy(driver):
            driver.background_app(-1) # Переводим приложение в фоновый режим
            driver.close()
            return True
        else:
            return False
    else:
        return False

# Добавляем прокси
def add_proxy(driver, proxy_ip, proxy_port, proxy_user, proxy_pass):
    for _ in range(3):
        try:
            driver.activate_app('com.scheler.superproxy')
            # Проверяем наличие прокси
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.view.View[@content-desc="No proxies available."]'))).click()
            except:
                return True
            
            # Кнопка "Добавить прокси"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@content-desc="Add proxy"]'))).click()
            
            # Стаим "HTTPS"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.EditText[@text="SOCKS5"]'))).click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View[1]/android.view.View/android.view.View[2]/android.widget.EditText[3]'))).click()
            
            # Стаим "Авторизацию"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.EditText[@text="None"]'))).click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.view.View[@content-desc="Username/Password"]'))).click()
            
            # Вводим данные
            ip_filed = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View[1]/android.view.View/android.view.View[2]/android.widget.EditText[3]')))
            port_filed = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View[1]/android.view.View/android.view.View[2]/android.widget.EditText[4]')))
            login_filed = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View[1]/android.view.View/android.view.View[2]/android.widget.EditText[6]')))
            password_filed = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View[1]/android.view.View/android.view.View[2]/android.widget.EditText[7]')))
            
            ip_filed.click()
            sleep(1)
            ip_filed.send_keys(proxy_ip)
            
            port_filed.click()
            sleep(1)
            port_filed.send_keys(proxy_port)
            
            login_filed.click()
            sleep(1)
            login_filed.send_keys(proxy_user)
            
            password_filed.click()
            sleep(1)
            password_filed.send_keys(proxy_pass)
            
            # Сохраняем настройки
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.FrameLayout[@resource-id="android:id/content"]/android.widget.FrameLayout/android.view.View/android.view.View/android.view.View/android.view.View[1]/android.view.View/android.view.View[1]/android.widget.Button[2]'))).click()
                        
            return True
        except:
            driver.terminate_app('com.scheler.superproxy')
            logger.debug(f'Ошибка при добавлении проксей')
            sleep(5)
    return False

# Подключаемся к прокси
def connect_proxy(driver):
    for _ in range(3):
        try:
            driver.activate_app('com.scheler.superproxy')
        except:
            pass
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.view.View[contains(@content-desc, "Default Profile")]'))).click()
        except:
            pass
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//android.widget.Button[@content-desc="Start"]'))).click()
            return True
        except:
            driver.terminate_app('com.scheler.superproxy')
            logger.debug(f'Ошибка при подключении к прокси')
            sleep(5)
    return False
    
# Подключение драйвера
def mobile_connect(first_run):
    if first_run:
        capabilities = {
            'platformName': 'Android',
            'deviceName': 'emulator-5558',
            'automationName': 'UiAutomator2',
            'noReset': True,
            'app': 'C:\\Users\\Cannl\\Downloads\\super-proxy-2-5-3.apk'
        }
    else:
        capabilities = {
            'platformName': 'Android',
            'deviceName': 'emulator-5558',
            'automationName': 'UiAutomator2',
            'noReset': True
        }
    return webdriver.Remote('http://localhost:4723/wd/hub', options=UiAutomator2Options().load_capabilities(capabilities))

