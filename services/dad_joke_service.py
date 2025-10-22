import requests

# UPDATE: The index URL is now constant
DAD_JOKE_URL = "https://icanhazdadjoke.com"

def getDadJoke():
    """Fetches a random dad joke from icanhazdadjoke.com."""

    #url     = "https://icanhazdadjoke.com"   # Indexes the string for the website
    url     = DAD_JOKE_URL
    headers = {"Accept": "application/json"} # Creates a dictionary

    try:
        response    = requests.get(url, headers=headers)# Indexes the 'response'
        response.raise_for_status()                     # Provides error if something went wrong with 'request'
        joke_data   = response.json()                   # Indexes the joke
        return joke_data["joke"]                        # Returns 'joke'
    except requests.RequestException as e:
        print(f"\nError getting joke: {e}")
        return None
