from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup


class LinkScraper:
    def __init__(self, htmlSrc: str, pageUrl: str):
        self.soup = BeautifulSoup(htmlSrc, features="html.parser")
        self.parsedUrl = urlparse(pageUrl)
        self.pageLinks = []
        self.imgLinks = []
        self.scriptLinks = []

    def formatRelativeLinks(self, links: list[str]) -> list[str]:
        """Parses list of links and constructs a full url
        according to self.parsedUrl for the ones that don't have a
        'netloc' property returned by urlparse.

        Full urls are returned unedited other than stripping any
        leading or trailing forward slashes."""
        formattedLinks = []
        for link in links:
            link = (
                link.strip(" \n\t\r")
                .replace('"', "")
                .replace("\\", "")
                .replace("'", "")
            )
            parsedUrl = urlparse(link)
            if all(ch not in link for ch in "@ "):
                parsedUrl = list(parsedUrl)
                if parsedUrl[0] == "":
                    parsedUrl[0] = self.parsedUrl.scheme
                if parsedUrl[1] == "":
                    parsedUrl[1] = self.parsedUrl.netloc
                formattedLinks.append(urlunparse(parsedUrl).strip("/"))
        return formattedLinks

    def removeDuplicates(self, obj: list) -> list:
        """Removes duplicate members."""
        return list(set(obj))

    def processLinks(self, links: list[str]) -> list[str]:
        """Formats relative links, removes duplicates, and sorts in alphabetical order."""
        return sorted(self.removeDuplicates(self.formatRelativeLinks(links)))

    def findAll(self, tagName: str, attributeName: str) -> list[str]:
        """Finds all results according to tagName and attributeName.\n
        Filters out fragments."""
        return [
            tag.get(attributeName)
            for tag in self.soup(tagName, recursive=True)
            if tag.get(attributeName) is not None and "#" not in tag.get(attributeName)
        ]

    def filterSameSite(self, links: list[str]) -> list[str]:
        """Filters out links that don't match self.parsedUrl.netloc"""
        return [
            link
            for link in links
            if urlparse(link).netloc.strip("www.")
            == self.parsedUrl.netloc.strip("www.")
        ]

    def scrapePageLinks(self):
        """Scrape links from href attribute of <a> and <link> tags."""
        links = self.findAll("a", "href")
        links.extend(self.findAll("link", "href"))
        self.pageLinks = self.processLinks(links)

    def scrapeImgLinks(self):
        """Scrape links from src attribute of <img> tags."""
        self.imgLinks = self.processLinks(
            self.findAll("img", "src") + self.findAll("img", "data-src")
        )

    def scrapeScriptLinks(self):
        """Scrape script links from src attribute of <script> tags."""
        self.scriptLinks = self.processLinks(self.findAll("script", "src"))

    def scrapePage(self):
        """Scrape all link types."""
        for scrape in [
            self.scrapePageLinks,
            self.scrapeImgLinks,
            self.scrapeScriptLinks,
        ]:
            scrape()
        self.mergeImageLinksFromNonImgTags()

    def mergeImageLinksFromNonImgTags(self):
        """Finds links in self.scriptLinks and self.pageLinks
        that have one of these image file extensions and adds them
        to self.imgLinks"""
        formats = [
            ".jpg",
            ".jpeg",
            ".png",
            ".svg",
            ".bmp",
            ".tiff",
            ".pdf",
            ".eps",
            ".gif",
            ".jfif",
            ".webp",
            ".heif",
            ".avif",
            ".bat",
            ".bpg",
        ]
        for link in self.scriptLinks + self.pageLinks:
            if any(ext in link for ext in formats):
                self.imgLinks.append(link)
        self.imgLinks = sorted(self.removeDuplicates(self.imgLinks))

    def getLinks(
        self,
        linkType: str = "all",
        sameSiteOnly: bool = False,
        excludedLinks: list[str] = None,
    ) -> list[str]:
        """Returns a list of urls found on the page.

        :param linkType: Can be 'all', 'page', 'img', or 'script'.

        :param sameSiteOnly: Excludes external urls if True.

        :param excludedLinks: A list of urls to filter out of the results.
        Useful for excluding duplicates when recursively scraping a website.
        Can also be used with linkType='all' to get two link types in one call:

        e.g. links = linkScraper.getLinks(linkType = 'all', excludedLinks = linkScraper.scriptLinks)
        will return page links and img links."""
        match linkType:
            case "all":
                links = self.removeDuplicates(
                    self.pageLinks + self.imgLinks + self.scriptLinks
                )
            case "page":
                links = self.pageLinks
            case "img":
                links = self.imgLinks
            case "script":
                links = self.scriptLinks
        if sameSiteOnly:
            links = self.filterSameSite(links)
        if excludedLinks:
            links = [link for link in links if link not in excludedLinks]
        return sorted(links)
