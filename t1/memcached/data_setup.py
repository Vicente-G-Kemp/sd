import json
import memcache

# Load/clear all data in memcached container. TESTING PURPOSES!!!
def setup():
    mode = bool(int(input("Select mode: 1 - load, 0 - clear\n")))
    ap = memcache.Client(['172.17.0.2:11211'])
    file_path="./cars.json"
    with open(file_path, 'r') as file:
        data = json.load(file)

    for item in data:
        key = f"id_{item['id']}"
        value = {
            "make": item["make"],
            "model": item["model"],
            "year": item["year"]
        }
        if mode:
            ap.set(key, value)
        else:
            ap.delete(key)
    print("Done.")
