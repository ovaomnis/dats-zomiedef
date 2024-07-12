from datetime import datetime
from typing import List
from decouple import config
import requests
from dataclasses import dataclass
from data_types import fetchUnitsResponse

@dataclass
class Round:
    duration: int
    endAt: datetime
    name: str
    repeat: int
    startAt: datetime
    status: str

@dataclass
class fetchRoundsResponse:
    gameName: str
    now: datetime
    rounds: List[Round]


def get_rounds():
    api_host = get_api_host()
    token = get_token()
    res = requests.get(f"{api_host}rounds/zombidef", headers={"X-Auth-Token": token})

    if res.status_code == 200:
        data = fetchRoundsResponse(**res.json())
        print(data.rounds)
    else:
        print(f"something went wrong..")
        try:
            print(res.json())
        except:
            print(res.status_code)


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
    get_rounds()