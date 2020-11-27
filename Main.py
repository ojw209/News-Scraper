import pandas as pd

import nltk
from nltk.corpus import stopwords
nltk.download('wordnet')
nltk.download('stopwords')
import string

from bs4 import BeautifulSoup
import requests

import matplotlib.pyplot as plt


#Function scrapes 'ThePaperBoy' for a list of urls for newspaper front pages.
def Address_Scraper(start_url):
    
    url = start_url
    
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
    
    return Daily_Overview_List, Front_Page_List

#Functions scrapes a list of  front page urls for there article infomation.
def Page_Scrapper(Front_Page_List):
    
    #List of urls that triggered errors and thus no data was retrieved from.
    Url_Error_List = []
    
    #Temporary lists storing scrapped data, ready for putting into pandas
    Paper_Type_List = []
    Paper_Date_List = []
    Paper_Article_List = []
        
    for page_url in Front_Page_List:
        
        url = base_url + page_url
        
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        
        Temp_Article = []
        
        #Extract data from news page - including paper type and date.
        try:
            
            Meta_Page_Text = soup.find('h1').text
        
            Temp_Paper_Type = Meta_Page_Text.partition("Headlines")[0][:-1]
            Temp_Paper_Date = Meta_Page_Text.partition("Headlines")[2][1:]
            
            Paper_Type_List.append(Temp_Paper_Type)
            Paper_Date_List.append(Temp_Paper_Date)
            
            #Extract rss feeds from newspaper page - equates to around 5 or 6 news articles per a page.
            for newsrss in soup.findAll('div', id="rssfeed"):
                
                Temp_Article.append(newsrss.text.split())
            #Creates a list of lists of news articles for that page.
            Paper_Article_List.append(Temp_Article)
                
        except:       
            
            print("Error at:", url)
            Url_Error_List.append(page_url)
        
    
    #Create a pandas dataframe for the newspaper name and date.
    Paper_Data = {'Date': Paper_Date_List, 'Paper Name':Paper_Type_List}
    Paper_Data_Store = pd.DataFrame(Paper_Data)
    
    #Create a pandas dataframe just for the newspaper articles
    Article_Data_Store = pd.DataFrame(Paper_Article_List, columns = [('Art' + str(i)) for i in range(5)]) 
    
    #Merge these 2 dataframes.
    Main_Store =  pd.concat([Paper_Data_Store, Article_Data_Store], axis=1, join='inner')
    
    
    
    return Main_Store, Url_Error_List

def Article_Normalizer(Word_List):
    
    #Define Punctuation string to remove. 
    Punc2Remove = string.punctuation + "“”’"
    
    #Define Stop Words
    stop_words = set(stopwords.words('english'))
    
    #NLTK lemmatizer dictionary
    lemma = nltk.wordnet.WordNetLemmatizer()
    
    #Lemmatize words
    Temp_Word_List = [lemma.lemmatize(t) for t in Word_List]
    
    #Convert all Tokents to lower-case
    Temp_Word_List = [t.lower() for t in Temp_Word_List]
    
    #Remove Punctuation from Strings
    Temp_Word_List = [t.translate(str.maketrans('','',Punc2Remove)) for t in Temp_Word_List]
    
    #Remove non-alphabetic words
    Temp_Word_List = [t for t in Temp_Word_List if t.isalpha()]
    
    #Remove Stop Words
    Temp_Word_List = [t for t in Temp_Word_List if not t in stop_words]
    
    return Temp_Word_List
    
    
#Define Starting URL to start scrapping from.
base_url = "https://www.thepaperboy.com"
start_postfix_url = "/uk/2020/01/01/front-pages-archive.cfm"
start_url = base_url + start_postfix_url

#How many months to scan for
Start_Date = '2020-01-01'
Months2Scan = 6

Daily_Overview_List, Front_Page_List = Address_Scraper(start_url)

Main_Store, Url_Error_List = Page_Scrapper(Front_Page_List)

#Normalize Text [Code needs generalizing]
Main_Store['Art0'] = Main_Store['Art0'].map(Article_Normalizer)
Main_Store['Art1'] = Main_Store['Art1'].map(Article_Normalizer)
Main_Store['Art2'] = Main_Store['Art2'].map(Article_Normalizer)
Main_Store['Art3'] = Main_Store['Art3'].map(Article_Normalizer)
Main_Store['Art4'] = Main_Store['Art4'].map(Article_Normalizer)

#NEED TO GENERALISE LINE - [Article Count fixed to 5 ]
Main_Store['FullArt'] = Main_Store['Art0'] + Main_Store['Art1'] + Main_Store['Art2'] + Main_Store['Art3'] + Main_Store['Art4']

#Convert data-time string to datetime format.
Main_Store['Date'] = pd.to_datetime(Main_Store['Date'])


from collections import Counter

Main_Store['Word_Count'] = Main_Store['FullArt'].map(Counter)

key_word = 'coronavirus'

Plot_Store = pd.DataFrame(pd.to_datetime(Main_Store['Date']))

plt.plot(Main_Store['Trump_Count'])

#test = Counter(Main_Store['FullArt'][1].split()).most_common()

