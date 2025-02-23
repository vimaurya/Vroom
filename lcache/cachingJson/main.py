import requests 
import json


def fetch_data(*, update:bool = False, json_cache: str, url: str):
    if update:
        json_data = None
    else:
        try:
            with open(json_cache, 'r') as file:
                json_data = json.load(file)
                print("fetched data from json cache")
                
        except(FileNotFoundError, json.JSONDecodeError) as e:
            print(f"No local cache found... {e}")
            json_data = None
            
            
    if not json_data:
        print("fetching new data..")
        json_data = requests.get(url).json()
        with open(json_cache, 'w') as file:
            json.dump(json_data, file)
            
    return json_data



if __name__ == '__main__':
    
    url = 'https://dummyjson.com/comments'
    
    url1 = 'https://jsonplaceholder.typicode.com/todos/1'
    
    cache_file = 'comments.json'
    
    data: dict = fetch_data(update=True,
                            json_cache=cache_file, 
                            url = url 
                            )
    
    print(data)