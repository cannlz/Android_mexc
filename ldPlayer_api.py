import subprocess
import os
from dotenv import load_dotenv
import json
from random import randint
import glob
import random
import string

load_dotenv()
LD_PATH = os.environ['LD_PATH']
LD_CONFIGS = os.environ['LD_CONFIGS']

# Создаём эмулятор
def add_emulator(name):
    try:
        command = f'{LD_PATH} add --name {name}'
        subprocess.run(command, shell=True)
        return True
    except:
        return False
    
# Открываем эмулятор
def start_emulator(name):
    try:
        command = f'{LD_PATH} launch --name {name}'
        subprocess.run(command, shell=True)
        return True
    except:
        return False
    
# Закрываем эмулятор
def stop_emulator(name):
    try:
        command = f'{LD_PATH} quit --name {name}'
        subprocess.run(command, shell=True)
        return True
    except:
        return False
    
# Список эмуляторов
def list_emulators():
    
    command = f'{LD_PATH} list2'

    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)

        # Проверяем, успешна ли команда
        if result.returncode == 0:
            output_list = result.stdout.splitlines()
            result = [item.split(',')[1] for item in output_list]
            return result
        else:
            print("Произошла ошибка list_emulators:")
            return False

    except Exception as e:
        return False
    
# Меняем настройки эмулятора
def stop_emulator(name):
    try:
        command = f'{LD_PATH} quit --name {name}'
        subprocess.run(command, shell=True)
        return True
    except:
        return False

# Меняем настройки эмулятора
def setup_emulator(name):
    random_device = random_deviceData()
    manufacturer = (str(random_device[1])).replace(' ', '_')
    model = (str(random_device[0])).replace(' ', '_')
    imei = generate_imei()
    imsi = generate_imsi()
    simserial = generate_serial_number()
    mac_addr = rand_mac()
    enable_adb()
    try:
        command = f'{LD_PATH} modify --name {name} --resolution 900,1600,320 --manufacturer {manufacturer} --model {model} --imei {imei} --imsi {imsi} --simserial {simserial} --mac {mac_addr}'
        subprocess.run(command, shell=True)
        return True
    except Exception as e:
        print(e)
        return False



# Получаем рандомные данные устройства
def random_deviceData():
    with open(f"{os.getcwd()}\\Android_mexc\\models_list.json") as fp:
        data = json.load(fp)
        questions = data["models"]
        random_index = randint(0, len(questions)-1)
        return questions[random_index]['model'], questions[random_index]['manufacturer']

# Включаем ADB
def enable_adb():
    # Шаблон для поиска файлов
    file_pattern = os.path.join(LD_CONFIGS, "leidian*.config")

    # Проходим по всем файлам, соответствующим шаблону
    for filepath in glob.glob(file_pattern):
        file_path = os.path.join(LD_CONFIGS, filepath)

        # Открываем и загружаем JSON данные
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                config_data = json.load(f)
            except json.JSONDecodeError:
                print(f"Ошибка в файле {filepath}: не удалось загрузить JSON.")
                continue

        # Проверяем наличие нужной строки
        if "basicSettings.adbDebug" not in config_data:
            # Добавляем строку
            config_data["basicSettings.adbDebug"] = 1
            
            # Сохраняем изменения обратно в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
        elif config_data["basicSettings.adbDebug"] == 0:
            # Добавляем строку
            config_data["basicSettings.adbDebug"] = 1
            
            # Сохраняем изменения обратно в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)

def checksum(number, alphabet='0123456789'):
    n = len(alphabet)
    number = tuple(alphabet.index(i)
                   for i in reversed(str(number)))
    return (sum(number[::2]) +
            sum(sum(divmod(i * 2, n))
                for i in number[1::2])) % n

def calc_check_digit(number, alphabet='0123456789'):
    check_digit = checksum(number + alphabet[0])
    return alphabet[-check_digit]

# Генерация imei
def generate_imei():
    imei = ''
    while len(imei) < 14:
        imei += str(random.randint(0, 9))

    imei += calc_check_digit(imei)
    return imei

# Генерация imsi
def generate_imsi(mcc=None, mnc=None):
    # Default MCC and MNC if not provided
    if mcc is None:
        mcc = '310'  # Example: USA
    if mnc is None:
        mnc = '260'  # Example: T-Mobile USA

    # Generate a random MSIN (9 or 10 digits)
    msin_length = 10  # Commonly MSIN length is 10 digits
    msin = ''.join(random.choices('0123456789', k=msin_length))

    # Construct the IMSI
    imsi = f"{mcc}{mnc}{msin}"
    return imsi

# generate simserial
def generate_serial_number(length=10):
    """Generate a random serial number of specified length."""
    
    # Define the characters to use in the serial number
    characters = string.ascii_uppercase + string.digits
    
    # Generate a random serial number
    serial_number = ''.join(random.choice(characters) for _ in range(length))
    
    return serial_number

# Генерация MAC адреса
def rand_mac():
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )


list_emulators()