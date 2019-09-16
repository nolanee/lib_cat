import json
import requests
import sys
from env.keys import keys

def do_request(query):
    try:
        request = requests.get(query)
        request.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        data = request.json()
        print(data)
        sys.exit(1)

    return request.json()

def run_query(query, max_results, page=0):
    api_key = keys[0]
    # google allows max of 40
    assert(max_results <= 40)
    s = query
    index = page * max_results

    prefix = 'https://www.googleapis.com/books/v1/volumes?q='
    query = prefix + s + '&maxResults=' + str(max_results) + '&key=' + api_key
    query += '&startIndex=' + str(index)
    
    # a json object of a search result page of 40 items
    return do_request(query)


def get_g_json(s):
    max_results = 40
    page = 0
    data = run_query(s, max_results)
    
    totalItems = data['totalItems']
    if totalItems <= 40:
        return data

    return_data = {'kind' : data['kind'], 'totalItems': totalItems,
    'items' : []}
    
    returns = 0
    # playing with this affects accuracy of results
    max_additional_returns = 140

    while ('items' in data.keys()):
        return_data['items'] += (data['items'])
        returns += 40
        page += 1
        data = run_query(s, max_results, page)
        if returns >= max_additional_returns:
            break
    
    return return_data
    

def get_searched_google_ids(s, use_limit=False, limit=3): 
    data = get_g_json(s)
    found_ids = []

    #can't find if search doesn't return items (may want to call other api)
    if 'items' not in data.keys() or data['totalItems'] == '0':
        return []

    count = 0
    items = data['items']
    for item in items:
        id = item['id']
        found_ids.append(id)
        count += 1
        if use_limit==True & count == limit:
            break

    return found_ids

def get_searched_loc_ids(s, use_limit=False, limit=5):
    query = 'https://www.loc.gov/books/?all=true&at=results&q=' + s + '&fo=json&c=100'
    try:
        search = do_request(query)
    except:
        return []

    results = search['results']

    nums = []

    i = 0
    for result in results:
        nums.append(result['id'])
        i+=1
        if use_limit==True and i == limit:
            break
    
    print(nums)
    return nums

if __name__ == "__main__":
    search = get_g_json("herodotus")
