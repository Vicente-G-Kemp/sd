import grpc
import json
import time
import random
import numpy as np
import cache_service_pb2
import cache_service_pb2_grpc
from find_car_by_id import find_car_by_id


class CacheClient:
    def __init__(self, host="master", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = cache_service_pb2_grpc.CacheServiceStub(self.channel)

    def get(self, key, en_cache_l, en_cache_i, simulated=False):
        start_time = time.time()  # Inicio del temporizador

        # Simulamos un retraso aletorio de 1 a 3 segundos, con una distribución normal en 2 para casos sin cache.
        delay = np.random.normal(2, 0.5)
        
        response = self.stub.Get(cache_service_pb2.Key(key=key))
        
        if response.value and en_cache_l:
            elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
            print(f"Time taken (cache): {elapsed_time:.5f} seconds")
            if not simulated:
                return response.value
            else:    
                return response.value, delay-elapsed_time
        else:
            print(f"Key not found in cache. Waiting {delay:.5f} seconds...")
            time.sleep(delay)

            # Si no está en el caché, buscar en el JSON
            value = find_car_by_id(int(key))
            value = str(value)
            if value:

                if en_cache_i:
                    # Agregando la llave-valor al caché si está activo.
                    print("Key found in JSON. Adding to cache...")
                    self.stub.Put(cache_service_pb2.CacheItem(key=key, value=value))
                
                elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido

                print(f"Time taken (JSON + delay): {elapsed_time:.5f} seconds")
                
                return value, 0
            else:
                elapsed_time = time.time() - start_time  # Calcula el tiempo transcurrido
                print(f"Time taken: {elapsed_time:.5f} seconds")
                print("Key not found.")
                return None
            
    def simulate_searches(self, n_searches, en_cache_l, en_cache_i, sim_type):
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
        # Métricas
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
            # time_without_cache += 3 + 0.001  # Estimado de tiempo de búsqueda en JSON
            value, delay = self.get(key, en_cache_l, en_cache_i, True)

            elapsed_time = time.time() - start_time

            total_time += elapsed_time

            if elapsed_time < 0.5:
                avoided_json_lookups += 1
                expected_delay += delay
                

        time_saved = expected_delay

        print(f"\nTime saved thanks to cache: {time_saved:.2f} seconds")
        print(f"Number of times JSON lookup was avoided: {avoided_json_lookups}")
        print(f"Total search time: {total_time}")

    def removal(self, key):
        value = find_car_by_id(int(key))
        value = str(value)
        if value:
            # print("Key found in JSON. Removing from cache...")
            self.stub.Remove(cache_service_pb2.CacheItem(key=key, value=value))

    def clear_cache(self):
        keys = list(range(100))
        print("clearing cache...")
        for key in keys:
            self.removal(f"{key}")
            print(".")
        print("Done!")

if __name__ == '__main__':

    client = CacheClient()

    while True:
        print("\nChoose an operation:")
        print("1. Get")
        print("2. Simulate Searches")
        print("3. Remove from cache [Testing only!!!]")
        print("4. Ensure cache clearance")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            key = input("Enter key: ")
            value = client.get(key, 1)
            if value is not None:
                print(f"Value: {value}")
        elif choice == "2":
            n_searches = int(input("Enter the number of searches you want to simulate: "))
            en_cache_l = bool(int(input("Enable load from cache? 1 - yes, 0 - no\n")))
            en_cache_i = bool(int(input("Enable cache insertion? 1 - yes, 0 - no\n")))
            sim_type = bool(int(input("Choose the type of simulation: 1 - regular, 0 - normal/gaussian\n")))
            client.simulate_searches(n_searches, en_cache_l, en_cache_i, sim_type)
        elif choice == "3":
            key = input("Enter key: ")
            client.removal(key)
        elif choice == "4":
            client.clear_cache()
        elif choice == "9":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")