import json
import requests

# Деперсонализация айдишников и email методом POST в веб-приложении

admin_name = '...'  # имя администратора по умолчанию в веб-приложении
url = '...'  # Адрес сервера
token = '...' # api-токен сервера
FAKE_MAIL_SERVER = '@example.local' # любое доменное имя сервера для замены


headers = {
    "Content-Type": "application/json"
}

# получаем данные сотрудников с контроллера "api_employees" в json-формате
api_employee = {

    "controller": "api_employees",
    "server_token": token,
    "query": {
        "items": [
            {

                "email": "",
                "first_name": "",
                "second_name": "",

            }
        ]
    }
}

employee_response = requests.post(url=url, headers=headers, data=json.dumps(api_employee),verify=False)
apiresponse = json.loads(employee_response.text)

pa_api = requests.post(url=url, headers=headers, data=json.dumps(api_employee),verify=False)
resp = json.loads(pa_api.text)

IDs = [] #список айдишников сотрудников (исключает айди администратора)

for admin in resp['items']:
    list_ids = admin['employee_id']
    IDs.append(list_ids)
    if admin['first_name'] == admin_name:
        a = admin['employee_id']
        IDs.remove(a)

for changingIDs in IDs:
    new_email = "username_" + str(changingIDs) + FAKE_MAIL_SERVER
    set_email_body = {
        "server_token": token,
        "controller": "WorkspaceActionController",
        "query": {
            "params": {
                "filter": {
                    "employee_id": changingIDs
                },
                "record": {
                    "email": new_email
                }
            },
            "action": "update",
            "domain": "employees"
        }
    }
    to_set_email = requests.post(url=url, headers=headers, data=json.dumps(set_email_body),verify=False)
    set_firstname_body = {
        "server_token": token,
        "controller": "WorkspaceActionController",
        "query": {
            "params": {
                "filter": {
                    "employee_id": changingIDs
                },
                "record": {
                    "first_name": str(changingIDs)
                }
            },
            "action": "update",
            "domain": "employees"
        }
    }
    to_set_firstname = requests.post(url=url, headers=headers, data=json.dumps(set_firstname_body),verify=False)
    set_second_name_body = {
        "server_token": token,
        "controller": "WorkspaceActionController",
        "query": {
            "params": {
                "filter": {
                    "employee_id": changingIDs
                },
                "record": {
                    "second_name": "username"
                }
            },
            "action": "update",
            "domain": "employees"
        }
    }
    to_set_second_name = requests.post(url=url, headers=headers, data=json.dumps(set_second_name_body),verify=False)


myfile = open('temp.txt', 'w')



for id in IDS:
    for small_data in data:
        id += 1
        logins = re.sub(r":.*$",f" username_{id}\n", f"{small_data}")
        print(logins)
        myfile.write(logins,)
    break

myfile.close()

print('Выполнено')





