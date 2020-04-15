# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 23:31:08 2020
Scraping other guidelines available as pdf version
First use any online pdf converter to convert to txt file
@author: yuany
"""

import os, re
import pandas as pd
import numpy as np

os.chdir('.\\OneDrive\\Documents\\Github\\silly-projects\\scraping-CRR')
 
 
 # read txt file 
File =  open(r"ssm.guidetointernalmodels_consolidated.txt","rb")
 
txt_raw = File.readlines()
 
File.close()
 
 # decode the bytes literals into utf-8 and remove the new line characters\n
txt = []
for i,j in enumerate(txt_raw):
    if txt_raw[i].decode('UTF-8') !='\n':
        txt.append(txt_raw[i].decode('UTF-8').replace('\n', ''))

# remove page numbers
i = 1
while i<len(txt):
    if 'ECB guide to internal models – ' in txt[i] and re.match(r'^\d+$', txt[i+1]):
        txt[i] = 'End of page'
        del txt[i+1]
        i += 1
        continue
    else:
        i += 1


# remove blank lines, and replace “” as "", remove '\x0c',  and remove blank lines     
txt = [i.replace("“", '"').replace("”", '"').replace("’", "'").replace('\x0c', '') for i in txt if i!='']     
        

# skip table of contents
for i in range(len(txt)):
    if txt[i]=='End of page' and txt[i+1]=='Foreword':
        break
txt = txt[(i+1):]


# remove market risk chapters

for i in range(len(txt)):
    if txt[i]=='End of page' and txt[i+1]=='Market risk':
        break
txt = txt[:i]



 # if the first letter in a line is lower case or space, merge it with the previous line
i = 1
while i< len(txt):
    j = txt[i]
    if j=='End of page':
        i += 2
        continue
    if re.match(r'^[a-z\(\"]', j):
       txt[i-1] = txt[i-1] + ' ' + j
       del txt[i]
    elif re.match(r'^\s[a-zA-Z]+', j) and (not re.match(r'\d\.?', txt[i-1][-1])):
       txt[i-1] = txt[i-1] + j
       del txt[i]
    else:
        i += 1

# if an element ends with a period and the previous element is not purely number, merge it with the previous element
i = len(txt)-1
while i>1:
    if (not re.match(r'.*[a-zA-Z\)\"]\.', txt[i])) or re.match(r'^\d+\.\s.*', txt[i]) :
        i-=1
        continue
    else:
        while txt[i-1]!='End of page' and (re.match(r'.*[a-zA-Z]+.*', txt[i-1])) and (not re.match(r'^\d+\.\s.*', txt[i])):
            txt[i-1] = txt[i-1] + ' ' + txt[i]
            del txt[i]
            i -= 1
        i -= 1
        continue
    
        

# Merge articles with their numbering
i = 1
while i< len(txt):
    if re.match(r'^\d+\.$', txt[i-1]) and (re.match(r'.*[a-z]+.*', txt[i]) is not None):
        txt[i-1] = txt[i-1] + ' ' + txt[i]
        del txt[i]
    else:
        i += 1

# merge foot notes with their numbering
i = 1
while i< len(txt):
    if re.match(r'^\d+$', txt[i-1]) and (re.match(r'.*[a-z]+.*\.$', txt[i]) is not None):
        txt[i-1] = txt[i-1] + ' ' + txt[i]
        del txt[i]
    else:
        i += 1

# remove regulatory references table
i = 1
while i  < len(txt):
    if re.match('Relevant regulatory references', txt[i]) or re.match('Regulatory references', txt[i]):
        if re.match(r'^[\d\.]+$', txt[i-1]):
            section_reg = txt[i-1]
            section_next = section_reg[:-1]+str(int(section_reg[-1]) + 1)
            j = i
            while txt[j]!=section_next and (re.match(r'^\d+\.+.*[A-Za-z]+.*', txt[j]) is None):
                j+=1
            del txt[(i+1):j]
            i += 1
        else:
            j = i
            while (re.match(r'^[\d\.]+.*', txt[j]) is None):
                j+=1
            del txt[(i+1):j]
            i += 1           
    else: 
        i += 1



        

# remove footnotes
i = 1
while i < len(txt):
    if re.match(r'^\d+\s[A-Za-z]+.*\.$', txt[i]) or txt[i] == 'End of page':
        del txt[i]
        continue
    else:
        i += 1




        
# Merge section with section numbering
i = 1
while i < len(txt):
    if re.match(r'^[\d\.]+$', txt[i-1]) and re.match(r'^[A-Za-z]+.*', txt[i]):
        txt[i-1] = txt[i-1] + ' '+ txt[i]
        del txt[i]
    else:
        i += 1
        


# some manual asjustments still needs to be made
        
df = pd.DataFrame(data={'txt':txt})
df.to_csv('ECB_guide.csv', index=False)

# read csv after manual changes
csv = pd.read_csv('Credit risk.csv', index_col = None)

# create df with section headers 
df = pd.DataFrame(data={})
df['Topic'] = ''
df['Chapter'] = ''
df['Section'] = ''
df['Subsection'] = ''
df['Article'] = ''
df['Content'] = ''

for i in range(len(csv)):
    if re.match(r'^[a-zA-Z]+.*[a-zA-Z\s\)]$', csv['Credit risk'][i]):
        df.loc[i, 'Topic'] = csv['Credit risk'][i]
    elif re.match(r'^\d+\s.*[a-zA-Z\s\)]$', csv['Credit risk'][i]):
        df.loc[i, 'Chapter'] = csv['Credit risk'][i]
    elif re.match(r'^\d+\.\d+\s.*[a-zA-Z\s\)]$', csv['Credit risk'][i]):
        df.loc[i, 'Section'] = csv['Credit risk'][i]
    elif re.match(r'^\d+\.\d+\.\d+\s.*[a-zA-Z\s\)]$', csv['Credit risk'][i]):
        df.loc[i, 'Subsection'] = csv['Credit risk'][i]   
    elif re.match(r'^\d+\.\s.*[a-zA-Z\d\.\)]+[\.\s]$', csv['Credit risk'][i]):
        df.loc[i, 'Article'] = re.match(r'^(\d+)?(\.\s.*[a-zA-Z\s\.])$', csv['Credit risk'][i]).group(1)
        df.loc[i, 'Content'] = re.match(r'^\d+\.\s(.*[a-zA-Z\s\.])?$', csv['Credit risk'][i]).group(1)
    else:
        print(i)
        


