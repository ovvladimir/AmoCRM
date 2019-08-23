# python amocrm.py --domain ***** --login *****@mail.ru --password *****
from selenium import webdriver
from tqdm import tqdm
import requests
import argparse
import arrow
from flask import Flask

import time
import json

app = Flask(__name__)


@app.route('/', methods=['Get', 'Post'])
def request_context():
    start = arrow.now().format('YYYY-MM-DD HH:mm:ss')
    contentsDictJsonALL = {}

    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--domain", required=True, help=" ")
    ap.add_argument("-l", "--login", required=True, help=" ")
    ap.add_argument("-p", "--password", required=True, help=" ")
    args = vars(ap.parse_args())

    # Данные для авторизации
    amo_domain = f'https://{args["domain"]}.amocrm.ru'
    amo_user = args["login"]
    amo_password = args["password"]

    options = webdriver.ChromeOptions()
    options.binary_location = 'chrome/google-chrome'
    options.headless = True
    browser = webdriver.Chrome(executable_path='chromedriver/chromedriver',
                               options=options)
    browser.implicitly_wait(10)
    try:
        browser.get(amo_domain)
    except Exception as e:
        browser.quit()
    else:
        # Авторизация
        username = browser.find_element_by_name("username")
        password = browser.find_element_by_name("password")
        username.send_keys(amo_user)
        password.send_keys(amo_password)
        try:
            browser.find_element_by_id("auth_submit").click()
        except Exception as e:
            browser.quit()
        else:
            time.sleep(1)

            cookies = browser.get_cookies()
            amo = 'https://' + cookies[1]["domain"]

    with requests.Session() as s:
        for cookie in cookies:
            s.cookies.set(cookie["name"], cookie["value"])

        # Запрос информации о лидах
        try:
            res = s.get(f'{amo_domain}/api/v2/leads')
        except Exception as e:
            browser.quit()
        else:
            if res.status_code == 200:
                # print('-'*25, "Авторизация", '-'*25)
                # print('status code', res.status_code)
                # print(f'domain: {amo}')
                data = json.loads(res.content)
            else:
                # print('Вы не авторизованы')
                browser.quit()

            # Получение всех id
            id_list = []
            number_id = len(data['_embedded']['items'])
            for i in range(number_id):
                id_list.append(data['_embedded']['items'][i]['id'])
            # print('id_list =', id_list)
            # print('-'*63)

        for id_ in tqdm(range(number_id)):
            # Вход на страницы с карточками клиентов
            try:
                browser.get(f'{amo_domain}/leads/detail/{id_list[id_]}')
            except Exception as e:
                break
            else:
                time.sleep(5)
            # Получение HTML-содержимого
            try:
                contents = browser.find_element_by_class_name('notes-wrapper__notes')
                # .get_attribute('innerText') или .text к предыдущей строке
            except Exception as e:
                break
            else:
                contentsList = contents.text.split('\n')
                contentsDict = {
                    'Upload Date': start, 'id': id_list[id_],
                    'start of correspondence': contentsList[0],
                    'inbox': [contentsList[index+2] for index, word in enumerate(contentsList)
                              if word == 'кому:' and contentsList[index+1] == 'всем '],
                    'outbox': [contentsList[index+2] for index, word in enumerate(contentsList)
                               if word == 'кому:' and contentsList[index+1] != 'всем ']
                    }
                contentsDictJson = json.dumps(contentsDict, ensure_ascii=False)
                contentsDictJsonALL[id_list[id_]] = contentsDict
                '''with open(f'UserID/{id_list[id_]}.txt', 'w') as w:
                    w.write(str(contentsDictJson))'''
    contentsALL = json.dumps(contentsDictJsonALL, ensure_ascii=False)
    browser.quit()
    # print('-'*4, f"started at {start} - finished at {time.strftime('%X')}", '-'*4)
    return contentsALL


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
