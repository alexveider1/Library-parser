import library_parser

import os
import requests
import tqdm
from time import sleep
from time import perf_counter
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Tuple
from termcolor import colored

if __name__ == 'main':
    # Программа
    init()
    start = perf_counter()
    temporary, downloads = path()
    login, password, url = auth()
    if "znanium" in url:
        znanium(login, password, url)
    if "urait" in url:
        urait(login, password, url)
    if "lan" in url:
        lan(login, password, url)
        print("Эта библиотека еще не поддерживается")
    if "prospekt" in url:
        prospekt(login, password, url)
        print("Эта библиотека еще не поддерживается")
    else:
        print("Данная ЭБС не поддерживается")
    create_pdf(temporary, downloads)
    delete_extra(temporary)
    end = perf_counter()
    print(
        f"Работа программы завершена. Время работы программы: {round(end-start, 1)} секунд. Окно закроется через 10 секунд. Файл с книгой сохранен по пути {os.path.join(downloads, 'Итог.pdf')}"
    )
    sleep(10)
