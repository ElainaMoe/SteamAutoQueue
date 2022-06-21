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
import redis

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


if __name__ == '__main__':
    logo = r''' __ _                           _         _            ____                       
/ _\ |_ ___  __ _ _ __ ___     /_\  _   _| |_ ___     /___ \_   _  ___ _   _  ___ 
\ \| __/ _ \/ _` | '_ ` _ \   //_\\| | | | __/ _ \   //  / / | | |/ _ \ | | |/ _ \
_\ \ ||  __/ (_| | | | | | | /  _  \ |_| | || (_) | / \_/ /| |_| |  __/ |_| |  __/
\__/\__\___|\__,_|_| |_| |_| \_/ \_/\__,_|\__\___/  \___,_\ \__,_|\___|\__,_|\___|

                                                            -- Made by GamerNoTitle'''
    print(logo)
    try:
        redisURL = os.environ.get('REDIS_URL')
        if redisURL != None:
            password, host, port = redisURL.replace(
                'redis://', '').replace('@', '|').replace(':', '|').split('|')
            sql = redis.Redis(host=host, password=password,
                              port=port, ssl=True)
            cookies = json.loads(sql.get('steamCookie').decode())
            print('[SteamAutoQueue] Cookie get from Redis')
            config = {'proxy': ''}
        else:
            print('[SteamAutoQueue] Redis URL not set.')
            print(f'[SteamAutoQueue] We are trying to use the local file config.json')
            if os.path.exists('config.json'):
                with open('config.json') as file:
                    config = json.load(file)
                    if config['steam'] != {'sessionid': '', 'steamRememberLogin': '', f'steamMachineAuth{config["steam"]["steamID64"]}': '', 'steamLoginSecure': '', 'browserid': ''}:
                        cookies = {'sessionid': config['steam']['sessionid'], 'steamRememberLogin': config['steam']['steamRememberLogin'], f'steamMachineAuth{config["steam"]["steamID64"]}': config['steam']
                                   ['steamMachineAuth'], 'steamLoginSecure': config['steam']['steamLoginSecure'], 'browserid': config['steam']['browserid']}
                        print(
                            '[SteamAutoQueue] Cookie get from local file config.json')
                    else:
                        print('You need to configure your cookie first!')
                        os._exit(0)
            else:
                print(
                    '[SteamAutoQueue] Cannot found local file config.json, we are trying to use environment variable.')
                if os.environ.get('sessionid') == None or os.environ.get('steamRememberLogin') == None or os.environ.get('steamMachineAuth') == None or os.environ.get('steamLoginSecure') == None or os.environ.get('browserid') == None:
                    print(
                        '[SteamAutoQueue] No information can be found in your system variable. We will now exit.')
                    os._exit(0)
                else:
                    cookies = {'sessionid': os.environ.get('sessionid'), 'steamRememberLogin': os.environ.get('steamRememberLogin'),
                               f'steamMachineAuth{os.environ.get("steamID64")}': os.environ.get('steamMachineAuth'),
                               'steamLoginSecure': os.environ.get('steamLoginSecure'), 'browserid': os.environ.get('browserid')}
                    config = {'proxy': ''}
                    print('[SteamAutoQueue] Cookie get from environment variable')
    except Exception as e:
        print(f'[SteamAutoQueue] Cannot read config with exception {e}')
        os.exit()
    # -ignore-ssl-errors for ignore SSL Errors, or the console will be filled with them
    option = webdriver.ChromeOptions()
    option.add_experimental_option(
        "excludeSwitches", ['ignore-certificate-errors', 'ignore-ssl-errors'])
    if debug:
        if config['proxy'] != '':
            option.add_argument(
                f'--ignore-certificate-errors --proxy-server={config["proxy"]}')
        else:
            option.add_argument(f'--ignore-certificate-errors')
    else:
        if config['proxy'] != '':
            option.add_argument(
                f'headless --ignore-certificate-errors --proxy-server={config["proxy"]}')
        else:
            option.add_argument(f'headless --ignore-certificate-errors')
    if sys.platform == 'linux':     # May not work on linux, will exit abnormally
        if not os.path.exists('./chromedriver'):
            download(
                'https://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_linux64.zip', 'chromedriver.zip')
            print('[SteamAutoQueue] Unzipping chromedriver.zip')
            os.system('unzip chromedriver.zip')
            os.system('sudo rm -rf "./chromedriver.zip"')
            print('[SteamAutoQueue] Giving permission to execute.')
            os.system('sudo chmod +x "chromedriver"')
            print('[SteamAutoQueue] Moving chromedriver to ./chromedriver')
            os.system('sudo cp chromedriver /usr/bin/')
            print('[SteamAutoQueue] Installing chrome...')
            os.system('sudo apt install chrome-stable -y')
            print('[SteamAutoQueue] Done!')
        option.add_argument('blink-settings=imagesEnabled=false')
        option.add_argument('--no-sandbox')
        option.add_argument('--disable-gpu')
        option.add_argument('--disable-dev-shm-usage')
        option.add_argument('--headless')
        print('[SteamAutoQueue] Initalizing instance...')
        # browser = webdriver.Chrome(
        #     service=Service('./chromedriver'), options=option)
        browser = webdriver.Chrome(service=Service(
            '/usr/bin/chromedriver'), options=option)
        print('[SteamAutoQueue] Instance initalized.')
    elif sys.platform == 'win32':
        if not os.path.exists('./driver/chromedriver.exe'):
            download(
                'https://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_win32.zip', 'chromedriver.zip')
            print('[SteamAutoQueue] Unzipping chromedriver.zip')
            with zipfile.ZipFile('./chromedriver.zip', 'r') as chromedriver:
                chromedriver.extractall(path='./driver')
            print('[SteamAutoQueue] Deleting chromedriver.zip')
            os.system('del /q /f "chromedriver.zip"')
            print('[SteamAutoQueue] Done!')
        browser = webdriver.Chrome(
            service=Service('./driver/chromedriver.exe'), options=option)
    else:
        print(f'[SteamAutoQueue] Unsupported platform {sys.platform}')
        os._exit(0)

    # Browse Steam page
    print('[SteamAutoQueue] Trying to access steam store.')
    browser.get('https://store.steampowered.com/')
    print('[SteamAutoQueue] Successfully access steam store. Adding cookie...')
    for i in cookies:   # Must behind of get, or the browser doesn't know which website to add
        # Set cookies to get logging in
        browser.add_cookie(cookie_dict={'name': i, 'value': cookies[i]})
    print('[SteamAutoQueue] Successfully add cookie.')
    browser.refresh()

    try:
        username = browser.find_element(
            by=By.ID, value='account_pulldown').text
        print(f'[SteamAutoQueue] You have been logged in as {username}')
    except Exception as e:
        print(
            f'[SteamAutoQueue] It seems that you are not logged in. Excepted: {e}')
        os._exit(0)

    '''
    webdriver.find_element_by_* has been deprecated, use webdriver.find_element(by=By.*, value='') instead
    '''

    try:
        print('[SteamAutoQueue] Try to start the queue.')
        # browser.find_element_by_id('discovery_queue_start_link').click()
        browser.find_element(
            by=By.ID, value='discovery_queue_start_link').click()
    # When the user has already explore a queue and not spawn another
    except ElementNotInteractableException or NoSuchElementException:
        print(
            '[SteamAutoQueue] Start the queue failed, maybe you have already started a queue.')
        print('[SteamAutoQueue] We will try to spawn a new one.')
        # browser.find_element_by_id('refresh_queue_btn').click()
        # browser.find_element(
        #     by=By.CLASS_NAME, value='discover_queue_empty_refresh_btn').click()
        browser.get('https://store.steampowered.com/explore/startnew')
    nextQueueCount = 0
    while nextQueueCount <= 2:     # When the spawn button has been clicked twice
        print(f'[SteamAutoQueue] Starting Queue No.{nextQueueCount+1}')
        while True:
            try:
                # game = browser.find_element_by_id('appHubAppName').text
                link = browser.current_url
                try:
                    game = browser.find_element(
                        by=By.ID, value='appHubAppName').text
                    print(
                        f'[SteamAutoQueue] Exploring {game} with link {link}')
                    # browser.find_element_by_class_name('next_in_queue_content').click()
                    browser.find_element(
                        by=By.CLASS_NAME, value='next_in_queue_content').click()
                except NoSuchElementException:
                    agecheck = browser.find_element(
                        by=By.CLASS_NAME, value='agegate_text_container')
                    if agecheck:
                        print(
                            f'[SteamAutoQueue] Found age check when accessing {link}, skipping.')
                        browser.find_element(
                            by=By.CLASS_NAME, value='next_in_queue_content').click()
            except:
                print('[SteamAutoQueue] Queue is empty, trying to spawn a new one.')
                # browser.find_element_by_name('refresh_queue_btn').click()
                # browser.find_element(
                #     by=By.ID, value='refresh_queue_btn').click()
                browser.get('https://store.steampowered.com/explore/startnew')
                print('[SteamAutoQueue] Spawned. Now we will continue the work.')
                nextQueueCount += 1
                break
    print('[SteamAutoQueue] SteamAutoQueue\'s work has done!')
    browser.quit()
    os._exit(0)
