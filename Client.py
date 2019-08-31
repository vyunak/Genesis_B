from flask import Flask
from flask import request
import time
import hashlib
import random
import json
import pymysql
from pymysql.cursors import DictCursor
import hashlib
app = Flask(__name__)

connection = pymysql.connect(
    host='185.148.82.46',
    user='admin_blockchain',
    password='blockchain',
    db='admin_blockchain',
    charset='utf8',
    cursorclass=DictCursor
)

def get_public(pubkey):
    sha_pub = hashlib.sha256()
    sha_pub.update(pubkey.encode('utf-8'))
    return sha_pub.hexdigest()

def mkprivkey():
    key = hashlib.sha256()
    key.update(str(random.randrange(1, 10e77, 1)).encode('utf-8'))
    return key.hexdigest()

def check_balance_fun(str):
    with connection.cursor() as cursor:
        connection.ping(reconnect=True)
        cursor.execute('SELECT * FROM transaction WHERE public_key = %s', (str))
        t1 = cursor.fetchall()
        sum = 0
        for row in t1:
            sum -= row['amount']
        connection.ping(reconnect=True)
        cursor.execute('SELECT * FROM transaction WHERE to_whom_public = %s', (str))
        t2 = cursor.fetchall()
        for row in t2:
            sum += row['amount']
        return (sum)

def generate_hash(prev_hash, public_key, amount, to_whom_public, time):
    hash = hashlib.sha256()
    hash.update(prev_hash.encode('utf-8'))
    hash.update(public_key.encode('utf-8'))
    hash.update(amount.encode('utf-8'))
    hash.update(to_whom_public.encode('utf-8'))
    hash.update(time.encode('utf-8'))
    return hash.hexdigest()

def check_genesis():
    with connection.cursor() as cursor:
        connection.ping(reconnect=True)
        cursor.execute('SELECT * FROM transaction')
        all = cursor.fetchall()
        for row in all:
            if (row['prev_hash'] != "NULL"):
                if hash_tmp != row['prev_hash']:
                    return 0
                hash_tmp = row['hash']
            else:
                hash_tmp = row['hash']
            hash = generate_hash(row['prev_hash'], row['public_key'], str(row['amount']), row['to_whom_public'], str(row['time_stmp']))
            if hash != row['hash']:
                return 0
    return 1

def zero_block_genesis():
    with connection.cursor() as cursor:
        connection.ping(reconnect=True)
        res = cursor.execute('SELECT * FROM `transaction` WHERE `public_key` = "GENESIS_BLOCK"')
        if res == 0:
            to_whom = "a3dc0ddc3f37ac02d3e4f815866ac31f146c148c81d844bdf09b55b7832dd95a"
            timestamp = str(int(time.time()))
            last_h = generate_hash("NULL", "GENESIS_BLOCK", str(float("100000")), to_whom,
                                   timestamp);
            connection.ping(reconnect=True)
            cursor.execute(
                'INSERT INTO `transaction` (`prev_hash`, `public_key`, `amount`, `to_whom_public`, `to_whom_amount`, `time_stmp`, `hash`) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                ("NULL", "GENESIS_BLOCK", str(float("100000")), to_whom, str(float("100000")),
                 timestamp, last_h))
            connection.commit()
            print("Genesis block created!")
        else:
            print("Genesis already created!")
    with connection.cursor() as cursor:
        connection.ping(reconnect=True)
        res1 = cursor.execute('SELECT * FROM `users` WHERE `login` = "Demo"')
        if res1 == 0:
            connection.ping(reconnect=True)
            cursor.execute(
                'INSERT INTO `users` (`login`, `password`, `privat_key`, `public_key`) VALUES (%s, %s, %s, %s)',
                ("Demo", "Demo", "615e80a1adbe14e6ee49919b3d82cb4861c00b8ceadd8bf8dfe56a74a01f4695", "a3dc0ddc3f37ac02d3e4f815866ac31f146c148c81d844bdf09b55b7832dd95a"))
            connection.commit()
            print("Demo user created!")
        else:
            print("User already created!")

