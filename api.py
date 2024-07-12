from datetime import datetime
from decouple import config
import requests


def get_api_host() -> str:
    api_host = config("API_HOST", default='https://games.datsteam.dev/')
    return api_host


def get_token() -> str:
    token = config("TOKEN", default='sdklfj;askdjflkjsad;f')
    return token


def get_rounds():
    from mock_rounds import rounds
    return rounds

    api_host = get_api_host()
    token = get_token()
    res = requests.get(f"{api_host}rounds/zombidef", headers={"X-Auth-Token": token})

    if res.status_code == 200:
        data = res.json()
        for round in data.rounds:
            print(round['startAt'])
    else:
        print(f"something went wrong..")
        try:
            print(res.json())
        except:
            print(res.status_code)


def fetchUnits():
    from mock_units import unit
    return unit

    api_host = get_api_host()
    token = get_token()
    res = requests.get(f"{api_host}play/zombidef/units", headers={"X-Auth-Token": token})

    if res.status_code == 200:
        data = res.json()
        print()
    else:
        print(f"something went wrong..")
        try:
            print(res.json())
        except:
            print(res.status_code)


    
if __name__ == "__main__":
    get_rounds()