from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup

class LinkScraper:
    def __init__(self, htmlSrc:str, pageUrl:str):
        self.soup = BeautifulSoup(htmlSrc, features='html.parser')
        self.url = urlparse(pageUrl)
        self.pageLinks = []
        self.imgLinks = []
        self.scriptLinks = []
    
    def _formatRelativeLinks(self, links:list[str])->list[str]:
        """ Parses list of links and constructs a full url\n
        according to self.url for the ones that don't have a\n
        'netloc' property returned by urlparse.\n
        Full urls are returned unedited other than stripping any
        leading or trailing forward slashes."""
        formattedLinks = []
        for link in links:
            link = link.strip(' \n\t\r').replace('"','').replace('\\','')
            parsedUrl = urlparse(link)
            if all(ch not in link for ch in '@ '):
                parsedUrl = list(parsedUrl)
                if parsedUrl[0] == '':
                    parsedUrl[0] = 'https'
                if parsedUrl[1] == '':
                    parsedUrl[1] = self.url.netloc
                formattedLinks.append(urlunparse(parsedUrl).strip('/'))
        return formattedLinks
    
    def _removeDuplicates(self, obj:list)->list:
        """ Removes duplicate members. """
        return list(set(obj))
    
    def _processLinks(self, links:list[str])->list[str]:
        """ Formats relative links, removes duplicates, and sorts in alphabetical order. """
        return sorted(self._removeDuplicates(self._formatRelativeLinks(links)))
    
    def _findAll(self, tagName:str, attributeName:str)->list[str]:
        """ Finds all results according to tagName and attributeName.\n
        Filters out fragments."""
        return [tag.get(attributeName) for tag in self.soup.find_all(tagName, recursive=True) if tag.get(attributeName) is not None and '#' not in tag.get(attributeName)]
    
    def _filterSameSite(self, links:list[str])->list[str]:
        """ Filters out links that don't match self.url.netloc """
        return [link for link in links if urlparse(link).netloc == self.url.netloc]
        
    def scrapePageLinks(self):
        """ Scrape links from href attribute of <a> and <link> tags. """
        links = self._findAll('a', 'href')
        links.extend(self._findAll('link', 'href'))
        self.pageLinks = self._processLinks(links)
    
    def scrapeImgLinks(self):
        """ Scrape links from src attribute of <img> tags. """
        self.imgLinks = self._processLinks(self._findAll('img', 'src')+self._findAll('img', 'data-src'))
    
    def scrapeScriptLinks(self):
        """ Scrape script links from src attribute of <script> tags. """
        self.scriptLinks = self._processLinks(self._findAll('script', 'src'))
    
    def scrapePage(self):
        """ Scrape all link types. """
        for scrape in [self.scrapePageLinks,self.scrapeImgLinks,self.scrapeScriptLinks]:
            scrape()
    
    def getLinks(self, linkType:str='all', sameSiteOnly:bool=False, excludedLinks:list[str]=None)->list[str]:
        """ Returns a list of urls found on page.\n
        'linkType' can be 'all', 'page', 'img', or 'script'.
        'sameSiteOnly' removes any external urls.\n
        'excludedLinks' can be a list of urls to filter out of the return results.\n
        Useful for excluding duplicates when recursively scraping a website.\n
        Can also be used with linkType='all' to get two link types in one call:\n
        e.g. links = linkScraper.getLinks(linkType = 'all', excludedLinks = linkScraper.scriptLinks)\n
        will return page links and img links."""
        match linkType:
            case 'all':
                links = self._removeDuplicates(self.pageLinks + self.imgLinks + self.scriptLinks)
            case 'page':
                links = self.pageLinks
            case 'img':
                links = self.imgLinks
            case 'script':
                links = self.scriptLinks
        if sameSiteOnly:
            links = self._filterSameSite(links)
        if excludedLinks:
            links = [link for link in links if link not in excludedLinks]
        return sorted(links)

    