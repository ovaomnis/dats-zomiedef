from datetime import datetime
from decouple import config
import requests
import json


def get_api_host() -> str:
    api_host = config("API_HOST", default='https://games.datsteam.dev/')
    return api_host


def get_token() -> str:
    token = config("TOKEN", default='sdklfj;askdjflkjsad;f')
    return token


def fetchUnits() -> dict:
    with open('./mock_units.json', 'r') as f:
        return json.loads(f.read())

    api_host = get_api_host()
    token = get_token()
    res = requests.get(f"{api_host}play/zombidef/units", headers={"X-Auth-Token": token})

    if res.status_code == 200:
        data = res.json()
        # print(data)
        return data
    else:
        print(f"something went wrong..")
        try:
            print(res.json())
        except:
            print(res.status_code)

    return None

def fetchWorld() -> dict:
 
    api_host = get_api_host()
    token = get_token()
    res = requests.get(f"{api_host}play/zombidef/world", headers={"X-Auth-Token": token})

    if res.status_code == 200:
        data = res.json()
        print(data)
        return data
    else:
        print(f"something went wrong..")
        try:
            print(res.json())
        except:
            print(res.status_code)

    return None

    
if __name__ == "__main__":
    # get_rounds()
    pass