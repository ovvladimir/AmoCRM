import json
import requests
import time
import arrow
from pprint import pprint

start = arrow.now().format('YYYY-MM-DD HH:mm:ss')

# Domain
amocrm_domain = 'https://*****.amocrm.ru'
# Login
amocrm_user = '*****@mail.ru'
# API key
amocrm_key = '**********************************'
cookie = {'cookies': None}


# Авторизация
def auth(user, key):
    url = f'{amocrm_domain}/private/api/auth.php'
    data = {'USER_LOGIN': user, 'USER_HASH': key}
    r = s.post(url, data=data, params={'type': 'json'})

    print('authorization status', r.status_code)

    if r.status_code == 200:
        cookie['cookies'] = r.cookies
        return r.json()


with requests.Session() as s:
    result = auth(amocrm_user, amocrm_key)
    pprint(result)

    print('-'*25, 'Запрос параметра аккаунта', '-'*25)
    r = s.get(f'{amocrm_domain}/api/v2/account',  # cookies=cookie['cookies']
              params={'with': 'pipelines,groups,note_types,task_types'})
    # params={'with': 'users&free_users=Y'})
    if r.status_code == 200:
        print('-'*25, 'Авторизация', '-'*25)
        data = r.json()
    pprint(data)

    print('-'*25, 'Запрос информации о лидах', '-'*25)
    r = s.get(f'{amocrm_domain}/api/v2/leads')
    # params={'with': 'is_price_modified_by_robot,loss_reason_name'})
    data = r.json()
    pprint(data)

    print('-'*25, 'Запрос информации о диалогах', '-'*25)
    r = s.get(f'{amocrm_domain}/api/v2/notes',
              params={'type': 'message_paragraph'})
    # params={'type': 'contact/lead/company/task'}  # params={'id': 6599375}
    data = r.json()
    pprint(data)

    print('-'*25, 'ONLINE ЧАТЫ', '-'*25)
    r = s.get(f'{amocrm_domain}/private/api/v2/json/accounts/current',
              params={'amojo': 'Y'})
    data = r.json()
    pprint(data)

print('-'*10, f"started at {start} - finished at {time.strftime('%X')}", '-'*10)
