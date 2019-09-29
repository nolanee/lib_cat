from flask import Flask, render_template, request
app = Flask(__name__)

from scrape_search import scrape_search

@app.route('/')
def render(page='index.html'):
    return render_template(page)

@app.route('/search')
def search():
    # @app.route('/?search=<search>')
    # will want to add to sanitize searches (length of them etc.)
    # url(?key=value)
    s = request.args.get('search', '')
    page = 'index.html'
    results = []
    if s:
        results = scrape_search(s, True)
    return render_template(page, query=s, results=results)

@app.route('/full_search')
# @app.route('/full_search?search=<search>')
# will want to add to sanitize searches (length of them etc.)
def full_search():
    # url(?key=value)
    s = request.args.get('search', '')
    page = 'index.html'
    results = []
    if s:
        # need to make other function called
        #results = scrape_search(s, True)
        #render_template(page, query=s, results=results, num_results=num_results)
        results = scrape_search(s)

    return render_template(page, query=s, results=results)

if __name__ == '__main__':
    app.run(debug=1)