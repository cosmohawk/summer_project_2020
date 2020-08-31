import sys

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

import pandas as pd


def get_webpage(url):
    '''
    Function wrapped around the urllib method "urlopen" to retrieve webpages.
    Provides an additional check for instances when urlopen returns None.

    Parameters
    ----------
    url : string
        The web address from which to retrieve a page.  

    Returns
    -------
    html : object
        A HTTPResponse object which contains the webpage as well as status
        response codes and page meta-data.
    '''
    html = urlopen(url)

    if html is None:
        Exception('urlopen request at '+url+' returned None.')
    
    return html

def parse_divs_in_webpage(webpage):
    '''
    Use BeautifulSoup to parse HTML in the webpage, and return all the "div"
    elements on the page.  

    Parameters
    ----------
    webpage : object
        A HTTPResponse object

    Returns
    -------
    div_list : list
        A list of all the div objects found using BeautifulSoup. 
    '''
    soup = BeautifulSoup(webpage, 'html.parser')
    div_list = []
    for div in soup.find_all('div', class_='holder'):
        div_list.append(div)
    
    return div_list

def get_handles_from_contents(contents):
    '''
    Use regex to identify twitter handles - which start with "@" - within the
    HTML of the div contents found using "parse_divs_in_webpage()".

    Parameters
    ----------
    contents : list object
        The parsed HTML contents of the page.  See `parse_divs_in_webpage()`
        for more.

    Results
    -------
    handles : list object
        A list of strings.  Each entry is the text preceded by an @ symbol,
        presumed to be a hashtag.  
    '''
    handles = re.findall(r'@(\w+)', str(contents))

    return handles

def iterate_func_over_pages(url, func):
    '''
    Facilitates execution of regex-based functions over multiple pages of 
    search results.

    Parameters
    ----------
    url : string
        The url of the search term, the page info will be appended to this.
    func : function
        Function containing regex used to extract items from parsed HTML.
        The output of func should be formatted as a list.
    args : tuple
        The arguments which are taken by func.  
    Returns
    -------
    complete_out : list
        List containing items retrieved from all pages by func.
    '''
    duplicate = False
    page_num = 0
    url += '&chunk='
    complete_out = []

    while not duplicate:
        webpage = get_webpage(url+str(page_num))
        page_contents = parse_divs_in_webpage(webpage)
        output = func(page_contents)
        
        duplicate = any(item in output for item in complete_out)

        if duplicate is False:
            complete_out.extend(output)
            page_num += 1
    
    return complete_out

def get_handles_by_keyword(kwd):
    '''
    Function which wraps around the webpage retrieval and parsing functions to
    provide a list of twitter handles for journalists relating to a topic 
    provided by `kwd`.

    Parameters
    ----------
    kwd : str
        String containing the search term to be used.  This should be a single
        word at present.
    
    Returns
    -------
    handle_list : list object
        A list of strings containing the twitter handles scraped over all pages of
        search results.
    '''
    kwd = kwd.replace(" ", "%20") # replace spaces in search keyword for use in URL

    url = r'https://www.journalism.co.uk/prof/?search='+kwd

    handle_list = iterate_func_over_pages(url, get_handles_from_contents)

    return handle_list