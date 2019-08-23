# py -3.7-64 -m pip install arrow
# py -3.7-64 -m pip install pydantic
# py -3.7-64 -m pip install aiohttp
# py -3.7-64 -m pip install pandas
# py -3.7-64 -m pip install html5lib
# py -3.7-64 -m pip install lxml
# py -3.7-64 -m pip install beautifulsoup4
# py -3.7-64 -m pip install requests
# py -3.7-64 -m pip install selenium
# C:\Users\BOB\AppData\Local\pyppeteer\pyppeteer\local-chromium\575458

from datetime import datetime
from pprint import pprint
import json
import arrow
import requests

# Subdomain AmoCRM
amo_domain = 'https://*****.amocrm.ru'
# Login AmoCRM
amo_user = '*****@mail.ru'
# Key API
amo_key = '****************************'

today = arrow.now().format('YYYY-MM-DD HH:mm:ss')
print(today)
state = {
    'cookies': None
}


# Авторизация
def auth(user, user_hash):
    url = amo_domain + '/private/api/auth.php'
    data = {
        'USER_LOGIN': user,
        'USER_HASH': user_hash
    }
    res = s.post(url, data=data, params={'type': 'json'})

    print('status code', res.status_code)

    if res.status_code == 200:
        state['cookies'] = res.cookies
        return res.json()


with requests.Session() as s:
    auth_result = auth(amo_user, amo_key)
    pprint(auth_result)

    print('-'*15, 'Запрос параметра аккаунта', '-'*15)
    res = s.get(f'{amo_domain}/api/v2/account',  # cookies=state['cookies']
                params={'with': 'pipelines,groups,note_types,task_types'})  # params={'with': 'users&free_users=Y'})
    if res.status_code == 200:
        data = res.json()
    pprint(data)

    print('-'*15, 'Запрос информации о лидах', '-'*15)
    res = s.get(f'{amo_domain}/api/v2/leads')
    # params={'with': 'is_price_modified_by_robot,loss_reason_name'})
    data = res.json()
    pprint(data)

    print('-'*15, 'Запрос информации о диалогах', '-'*15)
    res = s.get(f'{amo_domain}/api/v2/notes',
                params={'type': 'message_paragraph'})
    # params={'type': 'contact/lead/company/task'}  # params={'id': 6599375}
    data = res.json()
    pprint(data)

    print('-'*15, 'ONLINE ЧАТЫ', '-'*15)
    res = s.get(f'{amo_domain}/private/api/v2/json/accounts/current',
                params={'amojo': 'Y'})
    data = res.json()
    pprint(data)
