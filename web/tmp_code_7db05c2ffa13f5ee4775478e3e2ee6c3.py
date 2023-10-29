import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

start_url = "https://python.langchain.com/docs/get_started/introduction"
domain = "python.langchain.com"

def scrape_links(url):
    response = requests.get(url, timeout=5)  # Set a timeout of 5 seconds
    soup = BeautifulSoup(response.content, "html.parser")
    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href:
            absolute_url = urljoin(url, href)
            if absolute_url.startswith("/") or absolute_url.startswith("https://" + domain) or absolute_url.startswith("http://" + domain):
                links.append(absolute_url)
    return links

def scrape_all_links(url):
    visited = set()
    to_visit = [url]
    while to_visit:
        current_url = to_visit.pop(0)
        if current_url not in visited:
            visited.add(current_url)
            try:
                links = scrape_links(current_url)
                to_visit.extend(links)
            except requests.exceptions.Timeout:
                print(f"Timeout occurred while scraping: {current_url}")
    return visited

all_links = scrape_all_links(start_url)
print(all_links)