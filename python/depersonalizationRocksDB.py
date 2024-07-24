import os
import subprocess
import re
import json
import requests
import binascii

# Скрипт для обезличивания данных в БД RocksDB, который по ходу изменяет данные и в БД (с выключенной службой приложения)

path_database = r'...' #полный путь к базе данных приложения
admin_login = 'pochta@mail.ru' # любое доменное имя сервера для замены
admin_name = '...'  # логин администратора в крокотайм по умолчанию
url = '...'  # Адрес Crocotime Server
token = '...' # api-токен сервера



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

IDS = [] #список айдишников сотрудников (исключает айди администратора)

for admin in resp['items']:
    list_ids = admin['employee_id']
    IDS.append(list_ids)

tmp = open("temp.txt", "w+")

get_path_of_dir = os.getcwd()
path = os.path.join(get_path_of_dir, 'ldb32.exe')
tmp_file = os.path.join(get_path_of_dir, 'temp.txt')

cmd = f'{path} --db={path_database} --column_family=accounts scan --value_hex'
output = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout

bytes_admin_Login = str.encode(admin_login)
str_hex_Login_admin = '0x' + str(binascii.hexlify(bytes_admin_Login), encoding="utf-8")

sorted_logins = re.findall(r".*login.*", output)
sorted_first_name = re.findall(r".*first_name.*", output)
sorted_second_name = re.findall(r".*second_name.*", output)
sorted_emails = re.findall(r".*email.*", output)


temp_logins = open('temp.txt', 'w')

for id in IDS:
    for small_data in sorted_logins:
        id += 1
        logins = re.sub(r":.*$",f"username_{id} ", f"{small_data}")
        loginList = re.findall(r'username_[0-9]+', logins)
        str_logins = ''.join(loginList)
        bytes_logins = str.encode(str_logins)
        str_hex_logins = '0x' + str(binascii.hexlify(bytes_logins), encoding="utf-8")
        login = re.sub(r"username_[0-9]+",f"{str_hex_logins}", logins)
        temp_logins.write(login)
    break

temp_logins.close()
end_logins = open('temp.txt', 'r')
final_logins = end_logins.read()
match = re.compile('.*000001.login 0x\w*')
for mathcing in final_logins:
    final_logins = match.sub(f'00000001.login {str_hex_Login_admin}', final_logins)


cmd_logins = f'{path} --db={path_database} --column_family=accounts --value_hex batchput {final_logins}'
output_logins = subprocess.run(cmd_logins)
end_logins.close()


temp_first_names = open('temp.txt', 'w')
for id in IDS:
    for small_data in sorted_first_name:
        id += 1
        first_name = re.sub(r":.*$",f"username_{id} ", f"{small_data}")
        firstnamesList = re.findall(r'username_[0-9]+', first_name)
        str_first_names = ''.join(firstnamesList)
        bytes_first_names = str.encode(str_first_names)
        str_hex_first_names = '0x' + str(binascii.hexlify(bytes_first_names), encoding="utf-8")
        first_name = re.sub(r"username_[0-9]+",f"{str_hex_first_names}", first_name)
        temp_first_names.write(first_name)
    break

temp_first_names.close()
end_first_names = open('temp.txt', 'r')
final_first_names = end_first_names.read()


cmd_first_names = f'{path} --db={path_database} --column_family=accounts --value_hex batchput {final_first_names}'
output_first_name = subprocess.run(cmd_first_names)
end_first_names.close()


temp_second_names = open('temp.txt', 'w')
for id in IDS:
    for small_data in sorted_second_name:
        id += 1
        second_name = re.sub(r":.*$",f"secondname_{id} ", f"{small_data}")
        secondnamesList = re.findall(r'secondname_[0-9]+', second_name)
        str_second_names = ''.join(secondnamesList)
        bytes_second_names = str.encode(str_second_names)
        str_hex_second_names = '0x' + str(binascii.hexlify(bytes_second_names), encoding="utf-8")
        second_name = re.sub(r"secondname_[0-9]+",f"{str_hex_second_names}", second_name)
        temp_second_names.write(second_name)
    break

temp_second_names.close()
end_second_names = open('temp.txt', 'r')
final_second_names = end_second_names.read()

cmd_second_names = f'{path} --db={path_database} --column_family=accounts --value_hex batchput {final_second_names}'
output_second_name = subprocess.run(cmd_second_names)
end_second_names.close()


