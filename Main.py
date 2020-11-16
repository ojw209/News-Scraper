import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString, Comment

url = "https://www.thepaperboy.com/uk/the-mail-on-sunday/front-pages-today.cfm?frontpage=61580"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

soup.findAll('div', id="rssfeed")

for newsrss in soup.findAll('div', id="rssfeed"):
    article = newsrss.text
    print(article)
    
    