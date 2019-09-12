import json
import requests
import sys
from env.keys import keys

def get_g_json(s):
        
        api_key = keys[0]

        prefix = 'https://www.googleapis.com/books/v1/volumes?q='
        query = prefix + s + '&key=' + api_key
        
        #need to work on checking for bad requests and errors
        try:
            request = requests.get(query)
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            data = request.json()
            print(data)
            sys.exit(1)

        data = request.json()
        return data

def get_searched_google_ids(s, limit=3): 
    data = get_g_json(s)
    found_ids = []

    #can't find if search doesn't return items (may want to call other api)
    if 'items' not in data.keys() or data['totalItems'] == '0':
        return -1

    count = 0
    items = data['items']
    for item in items:
        id = item['id']
        found_ids.append(id)
        count += 1
        if count == limit:
            break

    return found_ids
    #print(searched_isbns)

def get_searched_loc_ids(s, limit=5):
    query = 'https://www.loc.gov/books/?all=true&at=results&q=' + s + '&fo=json'
    #print(query)
    request = requests.get(query)

    # make common function with g_search above
    try:
        request = requests.get(query)
        request.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        # data = request.json()
        # print(data)
        #sys.exit(1)
        return -1

    try:
        search = request.json()
    except:
        return []

    results = search['results']

    nums = []

    i = 0
    for result in results:
        #image_url = result['image_url']
        nums.append(result['id'])
        i+=1
        if i == limit:
            break
    
    return nums

def get_g_search_results(s):
    return