temp_email = open('temp.txt', 'w')
for id in IDS:
    for small_data in sorted_emails:
        id += 1
        email = re.sub(r":.*$",f"email_{id}@example.com ", f"{small_data}")
        emailList = re.findall(r'email_[0-9]@example.com', email)
        str_emaillist = ''.join(emailList)
        bytes_emails = str.encode(str_emaillist)
        str_hex_emails = '0x' + str(binascii.hexlify(bytes_emails), encoding="utf-8")
        email = re.sub(r"email_[0-9]@example.com",f"{str_hex_emails}", email)
        temp_email.write(email)
    break

temp_email.close()
end_emails = open('temp.txt', 'r')
final_emails = end_emails.read()
match = re.compile('.*000001.email 0x\w*')
for mathcing in final_emails:
    final_emails = match.sub(f'00000001.email {str_hex_Login_admin}', final_emails)

cmd_emails = f'{path} --db={path_database} --column_family=accounts --value_hex batchput {final_emails}'
output_emails = subprocess.run(cmd_emails)
end_emails.close()

cmd_computers = f'{path} --db={path_database} --column_family=computers scan --value_hex'
output_computers = subprocess.run(cmd_computers, check=True, capture_output=True, text=True).stdout
sorted_names = re.findall(r"\w\w\w\w\w\w\w\w.name.*", output_computers)

temp_names = open('temp.txt', 'w')
for id in IDS:
    for small_data in sorted_names:
        id += 1
        names = re.sub(r":.*$",f"computer_{id} ", f"{small_data}")
        namesList = re.findall(r'computer_[0-9]', names)
        str_names = ''.join(namesList)
        names = re.sub(r"computer_[0-9]",f"{str_names}", names)
        temp_names.write(names)
    break

temp_names.close()
end_names = open('temp.txt', 'r')
final_names = end_names.read()

cmd_names = f'{path} --db={path_database} --column_family=computers batchput {final_names}'
output_names = subprocess.run(cmd_names)
end_names.close()

cmd_departments = f'{path} --db={path_database} --column_family=departments scan --value_hex'
output_departments = subprocess.run(cmd_departments, check=True, capture_output=True, text=True).stdout
sorted_display_names = re.findall(r".*display_name.*", output_departments)

temp_display_names = open('temp.txt', 'w')
for id in IDS:
    for small_data in sorted_display_names:
        id += 1
        department = re.sub(r":.*$",f"department_{id} ", f"{small_data}")
        displaynamesList = re.findall(r'department_[0-9]', department)
        str_display_names = ''.join(displaynamesList)
        department = re.sub(r"department_[0-9]",f"{str_display_names}", department)
        temp_display_names.write(department)
    break

temp_display_names.close()
end_display_names = open('temp.txt', 'r')
final_display_names = end_display_names.read()

cmd_display_names = f'{path} --db={path_database} --column_family=departments batchput {final_display_names}'
output_display_names = subprocess.run(cmd_display_names)
end_display_names.close()


cmd_domains = f'{path} --db={path_database} --column_family=domains scan --value_hex'
output_domains = subprocess.run(cmd_domains, check=True, capture_output=True, text=True).stdout
sorted_domains_names = re.findall(r"\w\w\w\w\w\w\w\w.name.*", output_domains)

temp_domain_names = open('temp.txt', 'w')
for id in IDS:
    for small_data in sorted_domains_names:
        id += 1
        names = re.sub(r":.*$",f"domain_{id} ", f"{small_data}")
        namesList = re.findall(r'domain_[0-9]', names)
        str_names = ''.join(namesList)
        names = re.sub(r"domain_[0-9]",f"{str_names}", names)
        temp_domain_names.write(names)
    break

temp_domain_names.close()
end_domain_names = open('temp.txt', 'r')
final_domain_names = end_domain_names.read()

cmd_domain_names = f'{path} --db={path_database} --column_family=domains batchput {final_domain_names}'

output_domain_names = subprocess.run(cmd_domain_names)
end_domain_names.close()

cmd_employees = f'{path} --db={path_database} --column_family=employees scan --value_hex'
output_employees = subprocess.run(cmd_employees, check=True, capture_output=True, text=True).stdout
sorted_employee_fnames = re.findall(r".*first_name.*", output_employees)
sorted_employee_emails = re.findall(r".*email.*", output_employees)
sorted_employee_passwords = re.findall(r".*password.*", output_employees)

