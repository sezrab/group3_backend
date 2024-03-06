# Needs to return a list of article objects
from acl_anthology import Anthology

# Instantiate the Anthology from the official repository, will look for updates when called
anthology = Anthology.from_repo(verbose=False)

myarticle = {}
myauthors = []

for paper in anthology.papers():
    # lots of entries don't have an abstract
    if paper.abstract != None:
        myarticle['title'] = paper.title._content.text
        myarticle['abstract'] = paper.abstract._content
        myarticle['url'] = paper.web_url
        for i in range(len(paper.authors)):
            name = paper.authors[i].first + ' ' + paper.authors[i].last
            myauthors.append(name)
        myarticle['authors'] = ', '.join(myauthors) # unsure how to format this
        
