from library_utils import Book, get_libthing_json, book_list_to_dict_list, dict_list_to_book_dict
from search_utils import get_g_json, get_searched_google_ids, get_g_search_results
import requests
import json

class Library:
    def init_from_file(self, filename):
        file = open(filename, 'r')
        data = json.load(file)
        # FIXME: make just two different functions at some point?
        # can make books by isbn while creating and think can look in books by isbn so don't need set either
        #self.books_by_isbn = dict_list_to_book_list(data['books'], True)
        # make dict of lib_cat nums

        # start of changing to dictionary-based set-up -> in future this will be initialize from dict dict instead of dict list
        self.books = dict_list_to_book_dict(data['all_books'])
        #self.isbns = set(data['isbns'])

        # will get rid of list later, when other code does not depend on it (make things more encapsulated?)
        self.all_books = []

        # these dicts will be backbone of search (should not have to search through list)
        self.books_by_isbn = {}
        self.books_by_google_id = {}
        self.books_by_loc_id = {}
        self.books_by_tag = {}

        # can add a cleaned and lowercased title and author last name dict to search too, and use secondary authors/editors too for author
        # will want to updated secondary author/editor to make this work better too
        # can wait to see if way reddis works can fix that

        # Cf. Aristotle as well as Herodotus
        
        keys = self.books.keys()
        for key in keys:
            book = self.books[key]
            num = book.libthing_num

            self.all_books.append(self.books[key])

            isbn = book.isbn
            if isbn and isbn != 0:
                if isbn in self.books_by_isbn.keys():
                    self.books_by_isbn[isbn].append(num)
                else:
                    self.books_by_isbn[isbn] = [num]

            google_ids = book.possible_google_ids
            # negative one for books where search returned nothing
            if type(google_ids) != int:
                for g_id in google_ids:
                    if g_id in self.books_by_google_id.keys():
                        self.books_by_google_id[g_id].append(num)
                    else:
                        self.books_by_google_id[g_id] = [num]
            
            loc_ids = book.possible_loc_ids
            if loc_ids != 'not found':
                for loc_id in loc_ids:
                    if loc_id in self.books_by_loc_id.keys():
                        self.books_by_loc_id[loc_id].append(num)
                    else:
                        self.books_by_loc_id[loc_id] = [num]
            
            tags = book.tags
            for tag in tags:
                # want them all to be lower case, so can check against a lowercase of query
                tag = tag.lower()
                if tag in self.books_by_tag.keys():
                    self.books_by_tag[tag].append(num)
                else:
                    self.books_by_tag[tag] = [num]
            

    def save_to_file(self, filename):
        file = open(filename, 'w')
        data = {
            # also works for dicts
            #'books' : book_list_to_dict_list(self.books_by_isbn, True),
            'all_books' : book_list_to_dict_list(self.all_books),
            #'isbns' : list(self.isbns)
        }
        json.dump(data, file)
    
    def init_from_lib_thing(self, filename):
        self.books = {}
        catalog_id_entries = get_libthing_json(filename)

        keys = []
        for catalog_id_entry in catalog_id_entries:
            keys.append(catalog_id_entry)

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

            editor = ''
            if 'secondaryauthor' in keys and 'secondaryauthorroles' in keys and "Editor" in entry['secondaryauthorroles']:
                editor = entry['secondaryauthor']
            
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

            entry_date = entry['entrydate']

            book = Book(title, author, shelf_id, tags, list(), list(), editor, key, isbn, entry_date)
            
            self.books[key] = book

    def __init__ (self, filename='librarything_UMClassics.json', init_from_record=False):
        # do with list books now, can do with dict or set later
        self.books_by_isbn = {}
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
            
        for book in self.all_books:
            return_str += book + '\n'

        return return_str

    def get_book(self, isbn_num):
        return self.books_by_isbn[isbn_num]

    # add image getting feature so can show results with images?
    # still need to improve (compare Hdt. and Arist. with LibThing)
    # try library of congress or google translate api?
    # add to search by isbn, author, shelf_id
    def search(self, s):
        return_books = []

        # FIXME fit helper functions into other file, make search fit new way
        #return_books += get_g_search_results(self)
        data = get_g_json(s)
        # can't find if search doesn't return items 
        if not ('items' in data.keys() and data['totalItems'] != '0'):
            return -1

        searched_isbns = []
        id_list = []


        items = data['items']
        for item in items:
            volume_info = item['volumeInfo']
            # used below
            id_list.append(item['id'])

            # can't find if no isbn 13 available, may want to call other api
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

        ids = set(id_list)
        
        for book in self.all_books:
            # FIXME: make tags lowercase when initialize, get rid of first part
            if s in book.tags or s.lower() in book.tags or s.lower() in book.author.lower() or s.lower() in book.title.lower():
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

    ## add some of below to update?
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

    import requests

    def loc_search(self, s):
        # may want to use only dicts at some point if can make that work, then maybe go throught all
        # books to make up results up to a certain number?
        ## function to put in utils and take out requests from top starts here 

        # can get Geschichte der griechischen Religion (Neubearbeitung): Zweiter Band - 
        # Die hellenistische und römische Zeit (Handbuch der Altertumswissenschaft)?
        query = 'https://www.loc.gov/books/?all=true&q=' + s + '&fo=json'
        request = requests.get(query)
        print(request)

        search = request.json()
        print(search.keys())
        # list of results
        results = search['results']

        first = results[0]
        print(first.keys())

        # try with just titles and shelf_ids at first to limit requests
        titles = []
        shelf_ids = []
        for result in results:
            image_url = result['image_url']
            if result['other_title']:
                titles.append(result['other_title'])
            titles.append(result['title'].lower())
            print(titles)
            shelf_ids.append(result['shelf_id'])
        
        #function to take out should end here
        return_books = []

        num = 0

        for book in self.all_books:
            if book.title.lower() in titles or book.shelf_id in shelf_ids:
                if book not in return_books:
                    return_books.append(book)
                    num +=1
        
            for title in titles:
                if  title in book.title.lower():
                    if book not in return_books:
                        return_books.append(book)
                        num+=1
            
            for shelf_id in shelf_ids:
                if  shelf_id in book.shelf_id.lower():
                    if book not in return_books:
                        return_books.append(book)
                        num+=1
        
        return_books.append(str(num))
        return return_books

        """
        for i in pl:
            if i:
                print(i)
        

        id_num = result['id'].split('v/')[1]
        """

        #print(first['id'])
        #print(first['index'])

if __name__ == "__main__":
    filename = 'new_lib_info.json'
    lib = Library(filename, True)
    #print(lib.count_books_with_google_id())
    #print(lib)
    #lib.print_missing()
    returns = lib.loc_search("Herodotus")
    #for book in returns:
        #print(book)

    """
    lib.add_google_ids(100)
    lib.save_to_file(filename)
    new_lib = Library(filename, True)
    print(new_lib.count_books_with_google_id())
    lib.show_books_without_google_ids()
    """
    
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
        print(k, s)p {
  color: red;
}
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