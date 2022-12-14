# scrapetools
Install using <pre>python -m pip install git+https://github.com/matt-manes/scrapeTools</pre>
Git must be installed and in your PATH.<br>
<br>
scrapeTools contains four modules: emailScraper, linkScraper, phoneScraper, and inputScraper.<br>
Only linkScraper contains a class.<br>
<br>
Basic usage:<br>
<pre>
from scrapeTools.emailScraper import scrapeEmails
from scrapeTools.phoneScraper import scrapePhoneNumbers
from scrapeTools.linkScraper import LinkScraper
from scrapeTools.inputScraper import scrapeInputs
import requests

url = 'https://somewebsite.com'
source = requests.get(url).text

emails = scrapeEmails(source)

phoneNumbers = scrapePhoneNumbers(source)

linkScraper = LinkScraper(source, url)
linkScraper.scrapePage()
#links can be accessed and filtered via the getLinks() function
sameSiteLinks = linkScraper.getLinks(sameSiteOnly=True)
sameSiteImageLinks =linkScraper.getLinks(linkType='img', sameSiteOnly=True)
externalImageLinks = linkScraper.getLinks(linkType='img', excludedLinks=sameSiteImageLinks)

#scrapeInputs() returns a tuple of BeautifulSoup Tag elements for various user input elements
forms, inputs, buttons, selects, textAreas = scrapeInputs(source)
</pre>
