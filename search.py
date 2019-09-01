from library import Library

filename = 'new_lib_info.json'
lib = Library(filename, True)

s = input('Enter your search: ')
books = lib.search(s)
if books == []:
    print("No results for \'" + s + "\'")
for book in books:
    print(book)
