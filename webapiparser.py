import codecs
import hashlib
import json
import os
import csv
import sys
import requests
from pprint import pprint

# парсер из веб-приложения, который парсит данные о сотрудниках по подразделениям из json 

# initial data
uri = 'http://172.25.181.211'  # Server URI
port = ':8085'
login = '_@gmail.com'  # Admin Email
passw = 'root'  # Admin Pass
token = 'cf15af024e0022e81e80434ef58ad271debb72ab6bd630d3faf6d98f802a66a5'
url = uri + port

# string to MD5
passHash = hashlib.md5(passw.encode("utf-8")).hexdigest()

# Login to get the cookie for
logonBody = {
    "controller": "LogonController",
    "query": {
        "user": {
            "login": login,
            "password": passHash
        }
    },
    "subsystems": [
        {
            "uuid": "hidden",
            "app_version": "5.8.17"
        }
    ],
    "app_version": "5.8.17"
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url=url, headers=headers, data=json.dumps(logonBody))
dataresponse = response.text

    # save session token
jsonresponse = json.loads(dataresponse)
token_session = jsonresponse['result']['session']

    # тело запроса для Domain_accounts (WebAPI)
requestDomainAcc = {
    "controller": "BatchProcessing",
    "session": token_session,
    "query": {
        "items": [
            {
                "name": "AccountTree",
                "controller": "account_tree",
                "params": {
                    "name_filter": {
                        "name": ""
                    }
                }
            }
        ]
    }
}

acc_response = requests.post(url=url, headers=headers, data=json.dumps(requestDomainAcc))
pprint(acc_response.text)


    # Создаем/очищаем, заполняем CSV-файл (domain_acc_parsed.csv)

filepath = os.path.join(r'C:\Windows\Temp', 'domain_acc_parsed.csv')
with open("domain_acc_parsed.csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(
        ['employee_id', 'display_name', 'login', 'last_activity_utc_time', 'is_enabled']
    )
    deps_parsed = file
    #def collect_data():
    # получаем список сотрудников и OU от "api_departments" в json-формате
api_departments = {
    "controller": "api_departments",
    "server_token": token,
    "query": {
        "items": [
            {
                "department_id": "",
                "display_name": "",
                "is_enabled": "",
                "items": [
                    {
                        "employee_id": "",
                        "first_name": "",
                        "second_name": "",
                        "is_enabled": ""
                    }
                ]
            }
         ]
     }
}

dep_response = requests.post(url=url, headers=headers, data=json.dumps(api_departments))
api_deps = json.loads(dep_response.text)

api_deps_json = os.path.join(r'C:\Windows\Temp', 'api_deps.json')
with open('api_deps.json', 'w') as api_deps_data:
    json.dump(dep_response.json(), api_deps_data, indent=4, ensure_ascii=False)

api_deps_parsed = os.path.join(r'C:\Windows\Temp', 'api_deps_parsed.csv')
with open("api_deps_parsed.csv", "w") as csvdeps:
    writer = csv.writer(csvdeps)

ENCODING_ANSI = '1251'

class Parser:

    def __init__(self, separator=',', fio_to_second=True):
        self.fio_to_second = fio_to_second
        self.separator = separator
        self.result = self.separator.join(['department', 'Id', 'first_name', 'second_name', 'is_enabled', '\r\n'])

    def parse_item(self, data, parent_department):
        if 'items' in data:
            if 'display_name' in data:
                parent_department += ('' if parent_department == '' else '\\') + data['display_name']
            if 'items' in data:
                for item in data['items']:
                    self.parse_item(item, parent_department)
        elif 'employee_id' in data:
            self.result += self.separator.join([
                parent_department,
                str(data['employee_id']),
                (data['first_name'] if not self.fio_to_second or data['second_name'] else data['second_name']),
                (data['second_name'] if not self.fio_to_second or data['second_name'] else data['first_name']),
                ('enabled' if str(data['is_enabled']) == '1' else 'disabled'),
                '\r\n'])



if __name__ == "__main__":
    src_file = api_deps_data.name
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    if os.path.normpath(os.path.basename(src_file)) == os.path.normpath(src_file):
        src_file = os.path.join(cur_dir, src_file)
    f = codecs.open(src_file, mode='r', encoding=ENCODING_ANSI)
    parent_department = ''
    content = f.read()
    data = json.loads(content)
    f.close()
    parser = Parser()
    parser.parse_item(data, parent_department)
    dst_file = csvdeps.name
    if os.path.normpath(os.path.basename(dst_file)) == os.path.normpath(dst_file):
        os.path.join(cur_dir, dst_file)
    f = codecs.open(dst_file, mode='w', encoding=ENCODING_ANSI)
    f.write(parser.result)
    f.flush()
    f.close()

# f-файл - api_deps_parsed.csv

api_employee = {

    "controller": "api_employees",
    "server_token": token,
    "query": {
        "items": [
            {

                "employee_id": "",
                "display_name": "",
                "first_name": "",
                "second_name": "",
                "email": "",
                "privilege": "",
                "time_zone": "",
                "parent_group_id": ""
            }
        ]
    }
}

employee_response = requests.post(url=url, headers=headers, data=json.dumps(api_employee))
api_ER = json.loads(employee_response.text)
pprint(api_ER)

api_deps_json = os.path.join(r'C:\Windows\Temp', 'api_employee.json')
with open('api_employee.json', 'w') as api_empl:
    json.dump(employee_response.json(), api_empl, indent=4, ensure_ascii=False)

api_empl_parsed = os.path.join(r'C:\Windows\Temp', 'api_employees_parsed.csv')
with open("api_employees_parsed.csv", "w") as emplparsed:
    writer = csv.writer(emplparsed)
