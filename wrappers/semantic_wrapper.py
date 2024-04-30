import requests
import datetime
from models.article import Article
from topic_classifier import tagger

# Define the API endpoint URL
url = "https://api.semanticscholar.org/graph/v1/paper"
api_key = "K1V9sxPoyV8qu2JcxMx6e3FDi2x3vJVM4kLD3PJO"
# publicationDate:asc


# Define headers with API key
headers = {"x-api-key": api_key}


# waiting for API key from Semantic Scholar (5/3/24)
def getSemanticData(
    query, start_date, sort="publicationDate:asc", CONFIDENCE_THRESH=0.15
):
    """
    Retrieves semantic data based on the provided parameters.

    Args:
        start_date (datetime): A datetime object representing the start date for the query.
        query (str): The query string.
        sort (str): The sorting criteria, for example "publicationDate:asc", "citationCount:desc", etc.

    Returns:
        None

    Raises:
        None
    """
    publicationDateOrYear = start_date.strftime("%Y-%m-%d") + ":"
    # More specific query parameter
    query_params = {
        "query": query,
        "sort": sort,
        "publicationDateOrYear": publicationDateOrYear,
        "fields": "paperId,title,abstract,authors,publicationDate,fieldsOfStudy,url",
        "limit": 100,
    }
    try:
        # Send the API request
        response = requests.get(
            url + "/search", params=query_params, headers=headers, timeout=5
        )
    except requests.exceptions.RequestException as e:
        return []
    # Check response status
    if response.status_code == 200:
        response_data = response.json()
        article_objs = []
        if response_data.get("data") is None:
            return []
        for paper in response_data["data"]:
            if type(paper["publicationDate"]) == str:
                paper["publicationDate"] = datetime.datetime.strptime(
                    paper["publicationDate"], "%Y-%m-%d"
                )
            if paper["publicationDate"] is None or paper["abstract"] is None:
                continue
            tags = tagger.tag_abstract(
                paper["abstract"],
                thresh=CONFIDENCE_THRESH,
                data_folder="topic_classifier/data/",
            )
            obj = Article(
                title=paper["title"],
                abstract=paper["abstract"],
                authors=[a_dict["name"] for a_dict in paper["authors"]],
                published=paper["publicationDate"],
                tags=tags,
                url=paper["url"],
                source="Semantic Scholar",
            )
            article_objs.append(obj)

        return article_objs

    else:
        print("BAD RESPONSE FROM SEMANTIC SCHOLAR API")
        print(response.status_code)

        raise Exception("Failed to retrieve data from Semantic Scholar API")


if __name__ == "__main__":
    pprs = getSemanticData(
        "BERT", start_date=datetime.datetime(2024, 1, 1), sort="publicationDate:asc"
    )
