# Библиотеки
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


# Функции
def init() -> None:
    """Функция для приветствия пользователя программой `Library parser`. С помощью `Library parser` можно скачивать книги в формате `.pdf` из популярных российский ЭБС."""
    print(f"Вас приветствует программа {colored('`Library parser`', 'blue')}!")


def path() -> Tuple[str, str]:
    """Создает две папки в пути `downloads`: `temporary` и `downloads` для временных файлов и итогового файла соответственно. Возвращает адресса этих папок."""
    downloads = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Downloads")
    try:
        temporary = os.path.join(downloads, "temp")
        os.mkdir(temporary)
    except FileExistsError:
        print("Путь уже существует, все файлы оттуда будут удалены")
    finally:
        os.chdir(temporary)
    return (temporary, downloads)


def auth() -> Tuple[str, str, str]:
    """Функция собирает данные о пользователе для дальнейшей авторизации. Возвращает `login`, `password`, `url`, которые ввел пользователь. Все три возвращаемых результата имеют тип `str`."""
    login = input("Введите логин:\n")
    password = input("Введите пароль:\n")
    url = input("Введите ссылку на книгу:\n")
    return login, password, url


def save_image_from_binary(binary_data, filename) -> None:
    """Функция сохраняет изображение по байтам по пути `filename`."""
    with open(filename, mode="wb") as file:
        file.write(binary_data)


def create_pdf(temporary: str, downloads: str) -> None:
    """Функция создает файл `.pdf` в `downloads` из временных файлов в директории `temporary`."""
    images = []
    pages = [i for i in os.listdir(temporary) if "Result" in i]
    pages = sorted(pages, key=lambda x: os.path.getmtime(os.path.join(temporary, x)))
    for i in pages:
        images.append(Image.open(os.path.join(temporary, str(i))))
    images = [img.convert("RGB") for img in images]
    # Создаем общий файл pdf #
    os.chdir(downloads)
    images[0].save(
        f"Итог.pdf", "PDF", append_images=images[1 : len(images) : 1], save_all=True
    )


def delete_extra(temporary: str) -> None:
    """Функция удаляет все временные файлы в директории `temporary`."""
    os.chdir(temporary)
    for i in os.listdir(temporary):
        os.remove(os.path.join(temporary, str(i)))


def znanium(login: str, password: str, url: str) -> None:
    """Функция для парсинга сайта `Znanium`."""
    id = url.split("id=")[-1]
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=2560,1440")
    options.page_load_strategy = "eager"
    with webdriver.Chrome(options=options) as driver:
        driver.get("https://znanium.ru/site/login")
        sleep(10)
        log_1 = driver.find_element(By.ID, "loginform-username")
        log_2 = driver.find_element(By.ID, "loginform-password")
        log_1.click()
        log_1.send_keys(login)
        log_2.click()
        log_2.send_keys(password)
        btn = driver.find_element(By.CLASS_NAME, "btn")
        btn.click()
        sleep(5)
        driver.get(url=url)
        sleep(10)
        try:
            x = driver.find_element(By.CLASS_NAME, "book-labels__item").text.strip()
            print(x.capitalize())
        except NoSuchElementException:
            print("Книга не доступна в вашей подписке")
        if x != "в подписке":
            print("Книга не доступна в вашей подписке")
            print("Надо купить подписку")
            exit(1)
        driver.get(url=f"https://znanium.ru/read?id={id}")
        sleep(30)
        page_selector = driver.find_element(By.ID, "page")
        total_pages = int(
            driver.find_element(By.CLASS_NAME, "pages__all").text.split("/")[-1].strip()
        )
        for i in tqdm.tqdm(range(1, total_pages + 1)):
            sleep(4)
            page_selector.clear()
            page_selector.send_keys(str(i))
            page_selector.send_keys(Keys.ENTER)
            sleep(4)
            el = driver.find_element(By.ID, f"bookreadcont{i}")
            el.screenshot(f"Result-{i}.png")


def urait(login: str, password: str, url: str) -> None:
    """Функция для парсинга сайта `Urait`."""
    r = requests.get(url)
    if r.status_code == 200:
        print("Получаем информацию о книге...")
    book_name = (
        BeautifulSoup(r.text, "html.parser")
        .find(class_="page-content-head__title book_title")
        .text
    )
    book_pages = int(
        BeautifulSoup(r.text, "html.parser")
        .find(class_="book-about-produce__info")
        .text
    )
    print(f"Название книги: {book_name}", f"Число страниц: {book_pages}", sep="\n")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=3840,2160")
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://urait.ru/viewer/{url.split(r'/')[-1]}#page/{1}")
    sleep(3)
    button = driver.find_element(By.ID, "viewer__header__auth")
    button.click()
    sleep(3)
    auth_1 = driver.find_element(By.ID, "email")
    auth_1.send_keys(login)
    sleep(3)
    auth_2 = driver.find_element(By.ID, "password")
    auth_2.send_keys(password)
    sleep(3)
    button_ = driver.find_element(By.CLASS_NAME, "button-orange")
    button_.click()
    sleep(3)
    # создание скриншота каждой страницы книги/учебника
    flag = True
    for i in tqdm.tqdm(range(1, book_pages + 1)):
        sleep(3)
        driver.get(f"https://urait.ru/viewer/{url.split(r'/')[-1]}#page/{i}")
        sleep(3)
        if flag:
            flag = False  # в первый раз долго ждем полной прогрузки страницы
            el = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, f"page_{i}"))
            )
            el.screenshot(f"Result-{i}.png")
            sleep(5)
        else:
            el = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, f"page_{i}"))
            )
            el.screenshot(f"Result-{i}.png")


def lan(login: str, password: str, url: str) -> None:
    """Функция для парсинга сайта `Lanbook`."""
    pass


def prospekt(login: str, password: str, url: str) -> None:
    """Функция для парсинга сайта `Prospekt`."""
    pass
