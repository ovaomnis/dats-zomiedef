from decouple import config
import requests
from dataclasses import dataclass

@dataclass
class fetchUnitsResponse:
    realmName: str


def get_api_host() -> str:
    api_host = config("API_HOST", default='https://games.datsteam.dev/')
    return api_host

def get_token() -> str:
    token = config("TOKEN", default='sdklfj;askdjflkjsad;f')
    return token


def fetchUnits():
    api_host = get_api_host()
    token = get_token()
    res = requests.get(f"{api_host}play/zombidef/units", headers={"X-Auth-Token": token})

    if res.status_code == 200:
        data: fetchUnitsResponse = res.json()
        print(data.realmName)
    else:
        print(f"something went wrong..")
        try:
            print(res.json())
        except:
            print(res.status_code)


    
if __name__ == "__main__":
    fetchUnits()