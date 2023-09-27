import memcache
import time
import subprocess

ap = memcache.Client(['172.17.0.2:11211'])

def run_gather(access_counter, lock, min):
    while True:
        if access_counter.keys():
            break
    popper = list()
    while True:
        with lock:
            for key, count in access_counter.items():
                if count < min:
                    ap.delete("id_"+key)
                    # print("removed item: id_"+key)
                    popper.append(key) #access_counter.pop(key)
                else:
                    print("Not removed: id_"+key)
                    access_counter[key] = 0

        for p in popper:
            print("removed item: id_"+p)
            access_counter.pop(p, None)
        time.sleep(8)