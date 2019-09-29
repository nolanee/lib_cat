from selenium import webdriver
from bs4 import BeautifulSoup
import requests, sys
import multiprocessing

def do_request(query):
    try:
        request = requests.get(query)
        request.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)

    return request.content

def get_search_url(search):
    search = search.replace(' ', '+')
    url = "https://www.librarything.com/catalog_bottom.php?view=UMClassics&deepsearch=" + search
    return url

def simple_html(search):
    url = get_search_url(search)
    return do_request(url)

def search_to_soup(search):
    return BeautifulSoup(simple_html(search), 'html.parser')

def get_text_list_from_class(soup, class_name):
    li = []
    for item in soup.find_all(attrs={"class" : class_name}):
        li.append(item.get_text())
    return li        

# probelm with works with no author? Yes, need to grab at once, and edit fns used
# check that missing works
def get_results_from_soup(soup):
    results = []
    authors = get_text_list_from_class(soup, "lt-authorunflip")
    titles = get_text_list_from_class(soup, "lt-title")
    for i in range(len(authors)):
        results.append({'author' : authors[i], 'title' : titles[i]})
    return results

def get_num_pages_from_soup(soup):
    nav_bar = soup.find(id='pages')
    if not nav_bar:
        return 0
    pages = len(nav_bar.find_all('a')) + 1
    return pages
    
def scrape_search(search, quick_search=False):
    soup = search_to_soup(search)
    results = get_results_from_soup(soup)

    num_pages = get_num_pages_from_soup(soup)

    if num_pages == 1 or quick_search:
        return results
    
    other_pages = selenium_pages(search, num_pages)
    for page in other_pages:
        soup = BeautifulSoup(page, 'html.parser')
        results += get_results_from_soup(soup)
    return results

def get_link_html(driver, link, pages):
    link.click()
    pages.append(driver.page_source)

def selenium_pages(search, num_pages):
    # add headless driver option
    from selenium.webdriver.firefox.options import Options
    options = Options()
    options.add_argument("--headless")

    url = get_search_url(search)
    drivers = []
    links = {}
    for i in range(2, num_pages + 1):
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        links[driver] = driver.find_element_by_link_text(str(i))
        drivers.append(driver)
    
    processes = []
    manager = multiprocessing.Manager()
    pages = manager.list()
    for driver in drivers:
        link = links[driver]
        processes.append(multiprocessing.Process(target=get_link_html, args=(driver, link, pages)))
    
    for process in processes:
        process.start()

    for process in processes:
        process.join()
    
    for driver in drivers:
        driver.close() 

    return pages

if __name__ == "__main__":
    search = input("Please enter a search:\n")
    results = scrape_search(search)
    print(len(results))
    
