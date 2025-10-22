from dotenv import load_dotenv
import requests
import base64
import os

'''
For Spotify API info, visit: https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow
'''

load_dotenv() # Loads environment variables from a '.env' file into the os.environ dictionary

client_id       = os.getenv("SPOTIFY_CLIENT_ID")    # Retrieves the value of an environment variable
client_secret   = os.getenv("SPOTIFY_CLIENT_SECRET")# Retrieves the value of an environment variable
# UPDATE: Changed 'CLIENT_ID' to 'SPOTIFY_CLIENT_ID', and 'CLIENT_SECRET' to 'SPOTIFY_CLIENT_SECRET'

# Add these global constants near the imports
SPOTIFY_AUTH_URL        = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL      = "https://api.spotify.com/v1/search"
SPOTIFY_TRACKS_URL_BASE = "https://api.spotify.com/v1/artists/"


def get_token():
    auth_string = client_id + ":" + client_secret               # Creates the authentication string
    auth_bytes  = auth_string.encode("utf-8")                   # Encodes the string
    auth_base64 = str( base64.b64encode(auth_bytes), 'utf-8')   # Creates a base-64 encoded sting of the off-bites
    #url         = "https://accounts.spotify.com/api/token"      # Indexes URL string
    url         = SPOTIFY_AUTH_URL

    # Creates dictionaries
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data    = {'grant_type': 'client_credentials'}

    try:
        results = requests.post(url,
                                headers=headers,
                                data=data)  # Indexes the 'results'
        results.raise_for_status()          # Provides error if something went wrong with 'request'
        data    = results.json()            # Indexes the results of search in .json format
        token   = data["access_token"]      # Indexes the access token in the 'data' dictionary
        return token                        # Returns the 'token'
    except requests.HTTPError as http_err:
        print(f'HTTP Error occurred: {http_err}')
        print('\nPlease make sure the "SPOTIFY_CLIENT_ID" and "SPOTIFY_CLIENT_SECRET" are correct in the .env file')
    except requests.RequestException as ex:
        print(f'\nException occurred during token retrieval: {ex}')
        return None

def get_auth_header(token):
    return { "Authorization": "Bearer " + token }

def search_for_artist(token, artist_name):
    #url         = "https://api.spotify.com/v1/search"       # Indexes URL string (endpoint)
    #url         = SPOTIFY_SEARCH_URL
    #query       = f"?q={artist_name}&limit=1&type=artist"   # f-string
    #query_url   = url + query                               # Combines the strings
    query_url   = SPOTIFY_SEARCH_URL + f"?q={artist_name}&limit=1&type=artist"
    headers     = get_auth_header(token)

    try:
        result  = requests.get(query_url, headers=headers)  # Indexes the 'results'
        result.raise_for_status()                           # Provides error if something went wrong with 'request'
        data    = result.json()                             # Indexes the results of search in .json format
        items   = data.get('artists', {}).get('items', [])  # Indexes the 'artists' and 'items' info in 'data'
        #return items[0]                                     # Returns the first item in 'items'
        if items:
            return items[0]
        else:
            print(f"Artist '{artist_name}' not found.")
            return None
    except Exception as e:
        print(f"Unexpected error during artist search: {e}")


def get_songs_by_artist(token, artist_id):
    #url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US" # Indexes URL string
    url = f"{SPOTIFY_TRACKS_URL_BASE}{artist_id}/top-tracks?country=US"
    #headers = { "Authorization": "Bearer " + token }
    headers = get_auth_header(token)

    try:
        result  = requests.get(url, headers=headers)# Indexes the 'results'
        result.raise_for_status()                   # Provides error if something went wrong with 'request'
        data    = result.json()                     # Indexes the results of search in .json format
        #print(data["tracks"])                       # Displays the 'tracks' from 'data'
        #return data["tracks"]                       # Returns the 'tracks' from 'data'
        return data.get("tracks", [])
    except Exception as e:
        print(f"Error fetching tracks: {e}")
        return []