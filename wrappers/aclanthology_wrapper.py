# Needs to return a list of article objects
from acl_anthology import Anthology

# Instantiate the Anthology from the official repository, will look for updates when called
anthology = Anthology.from_repo(verbose=False)

for paper in anthology.papers():
    if paper.abstract != None:
        print(paper.abstract)
    