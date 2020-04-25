# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 04:11:23 2020

@author: yuany
"""


import os, re
import pandas as pd
import numpy as np

os.chdir('.\\OneDrive\\Documents\\Github\\silly-projects\\scraping-CRR')
 
 
 # read txt file 
#File =  open(r"GL on DoD.txt","rb")
#File =  open(r"GL on LGD downturn.txt","rb")
File =  open(r"GL on PD LGD.txt","rb")
#hdr = "FINAL REPORT ON GUIDELINES ON THE APPLICATION OF THE DEFINITION OF DEFAULT"
#hdr = "GL FOR THE ESTIMATION OF LGD APPROPRIATE FOR AN ECONOMIC DOWNTURN"
hdr = "GUIDELINES ON PD ESTIMATION, LGD ESTIMATION AND TREATMENT DEFAULTED EXPOSURES"
 
txt_raw = File.readlines()
 
File.close()
 
 # decode the bytes literals into utf-8 and remove the new line characters\n
txt = []
for i,j in enumerate(txt_raw):
    if txt_raw[i].decode('UTF-8') !='\n':
        txt.append(txt_raw[i].decode('UTF-8').replace('\n', '').replace('\r', ''))

# remove page numbers, page headers and blank lines
i = 1
while i<len(txt):
    if txt[i]==hdr and re.match(r'^\d+$', txt[i+1]):
        del txt[i+1]
        del txt[i]
        continue
    elif txt[i]=='':
        del txt[i]
    else:
        i += 1

# remove blank lines, and replace “” as "", remove '\x0c',  and remove blank lines     
txt = [i.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace('´', "'") for i in txt if i!='']     
     
# merge unfinished sentences
i=0
while i<len(txt):
    if (re.match(r'^[a-z\.,;\-]+.*', txt[i]) ) or \
    (re.match(r'^Approach.*', txt[i]) and  re.match(r'.*IRB$', txt[i-1])  ) or \
    (re.match(r'^\d+.*', txt[i]) and re.match(r'.*(?:Article|paragraph)$', txt[i-1]) ) or \
    re.match(r'.*\s(?:the|to|and|a|an|No|NO|on|\[EBA|,|of)$', txt[i-1]):
        txt[i-1] += ' '+ txt[i]
        del txt[i]
    else: 
        i+=1
        

# get Chapter titles (number XXXX)
chapters = []
i = 0
while i < len(txt)-1:
    if re.match(r'^\d+\s[A-Z]+[A-Za-z\s\-,]+$', txt[i]):
        txt[i] += ' [title]'
        chapters += [txt[i]]
    i += 1

# get section titles (number.number XXXX)
sections = []
i = 0
while i < len(txt)-1:
    if re.match(r'^\d+\.\d+\s[A-Z]+[A-Za-z\s\-,]+$', txt[i]):
        txt[i] += ' [title]'
        sections += [txt[i]]
    i += 1
    
# get subsection titles (number.number.number XXXX)
subsections = []
i = 0
while i < len(txt)-1:
    if re.match(r'^\d+\.\d+\.\d+\s[A-Z]+[A-Za-z\s\-,]+$', txt[i]):
        txt[i] += ' [title]'
        subsections += [txt[i]]
    i += 1
    
# get topics
topics = []
i=0
while i < len(txt)-1:
    if re.match(r'^[A-Z]+[A-Za-z\s\-,\(\)]+$', txt[i]) and re.match(r'^\d+\.\s[A-Z]+.*', txt[i+1]):
        txt[i] += ' [title]'
        topics += [txt[i]]
    i += 1        


# merge sentences from the last line until the sentence starts with a numbering format ("1. ", "(a)", )
i = len(txt)-1
while i>0:
    if re.match(r'.*\.$', txt[i]) and not re.match(r'.*[title]$', txt[i-1]) \
    and not re.match(r'^\d+\.\s[A-Z]+.*', txt[i]) and not re.match(r'^\([a-z]\)\s[A-Z]+.*', txt[i]):
        txt[i-1] += ' ' + txt[i]
        del txt[i]
    i-=1



    
# write to csv
df = pd.DataFrame(data={})
df['Section'] = ''
df['Subsection'] = ''
df['Subsubsection'] = ''
df['Topic'] = ''
df['Paragraph'] = ''        
i = 0
while i<len(txt):
    if re.match(r'^\d+\s[A-Z]+[A-Za-z\s\-,]+\[title\]$', txt[i]):
        df.loc[i, 'Section'] = txt[i].replace(' [title]', '')
    elif re.match(r'^\d+\.\d+\s[A-Z]+[A-Za-z\s\-,]+\[title\]$', txt[i]):
        df.loc[i, 'Subsection'] = txt[i].replace(' [title]', '')
    elif re.match(r'^\d+\.\d+\.\d+\s[A-Z]+[A-Za-z\s\-,]+\[title\]$', txt[i]):
        df.loc[i, 'Subsubsection'] = txt[i].replace(' [title]', '')
    elif re.match(r'[A-Z]+.*\[title\]$', txt[i]):
        df.loc[i, 'Topic'] = txt[i].replace(' [title]', '')
    else:
        df.loc[i, 'Paragraph'] = txt[i]
    i+=1
    
df.to_csv('GL on PD LGD checklist.csv', index=False)    

    
    

#while i<len(txt):
#    if re.match(r'\d+\s.*\[title\]$', txt[i]):
#        df.loc[i, 'Section'] = txt[i].replace(' [title]', '')
#    elif re.match(r'[A-Z]+.*\[title\]$', txt[i]):
#        df.loc[i, 'Topic'] = txt[i].replace(' [title]', '')
#    else:
#        df.loc[i, 'Paragraph'] = txt[i]
#    i+=1
#    
#df.to_csv('GL LGD downturn checklist.csv', index=False)    

    
    
        