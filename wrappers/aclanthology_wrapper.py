from acl_anthology import Anthology
from models.article import Article
from datetime import datetime

def getAclAnthologyData(search_query):
    # Instantiate the Anthology, looks for updates when called
    anthology = Anthology.from_repo(verbose=False)

    articles = []
    for paper in anthology.papers():
        if search_query.lower() in paper.title.lower() or search_query.lower() in paper.abstract.content.lower():
            title = str(paper.title)
            abstract = paper.abstract.content if paper.abstract.content else ""
            url = paper.web_url
            authors = [f"{author.first} {author.last}" for author in paper.authors]
            published_year = paper.year
            published_month = paper.month
            month_number = datetime.strptime(published_month, '%B').month
            published_date = datetime(int(published_year), month_number, 1) #months is broked

            article = Article(
                title=title,
                abstract=abstract,
                url=url,
                authors=authors,
                tags="", # don't know what to put here (i'm just a boy)
                published=published_date
            )
            articles.append(article)

    print(f"Total number of papers processed: {len(articles)}")
    return articles