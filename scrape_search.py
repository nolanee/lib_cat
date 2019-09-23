import requests
import sys
from bs4 import BeautifulSoup

def do_request(query):
    try:
        request = requests.get(query)
        request.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        data = request.json()
        print(data)
        sys.exit(1)

    return request.text

def scrape_search(search):
    search = search.replace(' ', '+')
    url = "https://www.librarything.com/catalog/UMClassics&deepsearch=" + search
    response = do_request(url)
    soup = BeautifulSoup(response, 'html.parser')
    tag = soup.find('frame', attrs={"name": "bottom"})
    url = "http://www.librarything.com" + tag['src']
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'html.parser')
    return str(soup.find(id="lt_catalog_list"))

if __name__ == "__main__":
    # break this into mini functions
    search = input("Please enter a search:\n")
    search = search.replace(' ', '+')
    url = "https://www.librarything.com/catalog/UMClassics&deepsearch=" + search
    response = do_request(url)
    soup = BeautifulSoup(response, 'html.parser')
    tag = soup.find('frame', attrs={"name": "bottom"})
    url = "http://www.librarything.com" + tag['src']
    response = do_request(url)
    soup = BeautifulSoup(response, 'html.parser')
    for tag in soup.find_all(True):
        print(tag)

    for tag in soup.find_all('td', id="ipe"):
        print(tag)

