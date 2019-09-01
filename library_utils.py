class Book:
    def __init__(self, title, author, shelf_id, tags=[], possible_google_ids=[]):
        self.title = title
        self.author = author
        self.shelf_id = shelf_id
        self.tags = tags
        self.possible_google_ids = possible_google_ids

    def __str__(self):
        return_title = self.title  + " " + self.author + " " + self.shelf_id
        return return_title
    
    def __eq__(self, other):
        ## update later with lib id numbers instead of shelf_id
        return (self.shelf_id == other.shelf_id) 

def book_list_to_dict_list(book_list, is_dict=False):
    if is_dict == False:
        return_list = []
        for book in book_list:
            return_list.append({
                'title' : book.title,
                'author' : book.author,
                'shelf_id' : book.shelf_id,
                'tags' : book.tags,
                'possible_google_ids' : book.possible_google_ids
            })
        return return_list

    return_dict = {}
    keys = book_list.keys()
    for key in keys:
        book = book_list[key]
        return_dict[key] = {'title' : book.title,
                'author' : book.author,
                'shelf_id' : book.shelf_id,
                'tags' : book.tags,
                'possible_google_ids' : book.possible_google_ids
        }
    return return_dict

def dict_list_to_book_list(dict_list, is_dict=False):
    if is_dict == False:
        return_list = []
        for book in dict_list:
            #print(book['possible_google_ids'])
            return_list.append(Book(book['title'], book['author'], book['shelf_id'], book['tags'], book['possible_google_ids']))
        return return_list

    return_dict = {}
    keys = dict_list.keys()
    for key in keys:
        book = dict_list[key]
        return_dict[key] = Book(book['title'], book['author'], book['shelf_id'], book['tags'], book['possible_google_ids'])
    return return_dict

import json
import html
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

def get_libthing_json(filename) :

    file = open(filename, 'r')
    filestr = file.read()
    filestr = html.unescape(filestr)
    titles = json.loads(filestr)

    return titles
    
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
