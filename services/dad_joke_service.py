import requests

# UPDATE: The index URL is now constant
DAD_JOKE_URL = "https://icanhazdadjoke.com"

def getDadJoke():
    """Fetches a random dad joke from icanhazdadjoke.com."""

    url     = DAD_JOKE_URL
    headers = {"Accept": "application/json"}

    try:
        response    = requests.get(url, headers=headers)
        response.raise_for_status()
        joke_data   = response.json()
        return joke_data["joke"]
    except requests.RequestException as e:
        print(f"\nError getting joke: {e}")
        return None
