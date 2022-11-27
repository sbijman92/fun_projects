'''
A program that counts all the words used in newsarticles on the main pages of a dutch newswebsite (www.nu.nl)
'''

import bs4, requests, re
import pandas as pd 

url = 'https://www.nu.nl'
res = requests.get(url)
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, 'html.parser')

# Emtpy list to store all the links in

links = []

# A for loop to get all the href on the main page.
for div in soup.findAll('div', {'zone clearfix'}):
    for li in div.findAll('li', attrs={'class': 'list__item--text'}):
        link = li.find('a')['href']
        links.append(link)

tekst = ''

# A for loop to get all the texts from the newsarticles pages.
for href in links:
    urlToOpen = url + href 
    res1 = requests.get(urlToOpen)
    res1.raise_for_status()
    soup1 = bs4.BeautifulSoup(res1.text, 'html.parser')
    
    for paragraph in soup1.findAll('p'): 
        tekst += paragraph.text

# Some regex to clean up the texts
titleTekst = tekst.title()
to_delete = re.compile(r'\.|\,|\n|\[bron\?\]|\[[0-9]*\]')
tekst_1 = re.sub('\.|\,|\n|\[bron\?\]|\[[0-9]*\]|·|', ' ', titleTekst)
tekst_2 = re.sub('\s\s', ' ', tekst_1)

# Function to cenvert the strings to a list
def string_to_list(string):
    listRes = list(string.split(' '))
    return listRes

list_of_string = string_to_list(tekst_2)

# Counting all the words used in the list above.
counts = dict()
for i in list_of_string:
    counts[i] = counts.get(i, 0) + 1
print(counts)

