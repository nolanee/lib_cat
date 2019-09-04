from library_utils import Book, get_g_json, get_libthing_json, book_list_to_dict_list, dict_list_to_book_list, get_searched_google_ids
import json

class Library:
    def init_from_file(self, filename):
        file = open(filename, 'r')
        data = json.load(file)
        self.books_by_isbn = dict_list_to_book_list(data['books'], True)
        self.books_without_isbns = dict_list_to_book_list(data['books_without_isbns'])
        self.all_books = dict_list_to_book_list(data['all_books'])
        self.isbns = set(data['isbns'])

    def save_to_file(self, filename):
        file = open(filename, 'w')
        data = {
            # also works for dicts
            'books' : book_list_to_dict_list(self.books_by_isbn, True),
            'books_without_isbns' : book_list_to_dict_list(self.books_without_isbn),
            'all_books' : book_list_to_dict_list(self.all_books),
            'isbns' : list(self.isbns)
        }
        json.dump(data, file)
    
    def init_from_lib_thing(self, filename):
        catalog_id_entries = get_libthing_json(filename)

        keys = []
        for catalog_id_entry in catalog_id_entries:
            keys.append(catalog_id_entry)

        isbn_list = []

        for key in keys:
            entry = catalog_id_entries[key]
            title = entry['title']
            keys = entry.keys()

            # not all entries record author the same way
            # each name is an array of names from primary author(??)
            author = ''
            if 'primaryauthor' in keys:
                author  = entry['primaryauthor']
            # does not cover the  about 54 records without primary author
            # eventually may want to do something about these (all will have
            # author = '')
            
            shelf_id = ''
            if type(entry['lcc']) == dict:
                shelf_id = entry['lcc']['code']
            else:
                shelf_id = 'No Library of Congress number available'

            tags = []
            if 'tags' in entry.keys():
                tags = entry['tags']

            isbn = 0
            if 'isbn' in keys:
                isbns = entry['isbn']
                if type(isbns) == list:
                    isbn = isbns[0]
                else: 
                    isbn = isbns['2']

            book = Book(title,author, shelf_id, tags)
            if isbn == 0:
                self.books_without_isbn.append(book)
            else:
                isbn_list.append(isbn)
                self.books_by_isbn[isbn] = book
            
            #keep this?
            self.all_books.append(book)

        self.isbns = set(isbn_list)
        return

    def __init__ (self, filename='librarything_UMClassics.json', init_from_record=False):
        # do with list books now, can do with dict or set later
        self.books_by_isbn = {}
        self.books_without_isbn = []
        self.all_books = []
        self.isbns = set()

        if (init_from_record == True):
            self.init_from_file(filename)
            return

        self.init_from_lib_thing(filename)
        
            
    def __contains__ (self, item):
        # will need to add ways to deal with ones without isbns eventually
        return item in self.isbns

    def __str__(self):
        return_str = ''
        for isbn in self.isbns:
            return_str += str(self.books_by_isbn[isbn]) + '\n'
            
        for book in self.books_without_isbn:
            return_str += str(book)

        return_str += '\n' + str(len(self.books_without_isbn)) + ' works do not have isbns.\n'
        return  return_str

    def get_book(self, isbn_num):
        return self.books_by_isbn[isbn_num]

    def search(self, s):
        return_books = []

        data = get_g_json(s)
        # can't find if search doesn't return items (may want to call other api)
        # could also use this as an excuse to search titles or authors?
        if 'items' not in data.keys() or data['totalItems'] == '0':
            return -1

        searched_isbns = []
        id_list = []


        items = data['items']
        for item in items:
            volume_info = item['volumeInfo']
            #used below
            id_list.append(item['id'])

            #can't find if no isbn 13 available, may want to call other api
            if 'industryIdentifiers' not in volume_info.keys():
                break
                
            industry_identifiers = volume_info['industryIdentifiers']
            for id_num in industry_identifiers:
                if id_num['type'] == 'ISBN_13':
                    searched_isbns.append(id_num['identifier'])

        for isbn in searched_isbns:
            
            if isbn in self:
                book = self.get_book(isbn)
                if book not in return_books:
                    return_books.append(book)

        # try adding google results to make searches like "Herodotus"
        # turn out better
        #if return_books != []:
            #return return_books

        ids = set(id_list)
        
        for book in self.all_books:
            if s in book.tags or s in book.author:
                if book not in return_books:
                    return_books.append(book)

            possible_ids = book.possible_google_ids
            if possible_ids == -1 or possible_ids == []:
                continue
            for id in possible_ids:
                if id in ids:
                    if book not in return_books:
                        return_books.append(book)
                        break
        return return_books

        

    def print_missing(self):
        count = 0
        for book in self.all_books:
            if "missing" in book.tags:
                print(book, book.shelf_id)
                count += 1
        print(count)

    def add_google_ids(self, num_entries=10):
        count = 0
        for book in self.all_books:
            if type(book.possible_google_ids) == list and len(book.possible_google_ids) > 0:
                continue
            # can't waste api calls going over books google can't find (-1 is returned from previous searches)
            # fix again after update all the entries with isbns but no google ids
            #if book.possible_google_ids == -1:
                #continue
            book.possible_google_ids = get_searched_google_ids(str(book))
            # if can't get results on first try with title + author, try just title
            if book.possible_google_ids == -1:
                book.possible_google_ids = get_searched_google_ids(book.title)
            if book.possible_google_ids == -1 and self.has_isbn(book):
                book.possible_google_ids = get_searched_google_ids("+isbn:" + self.get_isbn(book))
            count += 1
            print(count, str(book), book.possible_google_ids)
            if count == num_entries:
                break
        if count == 0:
            print('No entries without possible google ids recorded found')

    # will want ot make this more advanced to use some way of not just checking if empty but checking if formated as should be
    def count_books_with_google_id(self):
        count = 0
        for book in self.all_books:
            if type(book.possible_google_ids) == list and len(book.possible_google_ids) > 0:
                count += 1
        return count

    def has_isbn(self, book):
        keys = self.books_by_isbn.keys()
        for key in keys:
            if str(self.books_by_isbn[key]) == str(book):
                return True
        return False
    
    def get_isbn(self, book):
        keys = self.books_by_isbn.keys()
        for key in keys:
            if str(self.books_by_isbn[key]) == str(book):
                return key
        return False

    # will want to make a function to find -1 results so we can swee what can be done about them (and if they have isbn)
    def show_books_without_google_ids(self):
        count = 0
        for book in self.all_books:
            if not type(book.possible_google_ids) == list or book.possible_google_ids == []:
                count += 1
                print(count, book, book.possible_google_ids, 'Has isbn:', self.get_isbn(book))


