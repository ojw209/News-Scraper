import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

base_url = "https://www.thepaperboy.com"
start_postfix_url = "/uk/2020/01/01/front-pages-archive.cfm"
start_url = base_url + start_postfix_url
url = start_url

#How many months to scan for
Start_Date = '2020-01-01'
Months2Scan = 2

#Intialise list to store addresses of the collected website daily sumamrys. 
Daily_Overview_List = []

for NMonth in range(Months2Scan):
    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    
    #This loop scrapes the front page urls for a single month.
    for Cal_Scan in soup.find_all('a', class_ = "calendar"):
        Daily_Overview_List.append(Cal_Scan['href'])
        #print('Url Retrieved:', Cal_Scan['href'])
    
    #Scrape page to find link to next month.
    postfix_url = soup.find_all('a', class_ = "large")[1]['href']
    
    url = base_url + postfix_url
    

#Remove Duplicates
Daily_Overview_List = list( dict.fromkeys(Daily_Overview_List))


#Intialise list to store addresses of the collected front pages. 
Front_Page_List = []


#Retrieve Urls for indiviudal newspaper from the urls retrieved for website daily sumamrys   
for front_page_url in Daily_Overview_List:
    print(front_page_url)
    url = base_url + front_page_url
    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    for Front_Page in soup.find_all('span', class_ = "pdcover"):
        Front_Page_List.append(Front_Page.contents[1]['href'])

#Remove Duplicates 
Front_Page_List = list( dict.fromkeys(Front_Page_List))
        
Main_Data_Store = pd.date_range(Start_Date, periods = len(Daily_Overview_List))        
    
for page_url in Front_Page_List:
    
    url = base_url + page_url
    
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    
    print(page_url)