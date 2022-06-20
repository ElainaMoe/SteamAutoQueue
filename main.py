from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import sys
import requests as r
from tqdm import tqdm
import os
import zipfile
import json

# Debug mode, set true to show chrome window, false to hide it
debug = False

def download(url: str, fname: str, headers: dict = {}):
    resp = r.get(url, stream=True, headers=headers)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


if os.path.exists('config.json'):
    with open('config.json') as file:
        config = json.load(file)
else:
    config = json.loads(os.environ.get('CONFIG'))
    if config == '':
        print('You need to configure the config first!')
        os._exit(0)

if __name__ == '__main__':
    logo = r''' __ _                           _         _            ____                       
/ _\ |_ ___  __ _ _ __ ___     /_\  _   _| |_ ___     /___ \_   _  ___ _   _  ___ 
\ \| __/ _ \/ _` | '_ ` _ \   //_\\| | | | __/ _ \   //  / / | | |/ _ \ | | |/ _ \
_\ \ ||  __/ (_| | | | | | | /  _  \ |_| | || (_) | / \_/ /| |_| |  __/ |_| |  __/
\__/\__\___|\__,_|_| |_| |_| \_/ \_/\__,_|\__\___/  \___,_\ \__,_|\___|\__,_|\___|
                                                     -- Made by GamerNoTitle      '''
    print(logo)
    # -ignore-ssl-errors for ignore SSL Errors, or the console will be filled with them
    option = webdriver.ChromeOptions()
    option.add_experimental_option("excludeSwitches", ['ignore-certificate-errors','ignore-ssl-errors'])
    if debug:
        if config['proxy'] != '':
            option.add_argument(f'--ignore-certificate-errors --proxy-server={config["proxy"]}')
        else:
            option.add_argument(f'--ignore-certificate-errors')
    else:
        if config['proxy'] != '':
            option.add_argument(f'headless --ignore-certificate-errors --proxy-server={config["proxy"]}')
        else:
            option.add_argument(f'headless --ignore-certificate-errors')
    if config['steam'] != {'sessionid': '', 'steamRememberLogin': '', f'steamMachineAuth{config["steam"]["steamID64"]}': '', 'steamLoginSecure': '', 'browserid': ''}:
        cookies = {'sessionid': config['steam']['sessionid'], 'steamRememberLogin': config['steam']['steamRememberLogin'], f'steamMachineAuth{config["steam"]["steamID64"]}': config['steam']
                  ['steamMachineAuth'], 'steamLoginSecure': config['steam']['steamLoginSecure'], 'browserid': config['steam']['browserid']}
    else:
        print('You need to configure your cookie first!')
        os._exit(0)
    if sys.platform == 'linux':
        if not os.path.exists('./driver/chromedriver'):
            download(
                'https://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_linux64.zip', 'chromedriver.zip')
            os.system('unzip chromedriver.zip')
            os.system('sudo rm -rf "./chromedriver.zip"')
            os.system('sudo chmod +x "chromedriver"')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-gpu')
        browser = webdriver.Chrome(
            service=Service('./chromedriver'), options=option)
    elif sys.platform == 'win32':
        if not os.path.exists('./driver/chromedriver.exe'):
            download(
                'https://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_win32.zip', 'chromedriver.zip')
            with zipfile.ZipFile('./chromedriver.zip', 'r') as chromedriver:
                chromedriver.extractall(path='./driver')
            os.system('del /q /f "chromedriver.zip"')
        browser = webdriver.Chrome(
            service=Service('./driver/chromedriver.exe'), options=option)
    else:
        print(f'Unsupported platform {sys.platform}')
        os._exit(0)

    # Browse Steam page
    browser.get('https://store.steampowered.com/')
    for i in cookies:   # Must behind of get, or the browser doesn't know which website to add
        browser.add_cookie(cookie_dict={'name': i, 'value': cookies[i]})    # Set cookies to get logging in
    browser.refresh()

    '''
    webdriver.find_element_by_* has been deprecated, use webdriver.find_element(by=By.*, value='') instead
    '''

    try:
        print('Try to start the queue.')
        # browser.find_element_by_id('discovery_queue_start_link').click()
        browser.find_element(by=By.ID, value='discovery_queue_start_link').click()
    except ElementNotInteractableException or NoSuchElementException:     # When the user has already explore a queue and not spawn another
        print('Start the queue failed, maybe you have already started a queue.')
        print('We will try to spawn a new one.')
        # browser.find_element_by_id('refresh_queue_btn').click()     
        browser.find_element(by=By.ID, value='refresh_queue_btn').click()
    nextQueueCount = 0
    if nextQueueCount != 2:     # When the spawn button has been clicked twice
        while True:
            try:
                # game = browser.find_element_by_id('appHubAppName').text
                link = browser.current_url
                try:
                    game = browser.find_element(by=By.ID, value='appHubAppName').text
                    print(f'Exploring {game} with link {link}')
                    # browser.find_element_by_class_name('next_in_queue_content').click()
                    browser.find_element(by=By.CLASS_NAME, value='next_in_queue_content').click()
                except NoSuchElementException:
                    agecheck = browser.find_element(by=By.CLASS_NAME, value='agegate_text_container')
                    if agecheck:
                        print(f'Found age check when accessing {link}, skipping.')
                        browser.find_element(by=By.CLASS_NAME, value='next_in_queue_content').click()
            except:
                print('Queue is empty, trying to spawn a new one.')
                # browser.find_element_by_name('refresh_queue_btn').click()
                browser.find_element(by=By.ID, value='refresh_queue_btn').click()
                print('Spawned. Now we will continue the work.')
                nextQueueCount += 1
                break
    else:
        print('SteamAutoQueue\'s work has done!')
    browser.quit()
    os._exit(0)
