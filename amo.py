import requests
from pprint import pprint
import arrow

# Subdomain AmoCRM
amo_domain = 'https://*****.amocrm.ru'
# Login AmoCRM
amo_user = '*****@mail.ru'
# Key API
amo_key = '***************'

today = arrow.now().format('YYYY-MM-DD HH:mm:ss')
print(today)
state = {'cookies': None}


# Обработка вывода
def output_processing(item, level=0, path=[]):
    path_str = " > ".join(map(str, path))
    if isinstance(item, dict):
        print(f"[dict  {path_str}")
        for key, val in item.items():
            output_processing(val, level+1, [*path, key])
    elif isinstance(item, list):
        print(f"[list  {path_str}")
        for i, val in enumerate(item):
            output_processing(val, level+1, [*path, i])
    else:
        print(f'|      {path_str}={str(item)}')


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
    # output_processing(auth_result)

    print('-'*15, 'Запрос параметра аккаунта', '-'*15)
    res = s.get(f'{amo_domain}/api/v2/account',  # cookies=state['cookies']
                params={'with': 'pipelines,groups,note_types,task_types'})  # params={'with': 'users&free_users=Y'})
    if res.status_code == 200:
        data = res.json()
        # pprint(data)
        output_processing(data)

    print('-'*15, 'Запрос информации о лидах', '-'*15)
    res = s.get(f'{amo_domain}/api/v2/leads')
    # params={'with': 'is_price_modified_by_robot,loss_reason_name'})
    if res.status_code == 200:
        data = res.json()
        # pprint(data)
        output_processing(data)

    print('-'*15, 'Запрос информации о диалогах', '-'*15)
    res = s.get(f'{amo_domain}/api/v2/notes',  # ?id=22037173&type=lead)
                params={'element_id': 3113639, 'type': 'lead'})
    # params={'id': 22037173, 'type': 'lead'}
    # params={'type': 'lead'}
    # params={'type': 'message_paragraph'}
    # params={'type': 'contact/lead/company/task'} или
    if res.status_code == 200:
        data = res.json()
        dt = [data['_embedded']['items'][i]['text']
              for i, word in enumerate(data['_embedded']['items'])
              if 'text' in word]
        print(dt)
        # pprint(data)
        output_processing(data)

    print('-'*15, 'GET ЗАДАЧИ', '-'*15)
    date_to = arrow.utcnow().timestamp
    res = s.get(f'{amo_domain}/api/v2/tasks?filter[date_create][from]=1564703999&filter[date_create][to]={date_to}')
    # ?filter[status][]=0
    if res.status_code == 200:
        data = res.json()
        output_processing(data)
    else:
        print(res.status_code)

    print('-'*15, 'POST ЗАДАЧИ', '-'*15)
    res = s.post(f"{amo_domain}/api/v2/tasks",
                 json={
                    "add": [{
                        "element_id": "3113639",
                        "element_type": "2",
                        "complete_till_at": "1567321200",
                        "task_type": "1",
                        "text": "ПроверкаПроверкаПроверка"
                    }]
                 })
    if res.status_code == 200 or res.status_code == 204:
        data = res.json()
        output_processing(data)
    else:
        print(res.status_code)

    '''
    print('-'*15, 'ONLINE ЧАТЫ', '-'*15)
    res = s.get(f'{amo_domain}/private/api/v2/json/accounts/current',
                params={'amojo': 'Y'})
    if res.status_code == 200:
        data = res.json()
        # pprint(data)
        output_processing(data)
    '''
'''
with open('data.txt', 'w') as fd:
        fd.write(str(data))
'''
