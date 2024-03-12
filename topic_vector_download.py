import clipboard
from topic_classifier import paper_processor
# from topic_classifier import scraper
from wrappers.semantic_wrapper import getSemanticData
from datetime import datetime
from topic_classifier import utils

STOPWORD_SEARCH_TOP_PERCENT = 0.4
STOPWORD_OCCURRENCE_THRESHOLD = 0.6

input("Are you sure you want to run this script? (Press Enter to continue...) ")
input("This will take a long time to run. (Press Enter to continue...) ")
input("This will overwrite the existing topic vectors. (Press Enter to continue...) ")
input("So you're really sure... (Press Enter to continue...) ")
print("Okay, you're the boss.")

# load the topics.txt file
subtopics = utils.load_lines("topics.txt")

vf = utils.load_topic_vector_file(data_dir="topic_classifier/data/")

for topic in subtopics:
    print(f"Scraping topic '{topic}'...")
    abstracts = []
    papers = getSemanticData(topic, start_date=datetime(2020,1,1))
    abstracts += [paper.abstract for paper in papers]
    print(f"Analysing topic '{topic}'...")
    abstracts = " ".join(abstracts)
    tf = paper_processor.tf(abstracts)
    vf[topic] = tf

# The following code is used to identify stop words (?) specific to a given dataset.
# These might not actually be stop words, but rather common words that are not useful for distinguishing between topics.

common_word_counter = {}

total = len(vf.keys())

for topic in vf.keys():
    # sort the words by their weights
    words = sorted(vf[topic].items(), key=lambda x: x[1], reverse=True)
    n_words = len(words)

    # obtain the top 40% of the words
    stop_potential = int(STOPWORD_SEARCH_TOP_PERCENT * n_words)

    # increment the count of each word in the common_word_counter
    for word, weight in words[:stop_potential]:
        if word in common_word_counter:
            common_word_counter[word] += 1
        else:
            common_word_counter[word] = 1

# do the filtering
for word, count in common_word_counter.items():
    if count > STOPWORD_OCCURRENCE_THRESHOLD * total:
        # remove the word from the vocabulary
        for topic in vf.keys():
            vf[topic].pop(word, None)

utils.save_topic_vector_file(vf, data_dir="topic_classifier/data/")
