from urllib.parse import urljoin
from urllib.request import urlopen
from bs4 import BeautifulSoup
import psycopg2

# from pysqlite2 import dbapi2 as sqlite

# from urlparse import urljoin

# Create a list of words to ignore
ignorewords = {'the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'}


class Crawler:
    # initilize the crawler with the name of the database
    def __init__(self,):
        pass
        # self.con = sqlite.connect(dbname)

    def __del__(self):
        # self.con.close()
        return None

    def dbcommit(self):
        # self.con.commit()
        return None

    # Auxilliary function for getting an entry id and adding
    # it if it's not present
    def getentryid(self, table, field, value, createnew=True):
        return None

    # index an individual page

    def addtoindex(self, url, soup):
        print('Indexing %s' % url)

    # extract the text from an html page(no tags)
    def gettextonly(self, soup):
        return None

    # Separate the words by any non-whitespace character
    def separatewords(self, text):
        return None

    #     Return true if this url is already indexed
    def isindexed(self, url):
        return False

    #     Add a link between two pages

    def addlinkref(self, urlFrom, urlTo, linkText):
        pass

    #     Starting with a list of pages, do a breadth
    #   first search to the given depth, indexing pages as we go
    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urlopen(page)
                except:
                    print("Could not open %s" % page)
                    continue
                soup = BeautifulSoup(c.read(), features="html.parser")
                self.addtoindex(page, soup)
                links = soup('a')
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]
                        # remove location portion
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.add(url)
                            linkText = self.gettextonly(link)
                            self.addlinkref(page, url, linkText)

                self.dbcommit()
            pages = newpages

    #     Create the database tables

# crawler = Crawler('searchindex.db')
# pagelist = ['http://127.0.0.1:8000/me2ushop/']
# print(crawler.crawl(pagelist))
# crawler.createindextables()
