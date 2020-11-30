import pandas as pd

import nltk
from nltk.corpus import stopwords
nltk.download('wordnet')
nltk.download('stopwords')

import string
from collections import Counter

from bs4 import BeautifulSoup
import requests

import csv

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
    
    with open('Url_Error_List.txt', 'w') as f:
        for item in Url_Error_List:
            f.write("%s\n" % item)
    
    
    return Main_Store

#Function to tokenize text and carry out cleaning on text.
def Article_Normalizer(Word_List):
    
    try:
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
        
    except:
        print('Empty Article Found')
        Temp_Word_List = []
    
    return Temp_Word_List
    

#Function to merge daily and sunday papers together. Results saved under the daily paper name.
def UK_Paper_Merger(Data_Frame):
    
    Data_Frame = Data_Frame.fillna(0) 
    try:
        Data_Frame['Daily Express'] = Data_Frame['Daily Express'] + Data_Frame['Daily Express Sunday']
        del Data_Frame['Daily Express Sunday']
        
    except:
        print('Error: Problem merging Daily and Sunday Express')
    
    try:
        Data_Frame['Daily Mail'] = Data_Frame['Daily Mail'] + Data_Frame['The Mail on Sunday']
        del Data_Frame['The Mail on Sunday']
        
    except:
        print('Error: Problem merging Daily and Sunday Mail')
    
    try:
        Data_Frame['Daily Star'] = Data_Frame['Daily Star'] + Data_Frame['Daily Star Sunday']
        del Data_Frame['Daily Star Sunday']
    
    except:
        print('Error: Problem merging Daily and Sunday Star')
    
    try:
        Data_Frame['The Daily Telegraph'] = Data_Frame['The Daily Telegraph'] + Data_Frame['The Sunday Telegraph']
        del Data_Frame['The Sunday Telegraph']
        
    except:
      print('Error: Problem merging Daily and Sunday Telegraph')
    
    try:
        Data_Frame['The Guardian'] = Data_Frame['The Guardian'] + Data_Frame['The Observer']
        del Data_Frame['The Observer']
    
    except:
        print('Error: Problem merging Guardian and Observer')
    
    return Data_Frame

def Notepad_List_Extractor(FileName):
    
    Word_List = []
    FileName = FileName + '.txt'
    with open(FileName, 'r') as fd:
        reader = csv.reader(fd)
        for row in reader:
            Word_List.append(row)
    
    return Word_List


def Topic_Scanner(Word_List,Data_Frame,Topic):
    
    Temp_Store = pd.DataFrame(Data_Frame[['Date','Paper Name']])
    
    for KeyWord in Word_List:
        KeyWord = KeyWord[0]
        Temp_Store[KeyWord] = [Count[KeyWord] for Count in Data_Frame['Word_Count']]
    
    Temp_Store = pd.concat([pd.DataFrame(Data_Frame[['Date','Paper Name']]),Temp_Store.iloc[:, 2:].sum(axis=1)],axis=1)
    Temp_Store.columns = ['Date', 'Paper Name', Topic]
    
    
    return Temp_Store
    
#Define Starting URL to start scrapping from.
base_url = "https://www.thepaperboy.com"
start_postfix_url = "/uk/2018/01/01/front-pages-archive.cfm"
start_url = base_url + start_postfix_url

#How many months to scan for
Start_Date = '2019-01-01'
Months2Scan = 32

Daily_Overview_List, Front_Page_List = Address_Scraper(start_url)

Main_Store = Page_Scrapper(Front_Page_List)


#Retrieve list of lists of topic words that will be discovered in articles. 
Word_File_List = ['NHS_Word_Bank']
Topic_Words_List = []

for File_Name in Word_File_List:
    Topic_Words_List.append(Notepad_List_Extractor(File_Name))

#Normalize Text
for header in ['Art0','Art1','Art2','Art3','Art4']:
    Main_Store[header] = Main_Store[header].map(Article_Normalizer)
    
#Main_Store['Art0'] = Main_Store['Art0'].map(Article_Normalizer)
#Main_Store['Art1'] = Main_Store['Art1'].map(Article_Normalizer)
#Main_Store['Art2'] = Main_Store['Art2'].map(Article_Normalizer)
#Main_Store['Art3'] = Main_Store['Art3'].map(Article_Normalizer)
#Main_Store['Art4'] = Main_Store['Art4'].map(Article_Normalizer)

#NEED TO GENERALISE LINE - [Article Count fixed to 5 ]
Main_Store['FullArt'] = Main_Store['Art0'] + Main_Store['Art1'] + Main_Store['Art2'] + Main_Store['Art3'] + Main_Store['Art4']

#Convert data-time string to datetime format.
Main_Store['Date'] = pd.to_datetime(Main_Store['Date'])


#Create a dataframe with the Collections word counter function. (Stores a list
# of words with there orrurences counted)
Counter_Store = pd.DataFrame(Main_Store[['Date','Paper Name']])
Counter_Store['Word_Count'] = Main_Store['FullArt'].map(Counter)


#Temporary Topic Word
TopicWord = 'Health'
Word_List = Topic_Words_List[0]

KHealth_Store = Topic_Scanner(Word_List,Counter_Store, TopicWord)

KHealth_Store = KHealth_Store.pivot_table(index = 'Date', columns = 'Paper Name', values = TopicWord, aggfunc = 'first')

KHealth_Store  = UK_Paper_Merger(KHealth_Store)

KHealth_Store.to_csv('Health_Count_Paper.csv', sep=',')



Paper_Names = list(Counter_Store.columns.values)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyser = SentimentIntensityAnalyzer()


def sentiment_analyzer_scores(sentence):
    score = analyser.polarity_scores(sentence)
    print("{:-<40} {}".format(sentence, str(score)))
    
    
# https://pandas.pydata.org/pandas-docs/stable/user_guide/reshaping.html
# https://www.datacamp.com/community/tutorials/wordcloud-python




