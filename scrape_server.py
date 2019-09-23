from flask import Flask, render_template, request
app = Flask(__name__)

from scrape_search import scrape_search

# will need to fix all this to make work with lib thing
@app.route('/')
# @app.route('/?search=<search>')
# will want to add to sanitize searches (length of them etc.)
def search():
    # url(?key=value)
    s = request.args.get('search', '')
    page = 'scrape.html'
    results = []
    num_results = 0
    if s:
        results = scrape_search(s)
        f = open("templates/results.html", 'w')
        f.write(results)
        f.close()


        num_results = 1
        page = 'results.html'

    return render_template(page, query=s, results=results, num_results=num_results)

# still have issues with effectiveness of search re libthing (see Herodotous search and CM in library.py)
if __name__ == '__main__':
    app.run(debug=1)