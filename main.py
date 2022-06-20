from selenium import webdriver
import sys
import requests as r
from tqdm import tqdm
import os
import zipfile


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
    if sys.platform == 'linux':
        download(
            'https://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_linux64.zip', 'chromedriver.zip')
        with zipfile.ZipFile('./chromedriver.zip', 'r') as chromedriver:
            chromedriver.extractall(path='./driver')
        os.system('rm -rf "./chromedriver"')
        os.system('chmod +x "./driver/*"')
        browser = webdriver.Chrome(executable_path='./driver/chromedriver')
    elif sys.platform == 'win32':
        download('https://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_win32.zip', 'chromedriver.zip')
        with zipfile.ZipFile('./chromedriver.zip', 'r') as chromedriver:
            chromedriver.extractall(path='./driver')
        os.system('del /q /f "chromedriver.zip"')
        browser = webdriver.Chrome(executable_path='./driver/chromedriver.exe')
    else:
        print(f'Unsupported platform {sys.platform}')
        os._exit(0)

    browser.get('https://www.baidu.com')
    browser.add_cookie()