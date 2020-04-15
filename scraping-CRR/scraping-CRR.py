# scraping CRR


import pandas as pd
import numpy as np
import os, re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException        


os.chdir("OneDrive\Documents")


# Initiate a webdriver and get the desired url
browserCRR = webdriver.Firefox()
browserCRR.get("https://eba.europa.eu/regulation-and-policy/single-rulebook/interactive-single-rulebook/504")


df = pd.DataFrame(data={})
df['Part'] = ''
df['Title'] = ''
df['Chapter'] = ''
df['Section'] = ''
df['Subsection'] = ''
df['Article'] = ''
df['Hyperlink'] = ''
df['Content'] = ''
df['Annex'] = ''

# from the table of contents page, extract all titles and hyperlinks (if any)

list_titles = browserCRR.find_elements_by_class_name('isrba')
for i,element in enumerate(list_titles):
    ttype = element.get_attribute('text-type')
    if ttype not in ['Document' , 'Recital', 'Signs', 'Ending'] :
        df.loc[i, ttype] = element.text
    if ttype in ['Article', 'Annex']:
        df.loc[i, 'Hyperlink'] = element.get_attribute('href')

df = df.reset_index(drop=True)

# retrieve contents in the details page
for i in range(len(df)):
    if df['Hyperlink'][i] is not np.nan:
        browserCRR.get(df['Hyperlink'][i])
        browserCRR.implicitly_wait(5) 
        ct = browserCRR.find_elements(By.XPATH, "//dd")[3].text
        df.loc[i, 'Content'] = ct


# for each row, remove the \n (newline) characters for better readability; 
for i in range(len(df)):
    if df['Content'][i] is np.nan:
        continue
    if '\n' in df['Content'][i]:
        paragraphs = df['Content'][i].split('\n')
        paragraphs = [re.sub('\(\d+\)\sOJ\sL.*?p\.\s\d+\.', '', j).strip() for j in paragraphs]
        paragraphs = [j for j in paragraphs if j.strip()!='']
        insert = (df.iloc[[i]])
        insert = insert.append([df.iloc[i]] * (len(paragraphs)-1)).reset_index(drop=True)
        insert['Content'] = paragraphs
        df = pd.concat([df.iloc[:i], insert, df.iloc[(i+1):]]).reset_index(drop=True)



# Extract article number from title;
# replace special characters “”; 
# remove footnotes in the form of (\d+) OJ L .* p\. \d+\.  
# remove empty lines
ind_rm = []
for i in range(len(df)):
    if (df['Article'][i] is not np.nan) and re.match('^Article (\d*?):', df['Article'][i]):
        df.loc[i, 'Article_number'] = re.search('^Article (\d*?):', df['Article'][i]).group(1)
        tmp = df.loc[i, 'Content']
        tmp = tmp.replace("“", '"')
        df.loc[i, 'Content'] = tmp.replace("”", '"')
        df.loc[i, 'Content'] = re.sub('\(\d+\)\sOJ\sL.*?p\.\s\d+\.', '', df.loc[i, 'Content']).strip()
        if df.loc[i, 'Content']=='':
            ind_rm.append(i)
df = df.drop(df.index[ind_rm]).reset_index(drop=True)

#df= pd.read_csv('CRR_checklist.csv')
df.to_csv('CRR_checklist.csv', index = False)
        
    



