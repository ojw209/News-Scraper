import requests
from bs4 import BeautifulSoup

base_url = "https://www.thepaperboy.com"
start_postfix_url = "/uk/2020/01/01/front-pages-archive.cfm"
start_url = base_url + start_postfix_url
url = start_url

#How many months to scan for
Months2Scan = 6

#Intialise list to store addresses of the collected front pages. 
Front_Page_List = []

for NMonth in range(Months2Scan):
    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    
    #This loop scrapes the front page urls for a single month.
    for Cal_Scan in soup.find_all('a', class_ = "calendar"):
        Front_Page_List.append(Cal_Scan['href'])
        print('Url Retrieved:', Cal_Scan['href'])
    
    #Scrape page to find link to next month.
    postfix_url = soup.find_all('a', class_ = "large")[1]['href']
    
    url = base_url + postfix_url
    

#Remove Duplicates
Front_Page_List = list( dict.fromkeys(Front_Page_List))



