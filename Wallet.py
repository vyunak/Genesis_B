import json
import requests
import time
import hashlib

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    GREEN = '\033[42m'
    CYAN = '\033[46m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CBLACKBG = '\33[40m'
    CREDBG = '\33[41m'
    CGREENBG = '\33[42m'
    CYELLOWBG = '\33[43m'
    CBLUEBG = '\33[44m'
    CVIOLETBG = '\33[35m'
    CBEIGEBG = '\33[46m'
    CWHITEBG = '\33[47m'
    CGREYBG = '\33[100m'
    CGREEN = '\33[32m'

def get_public(pubkey):
    sha_pub = hashlib.sha256()
    sha_pub.update(pubkey.encode('utf-8'))
    return sha_pub.hexdigest()

def white_paper():
    print("The chick of the blockchain has been broken.")
    print("Inclusion of white paper operation!")
    input("Press any key to start...")
    print("The operation will start in 3 sec...")
    time.sleep(1)
    print("The operation will start in 2 sec...")
    time.sleep(1)
    print("The operation will start in 1 sec...")
    time.sleep(1)
    b = 0
    hash = get_public("-1")
    while 1:
        hash = get_public(hash)
        time.sleep(0.1)
        print(hash)
        if b >= 42:
            break
        b += 1
    print("Deleting all...")
    time.sleep(0.3)
    time.sleep(0.3)
    data = requests.post("http://localhost:5000/white_paper")
    return data.text

def check_balance(pub_key):
    data = requests.post("http://localhost:5000/check_balance", data={'public_key': pub_key})
    return data.text

def block_info(hash):
    data = requests.post("http://localhost:5000/block_info", data={'hash': hash})
    return data.text

def all_tranaction(pub_key):
    data = requests.post("http://localhost:5000/all_tranaction", data={'public_key': pub_key})
    return data.text

def make_tranaction(user):
    arr = {}
    arr['amount'] = input("Amount: ")
    if arr['amount'].replace('.', '').isdigit() == 0:
        print("Error amount!")
        input("Press any button...")
        wallet(user)
    arr['private_key'] = input("Private key: ")
    if len(arr['private_key']) != 64:
        print("Error len private key!")
        input("Press any button...")
        wallet(user)
    arr['public_key'] = user['public_key']
    if len(arr['public_key']) != 64:
        print("Error len public key!")
        input("Press any button...")
        wallet(user)
    arr['to_whom'] = input("To whom: ")
    if len(arr['to_whom']) != 64:
        print("Error len whom public key!")
        input("Press any button...")
        wallet(user)
    data = requests.post("http://localhost:5000/make_tranaction", data={'tmp': json.dumps(arr)})
    return data.text


def last_hash():
    data = requests.post("http://localhost:5000/last_hash")
    return json.loads(data.text)

def wallet(user):
    print(bcolors.BOLD +"\nMAIN MENU"+ bcolors.ENDC)
    print(bcolors.CGREYBG +"1) Check Balance"+ bcolors.ENDC)
    print(bcolors.CGREYBG  +"2) Block Info"+ bcolors.ENDC)
    print(bcolors.CGREYBG +"3) Last hash"+ bcolors.ENDC)
    print(bcolors.CGREYBG +"4) All Trancaction"+ bcolors.ENDC)
    print(bcolors.CGREYBG +"5) Make Trancaction"+ bcolors.ENDC)
    print(bcolors.CGREYBG +"6) Logout"+ bcolors.ENDC)
    print("\n")
    print(bcolors.UNDERLINE +"Your public key:", user['public_key']+ bcolors.ENDC)
    chose = input(bcolors.BOLD + "Chose operation: "+ bcolors.ENDC)
    if chose == '1':
        print("\n1) My balance")
        print("2) By public_key")
        print("3) Back to menu")
        balance_v = input(bcolors.BOLD + "Chose operation: "+ bcolors.ENDC)
        if balance_v == '1':
            print("Your balance is:", check_balance(user['public_key']))
            input("Press any button...")
            wallet(user)
        elif balance_v == '2':
            pub_key = input("Write public key: ")
            if len(pub_key) != 64:
                print("Error len public key!")
                input("Press any button...")
                wallet(user)
            print("Balance is:", check_balance(pub_key))
            input("Press any button...")
            wallet(user)
        else:
            wallet(user)
    elif chose == '2':
        hash = input("Write hash by block: ")
        info = json.loads(block_info(hash))
        if info == None:
            print("Block doesn't not exist!")
            input("Press any button...")
            wallet(user)
        print("\nPrevious hash:", info['prev_hash'])
        print((bcolors.UNDERLINE+ "From: {}"+bcolors.ENDC).format(info['public_key']))
        print((bcolors.BOLD+"Amount: {}"+ bcolors.ENDC).format(info['amount']))
        print("To whom:", info['to_whom_public'])
        print("Time:", info['time_stmp'])
        print("Hash:", info['hash'])
        input("\nPress any button...")
        wallet(user)
    elif chose == '3':
        print("Last hash:", last_hash()['hash'])
        input("Press any button...")
        wallet(user)
    elif chose == '4':
        print("1) My transaction")
        print("2) Transaction by public key")
        vn = input(bcolors.BOLD + "Chose operation: "+ bcolors.ENDC)
        # if vn == 2 and len(vn) != 64:
        #     print("Error len public key!")
        #     input("Press any button...")
        #     wallet(user)
        if vn == '1':
            info = all_tranaction(user['public_key'])
            info = json.loads(info)
            if info == None:
                print("Internal server error!")
                input("Press any button...")
                wallet(user)
            elif info == 0:
                print("\nPublic key don't have transactions!\n")
                input("Press any button...")
                wallet(user)
            for row in info:
                print(
                    "\nFrom: {1}, Amount: {2},\nTime: {4}, Previous hash: {0},\nTo whom: {3}, Block hash: {5}\n".format(
                        row['prev_hash'], row['public_key'], row['amount'], row['to_whom_public'], row['time_stmp'],
                        row['hash']))
            input("\nPress any button...")
            wallet(user)
        elif vn == '2':
            info = all_tranaction(input("Write public key: "))
            info = json.loads(info)
            if info == None:
                print("Internal server error!")
                input("Press any button...")
                wallet(user)
            elif info == 0:
                print("\nPublic key don't have transactions!\n")
                input("Press any button...")
                wallet(user)
            for row in info:
                print(
                    "\nFrom: {1}, Amount: {2},\nTime: {4}, Previous hash: {0},\nTo whom: {3}, Block hash: {5}\n".format(
                        row['prev_hash'], row['public_key'], row['amount'], row['to_whom_public'], row['time_stmp'],
                        row['hash']))
            input("\nPress any button...")
            wallet(user)
        else:
            wallet(user)
    elif chose == '5':
        info = make_tranaction(user)
        info = json.loads(info)
        if not info['message'] == 'error':
            print(info['message'])
            input("Press any button...")
            wallet(user)
        else:
            print(white_paper())
            input("Press any button...")
            main()
    elif chose == '6':
        main()
    else:
        wallet(user)

def login():
    loginx = input(bcolors.BOLD + "\nLogin: " + bcolors.ENDC)
    if len(loginx) == 0:
        print("\nLogin cannot be empty")
        input("Press any button...")
        login()
    password = input(bcolors.BOLD + "Password: " + bcolors.ENDC)
    if len(password) == 0:
        print("\nPassword cannot be empty")
        input("Press any button...")
        login()
    data = requests.post('http://127.0.0.1:5000/login', data={'login': loginx, 'password': password})
    data = json.loads(data.text)
    if data == 0:
        print("Incorrect login or password!")
        input("Press any button...")
        login()
    else:
        wallet(data)

def register():
    loginx = input(bcolors.BOLD + "\nLogin: " + bcolors.ENDC)
    if len(loginx) == 0:
        print("\nLogin cannot be empty")
        input("Press any button...")
        login()
    password = input(bcolors.BOLD + "Password: " + bcolors.ENDC)
    if len(password) == 0:
        print("\nPassword cannot be empty")
        input("Press any button...")
        login()
    data = requests.post('http://127.0.0.1:5000/register', data={'login': loginx, 'password': password})
    data = json.loads(data.text)
    if data == 0:
        print("User already exist!")
        input("Press any button...")
        main()
    else:
        print("Save private keys, in case of loss, you will lose all money on your wallet!")
        print("Private Key:", data['private_key'])
        print("Public Key:", data['public_key'])
        input("Press any button...")
        main()

def main():
    print(bcolors.WARNING + "\nChickenCoin v1.0"+ bcolors.ENDC)
    print(bcolors.HEADER + "1) Login" + bcolors.ENDC)
    print(bcolors.OKGREEN + "2) Register" + bcolors.ENDC)
    print(bcolors.FAIL + "3) Exit\n"+ bcolors.ENDC)
    var = input(bcolors.BOLD + "Chose operation: "+ bcolors.ENDC)
    if var == '1':
        login()
    elif var == '2':
        register()
    elif var == '3':
        exit(0)
    else:
        main()

main()