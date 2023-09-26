import memcache
import threading
import subprocess
import time
import random
import numpy as np
from data_retrieve import retrieve
from gather import run_gather
from data_setup import setup

access_counter = {}

lock = threading.Lock()
min_access = 2

thread = threading.Thread(target=run_gather, args=(access_counter, lock, min_access))
thread.daemon = True
thread.start()

def update_counter(key):
    with lock:
        if key in access_counter.keys():
            access_counter[key]+=1
        else:
            access_counter[key]=1

ap = memcache.Client(['172.17.0.2:11211'])

def Get(key):
    start_time = time.time()

    delay = np.random.normal(2, 0.5)
    
    response = ap.get("id_"+key)

    if response:
        print("Key found in cache...")
        elapsed_time = time.time() - start_time
        print(f"Time taken: {elapsed_time:.5f} seconds")
        update_counter(key)
        return response
    else:
        print(f"Key not found in cache. Waiting {delay:.5f} seconds...")
        time.sleep(delay)

        key_j, value = retrieve(key)
        if key_j:
            print("Adding key to cache.")
            ap.set(key_j, value)
            elapsed_time = time.time() - start_time
            print(f"Time taken: {elapsed_time:.5f} seconds")
            update_counter(key)
            return value
        else:
            print("Key not found.")
            return None
            
    
while True:
    print("\nSelect an action:")
    print("1. Get")
    print("9. exit")
    choice = input("Standing by... ")

    if choice == "1":
        key = input("Enter key: ")
        print(Get(key))
    if choice == "8":
        setup()
    if choice == "9":
        break
    else:
        print("opción inválida")