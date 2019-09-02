from flask import Flask, render_template, request
app = Flask(__name__)

from library import Library

@app.route('/')
#@app.route('/?search=<search>')
def search():
    # url(?key=value)
    s = request.args.get('search', '')

    filename = 'new_lib_info.json'
    lib = Library(filename, True)

    # will want to get right from search in future
    results = []
    if s:
        books = lib.search(s)
        for book in books:
            results.append(str(book))
        if results == []:
            results = -1

    return render_template('index.html', query=s, results=results)
    
if __name__ == '__main__':
    app.run(debug=1)