temp_employee_fnames = open('temp.txt', 'w')
for id in IDS:
    for small_data in sorted_employee_fnames:
        id += 1
        first_name = re.sub(r":.*$",f"username_{id} ", f"{small_data}")
        firstnamesList = re.findall(r'username_[0-9]+', first_name)
        str_first_names = ''.join(firstnamesList)
        bytes_first_names = str.encode(str_first_names)
        str_hex_first_names = '0x' + str(binascii.hexlify(bytes_first_names), encoding="utf-8")
        first_name = re.sub(r"username_[0-9]+",f"{str_hex_first_names}", first_name)
        temp_employee_fnames.write(first_name)
    break

temp_employee_fnames.close()
end_employee_fnames = open('temp.txt', 'r')
final_employee_fnames = end_employee_fnames.read()


cmd_employee_fnames = f'{path} --db={path_database} --column_family=employees --value_hex batchput {final_employee_fnames}'
output_employee_fnames = subprocess.run(cmd_employee_fnames)
end_employee_fnames.close()


temp_e_emails = open('temp.txt', 'w')

for id in IDS:
    for small_data in sorted_employee_emails:
        id += 1
        email = re.sub(r":.*$",f"email_{id}@example.com ", f"{small_data}")
        emailList = re.findall(r'email_[0-9]@example.com', email)
        str_email = ''.join(emailList)
        bytes_email = str.encode(str_email)
        str_hex_logins = '0x' + str(binascii.hexlify(bytes_email), encoding="utf-8")
        email = re.sub(r"email_[0-9]@example.com",f"{str_hex_logins}", email)
        temp_e_emails.write(email)
    break

temp_e_emails.close()
end_e_emails = open('temp.txt', 'r')
final_e_emails = end_e_emails.read()
match = re.compile('.*000001.email 0x\w*')
for mathcing in final_e_emails:
    final_e_emails = match.sub(f'00000001.email {str_hex_Login_admin}', final_e_emails)


cmd_e_emails = f'{path} --db={path_database} --column_family=employees --value_hex batchput {final_e_emails}'
output_e_emails = subprocess.run(cmd_e_emails)
end_e_emails.close()

temp_passwords = open('temp.txt', 'w')
for id in IDS:
    for small_data in sorted_employee_passwords:
        password = re.sub(r":.*$",f"0x ", f"{small_data}")
        passwordList = re.findall(r'.', password)
        str_password = ''.join(passwordList)
        temp_passwords.write(str_password)
    break

temp_passwords.close()
end_passwords = open('temp.txt', 'r')
final_passwords = end_passwords.read()

cmd_passwords = f'{path} --db={path_database} --column_family=employees --value_hex batchput {final_passwords}'
output_passwords = subprocess.run(cmd_passwords)
end_passwords.close()

cmd_paths = f'{path} --db={path_database} --column_family=pathes scan --value_hex'
output_paths = subprocess.run(cmd_paths, check=True, capture_output=True, text=True).stdout
sorted_uri = re.findall(r".*uri.*", output_paths)
sorted_params = re.findall(r".*parameters.*", output_paths)

temp_params = open('temp.txt', 'w')
for id in IDS:
    for small_data in sorted_params:
        params = re.sub(r":.*$",f"0x ", f"{small_data}")
        paramsList = re.findall(r'.', params)
        params_str = ''.join(paramsList)
        temp_params.write(params_str)
    break

temp_params.close()
end_params = open('temp.txt', 'r')
final_params = end_params.read()

cmd_params = f'{path} --db={path_database} --column_family=pathes --value_hex batchput {final_params}'
output_params = subprocess.run(cmd_params)
end_params.close()

temp_uri = open('temp.txt', 'w')
for id in IDS:
    for small_data in sorted_uri:
        uri = re.sub(r":.*$",f"0x ", f"{small_data}")
        uriList = re.findall(r'.', uri)
        uri_str = ''.join(uriList)
        temp_uri.write(uri_str)
    break

temp_uri.close()
end_uri = open('temp.txt', 'r')
final_uri = end_uri.read()

cmd_uri = f'{path} --db={path_database} --column_family=pathes --value_hex batchput {final_uri}'
output_uri = subprocess.run(cmd_uri)
end_uri.close()
