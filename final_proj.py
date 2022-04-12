from bs4 import BeautifulSoup
import requests 
import json
import secrets
import sqlite3
import plotly.graph_objects as go

# Caching 
CACHE_FNAME = 'cache.json'
def open_cache():
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache():
    cache_file = open(CACHE_FNAME, 'w')
    contents_to_write = json.dumps(CACHE_DICT)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url,cache):
    if url in cache.keys():
        print("Getting cached data...")
        return cache[url]
    else:
        print("Making a request for new data...")
        headers = {
            'X-RapidAPI-Host': 'coronavirus-smartable.p.rapidapi.com',
            'X-RapidAPI-Key':'3f54b35ec9msh3f587a3146600ecp1af59ejsn137682d60c7c'
            }      
        response = requests.request("GET", url, headers=headers)
        #print(reponse)
        cache[url] = response.text
        save_cache()
        return cache[url]

def get_state_names(state):
    url = 'https://www.nytimes.com/interactive/2020/us/covid-19-vaccine-doses.html'
    response = make_url_request_using_cache(url,CACHE_DICT)
    soup = BeautifulSoup(response, 'html.parser')
# still in progress...
