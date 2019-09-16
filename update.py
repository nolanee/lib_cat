from library import Library
from search_utils import get_searched_loc_ids


# for now have library with updated all books, not dict, but once have loc_ids and libthing nums (and anything else need), can initalize from list alone
# that gets sorted into dictionaries, and dictionaries will later become db
# FIXME: todo

# also want check/fix not found function, because e.g.
# Die Quellenangaben Bei Herodot, which was goal of getting LOC, not inlcuded
# in search results -> updated by hand but still want to check (and check other situations with works in multiple langs)
# may want to do something with lccn or loc num: or could just get searches better with google translate

# may want to see if title author also gets results aand if so replace it when loc not related (e.g. Géographie, vols. 1.1, 1.2, 2-9)
# this would take a long time tho, so probably can't or shouldn't just now (goolge was done with author so should be fine, hopefully)
def update_loc_ids(lib, filename, limit):
    count = 0
    book_i = 0
    total = len(lib.all_books)
    for book in lib.all_books:
        book_i += 1
        if book.possible_loc_ids:
            continue
        results = get_searched_loc_ids(book.title, True)
        #when fails want to return and try again
        if results == -1:
             return False
        if not results:
            # may want to make -1 later to fit with google search
            results = "not found"
        book.possible_loc_ids = results
        ""
        print(book.title)
        print(results)
        count += 1
        print(count)
        print(int((book_i/total) * 100))
        
        if count == limit:
            break

    lib.save_to_file(filename)
    # returns true once work done
    if count != limit:
        return True
    return False

# WARNING: not for regular use as will mess up libthing numbers of file that alreayd has them accurately
# will want ot create a new version that will include other secondary authors in editor and will not mess
# with parts already accurate
def update_libthing_ids_and_editors(filename, json_filename, write_file=''):
    if write_file == '':
        write_file = filename

    lib = Library(filename, True)
    libthing_lib = Library(json_filename)
    
    for book in libthing_lib.all_books:
        for other_book in lib.all_books:
            if other_book.title == book.title and other_book.isbn == book.isbn and other_book == book:
                other_book.libthing_num = book.libthing_num
                other_book.editor = book.editor

    lib.save_to_file(write_file)

def update_blank_libthing_ids(filename, json_filename, write_file=''):
    if write_file == '':
        write_file = filename

    lib = Library(filename, True)
    libthing_lib = Library(json_filename)
    
    for book in lib.all_books:
        if not book.libthing_num:
            for other_book in libthing_lib.all_books:
                if other_book.title == book.title:
                    book.libthing_num = other_book.libthing_num

    lib.save_to_file(write_file)

def check_libthing_valid(filename):
    # check to make sure all are unique
    # will want to put this script elsewhere and warning on script above because will actually mess up
    # properly formated data
    ids = []
    lib = Library(filename, True)
    for book in lib.all_books:
        id = book.libthing_num
        if id in ids:
            print(id, book)
        ids.append(id)
    print(len(ids), len(set(ids)))
    # found DUP and other problems: will have to clean by hand (now cleaned)
    

def add_books_from_lt(filename, json_filename):
    lib = Library(filename, True)
    libthing_lib = Library(json_filename)

    for book in libthing_lib.all_books:
        if book not in lib.all_books:
            print(book)
            lib.all_books.append(book)
    
    lib.save_to_file(filename) 


def update_isbns_from_lt(filename, json_filename, write_file=''):
    if write_file == '':
        write_file = filename
    lib = Library(filename, True)
    libthing_lib = Library(json_filename)

    for lib_book in libthing_lib.all_books:
        for book in lib.all_books:
            if lib_book == book:
                book.isbn = lib_book.isbn
      
    lib.save_to_file(write_file)

def add_entry_dates(lib, filename):
    ltlib = Library()
    keys = lib.books.keys()
    for key in keys:
        bk1 = lib.books[key]
        bk2 = ltlib.books[key]
        bk1.entry_date = bk2.entry_dat
    lib.save_to_file(filename)

    # will need to be updated
    """
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
    """
   
# FIXME add function to verify what's in file matches library thing

if __name__ == "__main__":
    filename = 'new_lib_info.json'
    json_filename = 'librarything_UMClassics.json'
    # check to see if safe, but also doesn't have to be
    # update_blank_libthing_ids(filename, json_filename)
    check_libthing_valid(filename)
    #add_books_from_lt(filename, json_filename)
    lib = Library(filename, True)
    #add_entry_dates(lib, filename)
    loc_indexed = update_loc_ids(lib, filename, 5) 
    while not loc_indexed:
        loc_indexed = update_loc_ids(lib, filename, 5) 
    #update_isbns_from_lt(filename, json_filename)
