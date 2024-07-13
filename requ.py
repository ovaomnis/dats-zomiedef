from decouple import config

import requests

# Основной URL API
BASE_URL = "https://games-test.datsteam.dev"

# Токен авторизации
AUTH_TOKEN = config('AUTH_TOKEN')

def get_endpoint(endpoint):
    """Общая функция для отправки GET-запросов."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {'X-Auth-Token': AUTH_TOKEN}
    response = requests.get(url, headers=headers)
    return response.json()


def get_units():
    """Получение информации о юнитах."""
    endpoint = "play/zombidef/units"
    return get_endpoint(endpoint)

def get_world():
    """Получение информации о мире."""
    endpoint = "play/zombidef/world"
    return get_endpoint(endpoint)

def get_rounds():
    """Получение информации о раундах."""
    endpoint = "rounds/zombidef"
    return get_endpoint(endpoint)

def post_endpoint(endpoint, data):
    """Функция для отправки POST-запроса с авторизацией."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': AUTH_TOKEN
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def put_endpoint(endpoint, data):
    """Функция для отправки PUT-запроса с авторизацией."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': AUTH_TOKEN
    }
    response = requests.put(url, json=data, headers=headers)
    return response.json()



def post_command(data):
    """Отправка команды в игре."""
    endpoint = "play/zombidef/command"
    return post_endpoint(endpoint, data)

def put_participate(data):
    """Участие в игре."""
    endpoint = "play/zombidef/participate"
    return put_endpoint(endpoint, data)








