# filename: scrape_links.py
import requests
from bs4 import BeautifulSoup

# Send a GET request to the webpage
url = "https://python.langchain.com/docs/get_started/introduction"
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Find all the <a> tags in the HTML
links = soup.find_all("a")

# Extract the href attribute from each <a> tag
for link in links:
    href = link.get("href")
    print(href)