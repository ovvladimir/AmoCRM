# https://chromium.woolyss.com/#development
# https://sites.google.com/a/chromium.org/chromedriver/downloads
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
import time
import json

start = time.strftime('%X')

# Данные для авторизации
amo = 'https://www.amocrm.ru'
amo_user = '*****@mail.ru'
amo_password = '*****'
# amo_key = '*****************************'

options = webdriver.ChromeOptions()
options.binary_location = 'chrome/chrome'
options.headless = False
# отключение всплывающих уведомлений
options.add_argument('--disable-notifications')
browser = webdriver.Chrome(executable_path='chromedriver/chromedriver',
                           options=options)
browser.implicitly_wait(10)

browser.get(amo)
# time.sleep(1)
# Авторизация
browser.find_element_by_id("page_header__auth_button").click()
username = browser.find_element_by_id("auth-email login")
username.send_keys(amo_user)
password = browser.find_element_by_id("auth-password Password")
password.send_keys(amo_password)
password.send_keys(Keys.RETURN)
# browser.find_element_by_id("form_auth__button_submit").click()
# time.sleep(3)
browser.find_element_by_id("user-select__header").click()
# time.sleep(2)

subdomain = browser.find_element_by_css_selector('a.user-select__link').text
amo_domain = 'https://' + f'{subdomain}.amocrm.ru'

cookies = browser.get_cookies()
with requests.Session() as s:
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])

    # Запрос информации о лидах
    res = s.get(f'{amo_domain}/api/v2/leads',
                params={'with': 'is_price_modified_by_robot,loss_reason_name'})
    if res.status_code == 200:
        print('-'*25, "Авторизация", '-'*25)
        print(amo_domain)
        print('status code', res.status_code)
        data = json.loads(res.content)
    else:
        print('Вы не авторизованы')

    # Получение всех id
    id_list = []
    number_id = len(data['_embedded']['items'])
    for i in range(number_id):
        id_list.append(data['_embedded']['items'][i]['id'])
    print('id_list =', id_list)
    print('-'*63)

    for id_ in range(number_id):
        # Вход на страницы с карточками клиентов
        browser.get(f'{amo_domain}/leads/detail/{id_list[id_]}')
        time.sleep(3)
        # Получение HTML-содержимого
        elem = browser.find_element_by_xpath("//*")
        html_code = elem.get_attribute("outerHTML")
        with open(f'UserID/html{id_list[id_]}.html', 'w') as fd:
            fd.write(html_code)

    browser.quit()

print('-'*9, f"started at {start} - finished at {time.strftime('%X')}", '-'*10)
