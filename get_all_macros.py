# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 06:27:23 2022

@author: stefa
"""

''' 
A program that gets all products from a supermarket. 
It saves all corresponding macro-nutritions and saves them in an excel file.
'''
import bs4, requests, re, json, time
import pandas as pd 

# Lists in where the products are stored.
first_categories = []
categories_to_use = []
next_input = []
last_output = []
produts = []
product_list = [] 


# Products are stored in categories. This first function gets all links to the different categories.
def get_all_first_categories(openurl): 
    global first_categories
    url = 'https://www.ah.nl/producten'
    res = requests.get(url) 
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    for links in soup.findAll('a', href=re.compile('^/producten/[^m]')):
        link = links.attrs['href'] 
        if link not in first_categories: 
            link_sliced = link[10:]
            first_categories.append(link_sliced)
                
# After getting the links from all the categories. THe products are stored in two smaller categories. Next two functions get the links to those pages. 
def get_all_links(x): 
    base_url = "https://www.ah.nl/producten/aardappel-groente-fruit"
    url = base_url + str(x)

    html_doc = requests.get(url).text

    data = re.search(r"window\.__INITIAL_STATE__= ({.*})", html_doc)
    data = data.group(1).replace("undefined", "null")
    data = json.loads(data)

# uncomment this to print all data:
# print(json.dumps(data, indent=4))
    
    taxonomies = {t["id"]: t for t in data["taxonomy"]["topLevel"]}
    for t in data["taxonomy"]["taxonomies"]:
        taxonomies[t["id"]] = t


    def get_taxonomy(t, current, dupl=None):
        if dupl is None:
            dupl = set()
        tmp = current + "/" + t["slugifiedName"]
        yield tmp
        for c in t["children"]:
            if c in taxonomies and c not in dupl:
                dupl.add(c)
                yield from get_taxonomy(taxonomies[c], tmp, dupl)
    
    global next_input 
    for t in taxonomies.values():
        if t["parents"] == [0]:
            for t in get_taxonomy(t, base_url):
                if url in t:  # print only URL from current category
                    t_sliced = t[27:]  
                    next_input.append(t_sliced)
    
# Same as function above
def get_all_last_links(y): 
    base_url = "https://www.ah.nl/producten"
    url = base_url + str(y)

    html_doc = requests.get(url).text

    data = re.search(r"window\.__INITIAL_STATE__= ({.*})", html_doc)
    data = data.group(1).replace("undefined", "null")
    data = json.loads(data)

# uncomment this to print all data:
# print(json.dumps(data, indent=4))
    
    taxonomies = {t["id"]: t for t in data["taxonomy"]["topLevel"]}
    for t in data["taxonomy"]["taxonomies"]:
        taxonomies[t["id"]] = t


    def get_taxonomy(t, current, dupl=None):
        if dupl is None:
            dupl = set()
        tmp = current + "/" + t["slugifiedName"]
        yield tmp
        for c in t["children"]:
            if c in taxonomies and c not in dupl:
                dupl.add(c)
                yield from get_taxonomy(taxonomies[c], tmp, dupl)
    
    global last_output
    for t in taxonomies.values():
        if t["parents"] == [0]:
            for t in get_taxonomy(t, base_url):
                if url in t:  # print only URL from current category
                    t_sliced = t[27:]  
                    last_output.append(t_sliced)
 

def get_final_page(z):   
    base_url = 'https://www.ah.nl/producten/'
    url = base_url + str(z)
    res = requests.get(url) 
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    for page_product in soup.findAll('a', href = re.compile('producten/product/w')):
             product = page_product.attrs['href']
             if product not in product_list:
                 product_list.append(product)
    
get_all_first_categories('')

categories_to_use = list(dict.fromkeys(first_categories))
categories_to_use.pop(15)
categories_to_use.pop(13)
categories_to_use.pop(10)
categories_to_use.pop(9)
categories_to_use.pop(8)
categories_to_use.pop(0)
categories_to_use.pop(9)
categories_to_use.pop(10)
categories_to_use.pop(10)

# Loops to go trhough all pages and get next link. Last loop gets the final product pages.
count = 0
for link in categories_to_use:
    get_all_links(link)
    time.sleep(0.5)
    count += 1
    print('Single product page number ' + str(count))

count = 0 
 
for link in next_input:
    get_all_last_links(link) 
    count += 1
    print('Next input page number ' + str(count))

count = 0 

for link in last_output:
    get_final_page(link)
    time.sleep(0.2)
    count += 1
    print('Product number ' + str(count))

print('Saving in excel')

all_dcts = []
# Final function to get all macro nutritions from the given product pages.
def get_macros(product_url) :
    base_url = 'https://www.ah.nl/'
    url = base_url + product_url
    res = requests.get(url) 
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    tr = soup.select('tr')
  
    if len(tr) > 0: 
        tr.pop(0)
    tr_str = ''
    #Next part cleans up the output so it is usable to create a dictionary
    for i in tr:
        regex = re.compile('(\d+(\.\d+)?%)')
        clean_tr_string = re.sub(regex, ' ', str(i))
        a = clean_tr_string.replace('</td><td>', ' : ')
        regex1 = re.compile('\<(.*?)\>')
        c = re.sub(regex1, ' ', a)   
        tr_str += c
    tr_str = re.sub('    ', ': ', tr_str)
    tr_str = re.sub(r"\s+", " ", tr_str)
    tr_str = tr_str[:-1]
    tr_str = tr_str.split(': ')
    for i in tr_str:
        regex = re.compile(':/')
        i = re.sub(regex, '',str(i))
    convert_to_dct(tr_str)
    
    
# Function to create a dictionary
def convert_to_dct(a):
    it = iter(a)
    res_dct = dict(zip(it, it)) 
    toevoeging_link = {'Link' : 'www.ah.nl' + str(product_url)}
    toevoeging_link.update(res_dct)
    new_link = product_url.replace('/producten/product/wi', '')
    regex = re.compile('\d*/')
    newest = re.sub(regex, '', new_link)
    newstt = newest.replace('-', ' ')
    neewst = newstt.title()
    laatste = {'Product' : str(neewst)}
    laatste.update(toevoeging_link)
    laatste.update(toevoeging_link)
    all_dcts.append(laatste)
    
nummer = 0

for product_url in product_list: 
    time.sleep(0.1)
    get_macros(product_url)
    nummer += 1
    print('Laatste loop ' + str(nummer))
    

# Final part to save the data stored in the dictionary in excel.  
df = pd.DataFrame(data=all_dcts)
df.to_excel("All_macros_from_ah.xlsx", index=False,) 
