import json

def retrieve(id):
    if int(id) not in range(0, 100):
        return None, None
    
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
        if str(item['id']) == str(id):
            break
    return key, value