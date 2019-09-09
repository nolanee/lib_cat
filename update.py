from library import Library
from library_utils import get_searched_loc_ids

# for now have library with updated all books, not dict, but once have loc_ids and libthing nums (and anything else need), can initalize from list alone
# that gets sorted into dictionaries, and dictionaries will later become db
# FIXME: todo
def update_loc_ids_from_lt(filename):
    lib = Library(filename, True)
    count = 0
    for book in lib.all_books:
        results = get_searched_loc_ids(book.title)
        book.possible_loc_ids = results
        count += 1
        print(count)
    lib.save_to_file(filename)

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

    # check to make sure all are unique
    # will want to put this script elsewhere and warning on script above because will actually mess up
    # properly formated data
    ids = []
    lib = Library(write_file, True)
    for book in lib.all_books:
        id = book.libthing_num
        if id in ids:
            print(id)
        ids.append(id)
    print(len(ids), len(set(ids)))
    # found DUP and other problems: will have to clean by hand
    

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
   

if __name__ == "__main__":
    filename = 'new_lib_info.json'
    json_filename = 'librarything_UMClassics.json'
    #add_books_from_lt(filename, json_filename)
    update_libthing_ids_and_editors(filename, json_filename)
    #update_loc_ids_from_lt(filename)
    #update_isbns_from_lt(filename, json_filename)