@app.route('/white_paper', methods=['POST'])
def white_paper():
    if (check_genesis() == 1):
        return "The blockchain chain is not broken!"
    with connection.cursor() as cursor:
        connection.ping(reconnect=True)
        cursor.execute('DELETE FROM `users`')
        cursor.execute('DELETE FROM `transaction`')
        cursor.execute('ALTER TABLE `users` auto_increment = 1;')
        cursor.execute('ALTER TABLE `transaction` auto_increment = 1;')
        connection.ping(reconnect=True)
        connection.commit()
    zero_block_genesis()
    return "Operation finished!\nGenesis block and Demo user generated!"

@app.route('/check_balance', methods=['POST'])
def check_balance():
    p_k = request.form.get('public_key')
    return str(check_balance_fun(p_k))

@app.route('/block_info', methods=['POST'])
def block_info():
    connection.ping(reconnect=True)
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM `transaction` WHERE `hash` = %s', request.form.get('hash'))
    return json.dumps(cursor.fetchone())

@app.route('/login', methods=['POST'])
def login():
    data = {}
    data['login'] = request.form.get('login')
    data['password'] = request.form.get('password')
    with connection.cursor() as cursor:
        connection.ping(reconnect=True)
        req = cursor.execute('SELECT * FROM users WHERE login = %s AND password = %s', (data['login'], data['password']))
        if req == 0:
            return json.dumps(0)
        else:
            return json.dumps(cursor.fetchone())

@app.route('/register', methods=['POST'])
def register():
    data = {}
    data['login'] = request.form.get('login')
    data['password'] = request.form.get('password')
    with connection.cursor() as cursor:
        connection.ping(reconnect=True)
        req = cursor.execute('SELECT * FROM users WHERE login = %s', data['login'])
        if req == 1:
            return json.dumps(0)
        else:
            connection.ping(reconnect=True)
            g_privatekey = mkprivkey()
            g_pubkey = get_public(g_privatekey)
            cursor.execute('INSERT INTO `users` (`login`, `password`, `privat_key`, `public_key`) VALUES (%s, %s, %s, %s)',(data['login'], data['password'], g_pubkey, g_privatekey))
            connection.commit()
            return json.dumps({'private_key': g_privatekey, 'public_key': g_pubkey})

@app.route('/make_tranaction', methods=['POST'])
def make_tranaction():
    re_message = {'message': 'Wrong private key!'}
    tmp = request.form.get('tmp')
    tmp = json.loads(tmp)
    connection.ping(reconnect=True)
    if (check_genesis() == 0):
        return json.dumps({'message': 'error'})
    if float(tmp['amount']) > check_balance_fun(tmp['public_key']):
        re_message['message'] = 'Incorrect amount!'
    elif tmp['public_key'] == get_public(tmp['private_key']):
        connection.ping(reconnect=True)
        with connection.cursor() as cursor:
            connection.ping(reconnect=True)
            timestamp = str(int(time.time()))
            last_h = generate_hash(json.loads(last_hash())['hash'], tmp['public_key'], str(float(tmp['amount'])), tmp['to_whom'],
                                   timestamp);
            cursor.execute(
                'INSERT INTO `transaction` (`prev_hash`, `public_key`, `amount`, `to_whom_public`, `to_whom_amount`, `time_stmp`, `hash`) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (json.loads(last_hash())['hash'], tmp['public_key'], str(float(tmp['amount'])), tmp['to_whom'], str(float(tmp['amount'])),
                 timestamp, last_h))
            connection.commit()
            re_message['message'] = 'Transaction success!'
    return json.dumps(re_message)

@app.route('/all_tranaction', methods=['POST'])
def all_tranaction():
    str = request.form.get('public_key')
    with connection.cursor() as cursor:
        connection.ping(reconnect=True)
        cursor.execute('SELECT * FROM transaction WHERE public_key = %s', (str))
        t1 = cursor.fetchall()
        connection.ping(reconnect=True)
        cursor.execute('SELECT * FROM transaction WHERE to_whom_public = %s', (str))
        t2 = cursor.fetchall()
    if not t2 and not t1:
        return json.dumps(0)
    elif not t1:
        return json.dumps(t2)
    elif not t2:
        return json.dumps(t1)
    else:
        return json.dumps(t1 + t2)


@app.route('/last_hash', methods=['POST'])
def last_hash():
    with connection.cursor() as cursor:
        connection.ping(reconnect=True)
        cursor.execute('SELECT `hash` FROM `transaction` ORDER BY id DESC LIMIT 1')
    return json.dumps(cursor.fetchone())

app.run()