if __name__ == "__main__":
    filename = 'new_lib_info.json'
    lib = Library(filename, True)
    print(lib.count_books_with_google_id())
    #lib.print_missing()
    lib.add_google_ids(100)
    lib.save_to_file(filename)
    new_lib = Library(filename, True)
    print(new_lib.count_books_with_google_id())
    lib.show_books_without_google_ids()
    
    """
    books = lib.all_books
    for book in books:
        if book.possible_google_ids != []:
            print(book, book.possible_google_ids)
    """

    """
    books = lib.all_books
    i = 0
    k = 0
    j = 1


    for book in books:
        k += 1
        s = str(book)
        print(k, s)
        d = lib.search(s)
        if d != -1 and d != -2 and d != []:
            i += 1
        for b in d:
            print(b, b.shelf_id)

        if k >= j:
            break
    
    print(i, '/', j)

    # will want to add (precise) searching for tag (+ title & author?) eventually
    d = lib.search("missing")
    for b in d:
        print(b)

    """

    # with just google and isbns:
    #   44 / 100 with loebs (issue for some is that google books does not return data with isbn)
    #       try to collect info about this issue, look elsewhere when can't find isbn from google (LoC?)
    #     Also look at worldcat!
    #       note that amazon was original source for most
    #   46 / 100 without loebs
    #   89 / 200 with
    #   89 / 200 wihout loebs (loebs seem to make not much difference)
    # search in title to get isbns so can match to library if don't have isbn?

    # 40 / 100
    # no results: 0
    # no isbn: 5
    # other: 55

    # should also test with searches expect to come up empty