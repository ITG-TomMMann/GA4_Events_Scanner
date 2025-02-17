
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 12:03:46 2024

PART 1

EXTRACTING WEB PAGE TEXT TO HELP WITH IDENTIFYING CONTENT ON WEBSITE

@author: martinconnor
"""

# pip install requests beautifulsoup4 pandas nltk spacy
# pip install requests beautifulsoup4 selenium webdriver_manager
# python -m spacy download en_core_web_sm

import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta




# WHICH MARKETS IS THIS FOR?
lst_markets = ['US','GB','DE']

# WHICH URL ARE WE STARTING FROM?
# BASE URLs TO START FROM
homepage_urls = ['https://www.landroverusa.com','https://www.landrover.co.uk/','https://www.landrover.de/']

# Dictionary of the Markets and URLs
# USing the URLs as the key as we might use multiple domains (eg. config) in the future
dict_homepage_urls ={'https://www.landroverusa.com' : 'US',
     'https://www.landrover.co.uk/' : 'GB',
     'https://www.landrover.de/' : 'DE'}


# BigQuery file to read in?
# BQ_filename = 'ITG_MC_CONTENT_GROUPS_MM.csv'

# =============================================================================
# CRALWERS FOR JUST THE LINKS
# =============================================================================

import requests
from bs4 import BeautifulSoup
# import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    return driver


def get_all_links(base_url, current_url, visited):
    """Recursively crawl a website and collect all links."""
    if current_url in visited:
        return []  # Avoid revisiting the same URL
    
    visited.add(current_url)
    
    try:
        response = requests.get(current_url)
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Failed to access {current_url}: {e}")
        return []
    
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        
        if link.startswith('/'):
            link = base_url + link
        elif not link.startswith('http'):
            continue  # Skip links that are not valid URLs
        
        if link.startswith(base_url) and link not in visited:
            links.append(link)
            links.extend(get_all_links(base_url, link, visited))
    
    return links

def crawl_website(base_url):
    """Crawl the website starting from base_url and return a DataFrame of all links found."""
    visited = set()
    all_links = get_all_links(base_url, base_url, visited)
    
    # Create a DataFrame from the list of links
    df = pd.DataFrame(all_links, columns=['URL'])
    return df

# RUN THE CRAWL AND CREATE A DF WITH THE URLs
# df_links = crawl_website(homepage_url)

# for key, value in dict_homepage_urls.items:
#     f'df_links_{value}' = crawl_website(key)
# # Example dictionary of URLs and corresponding countries
# url_dict = {
#     "https://example.com": "GB",
#     "https://another-example.com": "DE",
#     "https://site.com": "US"
# }

# Dictionary to store the DataFrames
df_links_dict = {}
# Loop through the dictionary and call the crawl_website function
for url, country in dict_homepage_urls.items():
    df_links_dict[country] = crawl_website(url)  # Store DataFrame with country as key


# Access individual DataFrames like:
# df_dict["GB"], df_dict["DE"], df_dict["US"]

    
# Display the DataFrame
print(df_links_dict["GB"].head())

# Save to CSV if needed
# site = 'US'
# current_date = datetime.now()
# date_string = current_date.strftime("%Y-%m-%d")
# links_filename = 'all_links_' + site + '_' + date_string + '.csv'
# df_links_dict[country].to_csv(links_filename, index=False)

for country in df_links_dict:
    site = country
    current_date = datetime.now()
    date_string = current_date.strftime("%Y-%m-%d")
    links_filename = 'all_links_' + country + '_' + date_string + '.csv'
    df_links_dict[country].to_csv(links_filename, index=False)

# Now do the screenshots with the precrawled links
links = set(df_links_dict['GB']['URL'])
df_gb = df_links_dict['GB']



