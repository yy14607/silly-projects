# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 18:20:01 2020

@author: yuany
"""

import os, re
import pandas as pd
import numpy as np

os.chdir('.\\OneDrive\\Documents\\Github\\silly-projects\\scraping-CRR')
 
 
 # read txt file 
File =  open(r"irbassessment.txt","rb")
 
txt_raw = File.readlines()
 
File.close()
 
 # decode the bytes literals into utf-8 and remove the new line characters\n
txt = []
for i,j in enumerate(txt_raw):
    if txt_raw[i].decode('UTF-8') !='\n':
        txt.append(txt_raw[i].decode('UTF-8').replace('\n', '').replace('\r', ''))



# remove the headers and page numbers
pages = []
i = 0
while i < len(txt):
    if txt[i].strip() == 'FINAL DRAFT RTS ON ASSESSMENT METHODOLOGY FOR IRB' and re.match(r'^\d+\s*', txt[i+1]):
        pages += [txt[i+1].strip()]
        txt[i] = ''
        del txt[i+1]
        i += 1
        continue
    i += 1
    continue

# merge article title with number
articles = []
i = 0
while i < len(txt)-1:
    if re.match(r'^Article\s\d+$', txt[i]) and re.match(r'^.*[^\.]+$', txt[i+1]):
        if re.match(r'^[a-z\s]+$', txt[i+2]):
            txt[i+1] += ' ' + txt[i+2]
            del txt[i+2]
        txt[i] += ' ' + txt[i+1] + ' [title]'
        articles += [txt[i]]
        del txt[i+1]
        i += 1
        continue
    i += 1
    continue


# remove blank lines, and replace “” as "", remove '\x0c',  and remove blank lines     
txt = [i.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace('´', "'") for i in txt if i!='']     
     

# merge chapter title with numbering
chapters = []
i = 0
while i < len(txt)-1:
    if re.match(r'^CHAPTER\s\d+$', txt[i]) and re.match(r'^.*[^\.]+$', txt[i+1]):
        while re.match(r'^[a-z\d\-\sSA]+$', txt[i+2]):
            txt[i+1] += ' ' + txt[i+2]
            del txt[i+2]
        txt[i] += ' ' + txt[i+1] + ' [title]'
        chapters += [txt[i]]
        del txt[i+1]
        i += 1
        continue
    i += 1
    continue

# merge section title with numbering
sections = []
i = 0
while i < len(txt)-1:
    if re.match(r'^SECTION\s\d+$', txt[i]) and re.match(r'^[A-Z\s\-]+$', txt[i+1]):
        if re.match(r'^[A-Z\s]+$', txt[i+2]):
            txt[i+1] += ' ' + txt[i+2]
            del txt[i+2]
        txt[i] += ' ' + txt[i+1] + ' [title]'
        sections += [txt[i]]
        del txt[i+1]
        i += 1
        continue
    i += 1
    continue


# find and remove strange patterns such as "the data o b t a i n e d f r o m i t "        
list_ind = []
for i in range(len(txt)):
    if re.match(r'^.*\s[a-z]\s[a-z]\s[a-z].*$', txt[i]):
        list_ind.append(i)
for i in list_ind:
    txt[i] = txt[i].replace('A r t i cl e', 'Article')
    txt[i] = txt[i].replace('A r t i c l e', 'Article')
    txt[i] = txt[i].replace('o b t a i n e d f r o m i t', 'obtained from it')
    txt[i] = txt[i].replace('a v a i l a b l e h i s t o r i c a l', 'available historical')

txt[-1] += '.'
txt[0] = '0 ' + txt[0]

txt[18]
txt[18] = 'firms and amending Regulation (EU) No 648/2012'
txt[36]
txt[36] = 'Regulation (EU) No 529/2014'
txt[47]
txt[47] = 'to use in accordance with Article 101(1) of Directive 2013/36/EU'
txt[417]
txt[417] = 'European Parliament and of the Council'
txt[445]
txt[445] = 'accordance with Article 101 of Directive 2013/36/EU of 26 June 2013'

# remove footnotes 
f_ind = [39,40,41,42,43,44,45, 91,92,93,94,419,420,421,422, 460, 461, 462, 463,3107, 3108, 3109,3110]
# [print(txt[i]) for i in f_ind]
txt =  [txt[i] for i in range(len(txt)) if i not in f_ind]



# merge unfinished sentences with previous element
i = len(txt) - 1
while i>0:
    if re.match(r'^[;,a-z]+.*', txt[i]):  
        txt[i-1] += ' ' + txt[i]
        del txt[i]
        i -= 1
        continue
    elif re.match(r'^.*[\.;:]$', txt[i]) and not re.match(r'.*\[title\]$', txt[i]):   
        while (not re.match(r'^\d+[\s\.]+.*', txt[i])) and (not re.match(r'^\([a-z\d]+\).*', txt[i])) and (not re.match(r'^.*\[title\]$', txt[i-1])):
            txt[i-1] += ' '+txt[i]
            del txt[i]
            i -= 1
        i -= 1
        continue
    else:
        i -= 1
        continue

df = pd.DataFrame(data={})
df['Chapter'] = ''
df['Section'] = ''
df['Article'] = ''
df['Paragraph'] = ''
# convert to df and save as csv
for i in range(len(txt)):
    if not re.match(r'.*\[title\]$', txt[i]):
        df.loc[i, 'Paragraph'] = txt[i]
    elif re.match(r'^CHAPTER\s.*$', txt[i]):
        df.loc[i, 'Chapter'] = txt[i].replace(' [title]', '')
    elif re.match(r'^SECTION\s.*$', txt[i]):
        df.loc[i, 'Section'] = txt[i].replace(' [title]', '') 
    elif re.match(r'^Article\s.*$', txt[i]):
        df.loc[i, 'Article'] = txt[i].replace(' [title]', '')
    else:
        print(i)
        
df.to_csv('GL IRB assessment checklist.csv', index=False)
    
        