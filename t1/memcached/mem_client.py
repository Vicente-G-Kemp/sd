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
# thread.start()

def update_counter(key):
    with lock:
        if key in access_counter.keys():
            access_counter[key]+=1
        else:
            access_counter[key]=1

ap = memcache.Client(['172.17.0.2:11211'])
def Get(key, simulated=False):
    start_time = time.time()

    delay = np.random.normal(2, 0.5)
    
    response = ap.get("id_"+key)

    if response:
        print("Key found in cache...")
        elapsed_time = time.time() - start_time
        print(f"Time taken: {elapsed_time:.5f} seconds")
        update_counter(key)
        if not simulated:
            return response
        else:    
            return response, delay-elapsed_time
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
            return value, 0
        else:
            print("Key not found.")
            return None

def sim(n_searches, sim_type):
    if sim_type:
        keys_to_search = [f"{i}" for i in np.random.randint(0, 100, n_searches)]
    else:
        keys_to_search = list()
        i=0
        while i<n_searches:
            hold_id = int(random.normalvariate(50,20))
            hold_id = max(0, min(99, hold_id))
            keys_to_search.append(f"{hold_id}")
            i+=1

    total_time = 0
    avoided_json_lookups = 0
    expected_delay = 0
    count = 0

    for key in keys_to_search:
        # clear console
        count += 1
        print("\033[H\033[J")
        print(f"Searching : {count}/{n_searches}")
        start_time = time.time()

        value, delay = Get(key, True)

        elapsed_time = time.time() - start_time

        total_time += elapsed_time

        if elapsed_time < 0.5:
            avoided_json_lookups += 1
            expected_delay += delay
            

    time_saved = expected_delay

    print(f"\nTime saved thanks to cache: {time_saved:.2f} seconds")
    print(f"Number of times JSON lookup was avoided: {avoided_json_lookups}")
    print(f"Total search time: {total_time}")
    return None
    
while True:
    print("\nSelect an action:")
    print("1. Get")
    print("2. simulate")
    print("7. Eviction mode")
    print("9. exit")
    choice = input("Standing by... ")

    if choice == "1":
        key = input("Enter key: ")
        print(Get(key))
    elif choice == "2":
        n_searches = int(input("Enter the number of searches you want to simulate: "))
        sim_type = bool(int(input("Choose the type of simulation: 1 - regular, 0 - normal/gaussian\n")))
        sim(n_searches, sim_type)
    elif choice == "7":
        thread.start()
    elif choice == "8":
        setup()
    elif choice == "9":
        break
    else:
        print("opción inválida")