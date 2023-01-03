#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

base_url = "https://github.com"
topics_url = "https://github.com/topics"

response = requests.get(topics_url)

if response.status_code != 200:
        raise Exception(" Failed to Load the Page ".format(topic_url))
        
content = response.text
doc = BeautifulSoup(content,'html.parser')     # Returns the Whole code of topics page


def get_titles(doc):
    topic_titles = []
    title_selector = "f3 lh-condensed mb-0 mt-1 Link--primary"
    topic_p_tags = doc.find_all('p', {"class":title_selector})
    for i in topic_p_tags:
        topic_titles.append(i.text)
    return topic_titles

def get_description(doc):
    topic_descriptions=[]
    desc_selector ="f5 color-fg-muted mb-0 mt-1"
    topic_p_tags = doc.find_all('p', {"class":desc_selector})
    for i in topic_p_tags:
        topic_descriptions.append(i.text.strip())
    return topic_descriptions

def get_url(doc):
    global topic_urls
    topic_urls = []
    base_url = "https://github.com"
    link_selector = "no-underline flex-grow-0"
    topic_link_tags = doc.find_all('a', {"class":link_selector})
    for i in topic_link_tags:
        topic_urls.append(base_url+i['href'])
    return topic_urls


def scrap_topics():
    """  Scraps the List of all topics from topic page
    """
    topic_dictionary = {
        "title":get_titles(doc),
        "description":get_description(doc),
        "url":get_url(doc)
    }
    topic_df = pd.DataFrame(topic_dictionary)
    return topic_df

scrap_topics()


# Now Getting the Information from inside each topics ( username,repositry name , repositery URL , stars) and save to csv file

def get_topic_repos(topic_url):
    """  This Function takes a topic URL and scrap the following information (username , repo name, repo URL and stars).
        and creates the  Dataframe from these information
    
    """
    
    response = requests.get(topic_url) # download the page of given URL
    if response.status_code != 200:
        raise Exception(" Failed to Load the Page ".format(topic_url))
    topic_doc = BeautifulSoup(response.text,"html.parser")
    
    # h3 tags contains username , repo URL and repo title.
    h3_tags=topic_doc.find_all('h3',{"class":"f3 color-fg-muted text-normal lh-condensed"})
    
    star_tags = topic_doc.find_all('span',{"class":"Counter js-social-count"})

    def star_count(star_str):
        star_str = star_str.strip()
        if star_str[-1]=='k':
            return int(float(star_str[:-1])*1000)
        return int(star_str)

    def get_repo_info(h3_tag,stars):
        a_tags = h3_tag.find_all("a")
        user_name = a_tags[0].text.strip()
        repo_name = a_tags[1].text.strip()
        repo_url = base_url + a_tags[1]['href']
        stars = star_count(stars.text)
        return user_name,repo_name,repo_url,stars
    repos_dictionary = {
        "username": [],
        "repo_name":[],
        "repo_url":[],
        "stars":[]
    }
    for i in range(len(h3_tags)):
        repo_info = get_repo_info(h3_tags[i],star_tags[i])
        repos_dictionary["username"].append(repo_info[0])
        repos_dictionary["repo_name"].append(repo_info[1])
        repos_dictionary["repo_url"].append(repo_info[2])
        repos_dictionary["stars"].append(repo_info[3])

    repo_df = pd.DataFrame(repos_dictionary)
    return repo_df


def save_to_csv(topic_url,topic_name):
    fname = topic_name + ".csv"
    if os.path.exists:
        print(" The File {} already Exists. Skipping...".format(fname))
        return
    topic_df = get_topic_repos(topic_url)
    topic_df.to_csv(fname , index=None)
    

def scrap_top_topics_repos():
    print("Scrapping List Of Topics ")
    df = scrap_topics()
    for index,row in df.iterrows():
        print("Scrapping top repositeries for '{}'".format(row['title']))
        save_to_csv(row['url'],row['title'])
        


scrap_top_topics_repos()

