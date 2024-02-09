from . import paper_processor
from . import utils


def tag_abstract(abstract, thresh=0.3, data_folder="topic_classifier/data/"):
    """
    Given an abstract, returns a list of topics and their corresponding scores based on their similarity to the abstract.

    Parameters:
    abstract (str): The abstract to be tagged.
    thresh (float): The threshold for the cosine similarity score. Topics with a score higher than this value will be returned.

    Returns:
    list: A list of tuples, where each tuple contains a topic and its corresponding similarity score.
    """

    # TODO: Generate stop words on a per-supertopic (supertopic, eg NLP) basis. For each topic, get the set of the N most common words, and the intersection of these sets is the stop words for that topic.
    # The above is just brainstorming
    # https://stackoverflow.com/a/49121636
    # This is better ^

    tf = paper_processor.tf(abstract)

    tvs = utils.load_topic_vector_file(data_dir=data_folder)

    topics = []
    for topic, tv in tvs.items():
        score = paper_processor.cosine_similarity(tf, tv)
        topics.append((topic, score))

    # # filter out topics with thresh
    # topics = [(topic, score) for topic, score in topics if score > thresh]

    # get mean score
    mean_score = sum([score for _, score in topics]) / len(topics)

    # get standard deviation
    std_dev = (sum([(score - mean_score)**2 for _,
               score in topics]) / len(topics))**0.5

    # get scores more than 2 standard deviation above the mean
    topics = [(topic, score) for topic, score in topics if score >
              mean_score + 1.3*std_dev and score > thresh]

    # sort topics by score
    topics.sort(key=lambda x: x[1], reverse=True)

    # return topic titles
    # return [topic for topic, _ in topics]

    return topics
