import requests
import pandas as pd
import random
from dotenv import load_dotenv
import os
from pytrends.request import TrendReq
load_dotenv()


df = pd.read_csv('temperatures.csv', header=None, names=['County', 'State'])
df2 = pd.read_csv('uscounties.csv', header=None, names=['County', 'State', 'Latitude', 'Longitude'])

def get_score(state: str):
    url = f"https://api.w1111am.xyz:8443/get_score?state={state}&password={os.getenv('ESG_SECRET_KEY')}"
    response = requests.get(url)
    data = response.json()
    if 'error' in data:
        return data['error']
    # example response {'Environmental Score': 0.8799876675480947, 'State': 'West Virginia'}
    # return ENV score
    return data['Environmental Score']

def get_county(state): 
    counties = df[df['State'].str.lower() == state.lower()]['County'].tolist()
    return counties    

def get_latitude(county, state): 
    result = df2[(df2['County'].str.lower() == county.lower()) & (df2['State'].str.lower() == state.lower())]
    
    return result['Latitude'].values[0]

def get_longtitude(county, state):
    result = df2[(df2['County'].str.lower() == county.lower()) & (df2['State'].str.lower() == state.lower())]
    return result['Longitude'].values[0]

def get_news(region: str):
    if region == '':
        return "Invalid input for region"
    
    badNews = ['hurricane', 'tornado', 'earthquake', 'flood', 'drought', 'tsunami', 'volcano', 'blizzard', 'avalanche', 'heatwave', 'coldwave', 'storm', 'cyclone', 'typhoon', 'landslide', 'sinkhole']
    keyword = random.choice(badNews)
    url = f"https://newsapi.org/v2/everything?q={region}%20{keyword}&sortBy=relevancy&apiKey={os.getenv('NEWS_API_KEY')}"
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        return "Region not found"
    
    if data['totalResults'] == 0:
        return "No news found", "No news found"
    
    valid_articles = [
        article for article in data['articles']
        if article['title'] != "[Removed]" and article['url'] != "https://removed.com"
    ]
    
    if valid_articles:
        chosen_article = random.choice(valid_articles)
        return chosen_article['title'], chosen_article['url']
    
    return "No valid news found", "No valid news found"

def fetch_trends_data(region: str):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload([region], timeframe='now 7-d', geo='US')
    data = pytrends.interest_over_time()
    data_cleaned = data.dropna()
 
    return data_cleaned.values