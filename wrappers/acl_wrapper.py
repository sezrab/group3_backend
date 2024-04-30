from acl_anthology import Anthology
from models.article import Article
from datetime import datetime
from topic_classifier import tagger

months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def getMonthInString(string):
    for i in range(len(months)):
        if months[i].lower() in string.lower():
            return i + 1
    return -1


def getAclAnthologyData(start_date, end_date=None, CONFIDENCE_THRESH=0.15):
    # Instantiate the Anthology, looks for updates when called
    anthology = Anthology.from_repo(verbose=False)

    articles = []

    # get all papers from the anthology
    # (papers is a generator, so we can iterate over it)

    lastYear = 0
    for paper in anthology.papers():
        published_year = paper.year
        published_month = paper.month
        published_day = 1

        if paper.language != None:
            continue

        if published_month is None:
            published_month = 1

        try:
            published_month = int(published_month)
        except (ValueError, TypeError):
            published_month = getMonthInString(published_month)
            if published_month == -1:
                published_month = 1
        try:
            published_year = int(published_year)
        except (ValueError, TypeError):
            continue

        published_date = datetime(published_year, published_month, published_day)

        if published_date < start_date:
            continue

        if end_date is not None and published_date > end_date:
            break

        if published_year != lastYear:
            lastYear = published_year
            print(f"Processing papers from {published_year}")

        title = str(paper.title)

        if paper.abstract is None:
            continue
        abstract = paper.abstract.as_text()
        url = paper.web_url

        authors = [f"{author.first} {author.last}" for author in paper.authors]

        tags = tagger.tag_abstract(
            abstract, thresh=CONFIDENCE_THRESH, data_folder="topic_classifier/data/"
        )
        article = Article(
            title=title,
            source="ACL Anthology",
            abstract=abstract,
            url=url,
            authors=authors,
            tags=tags,
            published=published_date,
        )
        articles.append(article)

    print(f"Total number of papers processed: {len(articles)}")
    return articles


if __name__ == "__main__":
    search_query = "machine learning"
    articles = getAclAnthologyData(search_query)
    for article in articles:
        print(article)
        print()
