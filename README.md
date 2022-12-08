# scrapetools
Install using <pre>python -m pip install git+https://github.com/matt-manes/scrapetools</pre>
Git must be installed and in your PATH.<br>
<br>
scrapeTools contains three modules: emailScraper, linkScraper, and phoneScraper.<br>
Only linkScraper contains a class.<br>
<br>
Basic usage:<br>
<pre>
from scrapeTools.emailScraper import scrapeEmails
from scrapeTools.phoneScraper import scrapePhoneNumbers
from scrapeTools.linkScraper import LinkScraper
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
</pre>
