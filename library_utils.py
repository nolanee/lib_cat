import json
import html

class Book:
    # need to update editor to secondaryauthor: perhaps better to do as dictionary or let initialize as a dictionary
    # also add image_url (but can be empty to update during search) and libcat num
    # also add date entered field
    def __init__(self, title, author, shelf_id, tags=[], possible_google_ids=[], possible_loc_ids=[],
      editor ='', libthing_num='', isbn='', entry_date='', image_url=''):
        self.title = title
        self.author = author
        self.shelf_id = shelf_id
        self.tags = tags
        self.possible_google_ids = possible_google_ids
        self.possible_loc_ids = possible_loc_ids
        self.editor = editor
        self.libthing_num = libthing_num
        self.isbn = isbn
        self.entry_date = entry_date 
        self.image_url = image_url
        
    def __str__(self):
        return_title = self.title  + " " + self.author + " " + self.shelf_id
        return return_title
    
    def __eq__(self, other):
        return (self.libthing_num == other.libthing_num) 
    
    # for now only works with strings
    def __add__ (self, other):
        return str(self) + other

def book_list_to_dict_list(book_list):
    return_list = []
    for book in book_list:
        return_list.append({
            'title' : book.title,
            'author' : book.author,
            'shelf_id' : book.shelf_id,
            'tags' : book.tags,
            'possible_google_ids' : book.possible_google_ids,
            'possible_loc_ids' : book.possible_loc_ids,
            'editor' : book.editor,
            'libthing_num' : book.libthing_num,
            'isbn' : book.isbn,
            'entry_date' : book.entry_date,
            'image_url' : book.image_url
        })
    return return_list
    
    # code to do as dict which will want to do
    """
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
    """

def dict_list_to_book_dict(dict_list):
    # FIXME will change for reading a dict and this will make it easier
    return_dict = {}
    for book in dict_list:
       return_dict[book['libthing_num']] = Book(book['title'], book['author'],
            book['shelf_id'], book['tags'], book['possible_google_ids'],
            book['possible_loc_ids'], book['editor'], book['libthing_num'], book['isbn'],
            book['entry_date'], book['image_url'])
    return return_dict

def get_libthing_json(filename) :

    file = open(filename, 'r')
    filestr = file.read()
    filestr = html.unescape(filestr)
    titles = json.loads(filestr)

    return titles

if __name__ == '__main__':
    from library import Library
    filename = 'new_lib_info.json'
    lib = Library(filename, True)
    ##for book in lib.all_books:
        #book.loc_id = get_searched_loc_ids(str(book.title))
    book = lib.all_books[0]
    book.possible_loc_ids = get_searched_loc_ids(str(book.title))
    print(book.possible_loc_ids)
