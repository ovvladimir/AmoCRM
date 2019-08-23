# https://digitalgod.be/guides/amocrm_initialization
# py -3.7-64 -m pip install -U git+https://github.com/madiedinro/rodin_helpers_py -q
# py -3.7-64 -m pip install arrow
# py -3.7-64 -m pip install pydantic
# py -3.7-64 -m pip install aiohttp
# py -3.7-64 -m pip install pandas
# py -3.7-64 -m pip install html5lib
# py -3.7-64 -m pip install lxml
# py -3.7-64 -m pip install beautifulsoup4
# py -3.7-64 -m pip install requests
# py -3.7-64 -m pip install requests_html - удален
# py -3.7-64 -m pip install selenium
# simplech - только папка
# C:\Users\BOB\AppData\Local\pyppeteer\pyppeteer\local-chromium\575458

# набор полезных функций для вывода данных
# import rodin_helpers as rh
# Стандатные классы даты и времени
from datetime import datetime
# Модуль для с методами для итеративной обработки данных
from itertools import count
# Вывод данные в структурированном виде
from pprint import pprint
# Стандартный пакет для работы с json
import json
# альтернативный пакет для работы с данными
import arrow
# библиотека для работы с http
import requests
# from simplech import ClickHouse

# import warnings
# from arrow.factory import ArrowParseWarning
# warnings.simplefilter("ignore", ArrowParseWarning)

# Subdomain AmoCRM
amo_domain = 'https://ovvladimir.amocrm.ru'
# Login AmoCRM
amo_user = 'ov.vladimir@mail.ru'
# Key API
amo_key = '519312ab2e0b6baa74731b5774c91319eb35b3e4'

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
    # rh.walk(auth_result, limit_list=1)

    print('-'*15, 'Запрос параметра аккаунта', '-'*15)
    res = s.get(f'{amo_domain}/api/v2/account',  # cookies=state['cookies']
                params={'with': 'pipelines,groups,note_types,task_types'})  # params={'with': 'users&free_users=Y'})
    if res.status_code == 200:
        data = res.json()
    pprint(data)
    # rh.walk(data)

    print('-'*15, 'Запрос информации о лидах', '-'*15)
    res = s.get(f'{amo_domain}/api/v2/leads')
    # params={'with': 'is_price_modified_by_robot,loss_reason_name'})
    data = res.json()
    pprint(data)
    # rh.walk(data)

    print('-'*15, 'Запрос информации о диалогах', '-'*15)
    res = s.get(f'{amo_domain}/api/v2/notes',
                params={'type': 'message_paragraph'})
    # params={'type': 'contact/lead/company/task'}  # params={'id': 6599375}
    data = res.json()
    pprint(data)
    # rh.walk(data)

    print('-'*15, 'ONLINE ЧАТЫ', '-'*15)
    res = s.get(f'{amo_domain}/private/api/v2/json/accounts/current',
                params={'amojo': 'Y'})
    data = res.json()
    pprint(data)
    # rh.walk(data, limit_list=1)

'''
    notes - выгржаешь все примечания (можно задать фильтр
    curl_setopt($curl, CURLOPT_HTTPHEADER, array('IF-MODIFIED-SINCE: Mon, 01 Aug 2017 08:12:22'));
    ) и по id сделки отбираешь свои

    # datetimes в RFC2616
    tim = datetime.strptime('Thu, 08 Aug 2019 08:00:00', '%a, %d %b %Y %H:%M:%S')
    print(tim)
'''

'''
orig_deals = data['_embedded']['items']


def format_deal(deal):
    fields = {f['name'].lower(): f['values'][0].get('value') for f in deal['custom_fields']}
    date = datetime.fromtimestamp(deal['closed_at'],)
    return {
        'id': deal['id'],
        'uid': fields.get('uid') or '',
        'cid': fields.get('cid') or '',
        'sale': deal['sale'],
        'date': date.strftime('%Y-%m-%d'),
        'date_time': date.strftime('%Y-%m-%d %H:%M:%S'),
        'account_id': deal['account_id']
    }

deal = format_deal(orig_deals[0])
pprint(deal)

deals = [format_deal(d) for d in orig_deals]

###

ch = ClickHouse()
td = ch.discover('deals', deals)
td
td.date('date').idx('account_id', 'date').metrics('sale')
schema = td.merge_tree()
print(schema)

ch.run("""
CREATE TABLE IF NOT EXISTS deals (
  date Date,
  date_time DateTime,
  id UInt64,
  account_id UInt64,
  uid String,
  cid String,
  sale Int64
) ENGINE = MergeTree() PARTITION BY toYYYYMM(date) ORDER BY (id, date) SETTINGS index_granularity=8192
""")
with ch.table('deals') as c:
    for deal in deals:
        c.push(deal)
rh.print_rows([*ch.objects_stream('SELECT * FROM deals LIMIT 10')])
'''
