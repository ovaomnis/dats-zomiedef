from decouple import config
import requests
import json
from dataclasses import dataclass

@dataclass
class fetchUnitsResponse:
    realmName: str


def get_api_host() -> str:
    api_host = config("API_HOST", default='https://games.datsteam.dev/')
    return api_host

def fetchUnits():
    api_host = get_api_host()
    res = requests.get(api_host)

    if res.status_code == 200:
        data: fetchUnitsResponse = res.json()
        print(data.realmName)
    else:
        print(f"something went wrong...\n{res.status_code}")
    

    
    
if __name__ == "__main__":
    fetchUnits()