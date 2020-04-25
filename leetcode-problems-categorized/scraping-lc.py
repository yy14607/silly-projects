# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 19:38:14 2020

To scrape the problems list of Leetcode.
Prerequisites:
    
- Selenium
- A web browser and corresponding webdriver (I'm using Firefox and Geckodriver)



@author: yuany
"""

import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException        


os.chdir("OneDrive\Documents\Github\leetcode-problems-categorized")


# Initiate a webdriver and get the desired url
browserLC = webdriver.Firefox()
browserLC.get("https://leetcode.com/problemset/all/")

browserLC.implicitly_wait(5) 

# define the relative xpath of the row selector 
# so that all problems are displayed on one page
xpath_rowselect = "//span[@class='row-selector']/select"
rowselector = Select(browserLC.find_element(By.XPATH, xpath_rowselect))
rowselector.select_by_visible_text("all")


# find all the href of problems listed on this page
xpath_problems = "//div[@class='table-responsive question-list-table']/table/tbody/tr/td/div/a"

list_problems = browserLC.find_elements(By.XPATH, xpath_problems)
list_href = []
for i in list_problems:
    href = i.get_attribute("href")
    list_href.append(href)

#df = pd.DataFrame(data={"href": list_href})
#
#
#df['title'] = ''
#df['difficulty'] = ''
#df['content'] = ''
#df['like'] = 0
#df['dislike'] = 0
#df['accepted'] = 0
#df['submissions'] = 0
#df['related_topics'] = ''
#df['similar_questions'] = ''
#df['hints'] = ''
#df['complete'] = ''

df = pd.read_csv('LC_problems.csv')

if len(set(list_href) - set(df['href'])) !=0:
    df_append = pd.DataFrame(data={'href': list(set(list_href) - set(df['href'])),
                                   'title': '', 'difficulty': '', 'content': '', 
                                   'like': 0, 'dislike': 0, 'accepted': 0, 
                                   'submissions': 0, 'related_topics': '', 
                                   'similar_questions': '', 'hints': '', 'complete': ''})
    df = pd.concat([df, df_append], sort=False, ignore_index = True)


not_complete = [i for i in range(len(df)) if df.loc[i, 'complete']!='y' and df.loc[i, 'complete']!='locked']

# for each problem, load the url and extraxt the relevant info:
for i in not_complete:
    href = df["href"][i]
    browserLC.get(href)
    try:
        browserLC.find_element_by_id('initial-loading')
        browserLC.implicitly_wait(3) 
    except NoSuchElementException:
        print(i)
        
    if 'login' in browserLC.current_url:
        df.loc[i, 'complete'] = 'locked'
        continue
    title = browserLC.find_element(By.XPATH, 
                                   "//div[@data-cy='question-title']").text
    diff = browserLC.find_element(By.XPATH, 
                                  "//div[@diff='easy']|//div[@diff='medium']|//div[@diff='hard']").text
    content = browserLC.find_elements(By.XPATH, 
                                  "//div[contains(@class, 'question-content')]/div/p|//div[contains(@class, 'question-content')]/div/pre|//div[contains(@class, 'question-content')]/div/ul")
    contents = ""
    if len(content)>=1:
        for j in content:
            contents += j.text + "\n"
    
    headers = browserLC.find_elements(By.XPATH, 
                              "//span[@class='title_3f2k']")
    likes = browserLC.find_elements(By.XPATH, 
                              "//button[contains(@class, 'btn__r7r7')]/span")
    accepted = browserLC.find_elements(By.XPATH, 
                              "//div[@class='css-jkjiwi']")
    
    df.loc[i, 'title'] = title
    df.loc[i, 'difficulty'] = diff
    df.loc[i, 'content'] = contents
    df.loc[i, 'like'] = int(likes[0].text.replace(",", ""))
    df.loc[i, 'dislike'] = int(likes[1].text.replace(",", ""))
    df.loc[i, 'accepted'] = int(accepted[0].text.replace(",", ""))
    df.loc[i, 'submissions'] = int(accepted[1].text.replace(",", ""))
    
    tags_element = browserLC.find_elements(By.XPATH, 
                              "//a[contains(@class, 'topic-tag')]")
    tags = ""
    if len(tags_element)>=1:
        for j in tags_element:
            tags += j.get_attribute("href") + "\n"
    tags = tags[:-1]
    
    df.loc[i, 'related_topics'] = tags
      
    
    hints_element = browserLC.find_elements(By.XPATH, 
                              "//div[./div/div[contains(text(), 'Show Hint')]]")
    
    hints = ""
    if len(hints_element)>=1:
        for j in hints_element:
            j.click()
            hints += j.find_element_by_xpath("./following-sibling::div").text  + "\n"
            j.click()
            
    q_element = browserLC.find_elements(By.XPATH, 
                              "//div[./div/div[contains(text(), 'Similar Questions')]]")
    
    questions = ""
    if len(q_element)>=1:
        for j in q_element:
            j.click()
            questions += j.find_element_by_xpath("./following-sibling::div").text  + "\n"
            j.click()
    
    df.loc[i, 'similar_questions'] = questions
    
    df.loc[i, 'hints'] = hints
    
    df.loc[i, 'complete'] = 'y'

df['acceptance_rate'] = df['accepted']/df['submissions'] 
df['like_rate'] = df['like']/(df['like'] + df['dislike'])
#
#
#df_complete = df[df['complete']=='y']
#a = df_complete.loc[df_complete['related_topics'].str.contains('hash', na=False)]
#a = a.sort_values(['like_rate', 'acceptance_rate'], ascending=[False, True])

    
df.to_csv("LC_problems.csv", index= False)    
    
    












