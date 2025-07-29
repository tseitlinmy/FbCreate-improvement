# Copyright: https://github.com/Mejatintiwari/FbCreator
import sys
import os
import datetime
#import threading
from queue import Queue
import requests
import random
import string
import json
import hashlib
from faker import Faker

import platform
if platform.system() == 'Windows':
    from colorama import just_fix_windows_console
    just_fix_windows_console()

print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓           
> › Github :- @jatintiwari0 
> › By      :- JATIN TIWARI
> › Proxy Support Added by @coopers-lab
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛                """)
print('\x1b[38;5;208m⇼'*60)
print('\x1b[38;5;22m•'*60)
print('\x1b[38;5;22m•'*60)
print('\x1b[38;5;208m⇼'*60+'\x1b[37m '*1)

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    # random.choice() - Returns a random item from a list, tuple, or string
    return ''.join(random.choice(letters_and_digits) for i in range(length)) 

def get_mail_domains(proxy=None):
    url = "https://api.mail.tm/domains"
    # https://docs.mail.tm/ - API for creating temporary email accounts
    try:
        response = requests.get(url, proxies=proxy)
        if response.status_code == 200:
            return response.json()['hydra:member']
        else:
            print(f'[×] E-mail Error : {response.text}')
            return None
    except Exception as e:
        print(f'[×] Error : {e}')
        return None

def generated_account_values():
    fake = Faker()
    password = fake.password()
    birthday = fake.date_of_birth(minimum_age=18, maximum_age=75)
    first_name = fake.first_name()
    last_name = fake.last_name()
    gender = random.choice(['M', 'F'])

    return password, birthday, first_name, last_name, gender

def create_mail_tm_account(password, proxy=None):
    mail_domains = get_mail_domains(proxy)
    if mail_domains:
        username = generate_random_string(10)
        domain = random.choice(mail_domains)['domain']
        url = "https://api.mail.tm/accounts"
        headers = {"Content-Type": "application/json"}
        data = {"address": f"{username}@{domain}", "password":password}       
        try:
            response = requests.post(url, headers=headers, json=data, proxies=proxy)
            if response.status_code == 201:
                return f"{username}@{domain}"
            else:
                print(f'[×] Email Error : {response.text}')
                return None
        except Exception as e:
            print(f'[×] Error : {e}')
            return None

def log_and_display(msg, fds):
    for fd in fds:
        print(msg, file=fd)

class Account_Config: pass
def get_initialized_acc_cfg():
    obj = Account_Config()
    obj.email = None
    obj.first_name = None
    obj.last_name = None
    obj.birthday = None
    obj.gender = None
    return obj

def make_account_values(proxy=None):
    if make_account_values.fd is None:
        cfg_fpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        cfg_fpath = os.path.join(cfg_fpath, "account_values.cfg")
        make_account_values.fd = open(cfg_fpath, "r")
        make_account_values.lines = make_account_values.fd.readlines()

    acc_cfg = None
    while make_account_values.idx < len(make_account_values.lines):
        line = make_account_values.lines[make_account_values.idx].strip()
        make_account_values.idx += 1
        if (not len(line)) or (line[0] == '#'):
            continue
        acc_cfg = get_initialized_acc_cfg()
        fields = line.split(',')
        for field in fields:
            idx = field.index(':') # exception on valid configuration string
            key = field[:idx].strip()
            value = field[idx + 1:].strip()
            # email: 6jM2JvLpwG@mechanicspedia.com, name: Kathy Barry, birthday: 1987-10-30, gender: F
            if key == "email":
                acc_cfg.email = value
            elif key == "name":
                i = value.find(' ')
                if i < 0:
                    acc_cfg.first_name = value
                else:
                    acc_cfg.first_name = value[:i]
                    acc_cfg.last_name = value[i+1:].strip()
            elif key == "birthday":
                acc_cfg.birthday = datetime.datetime.strptime(value, "%Y-%m-%d").date()
            elif key == "gender":
                acc_cfg.gender = value
        break

    password, birthday, first_name, last_name, gender = generated_account_values()
    birthday = birthday if (acc_cfg is None) or (acc_cfg.birthday is None) else acc_cfg.birthday
    first_name = first_name if (acc_cfg is None) or (acc_cfg.first_name is None) else acc_cfg.first_name
    last_name = last_name if (acc_cfg is None) or (acc_cfg.last_name is None) else acc_cfg.last_name
    gender = gender if (acc_cfg is None) or (acc_cfg.gender is None) else acc_cfg.gender
    email = create_mail_tm_account(password, proxy) if (acc_cfg is None) or (acc_cfg.email is None) else acc_cfg.email
    return email, password, first_name, last_name, birthday, gender

make_account_values.fd = None
make_account_values.lines = []
make_account_values.idx = 0

def register_facebook_account(email, password, first_name, last_name, birthday, gender, fds, proxy=None):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    req = {'api_key': api_key,'attempt_login': True,'birthday': birthday.strftime('%Y-%m-%d'),'client_country_code': 'EN','fb_api_caller_class': 'com.facebook.registration.protocol.RegisterAccountMethod','fb_api_req_friendly_name': 'registerAccount','firstname': first_name,'format': 'json','gender': gender,'lastname': last_name,'email': email,'locale': 'en_US','method': 'user.register','password': password,'reg_instance': generate_random_string(32),'return_multiple_errors': True}
    sorted_req = sorted(req.items(), key=lambda x: x[0])
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    ensig = hashlib.md5((sig + secret).encode()).hexdigest()
    req['sig'] = ensig
    api_url = 'https://b-api.facebook.com/method/user.register'
    reg = _call(api_url, req, proxy)
    print(req) ######### DEBUG
    id = reg['new_user_id']
    token = reg['session_info']['access_token']
    log_and_display(f'''
----------- GENERATED ACCOUNT -----------
EMAIL : {email}
ID : {id}
PASSWORD : {password}
NAME : {first_name} {last_name}
BIRTHDAY : {birthday} 
GENDER : {gender}

Token : {token}
-----------------------------------------''', fds)

def _call(url, params, proxy=None, post=True):
    headers = {'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBCR/;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'}
    if post:
        response = requests.post(url, data=params, headers=headers, proxies=proxy)
    else:
        response = requests.get(url, params=params, headers=headers, proxies=proxy)
    return response.json()

def test_proxy(proxy, q, valid_proxies):
    if test_proxy_helper(proxy):
        valid_proxies.append(proxy)
    q.task_done()

def test_proxy_helper(proxy):
    try:
        response = requests.get('https://api.mail.tm', proxies=proxy, timeout=5)
        print(f'Pass: {proxy}')
        return response.status_code == 200
    except:
        print(f'Fail: {proxy}')
        return False

def load_proxies():
    proxies = []
    with open('proxies.txt', 'r') as file:
        for line in file:
            if line[0] != '#': proxies.append(line.strip()) 
    return [{'http': f'http://{proxy}'} for proxy in proxies]

def get_working_proxies():
    proxies = load_proxies()
    if len(proxies) == 0:
        return [None]

    valid_proxies = []
    q = Queue()
    for proxy in proxies:
        q.put(proxy)
    
    for _ in range(10):  # 10 threads
        worker = threading.Thread(target=worker_test_proxy, args=(q, valid_proxies))
        worker.daemon = True
        worker.start()
    
    q.join()  # Block until all tasks are done
    return valid_proxies

def worker_test_proxy(q, valid_proxies):
    while True:
        proxy = q.get()
        if proxy is None:
            break
        test_proxy(proxy, q, valid_proxies)

working_proxies = get_working_proxies()

if not working_proxies:
    print('[×] No working proxies found. Please check your proxies.')
else:
    fds = [sys.stdout, open('username.txt', 'a')]
    for i in range(int(input('[+] How Many Accounts You Want:  '))):
        proxy = random.choice(working_proxies)
        email, password, first_name, last_name, birthday, gender =  make_account_values(proxy)
        if email and password and first_name and last_name and birthday:
            register_facebook_account(email, password, first_name, last_name, birthday, gender, fds, proxy)

print('\x1b[38;5;208m⇼'*60+'\x1b[37m '*1)
